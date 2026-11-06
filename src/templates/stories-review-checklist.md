# Stories Review — <product name>

> Fresh-context review of `docs/stories.md` against `docs/prd.md` and linked accepted intents. Each issue classified: critical / major / minor.

Sources reviewed: <PRD revision, intent ids and canonical revisions; inaccessible sources block>

## Perimeter coverage
| PRD feature / accepted intent outcome | Covered by | OK? |
|---|---|---|
| <feature> | <story id> | ✅ / ❌ |

- [ ] Every feature of the PRD "In scope (core loop)" table is delivered by at least one story
- [ ] Every linked intent is accepted and its outcome covered; canonical tracker sources verified

## Scope
- [ ] Any change to a PRD exclusion has an explicit approved intent decision
- [ ] No story goes beyond the perimeter

## Story quality
- [ ] Each story is an end-to-end shippable slice, not a technical layer
- [ ] Every acceptance criterion can become a test
- [ ] Agentic notes present and useful (files, constraints, traps)
- [ ] Complexity scored; no unsplit 5; every 4 states its risk

## The list as a whole
- [ ] Dependency order executable: no cycle, no forward reference
- [ ] Ids well-formed (`s<number>-<slug>`), unique and stable
- [ ] No overlap or duplication between stories

## Findings
<one line per issue: severity — story id (or "coverage") — what's wrong>

## Verdict
Max severity: <critical | major | minor | none>
Stories ready: <yes | no>
