---
description: Observe a deployment or a recent period, report production signals and route follow-up
argument-hint: <post-ship release timestamp | last N days>
allowed-tools:
  - Read
  - Glob
  - Grep
  - Write
  - Edit
  - Bash
  - AskUserQuestion
---
# ztp-ops — Production back into the loop

Request: $ARGUMENTS
Output structure: @templates/ops-report.md

This command observes and routes findings. It does not deploy, fix code, approve its own
intent, or run a rollback. The existing smoke-test rollback contract remains in `/ztp-ship`.

## 1. Context and declared sources

Read `AGENTS.local.md`, `docs/deployment.md`, previous `docs/ops/` reports and linked
intents/tickets. Missing settings → stop and point at `/ztp-setup`.
Use only `Deployment logs`, `Error tracking`, `Performance signals`, `Usage signals`.
Missing or `—` means unavailable. **No command declared → say "Operations not configured",
record `Ops status: not-configured` with the missing sources and stop.** Do not guess a
platform, CLI, service, query, credential or healthy result.

Reports live in the **repository base** at `docs/ops/<UTC timestamp>-<release-or-period>.md`,
including when called from a story worktree. Verify its `Target branch` and exclusive access
first; never switch it. An unavailable report destination blocks the run. Record only
redacted evidence and source links, never credentials, complete user payloads or personal data.
Before testing source availability, verify that destination and record any supplied work id,
release/deployment evidence and smoke result, even for a `not-configured` report. Metadata
passed by ship does not claim the telemetry was observed; absent evidence stays unrecorded.

## 2. Window and collection

- `post-ship`: require the deployed revision/release id and the actual deployment timestamp
  from the deployment evidence, not the PR creation/merge time. Read `Ops window` (minutes).
  Missing/invalid window → blocked report. Observe from deployment to the end of that window;
  compare to the immediately preceding window of the same length and release tags when
  available. If telemetry has not arrived or the window has not elapsed, record what was
  collected, mark the assessment incomplete and give a concrete time to rerun. Never sleep
  through a long observation period or claim an empty early query proves health.
  Record the smoke-test evidence supplied by ship; without that evidence write `not recorded`,
  never infer a successful smoke test from logs or re-run the test just to populate a report.
- `last N days`: use the positive N supplied by the caller, otherwise `Ops days`. No usable
  value → stop with the missing setting. Use UTC start/end, and the preceding equal period
  as baseline where the source supports it. Look for recurring errors, worsening query or
  request latency, and changes in usage. No performance/usage source → mark it not verified.

Execute the exact declared read commands with environment values `ZTP_OPS_FROM`,
`ZTP_OPS_TO`, `ZTP_OPS_BASELINE_FROM`, `ZTP_OPS_BASELINE_TO` (ISO-8601 UTC) and
`ZTP_OPS_RELEASE` (empty for a periodic run). Do not append invented flags. The project's
wrapper must consume these values or return evidence with explicit timestamps/release tags
that can be filtered to the requested window. Record exit codes, actual coverage and source
links. Failed collection or unfilterable output is unavailable evidence, never zero errors.

## 3. Findings and rollback proposal

Separate observations from hypotheses. A newly seen error is not automatically caused by
this deploy: name the release tag, first occurrence, baseline and touched path supporting
the correlation, or label it suspected. Show all new related errors, not only threshold breaches.

Read `Ops rollback threshold`: it must name a metric, comparator, value, unit and window.
Evaluate it against measured data, never an invented default. Missing/ambiguous threshold
or missing evidence → `Result: unknown`, name what cannot be decided. Breached →
`Ops status: attention`, show the evidence and **propose** the rollback from
`docs/deployment.md`, including what it does not undo. A missing runbook is a blocker, not
permission to invent one. The proposal never executes the rollback, even with automatic ship.

## 4. Close the loop

Give each finding a stable source id/fingerprint. Check previous reports and the configured
tracker before creating anything; link the existing ticket/intent for a repeated finding.

- **Defect** (promised behavior broken): create or update a ticket in `Issue tracker` using
  its available, documented access. Include evidence, actual/expected behavior, release and
  report link. It is not an intent and does not become product perimeter in `docs/stories.md`.
  Its treatment uses flow or the full story cycle according to the existing escalation rules.
- **New capability or product evolution**: propose `/ztp-intent <report#finding>`. With an
  originator present, run that interview and link the accepted intent. Without one, record
  `awaiting human` and the exact interview input; never fill an intent without validation.
- **Unknown**: record the missing evidence and a triage action; never fabricate a cause or
  turn an uncertain observation into a feature.

Tracker access absent, write rejected or timed out → report the pending ticket with its
prepared content; do not claim it was created. After an uncertain write, read/search before
retrying so a scheduled run cannot duplicate it. Do not contact people or configure schedules.

## 5. Report

Write the report even when observation is incomplete. `observed` requires complete coverage
of the configured sources/window and a decidable threshold; `attention` means findings or a
breach; `blocked` means required evidence is unavailable. Always list missing optional sources.
Commit only this report on `Target branch` if no unrelated staged changes exist. Otherwise
leave it saved and say it is uncommitted; never sweep another agent's changes into a commit.

End with the report path, observation status, rollback proposal (if any), ticket/intent links
or pending actions, and the next useful command. A scheduler may invoke this same command
headlessly with explicit N or release/time; it must have the declared read access and a
writable report destination. It never answers the intent interview on the human's behalf.
