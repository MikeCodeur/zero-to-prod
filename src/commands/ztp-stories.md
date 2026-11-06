---
description: Break the PRD or an accepted change intent down into shippable user stories
argument-hint: <optional intent id>
allowed-tools:
  - Read
  - Write
  - Bash
  - AskUserQuestion
---
You are breaking the approved scope down into user stories. Input: $ARGUMENTS

Read the PRD: docs/prd.md
Output structure: @templates/stories.md

Apply the agentic-stories skill for the breakdown.

## Choose the input

No argument → initial PRD breakdown, as below. If stories already exist, preserve their ids,
content and progress; never regenerate the perimeter over shipped work.

An intent id → read `AGENTS.local.md` and `docs/intents/<id>.md`. A repo intent must have
`validated: yes`, its approver/date and no blocking open question. A tracker pointer is not
approval: fetch the canonical record using `Intent read` with `ZTP_INTENT_REF` as environment
data, and verify its current approval and revision. Inaccessible, missing or draft → stop
and point at `/ztp-intent <id>`. Use the fetched content as the source, never a stale pointer.

**Append mode:** add only the stories needed for this intent, with the next unused story
numbers and a `Source:` link to the intent (and canonical revision for a tracker). Preserve
every existing id, criterion, dependency and progress marker. Re-running the same intent
does not duplicate its stories: show the existing mapping; changed approved scope needs an
explicitly reviewed delta. Do not rewrite `docs/prd.md`. An intent conflicting with the PRD's
exclusions must explicitly record the human-approved scope decision; otherwise stop.

The PRD plus these linked, approved intents is the scope `/ztp-stories-review` checks.
Record the new story ids on the intent (or via `Intent write` and read-back for a tracker).
An inaccessible write is reported, never silently treated as synchronized. Defects go to
tickets, not this breakdown; initial framing, chores and Quick Fix require no intent.

When the PRD names a reference (an existing product, a legacy system, mockups), it is a living spec: for each story, the agentic notes may point to its equivalent screen or flow. When it names none, the idea validation and the approved scope are the spec. Stay inside that scope; only an explicit approved intent decision can change an initial exclusion.

Proceed as follows:
1. Break the need into stories: each one an end-to-end shippable slice, testable. Give each story an id: `s<number>-<short-slug>` (e.g. s01-submit-testimonial) — this id names every pipeline file and the story branch, so keep it short and stable.
2. For each story, write verifiable acceptance criteria (each one must be able to become a test), the agentic notes useful for execution, and a complexity score (1-5, same scale as the PRD perimeter) — a 5 gets split now, not at planning.
3. Order the stories by dependency: no story may assume work not yet done.
4. Write the result to `docs/stories.md` and commit it on the default branch (docs: stories). Identify its source as `docs/prd.md` for initial stories or the accepted intent for appended ones. A previous stories-review report no longer covers this changed breakdown: rerun that review before presenting the new scope as reviewed.

End with: "Stories ready in docs/stories.md. Next step: /ztp-stories-review"
