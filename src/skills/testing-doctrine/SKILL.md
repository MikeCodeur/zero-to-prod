---
name: testing-doctrine
description: Acceptance tests first — one per criterion, red for the right reason, reviewed, frozen — then what to test where, how much, and when to run it. Preloaded in the implementer and the reviewer; the rest of the pipeline does not need it.
---
# Testing doctrine

The rules here decide what gets written and what gets run. They live in a skill rather than
in AGENTS.md because only two agents act on them — the one that writes the tests and the one
that judges them — and every other context was paying to load them.

**The only budget is `Test budget` in `AGENTS.local.md` (25 when absent).** A plan never declares its own budget or an override — not "Budget: 40", not anyone's exception, not one copied from an earlier plan. A story that needs more tests stops: the plan says so, and is not validated. Raising the budget is a change to AGENTS.local.md, made by its owner, outside the plan.

Measured in production use: the suite grows by dozens of tests per story, and **most of
those stories still ship their central invariant with no net at all** — every one found by
mutation during review, none by the volume. The number does not measure the net. It buys false confidence, and it is
slow: a suite that takes half an hour to run is a suite nobody runs.

**The cycle: acceptance tests first, then the code.**

1. **One test per acceptance criterion** — not one per function, and never several for one
   criterion: the plan's table has exactly one row per criterion, and `ztp-gate acceptance-tests
   <id>` refuses anything else. Its name carries the
   criterion's id (`AC2 — refuses a booking outside opening hours`), and it lives at the layer
   where the rule lives (table below). A purely visual criterion names its `UI check` instead.
2. **Red for the right reason.** Run the new files with `Test focused`: each fails on its
   assertion — never on an import, a syntax error, a missing fixture or a crashed setup. Write
   only skeletons to get there: the signatures the tests call, returning a neutral value
   (`null`, an empty list, `false`), no logic. Without them the test fails on a missing import,
   and that red proves nothing.
3. **Reviewed before any code**, per `Test validation`. The six hollow shapes below are
   cheaper to catch now than after the code makes them green.
4. **Frozen once validated.** The tests are committed alone (`test(<id>): acceptance tests`);
   `docs/tests/<id>.md` lists the frozen files. During the code phase no frozen file is edited,
   renamed, skipped, loosened or deleted. A test you believe wrong: stop and report it — it goes
   back to review, it is never fixed in passing.
5. **Code until green**, running only the test files concerned. The full suite runs once, at
   the stage `Full suite` sets.

**Which tools** — the ones `AGENTS.local.md` names: `E2E tool`, `UI check` and the project
commands. Never propose another, and never a web tool on a product whose `Target environment`
is not a browser.

**Where the tests go**

| Layer | What to test |
| --- | --- |
| Business/service layer and its authorization | Everything that matters, **with the repository mocked**. The **role or permission matrix belongs to the policy test, written once** — a service command invents no access rule, it calls the policy. The service test then covers the **business rule**: one nominal case, one refusal per rule it owns. |
| Persistence (DAO / repository) | **The only tests on a real database.** Only what no reading catches: the idempotency ordering of a retryable mutation, and the tenant/ownership clause of each query. Call the repository **directly** — the service refuses upstream, so an applicative call never reaches the guard. |
| Adapter (HTTP route, controller, CLI command, message handler, screen action) | Only what the service does not do: payload parsing, field clearing, status mapping. **An adapter never re-tests an access refusal** — it verifies once that a refusal becomes the adapter's refusal response (a 403, an error code, a message), never per role and never per rule. |
| Component / view | Almost none. Only genuine conditional logic of its own; rendering a list is not a rule. |
| End-to-end | One scenario, for what unit tests structurally cannot see — typically a side effect written inside a transaction, which mocked repositories hide. The rules below. |

Most tests are unit or service tests with a mocked repository; a real database for DAOs only;
one end-to-end per story.

**End-to-end, specifically**

An end-to-end run costs a cold start, a migration, a seed and a browser, device or platform
driver, and the suite is replayed by every story after this one. Measured on a real web
project: 86 specs, 216 tests, seven minutes a run, and most of the reds were specs repaired
for a wording change rather than a broken feature. The rules hold whatever the `E2E tool`; the
examples are a web app's — find the equivalent for yours.

- **One spec per story, one scenario in it** — none when no unit test is structurally blind
  to what the story does.
- **It asserts an effect**, observed from outside as a user or a caller would: on the web a
  URL reached, a row persisted and read back, a real HTTP status; on mobile or desktop a screen
  reached and a record still there after relaunch; for a CLI or a binary an exit code, an
  output, a file written. **A label, a heading or a button merely being visible is not an
  end-to-end assertion** — if the screen must be looked at, look at it with `UI check` and
  record it.
- **No matrix.** Locales × themes × viewports, devices × OS versions, every route or screen in
  a loop, every role: each one belongs to the layer that owns it (policy test, i18n check,
  visual check), or nowhere. Written inside one test, it still counts as what it replays.
- **Select on a stable identifier, never on copy that can change**: an accessible role or a
  `data-testid` on the web, a `testID` or accessibility identifier on mobile, an automation id
  on desktop. A wording change must not break a spec.
- **A story does not edit another story's spec**, unless its own change legitimately breaks
  it — and then the verification record says which, and why.

**Four cuts, each measured in real use**

1. **The matrix once, in the policy test.** Replayed per command, it takes a single service test file past fifty tests.
2. **No enum exhaustiveness.** Testing every ordered pair of a transition table proves nothing the legal transitions plus one representative refusal do not already say.
3. **Never the same rule at two layers.** Pick the layer where the rule lives.
4. **No adapter re-asserting an access refusal.**

**The guarantee now sits upstream.** Each criterion has a test, proven able to fail, reviewed
before the code, and frozen so the code cannot bend it to pass. The implementer neutralizes
nothing: the red run already proved each test can fail.

**Neutralization in review becomes a spot check**, not the main proof: the reviewer
neutralizes the one invariant the story turns on, on its own test files. Zero red is still a
finding — it means the frozen test passed review without exercising the rule.

**The failure mode this pipeline keeps producing: a test that names an invariant without
exercising it.** Most stories ship one. Six shapes seen repeatedly, worth citing
verbatim in a prompt because they are hard to spot by reading:

1. a hand-written query in the test instead of a call to the code under test — it tests the database, not the repository;
2. a payload the real interface never produces;
3. a `catch` that swallows the failure, so the assertion passes when nothing throws;
4. an end-to-end test that stays green while rendering zero rows;
5. a **fixture** whose identifier lets a downstream guard answer for the guard under test — invisible when reading assertions;
6. a **mock double that replays** the clause instead of evaluating it.

**The criterion that replaces the count: a test that stays green when the rule it names is
deleted is worse than no test** — it hides the hole it claims to cover.

**When to run what — each thing once, and once only**

A deterministic command re-run on the same code returns the same answer. Running the suite
in Execute, again in Review, again per mutation and again at Ship buys nothing and costs
four times the wall clock. Each check therefore has exactly one stage, and the stage is a
setting in `AGENTS.local.md`.

| Run | When | Setting |
| --- | --- | --- |
| Acceptance tests, red | **once, before any code** — the new test files only, to prove each fails on its assertion | `Test focused` |
| Focused suite | after each task — the working loop. Only the test files concerned, through `Test focused`, never the whole project; frozen files are run, never edited | `Test focused` |
| Full suite | **once**, after the last task | `Full suite` |
| Type check | **once at the very end, after the last edit, and not optional** — most runners transpile without checking types and most linters do not type, so a type error in a test file passes lint, passes the suite, and fails CI | — |
| End-to-end | **once, at ship, just before the merge** — never in the loop, never twice: a run costs a cold start, a migration, a seed and a browser, device or platform driver. At ship it is the story's own specs plus `E2E smoke`; the whole suite belongs to CI | `E2E stage` · `E2E scope` · `E2E smoke` · `E2E targets` |
| Production build | at ship, and **only when a route, a manifest or the packaging configuration moved** — that is the one rupture a type check cannot see. A modern build type-checks on its way, so it is the build or the type check, never both | `Build stage` |
| Format | never as a repo-wide sweep — format the staged files at commit; a story is one commit | — |

**Compiled languages** (C++, Rust, Go, Swift, Kotlin, Java…): compiling is part of running a
test, and the compiler is the type check. `Typecheck` is then the compile step — or `—` when
`Test` already compiles everything — and "production build" means the release build: optimized
binary, package or bundle. The stages do not change: focused tests per task, full suite once,
release build once at ship.

**The reviewer's spot check runs on the invariant's own test files, not on the suite.** A
neutralized guard turns red in the one or two files that name it; replaying the whole
project to learn that is the single most expensive habit this pipeline ever had.
