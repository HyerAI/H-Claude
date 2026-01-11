"""Test validation module - prevents trivial/cheating tests.

This module validates AI-generated tests to ensure they are meaningful:
- Detects trivial assertions (assert True, assert 1 == 1)
- Detects empty tests (only pass, no asserts)
- Verifies target module import
- Analyzes failure reasons (syntax vs assertion errors)

The validation runs AFTER the RED phase confirms a failing test,
but BEFORE accepting the test as valid for the GREEN phase.
"""

import ast
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class ValidationResult:
    """Result of test validation.

    Attributes:
        valid: Whether the test passes validation.
        errors: List of validation errors (make test invalid).
        warnings: List of warnings (informational, don't invalidate).
    """

    valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


class TestValidator:
    """Validates test files using AST analysis.

    Performs multiple checks:
    - Trivial assertion detection
    - Empty test detection
    - Module import verification
    - Failure reason classification

    Example:
        validator = TestValidator("tests/test_example.py", target_module="mymodule")
        trivial = validator.check_trivial_assertions()
        empty = validator.check_empty_tests()
        imports = validator.check_imports()
    """

    def __init__(
        self,
        test_path: str,
        target_module: Optional[str] = None,
    ) -> None:
        """Initialize TestValidator.

        Args:
            test_path: Path to the test file.
            target_module: Name of the module being tested.
        """
        self.test_path = test_path
        self.target_module = target_module
        self._ast: Optional[ast.Module] = None

    def _parse_ast(self) -> ast.Module:
        """Parse the test file into AST."""
        if self._ast is None:
            source = Path(self.test_path).read_text()
            self._ast = ast.parse(source)
        return self._ast

    def _is_constant(self, node: ast.expr) -> bool:
        """Check if node is a constant value."""
        return isinstance(node, ast.Constant)

    def _is_trivial_assertion(self, node: ast.Assert) -> tuple[bool, str]:
        """Check if an assertion is trivial.

        Returns:
            Tuple of (is_trivial, description).
        """
        test_node = node.test

        # assert True - always passes, trivial
        if isinstance(test_node, ast.Constant) and test_node.value is True:
            return (True, f"line {node.lineno}: assert True")

        # NOTE: assert False is NOT trivial - it's a valid "force failure" pattern
        # used to ensure tests fail in RED phase before implementation exists

        # assert <literal> == <literal>
        if isinstance(test_node, ast.Compare):
            left = test_node.left
            comparators = test_node.comparators

            if self._is_constant(left):
                if all(self._is_constant(c) for c in comparators):
                    return (True, f"line {node.lineno}: literal comparison")

        return (False, "")

    def check_trivial_assertions(self) -> list[str]:
        """Find trivial assertions in the test file.

        Returns:
            List of trivial assertion descriptions with line numbers.
        """
        tree = self._parse_ast()
        trivial = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Assert):
                is_trivial, desc = self._is_trivial_assertion(node)
                if is_trivial:
                    trivial.append(desc)

        return trivial

    def _get_test_functions(self) -> list[ast.FunctionDef | ast.AsyncFunctionDef]:
        """Get all test functions from the AST.

        Detects both sync (def test_*) and async (async def test_*) functions.
        """
        tree = self._parse_ast()
        test_funcs = []

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.name.startswith("test_"):
                    test_funcs.append(node)

        return test_funcs

    def _is_empty_body(self, body: list[ast.stmt]) -> bool:
        """Check if function body is effectively empty."""
        # Filter out docstrings and pass
        meaningful = []
        for stmt in body:
            # Skip docstrings
            if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant):
                if isinstance(stmt.value.value, str):
                    continue
            # Skip pass
            if isinstance(stmt, ast.Pass):
                continue
            meaningful.append(stmt)

        return len(meaningful) == 0

    def _has_assertion(self, func: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
        """Check if function has any assert statements or pytest.raises context managers.

        Recognizes:
        - assert statements
        - with pytest.raises(...) context managers
        """
        for node in ast.walk(func):
            # Standard assert statement
            if isinstance(node, ast.Assert):
                return True

            # pytest.raises context manager: with pytest.raises(...)
            if isinstance(node, ast.With):
                for item in node.items:
                    ctx = item.context_expr
                    if isinstance(ctx, ast.Call):
                        func_node = ctx.func
                        # Match pytest.raises
                        if isinstance(func_node, ast.Attribute):
                            if func_node.attr == "raises":
                                if isinstance(func_node.value, ast.Name):
                                    if func_node.value.id == "pytest":
                                        return True
        return False

    def check_empty_tests(self) -> list[str]:
        """Find empty test functions.

        Returns:
            List of empty test function names.
        """
        empty = []

        for func in self._get_test_functions():
            if self._is_empty_body(func.body):
                empty.append(f"{func.name}: only contains pass/docstring")
            elif not self._has_assertion(func):
                empty.append(f"{func.name}: no assert statements")

        return empty

    def check_imports(self) -> dict:
        """Check if target module is imported.

        Returns:
            Dict with import status and details.
        """
        if not self.target_module:
            return {"has_import": True, "reason": "no target module specified"}

        tree = self._parse_ast()
        module_name = self.target_module.replace(".py", "")

        for node in ast.walk(tree):
            # import X
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name == module_name:
                        return {"has_import": True, "style": "import"}

            # from X import Y or from .X import Y
            if isinstance(node, ast.ImportFrom):
                if node.module:
                    # Handle both exact match and relative imports
                    if node.module == module_name or node.module.endswith(f".{module_name}"):
                        return {"has_import": True, "style": "from"}
                    # Handle 'from .module import func' style
                    if module_name in node.module:
                        return {"has_import": True, "style": "from"}

        return {"has_import": False, "reason": f"module '{module_name}' not imported"}

    def check_failure_reason(self, pytest_output: str) -> dict:
        """Classify the failure reason from pytest output.

        Args:
            pytest_output: Raw output from pytest run.

        Returns:
            Dict with type and expected status.
        """
        output_lower = pytest_output.lower()

        # Check for syntax errors
        if "syntaxerror" in output_lower:
            return {
                "type": "syntax_error",
                "expected": False,
                "reason": "Test has syntax errors",
            }

        # Check for import errors (expected in RED phase)
        if "modulenotfounderror" in output_lower or "importerror" in output_lower:
            # Check if it's for our target module (expected)
            if self.target_module and self.target_module in pytest_output:
                return {
                    "type": "import_error",
                    "expected": True,
                    "reason": f"Target module '{self.target_module}' not found (expected in RED)",
                }
            return {
                "type": "import_error",
                "expected": True,
                "reason": "Module import error",
            }

        # Check for assertion errors (expected - test correctly fails)
        if "assertionerror" in output_lower:
            return {
                "type": "assertion_error",
                "expected": True,
                "reason": "Test assertion failed (expected in RED)",
            }

        # Check for collection errors (test code broken)
        if "error collecting" in output_lower:
            return {
                "type": "syntax_error",
                "expected": False,
                "reason": "Test collection failed (test code broken)",
            }

        # Default: unknown failure
        return {
            "type": "unknown",
            "expected": True,
            "reason": "Unknown failure type",
        }

    def validate(self) -> ValidationResult:
        """Run all validation checks.

        Returns:
            ValidationResult with overall status.
        """
        errors = []
        warnings = []

        # Check trivial assertions
        trivial = self.check_trivial_assertions()
        if trivial:
            errors.extend([f"Trivial assertion: {t}" for t in trivial])

        # Check empty tests
        empty = self.check_empty_tests()
        if empty:
            errors.extend([f"Empty test: {e}" for e in empty])

        # Check imports (warning only - module may not exist in RED phase)
        imports = self.check_imports()
        if not imports.get("has_import", True):
            warnings.append(f"Missing import: {imports.get('reason', 'unknown')}")

        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
        )


def validate(test_path: str, target_module: Optional[str] = None) -> ValidationResult:
    """Validate a test file.

    Main entry point for test validation.

    Args:
        test_path: Path to the test file.
        target_module: Name of the module being tested.

    Returns:
        ValidationResult with validation status and messages.
    """
    validator = TestValidator(test_path, target_module)
    return validator.validate()
