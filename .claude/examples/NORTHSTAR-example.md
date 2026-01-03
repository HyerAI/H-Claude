# Project NORTHSTAR - Customer Support Chatbot

**The guiding document for all agents working on this project.**

---

## Purpose

Build an AI-powered customer support chatbot that handles common inquiries, reduces support ticket volume by 60%, and provides 24/7 instant responses for our e-commerce platform.

---

## Vision

A seamless support experience where customers get instant, accurate answers to their questions without waiting for a human agent. The chatbot learns from interactions, escalates complex issues appropriately, and integrates with our existing helpdesk system.

---

## Goals

1. **Reduce Support Volume** - Handle 60% of Tier-1 inquiries automatically
2. **Instant Response** - <3 second average response time
3. **High Accuracy** - 90%+ customer satisfaction on resolved queries
4. **Seamless Escalation** - Complex issues routed to humans with full context

---

## Constraints

1. **KISS** - Keep it simple. Avoid unnecessary complexity.
2. **YAGNI** - Build only what is required now.
3. **Single Source of Truth** - One place for each piece of information.
4. **Context is precious** - Delegate to sub-agents to preserve main context window.
5. **Decisions are sacred** - Document in ADRs; changes require explicit pivot.

**Project-Specific Constraints:**
- **Budget** - $5,000 for MVP (API costs, hosting)
- **Timeline** - MVP in 4 weeks, full launch in 8 weeks
- **Team** - 1 developer, AI assistance
- **Tech Stack** - Must integrate with existing Zendesk helpdesk

---

## Non-Goals

- Voice/phone support (future phase)
- Multi-language support (English only for MVP)
- Training custom LLM models (use existing APIs)
- Replacing human agents entirely

---

## Quality Standards

| Aspect | Standard |
|--------|----------|
| Documentation | Clear, concise, actionable |
| Commands | Self-documenting, predictable |
| Context files | Valid YAML, regularly updated |
| Decisions | Documented as ADRs |
| Changes | Logged in CHANGELOG.md |
| Test Coverage | 80%+ for core business logic |
| Response Time | P95 < 3 seconds |

---

## Validation Checklist

When reviewing work, validate against:

- [ ] Does it follow KISS/YAGNI principles?
- [ ] Is context.yaml updated?
- [ ] Are decisions documented as ADRs?
- [ ] Is CHANGELOG.md updated?
- [ ] Does it break existing workflow?
- [ ] Does it handle edge cases gracefully?
- [ ] Is error handling user-friendly?

---

## Success Metrics

1. **Ticket Deflection Rate** - Target: 60% of Tier-1 tickets resolved by chatbot
2. **Customer Satisfaction** - Target: 90%+ positive ratings on resolved queries
3. **Response Time** - Target: P95 < 3 seconds
4. **Escalation Rate** - Target: <40% of conversations need human handoff

---

*Last updated: 2026-01-02*
