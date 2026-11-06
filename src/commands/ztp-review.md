---
description: Get a story reviewed by a fresh-context subagent. Gate before Ship. Never reviews in the context that wrote the code.
argument-hint: <story id or name>
allowed-tools:
  - Read
  - Grep
  - Agent
  - Write
  - Bash
---
# ztp-review — Delegated review + gate

Target story: $ARGUMENTS

## Execution contract (non-negotiable)
You MUST complete this command by delegating to the `reviewer` subagent (fresh context). You are FORBIDDEN from:
- Judging the code yourself: you are probably the context that produced it, hence blind to your own hallucinations.
- Modifying source code. Your only write right is the report docs/reviews/<id>.md, nothing else.
- Unblocking the Ship if a critical issue is reported.

If you can't invoke the Agent tool, stop and report the error. Don't improvise.

## Fix policy — shared by Execute, Flow, Orchestrator, Status and Ship

Other commands read this contract; deciding a next action does not itself invoke a reviewer.
Read these settings from `AGENTS.local.md` at each decision:

- `Fix level`: `critical` or `major`; absent means `critical`.
- `Critical fix loops`: a non-negative integer; absent means `2`.
- `Major fix loops`: a non-negative integer; absent means `1`.

These explicit defaults preserve existing projects without rewriting their settings. A present
but empty, `—`, duplicate or invalid value is an error: stop and name the setting.

**Count attempts per story, by trigger, in the report's Fix history.** The initial
implementation/review consumes none. Each row is one correction followed by its review;
count every row of that trigger, whether `started` or `reviewed`, including interrupted or
unsuccessful attempts. The budgets are
independent: a critical-triggered attempt can fix majors too, but only consumes the critical
budget. Never reset history on a new session, command, track or setting change. For an older
report without history, recover prior attempts from available reports, commits and session
evidence before requesting another correction; unknown history stops for clarification, never
silently becomes zero. A legacy passing report that needs no correction can still proceed.
Malformed or inconsistent history stops for recovery; never repair it by dropping rows.

**Decide from the latest report and the history, in this order:**

1. An attempt is `started` and has no review yet → `Fix action: review`. Verify the
   implementer has finished and the correction is committed before reviewing; uncertain
   ownership or uncommitted code → stop and report the recovery needed. Never launch another
   implementer over that attempt.
2. A critical is open, `Ship allowed: no`, or the review is incomplete → `critical` if its
   used count is below `Critical fix loops`, otherwise `stop`. Budget `0` stops immediately.
3. Only noncritical findings remain, with an open major, `Fix level: major`, and its used
   count below `Major fix loops` → `major`.
4. Otherwise → `none`, proceed to the normal Ship gates with residual findings recorded.
   A major budget of `0` disables major-triggered correction; minors alone never trigger one.

**Starting a correction** is the calling execution command's responsibility. Before delegating,
recheck the decision and record a row with trigger, current HEAD as `Before`, `After: —`,
`Status: started`, and start time when available. Set `Fix action: review`; keep the verdict
and findings. Commit only this report so the implementer receives a clean worktree; unrelated
dirty files stop execution. The row consumes its budget before the call: a crash cannot give
the next session a free attempt. Pass the whole report to the unchanged implementer fix mode.
If the call fails, preserve that row and record what is known; do not auto-start a replacement.

**Reviewing a correction** uses the started row and the preserved previous findings. Verify
`Before` exists and is an ancestor of the current correction HEAD; missing or inconsistent
evidence blocks review. For a major-triggered attempt, judge only
`git diff <Before> <correction-head>` plus its affected callers: pass both exact SHAs, the
previous report and "judge the correction diff only". A critical-triggered attempt retains
the full story review. An empty correction diff closes no finding without evidence.
After the review, mark that row `reviewed`, record `After`, result and elapsed time if measured,
then decide again. A failed/incomplete review still consumes the attempt and blocks Ship.
Carry every open finding forward; only the reviewer can close one with evidence. Preserve
history even in a failure report. The reviewer reports severity honestly; the caller computes
`Fix action` without rewriting `Ship allowed` to manufacture a failure for a major.

## Workflow

### Step 1 — Delegate
Resolve $ARGUMENTS to the story id (`s<number>-<slug>`) against docs/stories.md. Read AGENTS.local.md for the project commands, `Test budget` and the Fix policy above — missing file → STOP: "No project settings. Run /ztp-setup."
Locate `.worktrees/<id>`, verify its branch is exactly `feature/<id>`, and use
that absolute worktree as the reviewer working directory and report location.
Missing worktree, wrong branch, detached HEAD or repository base → STOP; never
switch branches. Preserve any existing report and Fix history before delegation. Resolve the
review scope from the Fix policy; without a started attempt, use the full story diff. Record
the current HEAD as `Reviewed head`. Then invoke the Agent tool:
- subagent_type: reviewer
- description: Anti-hallucination review of story <id>
- working directory: the absolute dedicated worktree path verified above.
- prompt: Review story <id>. Your agent definition and the preloaded `review-antihallu` skill are your contract — this prompt carries only what is specific to this run. Judge <the exact diff and scope resolved above>. Carry forward the supplied report's history and open findings, closing findings only with evidence. Fill the checklist from templates/review-checklist.md, and end with the exact lines "Max severity: <critical|major|minor|none>" and "Ship allowed: <yes|no>". Report every finding within this scope; never hold one back for a later pass. The project commands and settings are in AGENTS.local.md — quote them verbatim, and one left at `—` is reported as not run, never substituted. On a flow plan, "Verified facts" is the research; a contradiction is a finding.

Wait for the verdict. If the Agent call fails, times out, returns no report, or returns a report without both exact verdict lines, write `docs/reviews/<id>.md` yourself with `Review status: blocked`, the concrete failure cause, missing information/evidence, and the exact adaptation required. End it with `Max severity: critical` and `Ship allowed: no` when review completeness is compromised. Do not replace the failure with a vague "review failed" message.

### Step 2 — Report
Write the full report to docs/reviews/<id>.md. It MUST include a `Review status: complete|blocked` line, and, when blocked, the sections `Failure cause`, `Missing`, and `Required adaptation` with concrete details. It MUST end with the exact lines `Max severity: ...` and `Ship allowed: yes` or `Ship allowed: no` — /ztp-ship greps that line, and without it the ship stays blocked. A single critical = no. An incomplete review is never a pass.
Preserve the Fix history and all open findings, update the reviewed attempt when present,
and write `Reviewed head`, `Review scope`, used/allowed counts and `Fix action` before the
final verdict lines. On a first review, initialize empty history; never erase an existing one.

### Step 3 — Gate (fail-closed)
Apply the Fix policy above, show used/allowed counts for each trigger, then:

- `critical` or `major` → "Correction required (<trigger>, <used>/<limit> attempts used). Next: /ztp-execute <id>, then /ztp-review <id>."
- `review` → finish the pending correction review before another implementation or Ship.
- `stop` → stop with all open findings and the exact exhausted budget or missing evidence.
  Never change a severity, clear a critical or raise a budget just to keep going.
- `none` → "Review passed. Next step: /ztp-ship <id>"; name residual majors, if any.
