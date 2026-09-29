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
Verification mode: record
Full suite:        execute-end
E2E stage:         ship
E2E scope:         nominal
E2E targets:       —
Build stage:       ship-if-route
Issue tracker:     github
Worktree root:     .worktrees/
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
| Verification mode | `record` (the implementer records what it ran; the reviewer checks the record instead of re-running) · `rerun` (the reviewer runs everything itself) |
| Full suite | when the whole unit suite runs: `execute-end` · `ship` · `both` |
| E2E stage | when the end-to-end suite runs: `execute-end` · `ship` · `ci` · `—` |
| E2E scope | how far the end-to-end suite goes; `nominal` is one happy path |
| E2E targets | where the end-to-end suite runs during the story cycle — browsers (e.g. `chromium`), devices or simulators, platforms; `—` means the project's own default. Ship always runs them all |
| Build stage | when the release build runs: `ship-if-route` (only when a route, a manifest or the packaging configuration moved) · `ship` · `review` · `ci` · `—`. In a compiled language the test command already compiles; this setting governs the release build (optimized binary, package, bundle) |

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
Typecheck:         —
E2E:               —
Build:             —
Deploy:            —
Smoke test:        —
Rollback:          —
```

A command left at `—` is one the agents cannot run: they say so rather than guess one.
`Deploy`, `Smoke test` and `Rollback` are filled by `/ztp-architect` when they are commands; a
manual step stays `—` here and is described in `docs/deployment.md`.

## Project conventions

<< structure, stack, patterns, naming, commit rules — filled by /ztp-architect, as rules an agent can apply >>
