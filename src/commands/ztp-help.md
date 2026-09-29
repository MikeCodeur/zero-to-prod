---
description: Print the zero-to-prod pipeline — the order of the phases and the single rule
disable-model-invocation: true
---
# zero-to-prod — Pipeline

Single rule: no direct coding. Every feature goes through the pipeline.

## Framing — once per project
0. /ztp-setup             — project settings (AGENTS.local.md): merge, validation, design, commands
1. /ztp-prd <idea>        — frames the product: idea validation, starting point, perimeter, WHAT + WHY
2. /ztp-stories           — breaks it into user stories shippable end to end
3. /ztp-stories-review    — reviews the breakdown against the PRD perimeter (fresh context)
4. /ztp-architect         — stack (recommended, validated, ADR), verified foundation, conventions,
                            environments and deployment
5. /ztp-design-system     — captures the global design system (products with a user interface only)

## Per story (one feature = one cycle = one branch = one PR)
6. /ztp-research <story>  — explores the real context (current code, APIs, traps), checks the premise
7. /ztp-design <story>    — derives the screen from the design system (UI stories)
8. /ztp-plan <story>      — breaks the story into tasks
9. /ztp-execute <story>   — implements the story (isolated subagent)
10. /ztp-review <story>   — anti-hallucination review + gate
11. /ztp-ship <story>     — exit gate, merge per Merge mode / Ship confirmation, deployment,
                            smoke test in production, documented rollback if red

Blocked in review on a critical → back to /ztp-execute (fix mode). Otherwise → /ztp-ship.
Only a critical blocks: a major stays traced in the report and is fixed in a next cycle, a
minor is style. Neither reopens a loop.

## Short track — small stories
/ztp-flow <story>         — the same cycle in 3 contexts instead of 6: research and plan fused in
one pass, then the implementer subagent, then the reviewer in a fresh context, then ship. Nothing
is relaxed — worktree, validated plan, neutralization proof, gate.
For a complexity ≤ `Flow threshold`. Migration, genuinely new screen, authorization, API contract
or added dependency → escalate to the full pipeline, even mid-flight.

## Orchestrator
/ztp-orchestrator <story> — chains the 6 phases of the cycle in one command. With
`Story track: auto`, it picks between /ztp-flow and the full pipeline from the story's complexity.
It replaces nothing: same contracts, same subagents, same gates as the individual commands. It
stops on 2 blocking questions: validate the plan (written into the plan file), confirm the ship.
Routine cycle → orchestrator; need to steer or inspect a phase → individual commands.

Where the project stands (progress per story, next command): /ztp-status
