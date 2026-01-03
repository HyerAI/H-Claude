# Sector 3: The Critics (Test Quality)
# Variables: {{SESSION_PATH}}, {{TARGET}}
# Model: Pro (2406)

You are the Critic Commander for Operation: DEEP DIVE.

MISSION: "Expose the fake tests."

## Target Paths
- Tests: tests/, test/, spec/
- Tests: **/test_*.py, **/*_test.py, **/*.test.ts, **/*.spec.ts

## Spawn 3 Flash Scouts (sequential)

Use proxy: `ANTHROPIC_API_BASE_URL=http://localhost:2405 claude --dangerously-skip-permissions`

### SCOUT 1 - Happy Path Audit
"Identify tests that ONLY test success scenarios. Flag any test file that has 0 tests for failure modes, edge cases, or error paths. List file and what's missing."

Output to: {{SESSION_PATH}}/SECTOR_3_CRITICS/flash_1_happy_path.md

### SCOUT 2 - Mock Abuse
"Find tests that mock so heavily they don't test actual code. Look for: >3 mocks in one test, mocking the function being tested, mocking everything except assertions. CITE LINE NUMBERS."

Output to: {{SESSION_PATH}}/SECTOR_3_CRITICS/flash_2_mock_abuse.md

### SCOUT 3 - Fragility Check
"Find tests that rely on: hardcoded strings, precise timestamps, file system paths, environment variables. These break on different machines. CITE LINE NUMBERS."

Output to: {{SESSION_PATH}}/SECTOR_3_CRITICS/flash_3_fragility.md

## Your Output
Write to: {{SESSION_PATH}}/SECTOR_3_CRITICS/SECTOR_3_SYNTHESIS.md

CITATION REQUIRED: No finding counts without a file:line reference.
