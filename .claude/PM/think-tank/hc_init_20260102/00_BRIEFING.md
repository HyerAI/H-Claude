# Problem Briefing: H-Claude Init System

## The Decision/Problem

H-Claude template needs an initialization phase that:
1. Sets up folder structure
2. Validates proxy configurations (API keys)
3. Checks proxy health (are they running?)
4. Verifies Claude CLI connectivity
5. Reports status to user

Currently users must follow manual steps in GET_STARTED.md.

## Chosen Approach

**Hybrid Solution:**
- `hc-init` shell script for setup and manual checks
- Claude Code hook for automatic session-start validation

## Constraints

| Constraint | Type | Source |
|------------|------|--------|
| Linux/Mac support required | MUST | User environment |
| No additional runtime deps | SHOULD | KISS principle |
| Non-destructive (don't overwrite existing) | MUST | Safety |
| Clear error messages | MUST | UX |
| Works offline (except proxy health) | SHOULD | Flexibility |

## Success Criteria

1. New user can run `./hc-init` and get working environment
2. Existing user sees status on session start via hook
3. Clear actionable errors when something is wrong
4. Script is idempotent (safe to run multiple times)
