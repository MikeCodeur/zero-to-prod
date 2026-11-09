---
description: Propose project review rules from human PR feedback, then obtain tech-lead approval
argument-hint: <PR range, dates or supplied review export>
allowed-tools:
  - Read
  - Glob
  - Grep
  - Write
  - Edit
  - Bash
  - AskUserQuestion
---
# ztp-review-learn — Human feedback into review policy

Input: $ARGUMENTS
Output structure: @templates/review-rules.md

1. Read `AGENTS.local.md` and the current `docs/review-rules.md`, if any. Use the supplied PR
   export or the exact `Review history` command (input range in `ZTP_REVIEW_RANGE`, as an
   environment value). No access/export/command → stop and name what is missing. Never
   invent a platform API, a comment, or a review preference.
2. Read the **human** comments and their resolution/context. Exclude bots and automated
   findings; unknown authorship is unresolved evidence, not a human rule. Distinguish a
   repeated accepted concern from a one-off preference, and accepted feedback from a
   suggestion the team rejected. Keep canonical PR/comment links and the relevant scope.
3. Propose a compact "Report" / "Ignore" policy. Each rule has an id, precise applicability,
   a concrete example and evidence. Conflicting feedback goes under "Unresolved proposals".
   No inferred rule may weaken the generic review, severity scale, plan compliance,
   freeze check, neutralization spot check or gates. Ignore rules reduce noise; they never hide critical defects.
4. Write `docs/review-rules.proposed.md` with `Review rules status: proposed`, preserving
   the active file. Show the proposed delta and ask the **tech lead** to approve/change/reject
   it (AskUserQuestion where available). Record their identity and decision. Neither the
   agent nor `Plan validation: autonomous` can approve it; headless collection stops here.
5. Only explicit tech-lead approval writes `Review rules status: approved`, approver and UTC
   timestamp, and promotes the proposal to `docs/review-rules.md`. Remove only the consumed
   proposal. Commit those paths on `Target branch` with no unrelated staged work; never
   switch branches to force the commit. Declined proposals never replace active rules.

End with the evidence coverage, rules proposed/approved, unresolved items and file path.
The `reviewer` reads the approved file in its next fresh context.
