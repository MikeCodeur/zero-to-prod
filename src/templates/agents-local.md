# <project> — settings and conventions

**This file is yours. `install.sh` never overwrites it, and `/ztp-setup` is its only creator.**
`AGENTS.md` belongs to the method and is rebuilt on every update — write nothing there.

Every value below is read by the pipeline commands. One setting per line, `Name: value`, nothing
else on the line: a command reads the value as everything after the colon, trimmed. Change any of
them at any time.

**After changing anything here, rerun `install.sh`** — it reassembles `AGENTS.md` from the method's
rules plus this file, and `AGENTS.md` is what an agent loads automatically. Settings are also read
straight from here, so those take effect immediately; the conventions at the bottom only reach an
agent through `AGENTS.md`, and stay stale until you reinstall.

## Pipeline settings

```
Merge mode:        pr
Target branch:     main
Plan validation:   human
Ship confirmation: human
Story track:       auto
Flow threshold:    2
Design source:     internal
Design skill:      —
Design tool:       —
Test budget:       25
Test validation:   agent
Fix level:         critical
Critical fix loops: 2
Major fix loops:   1
Verification mode: record
Full suite:        execute-end
E2E stage:         ship
E2E scope:         story
E2E smoke:         —
E2E targets:       —
Build stage:       ship-if-route
Issue tracker:     github
Worktree root:     .worktrees/
Sandbox port base: 3000
Sandbox vars:      —
Sandbox schema:    —
Sandbox reset:     —
Intent source:     repo
Intent read:       —
Intent write:      —
Ops days:          7
Ops window:        —
Ops rollback threshold: —
Protected paths:   []
Production commands: []
Merge commands:    []
Merge resolve:     —
Eval model:        —
Eval config paths: []
Eval timeout:      600
CI review:         no
CI evals:          no
```

| Setting | Accepted values |
| --- | --- |
| Merge mode | `local` (squash-merged locally, no review platform) · `pr` (a pull request against the target branch) |
| Plan validation | `human` (a checkpoint blocks until you validate) · `autonomous` (the agent validates its own plan) |
| Ship confirmation | `human` (asked before any merge) · `automatic` |
| Design source | `internal` (the agent draws, using `Design skill`) · `external` (a brief goes to `Design tool`) |
| Story track | `auto` (the story's complexity picks the lane) · `full` (always the six-phase pipeline) · `flow` (always `/ztp-flow`) |
| Flow threshold | complexity at or below which `auto` picks `/ztp-flow` |
| Test budget | tests per story — a plan wanting more says why |
| Test validation | who reviews the acceptance tests before any code: `agent` (the reviewer, fresh context) · `human` (a checkpoint blocks) |
| Fix level | `critical` (only blocking reviews trigger correction) · `major` (also correct majors); absent → `critical` |
| Critical fix loops | non-negative integer, maximum correction/review attempts triggered by a critical or blocked review per story; absent → `2`. `0` stops at the first blocking review |
| Major fix loops | non-negative integer, maximum correction/review attempts triggered by majors per story with `Fix level: major`; absent → `1`. `0` leaves majors in the report and proceeds to Ship |
| Verification mode | `record` (the implementer records what it ran; the reviewer checks the record instead of re-running) · `rerun` (the reviewer runs everything itself) |
| Full suite | when the whole unit suite runs: `execute-end` · `ship` · `both` |
| E2E stage | when the end-to-end suite runs: `execute-end` · `ship` · `ci` · `—` |
| E2E scope | what the ship's single run covers: `story` (the spec files the story's diff adds or changes, plus `E2E smoke`; an older `nominal` reads as `story`) · `full` (the whole suite — normally CI's job) |
| E2E smoke | the few spec files every ship also runs, comma-separated — sign-in and the core loop, nothing more. `—` means none |
| E2E targets | where the end-to-end suite runs during the story cycle — browsers (e.g. `chromium`), devices or simulators, platforms; `—` means the project's own default. Ship always runs them all |
| Sandbox port base | a story's port or instance number is this plus its story number (`s04` → 3004) — see the `story-sandbox` skill. `—` when the product listens on nothing |
| Sandbox vars | the configuration values that must point at the story's own resources (a web app's own URLs, a mobile app's API base URL…), comma-separated |
| Sandbox schema | paths whose change means a schema or storage-format change, so the story gets its own data, comma-separated |
| Sandbox reset | the command that resets and seeds the local data |
| Build stage | when the release build runs: `ship-if-route` (only when a route, a manifest or the packaging configuration moved) · `ship` · `review` · `ci` · `—`. In a compiled language the test command already compiles; this setting governs the release build (optimized binary, package, bundle) |
| Intent source | `repo` (`docs/intents/`) or `tracker` (canonical external record, local pointer); applies only to new changes on an existing product |
| Intent read / Intent write | exact commands for the chosen tracker; environment: `ZTP_INTENT_REF`, `ZTP_INTENT_FILE`. `—` disables that access |
| Ops days | positive number of days for a periodic report; a caller may supply N explicitly |
| Ops window | positive number of minutes after deployment to observe; `—` means undecided |
| Ops rollback threshold | explicit metric, comparator, value, unit and window; `—` means the rollback assessment is unavailable |
| Protected paths | JSON array of repo-relative glob patterns; a trailing `/` protects its subtree. `[]` explicitly protects none |
| Production commands | JSON array of regular expressions for commands that must be blocked under Claude Code; `[]` declares none |
| Merge commands | JSON array of regular expressions for merge commands. Capture the target as `(?P<branch>...)` or declare `Merge resolve`; an unresolved target blocks |
| Merge resolve | exact read-only command returning the target `feature/<id>` or `chore/<id>`; receives `ZTP_GUARD_COMMAND`. `—` requires a branch capture |
| Eval model | exact model chosen by the declared headless runner; `—` disables evals |
| Eval config paths | JSON array of existing repo-relative current rules/skills/hooks to overlay on each pinned task base; must be nonempty to run |
| Eval timeout | positive maximum seconds for each headless/check command |
| CI review / CI evals | `yes` or `no`; optional jobs disabled by default |

## Project profile

Settled once by `/ztp-architect`, read by every agent. What is written here is never asked
again, and a tool it does not name is never proposed — no browser test on a product that has
no browser.

```
Product type:       —
Target environment: —
UI check:           —
E2E tool:           —
```

| Setting | What it says |
| --- | --- |
| Product type | from the PRD: `web app` · `mobile app` · `desktop app` · `api` · `cli` · `library` · `internal tool` · `system` · … |
| Target environment | where the product runs and is checked: `browser` · `ios simulator` · `android emulator` · `desktop` · `terminal` · `server` · `device` · … |
| UI check | how a screen is opened and looked at, e.g. `browser via <tool>`, `ios simulator + screenshot`. `—`: the product has no user interface — no screen is opened, no mockup is drawn |
| E2E tool | the end-to-end tool the `E2E` command runs, e.g. `playwright`, `detox`, `maestro`, `ctest`, `pytest`. `—`: none |

## Project commands

```
Package manager:   —
Test:              —
Test focused:      —
Typecheck:         —
E2E:               —
Build:             —
Deploy:            —
Smoke test:        —
Rollback:          —
Deployment logs:   —
Error tracking:    —
Performance signals: —
Usage signals:     —
Secret scan:       —
Review history:    —
Eval runner:       —
Eval check:        —
CI review runner:  —
```

A command left at `—` is one the agents cannot run: they say so rather than guess one.
`Test focused` runs only the given test files: `{files}` is replaced by their paths
(e.g. `pnpm vitest run {files}`). Left at `—`, the agents run `Test` followed by the paths.
`Deploy`, `Smoke test` and `Rollback` are filled by `/ztp-architect` when they are commands; a
manual step stays `—` here and is described in `docs/deployment.md`.

Observability is optional: `/ztp-setup` offers deployment logs and error tracking without
requiring them. `/ztp-ops` supplies its UTC windows/release as `ZTP_OPS_*` environment values
(see the command); the declared wrappers must support them or return filterable evidence.
With `--hooks`, `Secret scan` is required to commit: it must scan the exported staged blobs
at `ZTP_SCAN_DIR` and exit nonzero on a secret or an error. The hook runs it from the repo
root and never prints scanner output. `—` blocks commits rather than skipping the scan.
Guard arrays are declarations, not guessed defaults; review them before enabling hooks.

Headless contracts and CI activation are documented in DOC.md. `Eval runner` receives
`ZTP_EVAL_TASK`, `ZTP_EVAL_RESULT`, `ZTP_EVAL_MODEL`; `Eval check` also receives
`ZTP_EVAL_WORKTREE` and `ZTP_EVAL_ACCEPTED`. Both run with the replay as cwd. The checker
command/script must be trusted and outside the replay; use `ZTP_EVAL_SOURCE` to locate it.

## Project conventions

<< structure, stack, patterns, naming, commit rules — filled by /ztp-architect, as rules an agent can apply >>

### Zone rules

<< written by /ztp-architect, Step 6 — the detail lives only in the rule file; this table points to it, with the same `paths` >>

| Zone | Paths | Rule | Summary |
|---|---|---|---|
| << zone >> | `<< **/src/… /** >>` | .claude/rules/<< zone >>.md | << one line >> |
