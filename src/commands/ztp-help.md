---
description: Print the zero-to-prod pipeline — the order of the phases and the single rule
disable-model-invocation: true
---
# zero-to-prod — Pipeline

Single rule: no direct coding. Every feature goes through the pipeline.

## The loop
Initial framing stays the PRD. Once the product exists:
`/ztp-intent` → `/ztp-stories <intent>` → existing story cycle → ship → `/ztp-ops` → follow-up.
An intent is required for a **new feature or product evolution**, not for initial framing.
A defect goes to a ticket, then flow or the full story cycle according to its scope, **without
an intent**. Chore and Quick Fix need no intent. Bugs never inflate the product perimeter.

## Framing — once per project
0. /ztp-setup             — project settings (AGENTS.local.md): merge, validation, design, commands
1. /ztp-prd <idea>        — frames the product: idea validation, starting point, perimeter, WHAT + WHY
2. /ztp-stories           — breaks it into user stories shippable end to end
3. /ztp-stories-review    — reviews the breakdown against the PRD perimeter (fresh context)
4. /ztp-architect         — stack (recommended, validated, ADR), verified foundation, conventions,
                            environments and deployment, zone rules (.claude/rules/)
5. /ztp-design-system     — sets up the design system (your input, or 3 directions from the tool
                            you choose) and implements its foundations: tokens, components,
                            layout, page templates — UI only

## Per story (one feature = one cycle = one branch = one PR)
6. /ztp-research <story>  — explores the real context (current code, APIs, traps), checks the premise
7. /ztp-design <story>    — derives the screen from the design system (UI stories), then the
                            design validation gate: human or agent per `Design validation`
8. /ztp-plan <story>      — breaks the story into tasks
9. /ztp-execute <story>   — implements the story (isolated subagent)
10. /ztp-review <story>   — anti-hallucination review + gate
11. /ztp-ship <story>     — exit gate, merge per Merge mode / Ship confirmation, deployment,
                            smoke test in production, documented rollback if red

Review chooses the next step through /ztp-review's Fix policy: /ztp-execute for a correction
within budget, /ztp-ship when none is due, or stop when a blocking budget is exhausted.
`Fix level`, `Critical fix loops` and `Major fix loops` are project settings. A critical
always blocks; unresolved majors stay traced, and minors alone never reopen a loop.

## Short track — small stories
/ztp-flow <story>         — the same cycle in 3 contexts instead of 6: research and plan fused in
one pass, then the implementer subagent, then the reviewer in a fresh context, then ship. Nothing
is relaxed — worktree, validated plan, frozen acceptance tests, review spot check, gate.
For a complexity ≤ `Flow threshold`. Migration, genuinely new screen, authorization, API contract
or added dependency → escalate to the full pipeline, even mid-flight.

## Orchestrator
/ztp-orchestrator <story> — chains the 6 phases of the cycle in one command. With
`Story track: auto`, it picks between /ztp-flow and the full pipeline from the story's complexity.
It replaces nothing: same contracts, same subagents, same gates as the individual commands. It
stops on blocking questions: validate the design (UI stories, `Design validation: human`),
validate the plan (written into the plan file), confirm the ship.
Routine cycle → orchestrator; need to steer or inspect a phase → individual commands.

Where the project stands (progress per story, next command): /ztp-status

New change on an existing product: /ztp-intent <change> — one question at a time, confirmed
answers, human acceptance; repo document or declared tracker. Then /ztp-stories <intent> adds
the stories and /ztp-stories-review checks the enlarged scope without rewriting the PRD.

Production observation: /ztp-ops post-ship <release> <deployed-at> (called by ship), or
/ztp-ops last <N> days on demand/from a scheduler. Reports go to docs/ops/; defects become
tickets, product changes enter an intent interview. No declared observability → it says so
and stops. /ztp-setup --observability offers optional deployment logs and error tracking.

Corrective work starts from /ztp-flow ticket:<reference> or /ztp-orchestrator ticket:<reference>;
its linked brief lives in docs/tickets/, outside the product perimeter.

Optional quality feedback:
/ztp-review-learn <PR history> — learns report/ignore rules from human comments; the tech lead
must approve docs/review-rules.md before it applies.
/ztp-eval collect, then /ztp-eval run — 20–50 accepted reference tasks, replayed headlessly
when the model, rules or skills change. Declared runner/checker required.
install.sh --ci — PR gates; fresh review and evals opt-in. Automated build repair stays off.

Work that changes no product behavior (docs, content, tests, tooling): /ztp-chore <request> —
validated mini-plan, implementer, targeted verification, no review. One request = one chore.

End-to-end suite grown slow or brittle: /ztp-test-prune — audits each spec (keep, rewrite,
delete), you validate the list, then it prunes in its own worktree.
