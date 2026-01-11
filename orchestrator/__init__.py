"""H-Conductor orchestrator package.

This package provides the core orchestration components for H-Conductor:
- Task queue models and validation
- Git worktree isolation for safe worker execution
- Disk space safety checks
- Logging configuration
- DNA drift check (NorthStar traceability validation)
- Proxy configuration for model hierarchy
- Prompt templates for model interactions
- Model dispatcher for routing tasks to appropriate proxies
"""

__version__ = "0.1.0"

from orchestrator.config import ModelConfig, PROXIES, get_proxy_config, ConfigError
from orchestrator.prompts import (
    PromptTemplate,
    TEMPLATES,
    get_prompt,
    TemplateNotFoundError,
)
from orchestrator.dispatcher import (
    ModelDispatcher,
    check_proxy_health,
    check_all_proxies,
    HealthCheckResult,
    AllProxiesHealthResult,
    DispatchResult,
    ParsedResponse,
    UnknownTaskTypeError,
    ParseError,
)
from orchestrator.models import TaskModel, QueueModel, TaskStatus
from orchestrator.validator import validate_queue
from orchestrator.logging_config import setup_logging
from orchestrator.disk_check import check_disk_space, DiskSpaceError
from orchestrator.worktree import (
    WorktreeManager,
    WorktreeCreateError,
    WorktreeCleanupError,
    WorktreeMergeError,
    MergeResult,
    find_orphaned_worktrees,
    cleanup_orphaned_worktrees,
    startup_recovery,
)
from orchestrator.dna_check import (
    parse_northstar,
    normalize_goal,
    check_lineage,
    validate_queue_dna,
    check_task_before_merge,
    LineageResult,
    DNAValidationResult,
    MergeGateResult,
    NorthStarError,
    TaskNotFoundError,
)
from orchestrator.pytest_runner import (
    PytestRunner,
    PytestResult,
    TestStatus,
)
from orchestrator.tdd_cycle import (
    TDDCycle,
    CycleState,
    TDDCycleExecutor,
    TDDFullCycleRunner,
    RedResult,
    GreenResult,
    RefactorResult,
    CycleResult,
    InvalidTransitionError,
    InvalidTestError,
    NeedsRetryError,
    DispatchError,
    MaxRetriesExceeded,
)
from orchestrator.retry_policy import RetryPolicy
from orchestrator.escalation import EscalationPolicy, EscalationResult
from orchestrator.validate_test import (
    validate,
    ValidationResult,
    TestValidator,
)
from orchestrator.qa_agent import (
    QAAgent,
    ReviewResult,
    ReviewIssue,
    ReviewCategory,
    format_feedback,
    save_feedback,
)
from orchestrator.memory_agent import (
    MemoryAgent,
    MemoryUpdateResult,
    format_action_entry,
    get_next_active_phases,
)
from orchestrator.task_selector import TaskSelector
from orchestrator.queue_manager import QueueManager
from orchestrator.execution import (
    ExecutionContext,
    ExecutionResult,
    TaskPipeline,
    execution_loop,
    stage_create_worktree,
    stage_run_tdd,
    stage_qa_review,
    stage_dna_check,
    stage_merge,
    stage_update_memory,
    stage_cleanup,
    StageError,
)
from orchestrator.cli import (
    cli_main,
    status_command,
    queue_command,
)

__all__ = [
    # Package version
    "__version__",
    # Proxy configuration
    "ModelConfig",
    "PROXIES",
    "get_proxy_config",
    "ConfigError",
    # Prompt templates
    "PromptTemplate",
    "TEMPLATES",
    "get_prompt",
    "TemplateNotFoundError",
    # Model dispatcher
    "ModelDispatcher",
    "check_proxy_health",
    "check_all_proxies",
    "HealthCheckResult",
    "AllProxiesHealthResult",
    "DispatchResult",
    "ParsedResponse",
    "UnknownTaskTypeError",
    "ParseError",
    # Queue models
    "TaskModel",
    "QueueModel",
    "TaskStatus",
    "validate_queue",
    # Logging
    "setup_logging",
    # Disk check
    "check_disk_space",
    "DiskSpaceError",
    # Worktree management
    "WorktreeManager",
    "WorktreeCreateError",
    "WorktreeCleanupError",
    "WorktreeMergeError",
    "MergeResult",
    "find_orphaned_worktrees",
    "cleanup_orphaned_worktrees",
    "startup_recovery",
    # DNA drift check
    "parse_northstar",
    "normalize_goal",
    "check_lineage",
    "validate_queue_dna",
    "check_task_before_merge",
    "LineageResult",
    "DNAValidationResult",
    "MergeGateResult",
    "NorthStarError",
    "TaskNotFoundError",
    # PytestRunner (T001-T002)
    "PytestRunner",
    "PytestResult",
    "TestStatus",
    # TDDCycle (T003-T009)
    "TDDCycle",
    "CycleState",
    "TDDCycleExecutor",
    "TDDFullCycleRunner",
    "RedResult",
    "GreenResult",
    "RefactorResult",
    "CycleResult",
    "InvalidTransitionError",
    "InvalidTestError",
    "NeedsRetryError",
    "DispatchError",
    "MaxRetriesExceeded",
    # RetryPolicy (T007)
    "RetryPolicy",
    # EscalationPolicy (T010)
    "EscalationPolicy",
    "EscalationResult",
    # Test validation (PHASE-004)
    "validate",
    "ValidationResult",
    "TestValidator",
    # QA Agent (PHASE-007)
    "QAAgent",
    "ReviewResult",
    "ReviewIssue",
    "ReviewCategory",
    "format_feedback",
    "save_feedback",
    # Memory Agent (PHASE-008)
    "MemoryAgent",
    "MemoryUpdateResult",
    "format_action_entry",
    "get_next_active_phases",
    # Execution (PHASE-009)
    "TaskSelector",
    "QueueManager",
    "ExecutionContext",
    "ExecutionResult",
    "TaskPipeline",
    "execution_loop",
    "stage_create_worktree",
    "stage_run_tdd",
    "stage_qa_review",
    "stage_dna_check",
    "stage_merge",
    "stage_update_memory",
    "stage_cleanup",
    "StageError",
    # CLI (PHASE-010)
    "cli_main",
    "status_command",
    "queue_command",
]
