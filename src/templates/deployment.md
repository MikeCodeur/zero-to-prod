# Deployment — <product name>

> Defined once by /itp-architect. Read by /itp-ship after every merge. The commands quoted
> here are the ones in the "Project commands" block of AGENTS.local.md.

## Environments

"Production" is wherever users get the product: a server or hosting platform, a package registry
(library, CLI), an internal distribution channel or an installer download (desktop), an app store
(mobile — publication itself is out of V1 scope).

| Environment | URL / access point / registry | Deployed from | Configuration and secrets |
|---|---|---|---|
| production | <...> | <target branch> | <where they live, how they reach the environment — never the values> |
| <staging / preview> | <...> | <...> | <...> |

## Deployment trigger
<automatic on merge into the target branch (platform, pipeline) | command: `<Deploy>` | manual procedure, step by step>

## Smoke test
<the few checks that prove production is alive and the core loop answers — a command (`<Smoke test>`) or a short list of requests, screens or commands with their expected result; for a published package or binary: install the released version and run its core loop. Runnable in minutes, right after a deployment.>

## Rollback
<the exact procedure that restores the previous version: command (`<Rollback>`) or steps. For a published package, a registry usually forbids overwriting a version: the rollback is then a deprecation plus a corrective release — say so.>

What a rollback does NOT undo:
<schema migrations, data written, emails sent, external calls — and what to do about each>

## Open points
<anything not decided yet — hosting target, domain, secrets management. /itp-ship stops on an open point that blocks a deployment.>
