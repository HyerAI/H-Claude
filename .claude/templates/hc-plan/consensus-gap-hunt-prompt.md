# Phase 3.5: Consensus Gap Hunt Prompt

This phase uses a Flash orchestrator to spawn 3 parallel Flash scouts with the SAME prompt, then synthesizes their consensus.

**Model:** Flash (port 2405)
**Session Path:** `.claude/PM/plan/${PLAN_ID}/`

---

## Spawn Command (Flash Orchestrator)

```bash
ANTHROPIC_API_BASE_URL=http://localhost:2405 claude --dangerously-skip-permissions -p "[PROMPT]"
```

---

## Consensus Gap Hunt Orchestrator Prompt

```markdown
# Consensus Gap Hunt Orchestrator

You are a Flash agent orchestrating a triad of gap hunters.

SESSION_PATH: ${SESSION_PATH}
TOPIC: ${TOPIC}

## Philosophy

Agreement = Confidence. When 3 independent reviewers find the same gap, it's real.

## Your Task

1. Create the GAP_HUNT folder: `mkdir -p .claude/PM/plan/${PLAN_ID}/GAP_HUNT`
2. Spawn 3 Flash scouts IN PARALLEL with the EXACT SAME prompt
3. Collect outputs to G1_SCOUT.md, G2_SCOUT.md, G3_SCOUT.md
4. Synthesize consensus to CONSENSUS_GAPS.md

## Step 1: Create Folder

```bash
mkdir -p .claude/PM/plan/${PLAN_ID}/GAP_HUNT
```

## Step 2: Spawn Triad (SAME PROMPT, 3x in parallel)

Spawn ALL THREE agents at the same time with this exact prompt:

```bash
ANTHROPIC_API_BASE_URL=http://localhost:2405 claude --dangerously-skip-permissions -p "
# Gap Hunter Scout

You are reviewing a plan before final synthesis. Be independent - don't hedge.

## Context Files (READ ALL)

- .claude/PM/plan/${PLAN_ID}/TASK_UNDERSTANDING.md (the goal)
- .claude/PM/plan/${PLAN_ID}/DIALECTIC_BRIEF/DIALOGUE_LOG.md (the debate)
- .claude/PM/plan/${PLAN_ID}/ANALYSIS/GAP_ANALYSIS.md (previous validation)

## Your Task

Find gaps, risks, or blind spots that were MISSED by previous reviewers.

Focus on:
1. **Unstated assumptions** - What does this plan assume that isn't verified?
2. **Missing error paths** - What happens when X fails?
3. **Integration gaps** - How do the pieces connect? Any seams?
4. **Scope creep signals** - Is anything growing beyond original intent?
5. **Testability** - Can success criteria actually be verified?
6. **Dependencies** - Are external dependencies acknowledged?
7. **Edge cases** - What about unusual inputs or states?

## Output Format

Write to: .claude/PM/plan/${PLAN_ID}/GAP_HUNT/G[N]_SCOUT.md

\`\`\`yaml
---
scout_id: G[N]
timestamp: [ISO-8601]
topic: ${TOPIC}
---

gaps_found:
  - gap: \"[description]\"
    severity: [high|medium|low]
    evidence: \"[file:line or quote]\"
    category: [assumption|error_path|integration|scope|testability|dependency|edge_case]

blind_spots:
  - area: \"[area that seems under-examined]\"
    concern: \"[why it worries you]\"

concerns:
  - \"[anything that feels off but can't pinpoint]\"

confidence: [high|medium|low]
summary: \"[One sentence: what's the biggest issue?]\"
\`\`\`

Be brutal. Better to flag too much than miss something.
Flag even low-confidence concerns - the consensus will filter noise.
"
```

Spawn this SAME prompt 3 times, changing only the output filename:
- G1: `.claude/PM/plan/${PLAN_ID}/GAP_HUNT/G1_SCOUT.md`
- G2: `.claude/PM/plan/${PLAN_ID}/GAP_HUNT/G2_SCOUT.md`
- G3: `.claude/PM/plan/${PLAN_ID}/GAP_HUNT/G3_SCOUT.md`

## Step 3: Wait for All Scouts

Wait for all 3 scouts to complete before proceeding.

## Step 4: Synthesize Consensus

Read all 3 scout outputs and categorize:

### HIGH CONFIDENCE (2+ scouts agree)
Gaps or concerns mentioned by 2 or more scouts.

### UNIQUE FINDINGS (1 scout only)
May be noise, may be insight. Worth noting but lower confidence.

### CONFLICTS
Where scouts explicitly disagreed. Flag for Opus to resolve.

## Step 5: Write CONSENSUS_GAPS.md

Write to: .claude/PM/plan/${PLAN_ID}/ANALYSIS/CONSENSUS_GAPS.md

\`\`\`markdown
---
phase: 3.5
orchestrator: flash
scouts: [G1, G2, G3]
timestamp: [ISO-8601]
topic: ${TOPIC}
---

# Consensus Gap Analysis

## Methodology

3 independent Flash scouts reviewed the plan with identical prompts.
Findings are categorized by agreement level.

## High Confidence Findings (2+ scouts)

These gaps were independently identified by multiple scouts:

| Gap | Scouts | Severity | Evidence | Category |
|-----|--------|----------|----------|----------|
| [description] | G1, G2 | high | [cite] | [cat] |
| [description] | G1, G2, G3 | medium | [cite] | [cat] |

### Detail

1. **[Gap Title]** (G1, G2)
   - Description: [what's missing]
   - Evidence: [from scouts]
   - Recommended Action: [what to add to plan]

## Unique Findings (1 scout)

Lower confidence - may be noise or insight:

| Gap | Scout | Severity | Notes |
|-----|-------|----------|-------|
| [description] | G1 | low | [why might be valid] |

## Conflicts

Scouts disagreed on these points:

| Topic | G1 Says | G2 Says | G3 Says | Resolution Needed |
|-------|---------|---------|---------|-------------------|
| [topic] | [view] | [view] | [view] | [what Opus should decide] |

## Blind Spots Identified

Areas multiple scouts flagged as under-examined:

1. **[Area]** - [Why it needs more attention]

## Concerns (Low Confidence)

Gut feelings that didn't fully crystallize:

- [concern from scout]

## Summary for Opus

**Total High-Confidence Gaps:** [N]
**Action Required:** [Yes/No]
**Conflicts to Resolve:** [N]

### Recommended Additions to Final Plan

1. [Specific addition based on consensus]
2. [Specific addition based on consensus]
\`\`\`
```

---

## Triad Scout Output Files

Each Flash scout writes to:
- `.claude/PM/plan/${PLAN_ID}/GAP_HUNT/G1_SCOUT.md`
- `.claude/PM/plan/${PLAN_ID}/GAP_HUNT/G2_SCOUT.md`
- `.claude/PM/plan/${PLAN_ID}/GAP_HUNT/G3_SCOUT.md`

These are raw inputs. The CONSENSUS_GAPS.md is the synthesized output.

---

## Why This Pattern Works

| Benefit | Explanation |
|---------|-------------|
| Independent views | Same prompt, different model instances may catch different things |
| Confidence signal | 2+ agreement = higher likelihood of real issue |
| Noise filtering | Single-scout findings get lower priority |
| Cheap validation | 3 Flash agents < 1 Pro agent cost |
| Parallel execution | All 3 run simultaneously, minimal latency |

---

## Integration with Final Output

After CONSENSUS_GAPS.md is written:
- Opus reads it along with GAP_ANALYSIS.md
- HIGH CONFIDENCE findings are incorporated into final plan
- UNIQUE FINDINGS become "Considerations" section
- CONFLICTS are flagged for HD if critical
