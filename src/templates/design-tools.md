# Design tools — recommended by the method

The only place a design tool is named. `/ztp-design-system` and `/ztp-design` read it; edit this
file to add, remove or update a tool. An entry is a recommendation, never a requirement: any
tool that holds the design system qualifies, and with none the agent draws itself.

| Tool | Kind | Path | Runs under | What it brings | Link | Install |
|---|---|---|---|---|---|---|
| Impeccable | skill | internal | Claude Code, Codex, other harnesses | Design direction, critique and polish of an interface, with tokens and a design system as outputs | https://impeccable.style | `npx impeccable skills install` (project root) |
| frontend-design | plugin | internal | Claude Code | Distinctive, production-grade interfaces that avoid the generic look | https://github.com/anthropics/claude-plugins-official | `/plugin install frontend-design@claude-plugins-official` |
| Claude Design | platform | external | browser (claude.ai, paid plans, research preview) | Prototypes and design systems on a canvas, exported as HTML | https://claude.ai/design | none — send it the brief, bring the HTML export back |

- **Kind**: `skill` · `plugin` · `platform`.
- **Path**: `internal` (the tool draws in the session) · `external` (it receives the brief, the
  files come back into the repository). It decides `Design source` when that is still empty.
- **Runs under**: an entry that does not run under the current environment is not offered there.
- **Install**: copied from the tool's own documentation, never written from memory. Check it
  again when updating this file.
