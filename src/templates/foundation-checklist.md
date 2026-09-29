# Foundation — <product name>

> Written by /ztp-architect. Every item is run, not read: the command, its exit code, and the
> date. An item that does not apply says `n/a` and why. On a new project, every applicable
> item is green before the phase ends.

| # | Check | Command | Result |
|---|---|---|---|
| 1 | Dependencies install and the project configures from a clean checkout | `<...>` | <exit code> |
| 2 | The example test runs and passes | `<Test>` | <exit code · N passed> |
| 3 | The type check passes — the compile step in a compiled language | `<Typecheck>` | <exit code · n/a> |
| 4 | The linter passes | `<...>` | <exit code · n/a> |
| 5 | The release build succeeds (bundle, binary, package) | `<Build>` | <exit code · n/a> |
| 6 | The product starts in its target environment (server, browser, simulator, CLI) | `<...>` | <what was observed> |
| 7 | Secrets are ignored by version control; an example environment file documents every variable | — | <yes / no> |
| 8 | "Project commands" in AGENTS.local.md match the repository — none invented | — | <yes / no> |
| 9 | "Project conventions" in AGENTS.local.md describe the real code, as rules | — | <yes / no> |
| 10 | "Project profile" in AGENTS.local.md is filled — product type, target environment, UI check, E2E tool | — | <yes / no> |
| 11 | Every structural choice has an ADR in docs/decisions/ | — | <list> |
| 12 | docs/deployment.md defines production, the trigger, the smoke test and the rollback | — | <yes / open points> |

## Red items
<each red item: what failed, the error, and — on an existing codebase — the user's decision on whether it blocks>

Foundation status: <verified | verified with accepted red items | not verified>
