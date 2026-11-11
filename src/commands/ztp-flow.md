---
description: One small story, end to end, in three contexts instead of six — research and plan fused, same implementer, same fresh-context review, same gates
argument-hint: <story id or name>
allowed-tools:
  - Read
  - Glob
  - Grep
  - Write
  - AskUserQuestion
  - Agent
  - Bash
---
# ztp-flow — The short track for a small story

Target story: $ARGUMENTS

A story of complexity 1 does not need six cold contexts to read the same four documents.
This track runs the same cycle in three: you research and plan in one pass, the
`implementer` builds, the `reviewer` judges in fresh context, and it ships.

**Nothing is relaxed.** The dedicated worktree, the validated plan, the fresh-context review
with its frozen acceptance tests and neutralization spot check, the rendered-screen pass, the `Ship allowed` gate and the test budget
all hold exactly as on the full track. What disappears is repetition, not verification —
if you find yourself dropping a check to go faster, you are on the wrong track: stop and
escalate.

## Execution contract (non-negotiable)
You are FORBIDDEN from:
- Writing or modifying production code yourself. Implementation is delegated to the
  `implementer` subagent, always.
- Judging the implementation yourself. Review is delegated to the `reviewer` subagent in a
  fresh context, always — you are the context that planned it, hence blind to your own gaps.
- Running this track on a story that trips any escalation signal, in Phase 0 or in Phase 2.
- Skipping the plan checkpoint, the review, or the ship gate to save time.

## Phase 0 — Prerequisites and eligibility (fail-closed)

1. `AGENTS.local.md` exists? Missing → STOP: "This project has no settings. Run /ztp-setup."
   Read `Story track`, `Flow threshold`, `Plan validation`, `Design validation`, `Merge mode`, `Ship confirmation`,
   the project commands and the stages from it. Read the correction settings and defaults
   through `/ztp-review`, "Fix policy"; the same contract governs every retry below.
2. `docs/prd.md`, `docs/stories.md` and `docs/architecture.md` exist? Any missing → STOP and
   point at the phase that produces it. This track drives one story; it never replaces framing.
3. Resolve $ARGUMENTS using AGENTS.md, "Work sources" (story or `ticket:<reference>`).
   No unambiguous source → stop. Use its criteria, complexity and dependencies throughout.
4. `Story track: full` → STOP: "This project runs every story on the full pipeline. Use
   /ztp-orchestrator <id>." `Story track: flow` → continue. `Story track: auto` → continue
   only if the story's complexity is at or below `Flow threshold`; above it, STOP and say:
   "Story <id> is complexity <n>, above `Flow threshold` <t>. Run /ztp-orchestrator <id>."

**Escalation signals.** Whatever the score, this track does not carry a story that involves
a schema migration, a genuinely new screen, a change to authorization or tenant scope, a
change to an API contract, or an added dependency. If the resolved work source already shows one,
STOP now and say which: "Story <id> <signal>. That belongs on the full pipeline —
/ztp-orchestrator <id>."

## Phase 1 — Workspace (fail-closed)

Bootstrap or verify the story's workspace exactly as AGENTS.md, "Where work happens",
specifies, and perform every read and write there. Report the absolute path, the branch and
the environment files copied (names only, never values). Any conflict it names is a hard stop.

## Phase 2 — Research and plan, one pass

Apply the `testing-doctrine` skill when you write the test strategy.

Read: the resolved work source, `docs/architecture.md`, AGENTS.md — and
`docs/design-system.md` plus `docs/designs/<id>/design.md` when the story touches UI.
Output structure: @templates/plan-flow.md

The two acts are fused, not skipped. Apply the `codebase-analysis` skill to the story's
scope and establish the facts **before** writing a single task:

1. **Verify the story's PREMISE, not just that the things it names exist.** Open the code
   and check each assertion: exact name, signature, location, AND behaviour on the story's
   own case. A function that exists and throws on that case invalidates the premise — say
   it first, and repair the story rather than patching around it.
2. Locate the files actually involved and their current state; note the existing tests, the
   dependencies between modules, the traps left by previous stories.
3. Write what you could not settle under "Open questions". An honest unknown beats a
   plausible guess.
4. **Run the escalation check again, now that you have read the code.** Reading it is what
   reveals a migration hiding behind a nullable column, a screen that turns out to be new,
   or a guard that has to move. One signal → STOP, say which, and hand over:
   "Escalating <id> to the full pipeline: <signal>. Run /ztp-research <id>." The research
   you just did was needed either way; nothing is lost.
5. Break the story into ordered tasks, each small and verifiable, resting on the facts you
   just established. A behaviour, business rule, data contract or interaction names the test
   that can fail; a purely presentational task names its visual check (per `UI check`) plus lint and typecheck
   instead — never a manufactured component test. `Test budget` from AGENTS.local.md; a plan
   that wants more says why. Where the tests go is settled in the `testing-doctrine` skill.
   Map every acceptance criterion to exactly one test in the "Acceptance tests" table.
6. Past roughly six tasks, the story is not small: say so and suggest `/ztp-orchestrator <id>`
   rather than growing a short-track plan into a long one.
7. **Design.** This track never draws a new screen: that is an escalation signal. When the
   story touches UI and `docs/designs/<id>/design.md` exists, it goes through the same gate as
   on the full track before the plan is written — `validated: yes` already → continue;
   otherwise apply `Design validation` exactly as /ztp-design's Step 7 does (`human`: show it
   and ask "Validate this design?" — Validate / Modify / Stop; `agent`: check it, validate it,
   say nobody else looked). Stop or an unvalidated design → no plan.
8. Write `docs/plans/<id>.md`, frontmatter `validated: no` and `track: flow`. **Cap it at
   ~150 lines.**

**CHECKPOINT — per `Plan validation`.** `human`: present the summary (verified facts, tasks,
files touched, test strategy) and ask via AskUserQuestion: "Validate this plan?" — options:
Validate / Modify / Stop. Only Validate writes `validated: yes`; anything else stops.
`autonomous`: re-read the plan against the story's acceptance criteria, set `validated: yes`
yourself, and say plainly that nobody else looked at it. An existing plan file never counts
as validated on its own.

Write no code in this phase.

## Phase 3 — Execute (delegated)

Run `/ztp-execute`'s contract in the absolute worktree verified in Phase 1: validated plan,
acceptance tests written, reviewed per `Test validation` and frozen before any code, same implementer, and the plan's "Verified facts" as research. On a correction, apply
`/ztp-review`, "Fix policy", and reserve exactly one attempt before delegating. On resume,
`review` goes straight to Phase 4, `none` to Phase 5, and `stop` stops; never replay the
initial implementation or reset history. Capture the implementer's summary and blockers.

## Phase 4 — Review (delegated, fresh context)

Run `/ztp-review`'s complete contract in the same worktree: fresh reviewer, scope selected
by the correction trigger, preserved history/findings and fail-closed failure reporting.
It owns the budget decision; do not substitute a local retry counter or a fixed limit.

**Gate.** Follow its `Fix action`: `critical` or `major` → Phase 3 in fix mode; `review` →
finish the pending review; `none` → Phase 5; `stop` → stop with open findings and used/allowed
counts. Exhausting a budget does not authorize Ship over a critical or an incomplete review.

## Phase 5 — Ship

CHECKPOINT — per `Ship confirmation`. `human`: show the verdict and ask via AskUserQuestion:
"Ship now?" — options: Ship / Not now; only an explicit Ship proceeds. `automatic`: proceed.

Then run `/ztp-ship`'s flow unchanged: the mechanical gate
(`grep -q '^Ship allowed: yes' docs/reviews/<id>.md`), then its exit gate — the cycle's only
end-to-end and production-build run, per `E2E stage` and `Build stage` — then `Merge mode`,
squash, then — after a proven merge — the deployment and the smoke test per
docs/deployment.md, the rollback on a red smoke test, and cleanup only once it is green.

End with: "Story <id> shipped (flow) — deployed, smoke test green. Cycle complete." when production is proven, "PR opened —
merging is yours." when it stops at the PR, or the exact blocking state if stopped: which
phase, what is missing, which command comes next.
