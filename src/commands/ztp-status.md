---
description: Show the project's pipeline state — framing docs, per-story progress, next command
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash
---
# ztp-status — Where the project stands

Derive the state from the files — never guess. Bash is for read-only git and declared source queries here.

1. Settings: does AGENTS.local.md exist? Missing → the next step is /ztp-setup, and nothing else can run. Present → show `Merge mode`, `Plan validation`, `Design source`, `Story track` and `Flow threshold` on one line, and the project profile (`Product type`, `Target environment`, `UI check`) on a second — `—` everywhere after the architecture phase means it was never settled.
   Framing: do docs/prd.md, docs/stories.md, docs/architecture.md, docs/foundation.md, docs/deployment.md exist — and docs/design-system.md, for a product with a user interface? A missing one is the next step. Show `Foundation status:` from docs/foundation.md, and say when docs/deployment.md still lists open points: stories can be built, not shipped to production. Also grep '^Stories ready:' docs/reviews/stories.md → yes / no / none, and show it on the framing line (a `no` or a missing review means the breakdown hasn't passed /ztp-stories-review).
2. Stories: list the ids from docs/stories.md. For each id derive:
   - complexity: the story's score (from docs/stories.md) — show it next to the id.
   - research: docs/research/<id>.md exists?
   - design: docs/designs/<id>/design.md exists? (UI stories only — otherwise n/a)
   - plan: docs/plans/<id>.md — missing / draft (no `validated: yes` in the frontmatter) / validated, plus ticked vs total task checkboxes (x/y). A plan whose frontmatter says `track: flow` carries its research inside it: show the story as `flow`, and read its research column as n/a rather than missing.
   - verification: docs/verif/<id>.md exists in the story's worktree? — shown only for a story past execution. It is never committed: absent from a clone, it reads `local only`, not a failure.
   - review: grep '^Ship allowed:' docs/reviews/<id>.md → yes / no / none.
   - correction: apply `/ztp-review`, "Fix policy", read-only to the current settings and
     report. Show `Fix level`, critical and major attempts used/allowed, and the resulting
     action; missing legacy history is unknown until established, never an invented zero.
   - ship state: proven merge plus recorded deployment and passing smoke-test evidence (including the post-ship ops report) → shipped. Merge alone → "merged — production not evidenced"; open PR → "PR open — merge pending"; otherwise —. Do not call a deployed story healthy just because its smoke test passed; observation is shown separately.
   - blocked: a story whose Dependencies (docs/stories.md) aren't all shipped is blocked — its next command is "blocked by <ids>", never a pipeline step.
3. Start with a one-line summary: X shipped / Y in flight / Z not started. Then print a compact table: story (complexity) | research | design | plan | review | ship | next. The next command follows the pipeline: research → design (UI) → plan → validate the plan (rerun /ztp-plan) → execute → review → ship — or "merge pending" while the PR awaits a human merge. The Fix policy takes precedence after review: `critical`/`major` → /ztp-execute, `review` → /ztp-review, `stop` → the exhausted budget or concrete blocker, never another automatic correction. One exception at the start: for a story not yet begun, whose complexity is at or below `Flow threshold` and whose `Story track` is not `full`, the next command is `/ztp-flow <id>` rather than `/ztp-research <id>`. Keep shipped stories to one line each.
4. Decisions: if docs/decisions/ exists, mention the ADR count and the latest one.
   Corrective work: list `docs/tickets/` briefs in the base and dedicated worktrees separately
   from the product story totals, derive their same cycle progress, and show the canonical
   ticket reference. A new ticket starts with `/ztp-flow ticket:<reference>` or
   `/ztp-orchestrator ticket:<reference>` according to its scope, never `/ztp-intent`.
5. Intents: read `docs/intents/`. Show id, title, source, draft/accepted state, linked stories
   and the next action. Repo approval comes from the intent; a tracker pointer alone cannot
   prove current acceptance. Read it using declared `Intent read` (read-only Bash is allowed
   for this query, with `ZTP_INTENT_REF` as environment data); inaccessible → `unverified`,
   never accepted. Draft → `/ztp-intent <id>`; accepted with no breakdown → `/ztp-stories <id>`.
   Do not count intents as extra stories. Initial framing, defects, chores and Quick Fix
   need no intent. A stories-review predating an appended breakdown is stale, not a pass.
6. Operations: read the repository base's `docs/ops/` reports, including after worktree
   cleanup. Show latest release/window, `Ops status`, threshold assessment, open ticket links,
   pending intent interviews and next observation time. No report or no declared sources is
   `not observed`, never healthy. An ops report is separate from the story's merge/smoke
   evidence: do not infer production health from a merged branch. Prioritize a breached
   threshold or blocked post-deploy assessment in the final next action; otherwise keep the
   existing story ordering. Do not run telemetry queries as a side effect of status.
7. Optional quality: show whether `docs/review-rules.md` is approved and any pending proposal;
   show the latest `docs/evals/runs/` status, model and full-suite/pilot scope when present.
   Never run a paid eval or start a review while displaying status.

If AGENTS.local.md doesn't exist, the project hasn't been set up: point to /ztp-setup. If it exists but docs/ doesn't, point to /ztp-prd.

End with the single most useful next command for this project, e.g.: "Next: /ztp-plan s02-...".
