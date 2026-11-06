---
description: Interview the originator of a new product change and record its validated intent
argument-hint: <new change, intent id, or ops report finding>
allowed-tools:
  - Read
  - Glob
  - Grep
  - Write
  - Edit
  - Bash
  - AskUserQuestion
---
# ztp-intent — Why this change

Subject: $ARGUMENTS
Output structure: @templates/intent.md

## Scope and prerequisites

This is for a **new feature or evolution of an existing, framed product**. Initial framing
starts with `/ztp-prd`. A defect stays a ticket and enters the appropriate flow or full story
cycle without an intent. Chores and Quick Fix do not need one either. Do not turn maintenance
into product scope. If the request is a defect, identify its ticket or route it to `Issue tracker`.

Read `AGENTS.local.md`, `docs/prd.md`, `docs/stories.md` and any referenced ops finding.
Missing settings or initial framing → stop and point at `/ztp-setup` or `/ztp-prd`.
Read `Intent source`: `repo` or `tracker`. Missing/invalid → stop and request that setting;
never choose a tracker or a command. Work on `Target branch` in the repository base directory;
wrong branch or another agent owning it → stop, never switch or overwrite their work.

## Interview — always human, including an ops-originated change

1. Read the context before asking. Resolve an existing intent unambiguously; otherwise pick
   the next unused `iNNN-short-slug` among `docs/intents/` (including tracker pointers).
2. Ask **one question at a time**, using AskUserQuestion when available. Start with the
   problem, then follow that branch until it is understood before moving on: expected
   outcome and success signal, affected users, constraints, open questions. Reformulate
   ambiguous answers and have the originator correct them. Never send a questionnaire batch.
3. Nothing is filled without validation: show a proposed section in the conversation and
   have it confirmed before recording it. Do not infer an answer from silence, an ops
   diagnosis or `Plan validation: autonomous`. A scheduled run with nobody to answer stops
   with a pending interview in its ops report; it never manufactures an accepted intent.
4. Compare the change with the PRD constraints and exclusions. An intentional scope change
   needs an explicit human decision in "Scope decisions"; unresolved conflict blocks the
   intent. Keep the PRD intact. An intent explains **why**; stories will specify **what**.
5. Present the whole confirmed document and ask for final acceptance. Only explicit
   acceptance with no blocking open question writes `validated: yes`, the approver and the
   UTC timestamp. An interrupted interview may save only the confirmed sections as a draft
   (`validated: no`); unconfirmed fields stay unanswered. Existing accepted content changed
   → return to draft and revalidate before downstream use.

## Record it in the declared home

- `repo`: write `docs/intents/<id>.md` using the template.
- `tracker`: read `Intent read` and `Intent write`. They are exact project commands, with
  `ZTP_INTENT_REF` carrying the external reference and `ZTP_INTENT_FILE` the absolute path to
  the confirmed Markdown document. Set environment values as data; never interpolate a
  reference into shell code or invent CLI flags. Missing command, inaccessible record or
  uncertain write → stop, retain the confirmed local draft and report the missing access.
  Read back the canonical record after a write. Keep `docs/intents/<id>.md` as a **pointer**:
  id, title, `source: tracker`, canonical reference and revision, retrieval time. The tracker
  holds the content and approval; the pointer is not an independently approved copy.

Commit only the intent or pointer on `Target branch` when no unrelated staged work exists.
Do not start a story, create a feature worktree or write product code in this command.

End with the source of truth and approval state. Accepted → `/ztp-stories <id>`; draft →
`/ztp-intent <id>` to finish the interview.
