---
description: Print the idea-to-prod pipeline — the order of the phases and the single rule
disable-model-invocation: true
---
# idea-to-prod — Pipeline

Single rule: no direct coding. Every feature goes through the pipeline.

## Framing — once per project
0. /itp-setup             — project settings (AGENTS.local.md): merge, validation, design, commands
1. /itp-prd <idea>        — frames the product: idea validation, starting point, perimeter, WHAT + WHY
2. /itp-stories           — breaks it into user stories shippable end to end
3. /itp-stories-review    — reviews the breakdown against the PRD perimeter (fresh context)
4. /itp-architect         — stack (recommended, validated, ADR), verified foundation, conventions,
                            environments and deployment
5. /itp-design-system     — captures the global design system (products with a user interface only)

## Per story (one feature = one cycle = one branch = one PR)
6. /itp-research <story>  — explores the real context (current code, APIs, traps), checks the premise
7. /itp-design <story>    — derives the screen from the design system (UI stories)
8. /itp-plan <story>      — breaks the story into tasks
9. /itp-execute <story>   — implements the story (isolated subagent)
10. /itp-review <story>   — anti-hallucination review + gate
11. /itp-ship <story>     — exit gate, merge per Merge mode / Ship confirmation, deployment,
                            smoke test in production, documented rollback if red

Blocked in review on a critical → back to /itp-execute (fix mode). Otherwise → /itp-ship.
Only a critical blocks: a major stays traced in the report and is fixed in a next cycle, a
minor is style. Neither reopens a loop.

## Short track — small stories
/itp-flow <story>         — the same cycle in 3 contexts instead of 6: research and plan fused in
one pass, then the implementer subagent, then the reviewer in a fresh context, then ship. Nothing
is relaxed — worktree, validated plan, neutralization proof, gate.
For a complexity ≤ `Flow threshold`. Migration, genuinely new screen, authorization, API contract
or added dependency → escalate to the full pipeline, even mid-flight.

## Orchestrator
/itp-orchestrator <story> — chains the 6 phases of the cycle in one command. With
`Story track: auto`, it picks between /itp-flow and the full pipeline from the story's complexity.
It replaces nothing: same contracts, same subagents, same gates as the individual commands. It
stops on 2 blocking questions: validate the plan (written into the plan file), confirm the ship.
Routine cycle → orchestrator; need to steer or inspect a phase → individual commands.

Where the project stands (progress per story, next command): /itp-status
