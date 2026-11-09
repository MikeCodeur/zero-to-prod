---
validated: no
validated by: <reviewer | human>
---
# Acceptance tests — <id>

> Written by the implementer in tests mode and committed with the tests, alone:
> `test(<id>): acceptance tests`. `ztp-gate tests-frozen <id>` finds that commit in the
> history and checks the files below have not changed since. The verdict is written by the
> reviewer in tests mode, or after the human checkpoint, per `Test validation`.

## Frozen files
<every test file, fixture and helper the code phase must not touch, one path per line>
- <path>

## Findings
<filled only when `validated: no` — what to change before the tests can be frozen>
