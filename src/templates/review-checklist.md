# Review — Story <id>

> Fresh-context review. Each issue classified: critical / major / minor.
> Diff reviewed: <exact command and commit range; story diff or correction diff supplied by the caller>

Review status: <complete | blocked>
Reviewed head: <commit SHA>
Review scope: <story | correction>

## Fix history

<Preserve previous rows and findings on every rewrite. Follow /ztp-review, "Fix policy".
Initial review: an empty table, not a correction attempt. Counts derive from the rows.>

| Attempt | Trigger | Before | After | Status | Duration / evidence |
| --- | --- | --- | --- | --- | --- |

Critical fixes used: <count> / <current limit>
Major fixes used: <count> / <current limit>
Fix action: <none | critical | major | review | stop>

If blocked, do not leave this implicit:

## Review failure
### Failure cause
<concrete command, tool, prerequisite, or state that prevented completion, including the error>

### Missing
<exact evidence, file, setting, or access that was unavailable>

### Required adaptation
<precise change or input the project agent must provide before rerunning>

### Next action
<exact command or human gesture>

## Plan compliance
- [ ] The code does what the plan specifies, nothing more
- [ ] Run interdicts respected — each one checked and named

## Anti-hallucination
- [ ] No invented API/function/import (each one opened and verified)
- [ ] No plausible-but-wrong value or logic
- [ ] The code matches what it claims to do

## Rules compliance
- [ ] Repo conventions followed (AGENTS.md)
- [ ] No accepted ADR contradicted (docs/decisions/)
- [ ] Only the tools the project profile names (`E2E tool`, `UI check`) — none foreign to the target environment
- [ ] Design system respected — components/tokens from docs/design-system.md, screen matches the intent of docs/designs/<id>/design.md (UI stories)

## Tests
- [ ] Verification record checked (`ztp-gate verif-current <id>`): <current, taken as proof | stale/missing → suite and type check re-run here>
- [ ] Assertions pin the acceptance criteria (no assertion-free tests)
- [ ] Bite proven by neutralization: <what was neutralized> → <N> tests red, restored (`git diff --exit-code` clean)
- [ ] Tests the story made redundant are named and removed — or their absence justified

## Regressions
- [ ] No impact on existing code paths

## Findings
<one line per issue: stable id — severity — file — what's wrong — open/closed, with closure evidence.
Carry forward every open finding, even outside the correction diff; Max severity covers all open findings.>

## Not verified
<what this review could NOT check, and why: no browser, no database, no real third-party call.
 Name the concrete gestures a human should make — the screen to open, the button to click, the
 device to test on. A review that lists nothing here is claiming it saw everything.>

## Verdict
Max severity: <critical | major | minor | none>
Ship allowed: <yes | no>
