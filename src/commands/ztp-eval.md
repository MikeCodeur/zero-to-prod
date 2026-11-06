---
description: Collect accepted reference tasks and replay them headlessly against the current agent configuration
argument-hint: <collect | run | run --case id>
allowed-tools:
  - Read
  - Glob
  - Grep
  - Write
  - Bash
  - AskUserQuestion
---
# ztp-eval — Agent configuration regression checks (optional)

Request: $ARGUMENTS
Templates: @templates/eval-task.md and @templates/eval-report.md

## Collect
Read the project's real completed work and accepted results. Assemble **20–50 representative
tasks**, one `docs/evals/<id>.md` each: original prompt, pinned starting commit, accepted
commit, expected result, executable checks and source evidence. Do not manufacture 20 cases
or label unverified work successful to reach the target. If the history is insufficient,
show the smaller candidate set and what evidence is missing. A resolved incident is a useful
candidate; neither an unresolved ops finding nor a synthetic success is a reference result.

Have the owner confirm cases and expected results. `Eval check` must verify behavior against
these expectations, not trust the model saying "done". Confirm the accepted commit passes
that check before adding the case. Keep the checker and its task input outside the agent's
writable replay directory; the runner must not be able to weaken its own evaluation.

## Run
Read `AGENTS.local.md`: `Eval runner`, `Eval check`, `Eval model`, `Eval config paths`,
`Eval timeout`. Missing/`—` commands, unknown model, missing configuration or unproven cases
→ stop, never invent a CLI, flags or result. `Eval config paths` lists the **current** rule,
skill and hook files to copy over each historical base; the runner selects the declared model.

Run `python3 .ztp-tools/ztp-eval.py` (or add `--case <id>` for a named pilot). The installed
runner creates a disposable worktree per case, copies the declared current configuration,
invokes the exact headless runner and trusted checker, records exits and writes a Markdown
report in `docs/evals/runs/`. No production access, publish, merge or application of the
generated diff. The headless command must itself enforce the project's sandbox/tool limits;
a Git worktree is filesystem isolation, not a credential sandbox. Never resume an author
session. Missing resources, runner/check errors or timeouts are failures, not successes.

Every case in a full suite must pass. Compare failures only across identical task/check
sets; do not rewrite expectations to accept a regression. A single-case pilot cannot certify
the full suite. Re-run when the model, rules or skills change; CI can opt in with `CI evals: yes`.
No schedule, paid run or credential is set up implicitly by installation.

End with the report path, model/configuration identity, pass/fail counts, comparison limits
and newly failing cases. Keep raw model output out of the committed report.
