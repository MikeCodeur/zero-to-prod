---
id: <short-slug>
base: <full commit hash before the successful task>
accepted: <full commit hash of the accepted result>
---
# Eval — <title>

## Task
<the original task prompt; enough context to replay it from the base commit>

## Expected result
<observable accepted behavior, policy and constraints; no implementation copied as an answer>

## Checks
<how the declared Eval check verifies this case: real tests/output/behavior, including refusals>

## Provenance
<successful PR/task/incident resolution and evidence that the accepted commit satisfies the checks>

## Isolation requirements
<fixtures, local services and allowed tools; no production writes or standing production credentials>
