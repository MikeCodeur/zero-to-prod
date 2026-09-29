---
description: Set the technical HOW — stack, foundation, conventions, environments and deployment
allowed-tools:
  - Read
  - Glob
  - Grep
  - Write
  - Edit
  - Bash
  - AskUserQuestion
---
You are setting the product's technical architecture.

Read: docs/prd.md, docs/stories.md, AGENTS.local.md
Output structure: @templates/architecture.md, @templates/deployment.md, @templates/foundation-checklist.md

The PRD's "Starting point" decides the path: an **existing codebase** is mapped and conformed to; a **new project** gets a recommended stack and a foundation built here. Either way the phase ends on a foundation that has been verified, not assumed. The user does not need to be an architecture expert: on a new project you recommend and justify, they decide.

This phase writes the only code that does not go through a story: the foundation — structure, configuration, tooling, one example test. No feature code. Anything a user would see as value belongs to a story.

## Step 1 — Existing codebase, or new project?
Read "Starting point" in docs/prd.md, and confirm it against the repository (AskUserQuestion only if they disagree).

### Existing codebase
Apply the codebase-analysis skill: actual structure, conventions, patterns, anchor points. This is code the user may not have written — map it before deciding anything. The codebase is imposed: conform to it, never propose a rewrite. Go to Step 3.

### New project
Go to Step 2.

## Step 2 — New project: recommend, validate, build

1. **Recommend one stack.** Derive it from the PRD — product type, constraints, integrations, the complexity of the in-scope perimeter — and from what the user or the team already masters (ask once, AskUserQuestion). Present **one recommendation**, with the reason for each structural choice (language, framework, data storage, authentication if the perimeter needs it, hosting target), and one or two alternatives with why they rank lower. Prefer mature, documented, widely used options: agents work best on stacks they know well.
2. **Validate** (AskUserQuestion): Accept / Change a component / Stop. Nothing is scaffolded before an explicit Accept.
3. **Record** each structural choice as an ADR in `docs/decisions/NNN-<slug>.md`, following @templates/adr.md — with the options considered and why they were rejected.
4. **Build the foundation**, using the official generators of the chosen stack rather than hand-written boilerplate:
   - the project structure, organized by the layers the testing doctrine names (business/service, persistence, adapter, view);
   - the configuration: formatter, linter, type checker if the language has one, test runner with **one example test that passes**, environment variables documented in an example file, secrets ignored by version control;
   - the commands the pipeline needs — test, typecheck (the compile step in a compiled language), e2e if the product has a user interface, build — through the stack's own build system or task runner.
   Keep it minimal: what every story will need, nothing a single story will add itself.
5. Then map what you just built exactly as you would an existing codebase (codebase-analysis skill): the conventions below must describe the real code, not the intention.

## Step 3 — Profile, conventions and project commands
1. Fill the architecture template from the analysis and the PRD needs.
2. Write the **"Project profile"** block of `AGENTS.local.md` — `Product type`, `Target environment`, `UI check`, `E2E tool` — from the PRD and the stack. This is the one place the project's nature is settled: every later agent reads it instead of asking, and never proposes a tool it does not name. A product without a user interface gets `UI check: —`. Set `E2E targets` to match (browsers, devices, platforms, or `—`).
3. Write the concrete conventions into `AGENTS.local.md`, under "Project conventions": structure, naming, patterns, error handling, data access, where tests go, commit rules. Written as rules an agent can apply ("one service file per domain in src/services"), not observations ("there are some services"). Keep them short: every agent context loads them.
4. Complete the "Project commands" block in `AGENTS.local.md` with the commands that now exist — `Package manager`, `Test`, `Typecheck`, `E2E`, `Build`. Quote them from the repository; a command the project does not have stays `—`, never invented.

## Step 4 — Environments and deployment (once per project)
Define how the product reaches production, following @templates/deployment.md, and ask what the repository cannot answer (AskUserQuestion):
- the environments (at minimum production — wherever users get the product: a server, a hosting platform, a package registry, an internal distribution channel; staging or preview if they exist), their URL, access point or registry, and how configuration and secrets reach each one;
- how a deployment is triggered — automatically on merge into the target branch, or by a command;
- the **smoke test**: the few checks that prove production is alive and the core loop answers, runnable right after a deployment;
- the **rollback**: the exact procedure that restores the previous version, and what it does not undo (a migration, sent emails, external calls).

Write it to `docs/deployment.md`. Fill `Deploy`, `Smoke test` and `Rollback` in the "Project commands" block of `AGENTS.local.md` when they are commands; a step that is manual stays `—` there and is described in `docs/deployment.md`. Nothing here is invented: a hosting target not chosen yet is written as an open point, and `/ztp-ship` will stop on it.

## Step 5 — Verify the foundation
Run every item of @templates/foundation-checklist.md for real, using the project commands quoted verbatim, and record the result — command, exit code — in `docs/foundation.md`. On an existing codebase the checklist verifies what is there: a red item is reported, never silently fixed, and whether it blocks is the user's decision. On a new project every applicable item must be green before the phase ends: a foundation that does not build is not a foundation.

## Step 6 — Commit
Run `./install.sh --target <the targets this project uses>` so the conventions reach `AGENTS.md`. Commit the foundation, `docs/architecture.md`, `docs/deployment.md`, `docs/foundation.md`, the ADRs and `AGENTS.local.md` on the default branch (`chore: foundation` for the code, `docs: architecture` for the documents).

End with: "Architecture ready, foundation verified (docs/foundation.md), deployment defined (docs/deployment.md). Next step: /ztp-design-system (products with a user interface), then /ztp-research <story>"
