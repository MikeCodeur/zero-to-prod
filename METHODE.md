# Idea to Prod — the method

Idea to Prod is a software delivery method driven by AI agents (Claude Code, Codex). It takes a project from an idea to production: a web or mobile application, an internal tool, an API, a new project or an existing codebase, on any stack.

It rests on one observation: an agent produces plausible code, and plausible is not correct. The method therefore organizes the work so that every claim is verified by a context that did not write it, and every step blocks until the previous one is proven.

This document explains the method. The exact rules live in `src/AGENTS.md` and in each command; where they differ from this page, they win.

## 1. Principles

**No code outside the pipeline.** No feature is written without a story, a validated plan and a review. The context that drives execution does not have the write tools: it delegates to an implementation agent. The rule is carried by the tooling, not by good intentions.

**The context that writes never reviews itself.** An agent is blind to its own mistakes. Reviews — of the breakdown and of the code — run in fresh-context, read-only subagents.

**Everything blocks by default.** No validated plan, no execution. A critical defect in review, no ship. A red smoke test in production, no ship. Nothing is forced through.

**Each check runs once, and once only.** A deterministic command re-run on the same code returns the same answer. Focused tests run during the work, the full suite and the type check once at the end, end-to-end tests and the production build once when shipping.

**The files are the state.** Everything the pipeline produces is markdown under `docs/`, versioned. No database, no state file: progress is derived from the files and git, so it cannot go stale.

## 2. Framing — once per project

| Step | Command | What it produces |
|---|---|---|
| Settings | `/itp-setup` | `AGENTS.local.md`: where a story lands, who validates a plan, who draws the screens, the project's commands. Four questions; everything else has a default. |
| Product frame | `/itp-prd <idea>` | `docs/prd.md`: the WHAT and the WHY, never the HOW. |
| Breakdown | `/itp-stories` | `docs/stories.md`: stories shippable end to end. |
| Breakdown review | `/itp-stories-review` | `docs/reviews/stories.md`: perimeter coverage checked in a fresh context. |
| Architecture | `/itp-architect` | The stack, a verified foundation, the conventions, the environments and the deployment. |
| Design system | `/itp-design-system` | `docs/design-system.md`: tokens, components, measured contrasts. Only for a product with a user interface. |

**The product frame** starts with **idea validation**: the problem and what it costs today, the users, and the unproven hypothesis the project stands on, with the measurable signal that will confirm it. This is what stands in for a specification when no reference product exists. Then come the **starting point** (new project, existing codebase, replacement of a product or system) and the **product type**, an optional **reference** (existing product, legacy system, mockups), the **perimeter** (each feature scored for complexity 1 to 5), the exhaustive **out-of-scope** list, the constraints and measurable success criteria. Nothing is filled in without the user's validation.

**The breakdown** produces stories that each deliver shippable value, never a technical layer ("create the table" is not a story; the table is created inside the story that needs it). Every acceptance criterion must be able to become a test. Every story carries an id `s<number>-<slug>` that names all its files and its branch, a complexity score (a 5 is split before planning) and notes for the agent. The breakdown review walks the perimeter table first: a promised feature covered by no story is the most expensive defect in the pipeline, invisible until ship.

**The architecture** follows the starting point.
- *Existing codebase*: the agent maps it (structure, conventions, anchor points) and conforms to it, never proposing a rewrite.
- *New project*: the user does not need to be an architecture expert. The agent **recommends one stack**, justified by the PRD and by what the team already masters, with the alternatives it ranks lower. The user accepts or changes it; each structural choice becomes a recorded decision (ADR). The agent then **builds the foundation** with the stack's official generators: structure, tooling, one passing example test, documented environment variables, the pipeline's scripts.

Either way, the conventions are written as rules the development agents can apply, and the **environments and the deployment** are defined once in `docs/deployment.md`: production (and staging if it exists), what triggers a deployment, the smoke test, the rollback procedure and what it does not undo. The phase ends with an **executed checklist** (`docs/foundation.md`): install, example test, type check, lint, build, start in the target environment, secrets kept out of the repository, commands and conventions true to the code. On a new project every applicable item must be green.

## 3. The cycle — once per story

One story = one `feature/<id>` branch = one dedicated worktree = one PR = one commit on the target branch.

    Research → Design → Plan → Execute → Review → Ship

| Step | Who | What matters |
|---|---|---|
| **Research** | main agent | The real state of the code, not the one the docs describe. Checks the story's **premise**: a function that exists but fails on the story's case invalidates the story. Re-scores complexity. |
| **Design** | main agent | Screens derived from the design system, nothing invented. An existing screen changed: a list of deltas, no mockup. A new screen: exactly one mockup, rendered and looked at in the target environment. |
| **Plan** | main agent | Small verifiable tasks, the story's interdicts, the point everything turns on, the test strategy. Validated by a human or by the agent per the settings; `validated: yes` conditions execution. |
| **Execute** | `implementer` subagent | Task by task, focused tests, then the full suite and the type check once. Writes a **verification record** that ties the results to the exact code tree. One commit. |
| **Review** | `reviewer` subagent, fresh context | Opens every import and API the diff cites, compares the diff to the plan, and **proves the tests bite**: it neutralizes the central invariant and counts the tests that turn red. Zero red means the invariant is untested. |
| **Ship** | main agent | Exit gate (end-to-end, build), squash merge, **deployment, smoke test in production**, documented rollback if red, cleanup only after proof. |

**Only a critical defect blocks.** A major stays traced in the report and is fixed in a next cycle; a minor is style. Two fix loops at most. **A defect is not a story**: it goes to the issue tracker, not into the perimeter.

**Three tracks, the same gates.**
- *Full pipeline*: the six steps, six contexts.
- *Short track* (`/itp-flow`): for a simple story, research and plan fused into one pass, then the same implementer, the same review, the same ship. A migration, a new screen, an authorization or API contract change, or an added dependency sends it back to the full pipeline, even mid-flight.
- *Quick Fix*: on explicit request, for a local, reversible adjustment with no business impact (a color, a label). Everything else goes through the pipeline.

`/itp-orchestrator` chains a full cycle with two human checkpoints (validate the plan, confirm the ship); `/itp-status` shows progress and the next useful command.

## 4. Gates and tests

| Gate | Check | What it blocks |
|---|---|---|
| Plan validated | `validated: yes` in `docs/plans/<id>.md` | Execution, and any code commit on the story branch (git hook) |
| Verification current | The tree recorded in `docs/verif/<id>.md` matches the commit | Decides whether the review trusts the results or replays them |
| Ship allowed | `Ship allowed: yes` at the end of `docs/reviews/<id>.md` | The ship, entirely |
| Production verified | Green smoke test after deployment | The story's cleanup; a red one triggers the rollback |

These gates are file reads, not judgment calls: they work the same under Claude Code, under Codex and in CI (`itp-gate.sh`).

**Testing doctrine.** Volume is not a safety net: a test budget per story (25 by default), and a plan that wants more must say why. Each rule is tested at the layer where it lives, once. The criterion that replaces the count: **a test that stays green when the rule it names is deleted is worse than no test.** No "red first" ceremony during implementation; the neutralization proof happens in review, in a fresh context, where it actually finds defects.

## 5. Tools, installation, settings

One source (`src/`), one installer, one output per tool:

    curl -fsSL https://raw.githubusercontent.com/MikeCodeur/idea-to-prod/main/install.sh | bash                      # Claude Code
    curl -fsSL https://raw.githubusercontent.com/MikeCodeur/idea-to-prod/main/install.sh | bash -s -- --target codex  # Codex

**The project's nature is settled once.** `/itp-architect` writes a *project profile* in `AGENTS.local.md` — product type, target environment, how a screen is checked (`UI check`, or `—` when there is no user interface), end-to-end tool. Every agent reads it and never asks again, nor proposes a tool it does not name: no browser test on a C++ program.

**No stack is assumed.** The pipeline never runs a command it invented: it runs the project's own commands (test, typecheck, e2e, build, deploy, smoke test), quoted from `AGENTS.local.md`. The same stages hold for a web app, a mobile app, a C++ program or a library: in a compiled language the compile step is the type check, the "production build" is the release build, and "production" is wherever users get the product — a server, a registry, an installer.

Options: `--target claude|codex|all`, `--global` then `init` per project, `update`, `--check` (lists installed files modified locally), `--hooks` (gates enforced by git). The rules live in `AGENTS.md`, read natively by both tools; the project's settings in `AGENTS.local.md`, which the installer never touches. Commands are slash commands under Claude Code and skills under Codex. The guarantees carried by tool permissions are mechanical under Claude Code and looser under Codex; that is why the gates are also carried by the repository.

## 6. Known limits of V1

- **Team mode.** The method assumes one operator per repository: no distribution of stories between people, no lock on a story in progress, no convention for cross human review. To be addressed in V2.
- **Mobile.** The "target environment" abstraction covers screen verification; native builds, signing and store publication are not covered.
- **Operations.** Deployment stops at the smoke test and the documented rollback: no monitoring, alerting or production error tracking.
- **Tools.** Claude Code and Codex only.
