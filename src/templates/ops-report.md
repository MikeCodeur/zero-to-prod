# Operations — <UTC timestamp / release>

Mode: <post-ship | periodic>
Work: <story/ticket work id supplied by ship | n/a>
Ops status: <observed | attention | blocked | not-configured>
Release: <deployed revision / release id, or n/a for a periodic run>
Deployed at: <UTC timestamp, or n/a>
Smoke test: <passed with evidence reference | not recorded | n/a>
Window: <UTC start → end>
Baseline: <UTC start → end, or unavailable with reason>

## Collection
| Source | Declared command | Exit / coverage | Evidence |
|---|---|---|---|
| <logs / errors / performance / usage> | <verbatim setting> | <exit, window actually covered, limitations> | <redacted summary / link> |

## Findings and follow-up
| Key | Evidence / affected release | Classification | Follow-up | State |
|---|---|---|---|---|
| <stable error id or fingerprint> | <observed facts; label a suspected correlation> | <defect / product change / unknown> | <existing or created ticket / validated intent / pending interview> | <open / linked / resolved / awaiting human> |

## Rollback assessment
Threshold: <verbatim setting, or unavailable>
Observation: <metric, unit, measured value, window>
Result: <below | breached | unknown>
Proposal: <documented rollback reference if breached; no improvised command>
Decision: <pending | approved | declined | n/a>

## Not verified
<missing sources, insufficient baseline, failed commands, late telemetry, unresolved attribution>

## Next action
<concrete command or decision; include the next observation time if the window is incomplete>
