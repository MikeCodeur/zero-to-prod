---
name: story-sandbox
description: The isolated runtime of a story worktree — whatever the product needs to run and be tested without touching another story's: port, database, simulator, data directory. Loaded by the commands that bootstrap a worktree, preloaded in the implementer and the reviewer.
---
# Story sandbox

A story lives in its worktree. It must also run in **its own** resources: otherwise two
stories step on each other, and the symptoms never look like their cause — a login that works
then fails, a test reading data another agent wrote, an old process still serving a stale build.

**The principle is universal; the resources depend on `Product type` and `Target environment`
(`AGENTS.local.md`).** The examples below are a web app's. For another technology, find the
equivalent of each resource and apply the same rules:

| Resource | Web app (example) | Elsewhere — find the equivalent |
| --- | --- | --- |
| Where it is served | a port | mobile: a simulator/emulator instance, a bundler port · desktop: a profile or instance name · server/daemon: a port or socket · CLI/library: usually none |
| Its data | a local database | a local SQLite file, an app container, a data directory, a temp directory per story |
| Its configuration | `.env*` files | config files, plist/gradle properties, a profile, environment variables |
| What runs the end-to-end check | a browser on a production build | a release build on a simulator or device, the packaged binary, the CLI invoked as a user would |

The project-specific values come from `AGENTS.local.md`: `Sandbox port base`,
`Sandbox vars`, `Sandbox schema`, `Sandbox reset`. A setting at `—` is a resource this
product does not have: skip that step and say so, never guess one.

## The convention

| Element | Rule | `s179-use-admin`, port base 3000 |
| --- | --- | --- |
| Branch | `feature/<id>` | `feature/s179-use-admin` |
| Worktree | `.worktrees/<id>` | `.worktrees/s179-use-admin` |
| Port (or instance) | `Sandbox port base` + story number | `3179` (`s04` → `3004`) |
| Data | shared `<repo>_dev` by default, `<repo>_<id_snake>` when the story needs its own | `myapp_s179_use_admin` |

Everything derives from the story number, so two stories never collide and nobody asks
"which one is free?". **Never pick another port or instance because this one was taken** —
free it instead: the configuration points at the derived one, and anything else makes it lie.

## 1. Local configuration

A new worktree has none of the untracked configuration files. Copy them from the repository
base before anything else — including the ones only a release build reads. Report the names,
never the values.

**Never link dependency directories** (`node_modules`, vendored packages, build caches) to the
base directory: many toolchains refuse a path outside their root, and nothing can run. Install
or build for real, from the lockfile.

## 2. Data: reuse before creating

A name always carries the repository as prefix: one local database server, or one temp
directory, serves several projects.

**Default: the shared one.** One store per story is ten stores to seed, migrate and forget, for
work that mostly never touches the schema. A dedicated one in two cases only:

1. **The story changes the schema or the storage format** — a path under `Sandbox schema`
   appears in `git diff <default-branch>...HEAD --name-only`. A migration applied to shared data
   breaks every other branch. Check it, don't guess it.
2. **Another agent is already using the shared one** — two concurrent resets and both sessions
   test data they did not write.

## 3. Point the configuration — in the worktree's own files

In the worktree's configuration, never in a shared file:

- the data location, on the store chosen in step 2;
- **every variable listed in `Sandbox vars`, on the story's own port or instance.** They go
  together: a web app's auth URL on another port breaks client calls without a clear message;
  a mobile app's API base URL on the wrong host tests another backend.

**Check the test configuration too** (`.env.test` on the web, a test scheme or profile
elsewhere). It is copied with the rest and often forgotten: it may point at a remote service, or
carry another story's settings that switch on tests unrelated to this one.

## 4. Before any destructive command

Reset, clear, migrate, seed, wipe a simulator — first read where the command will act and prove:

- it is local (`localhost`, `127.0.0.1`, a local socket, a local file or simulator);
- it is exactly the store chosen in step 2.

Remote, production, preview, ambiguous, or the base checkout's own development data → refuse.
On shared data a reset is visible to every worktree using it: announce it, never run it in the
middle of another agent's test.

Then `Sandbox reset`. Test accounts come from the seed, never from invention. Never a real
account.

## 5. Run

Start the product on the story's own port or instance, then tell the human the five facts
together: **where it runs, port or instance, worktree, branch, data**.

## 6. End-to-end

End-to-end tests run against a **release build** in the story's sandbox — on the web a
production build served on the story's port, on mobile a release build on the story's
simulator, for a CLI or a binary the packaged artifact. Values baked in at build time point at
the resources the build was made for; a build run elsewhere tests something else, often without
an error.

Before running: nothing else holds the story's port or instance. A server that fails to bind
fails silently while the old process keeps serving a stale build — stop it first. Test
configuration pointing at a remote service → do not run.

Tests that create data leave it behind; `Sandbox reset` puts it back.

## 7. Clean up

At the end of a test session, stop what holds the story's port or instance. A dedicated store
is dropped with its branch, when the story ships; **never drop the shared one**, other worktrees
use it. Never stop a shared service itself — only the stores are isolated.

## Never

- Two worktrees on the same port or instance.
- A destructive command without reading where it acts right before.
- A shared configuration file edited to rescue one story.
- A port or instance picked "because the other one was taken".
