---
description: Ship the story — exit gate, merge per Merge mode and Ship confirmation, deployment, smoke test in production
argument-hint: <story id or name>
allowed-tools:
  - Read
  - Bash
  - AskUserQuestion
---
You are shipping a story. Target story: $ARGUMENTS

Resolve $ARGUMENTS to the story id (`s<number>-<slug>`) — the review file docs/reviews/<id>.md must exist for it.

Locate `.worktrees/<id>`, verify its branch is exactly `feature/<id>`, and run
the entire command from that absolute worktree. Missing worktree, wrong branch,
detached HEAD or repository base → STOP; never checkout the feature branch in
the repository base directory.

## Step 0 — Gate (fail-closed, mechanical)
Run: `grep -q '^Ship allowed: yes' docs/reviews/<id>.md`
If the file is missing or the command fails, STOP immediately: "Ship blocked — review missing or negative. Run /itp-review <id>." Nothing below runs without a passing gate.

Then proceed:
1. Read `Merge mode`, `Target branch`, `Ship confirmation`, the stages (`Full suite`, `E2E stage`, `E2E scope`, `Build stage`) and the project commands (including `Deploy`, `Smoke test`, `Rollback`) from AGENTS.local.md, and read docs/deployment.md. Missing file or missing setting → STOP: "No project settings. Run /itp-setup." Never assume a mode — every step below branches on them.
2. Without switching branches, commit docs/reviews/<id>.md on the already verified feature branch if not already committed (the PR must carry its review). Then run the **exit gate — the one place the expensive checks run in the whole cycle**, per the stages in AGENTS.local.md, using the project's own commands quoted verbatim:
   - **Unit suite.** `Full suite: execute-end` (the default) → it already ran in Execute, and docs/verif/<id>.md proves it for this exact tree: check `itp-gate verif-current <id>` instead of re-running, and run `<Test>` only if that check fails. `ship` or `both` → run `<Test>` in full here.
   - **End-to-end.** `E2E stage: ship` → run `<E2E>` once, at `E2E scope`, on every target — browser, device, platform — the project configures. This is the cycle's only end-to-end run; nothing upstream is allowed to have made it.
   - **Production build.** `Build stage: ship` → run `<Build>`. `ship-if-route` → run it only when the story's diff moved a route, a manifest, the file-based routing or the packaging configuration — the one rupture a type check cannot see; otherwise skip it and say so.
   - **`ci` for any of them** → do not run it here: read the branch's checks (`gh pr checks`) and stop unless they are green.
   A command given as `—` does not exist in this project: say so, never substitute one. Any red → stop, and back to `/itp-execute <id>` in fix mode. Nothing merges on a red gate.
3. `Merge mode: local` → skip this step entirely, there is no PR. Otherwise: if a PR for feature/<id> already exists, don't open a duplicate — check its state: MERGED → jump straight to the Deploy step; OPEN → continue. Otherwise push the branch and open a clean PR from feature/<id> to the target branch: clear title, structured description (what, why, how to test), readable diff. Include the review verdict (max severity + findings summary) in the PR body.

## Step 4 — Merge (per the project's settings)

**Always squash.** One story = one commit on the target branch. The working commits stay on the branch, the history stays readable, and no merge commit is created. Without it a seven-story release lands as fifty commits nobody can read.

`Ship confirmation: human` → ask via AskUserQuestion before merging, whatever the mode: "Merge <id> into <target branch>?" — Merge / Not now. Only an explicit Merge proceeds. The gate authorizes the ship; the human decides it.

- **`Merge mode: pr`, confirmation `human`: do NOT merge.** End with: "PR opened: <url>. Merging is yours to decide (human review, protected branch, CI) — **squash-merge it**. After merging, rerun /itp-ship <id> to deploy, run the smoke test and clean up the branch."
- **`Merge mode: pr`, confirmation `automatic`**: `gh pr merge <url> --squash --delete-branch=false`, then the Deploy step.
- **`Merge mode: local`**: no PR at all. From the repository base directory, squash the story into the target branch: `git merge --squash feature/<id>` then commit with the story's message. Push it if the project has a remote. Then the Deploy step.

## Step 5 — Deploy and smoke test (ONLY after a PROVEN merge)
The merge is proven first, exactly as the Cleanup step's point 1 says. Then production, per docs/deployment.md:

1. **Deploy.** Deployment automatic on merge → wait for it and read its status where docs/deployment.md says it is visible. Deployment by command → run `<Deploy>`, quoted verbatim. Manual procedure → state each step and ask the user (AskUserQuestion) to confirm it is done. No docs/deployment.md, or an open point that blocks the deployment → STOP here: "Merged, not deployed — docs/deployment.md is missing or incomplete. Run /itp-architect to define the deployment." Never improvise a deployment.
2. **Smoke test.** Run `<Smoke test>`, or the checks listed in docs/deployment.md, against production. Report each check and its result.
3. **Red smoke test → the story is not shipped.** Apply the rollback from docs/deployment.md (`<Rollback>` or its steps) — `Ship confirmation: human` → ask first (AskUserQuestion: "Roll back production?" — Roll back / Not now); `automatic` → run it. State what the rollback does not undo, as docs/deployment.md lists it. Open the defect in the issue tracker (`Issue tracker`), never in docs/stories.md, and STOP: no cleanup, the worktree stays for the fix.
4. Green → the Cleanup step.

End a completed ship with: "Story shipped — deployed, smoke test green (<production URL>). Cycle complete. Next story: /itp-research <story>"

## Final step — Cleanup (ONLY after a PROVEN merge and a green smoke test)
Never clean up on the promise of a merge — only on proof:
1. Verify the merge really happened. `Merge mode: pr` → `gh pr view feature/<id> --json state,mergedAt --jq '.state'` must return exactly `MERGED`; an OPEN PR, a closed-unmerged PR, or an "about to be merged" does NOT qualify: skip cleanup entirely. `Merge mode: local` → the squash commit must be present on the target branch.

   Do NOT use `git merge-base --is-ancestor` here: a squash merge rewrites the work into a new commit, so the branch's commits are never ancestors of the default branch. The check would fail on every correctly merged story and no branch would ever be cleaned up.
2. Verify the dedicated worktree is clean, then remove that exact worktree with
   `git worktree remove <repository-base>/.worktrees/<id>`. A dirty worktree is
   a hard stop; never use `--force`.
3. Only after the worktree is gone, delete the branch, local and remote:
   `git branch -D feature/<id>` and `git push origin --delete feature/<id>`.

   `-D` is required, again because of the squash: `-d` refuses a branch git
   considers unmerged, which is every squashed branch. The safety therefore
   rests entirely on step 1 — never remove the worktree or branch without the
   `MERGED` proof.

The content is in the default branch, the audit trail is in the merged PR: the branch has no further use.
