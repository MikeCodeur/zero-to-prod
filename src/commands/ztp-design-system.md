---
description: Set up the global design system and implement its foundations in the product — from an existing input, or from nothing through the design tool you choose. The tool draws the proposals; ZTP orchestrates, checks and implements.
argument-hint: (optional) the input — a file, a folder, a URL or a description
allowed-tools:
  - Read
  - Glob
  - Grep
  - Write
  - Edit
  - Bash
  - Skill
  - AskUserQuestion
---
# ztp-design-system — Global design system

ZTP orchestrates here: it asks the questions, fixes the deliverables, checks them, then
implements the design system in the code. The visual proposals come from the tool the user
chooses — a skill, a plugin, an external platform, or the agent itself when the user asks. This
command carries no design logic of its own.

Apply the `design-doctrine` skill.

## Execution contract (non-negotiable)
- **The user always chooses the direction.** Never pick one in silence, never fall back to a
  default system.
- **A missing piece is asked of the tool, never invented.**
- **Nothing is installed without the user's go** — no design tool, no package.
- No tool is named here: the recommended ones live in @templates/design-tools.md.
- **Foundations only, no story.** Tokens, the CSS framework's configuration, the component
  library's theme and base components, the layout and empty page templates. No business content,
  no feature screen: those are built story by story, from /ztp-design's mockup.
- **A validation point at each step marked ✋.** Nothing moves to the next step without it.

## The showcases — the contract
The same on every path:
1. **Visible tokens** — colors, typography, spacing, radius, in the light and dark themes.
2. **Blocks, each with its states** — empty, loading, error, filled.
3. **The app** — the layout and 2–3 screens from the initial batch of docs/stories.md, linked
   and clickable.

Recommended: three files — docs/design/design-system.html, docs/design/blocks.html,
docs/design/app.html. A single file is accepted when it holds all three sections. Checking means
opening them the way `UI check` says and seeing each section — not finding file names.

## Step 0 — Which case
Read, in order: $ARGUMENTS; docs/design/; docs/design-system.md; the codebase (apply the
codebase-analysis skill: theme, component library, the stylesheet that defines the tokens).

- docs/design/ holds the contract → **Case A**, with it as the input.
- docs/design/directions/ holds directions but none is chosen → **B3**, the choice.
- docs/design/design-system-brief.md exists and nothing came back → say the brief is pending and
  stop.
- An input exists — an external design system, an HTML export, mockups, tokens, a written
  description, a system already in the code → **Case A**.
- Nothing: no docs/design-system.md, no input, and the code holds only the generator's default
  theme → **Case B**. Unsure whether a theme is a default or a choice → ask, don't guess.
- docs/design-system.md exists and nothing new is supplied → say so, and ask whether to revise it
  from a new input or keep it.

## Case A — an input exists
1. Check the input against the contract: which of the three sections it covers.
2. A section is missing → the tool produces it from the input; it extends the input's direction
   and never picks a new one. The tool is `Design skill` / `Design tool` when set; otherwise ask,
   as in B1. External tool → write only the missing sections into
   docs/design/design-system-brief.md and stop, as in B3.
3. Complete → **Implementation**.

## Case B — nothing is defined

### B1 — Choose the tool
1. Detect the design skills and plugins this environment already has: the skills the session
   exposes, .claude/skills/, ~/.claude/skills/, .codex/skills/, ~/.agents/skills/, installed
   plugins. Read @templates/design-tools.md and mark which of its entries are present and run
   under this environment.
2. Ask (AskUserQuestion): "How do you want to create your design system?" — the detected tools,
   the external platforms from design-tools.md, "another skill, plugin or tool you use", "I
   generate the proposals myself". Ask in the same breath whether they have skills of their own
   that could help — design, brand, charter — and to load or name them.
3. Nothing detected, nothing of their own → recommend two or three entries from design-tools.md,
   each with its one line, its link and its install command, and invite them to install one or
   find another. Install nothing without their go. A skill installed mid-session may need a
   restart before it shows up: say so.
4. "I generate them myself" → warn once: "I can, but a design skill will give a less generic
   result." Continue on their confirmation.
5. `Design source` in AGENTS.local.md absent or `—` → set it from this choice: a skill, a plugin
   or the agent → `internal` and `Design skill` (its name, or `—`); an external platform →
   `external` and `Design tool`. Say so in the final recap. Already set → leave it; if the choice
   differs, say that stories will follow the setting, not this choice.

### B2 — Frame
Short questions, one AskUserQuestion: the product and its audience (pre-filled from
docs/prd.md), the mood sought, 3 to 5 real references, an existing brand charter or not, the
component base (e.g. shadcn — pre-filled from the codebase).

**Witness screen:** taken from the initial batch of docs/stories.md — the screen of the UI story
that carries the core loop, never a generic screen. No docs/stories.md → stop: /ztp-stories first.

### B3 — Three directions ✋
- **Internal** (skill, plugin, or the agent): the tool produces three distinct directions on the
  witness screen, in HTML: docs/design/directions/a.html, b.html, c.html. Render each the way
  `UI check` says; three variants of one direction are not three directions.
- **External**: write docs/design/design-system-brief.md from @templates/design-system-brief.md,
  then stop: "Send this brief to your tool, drop the files into docs/design/, then rerun
  /ztp-design-system." Only directions came back → ask for the choice, record it in the brief
  under "Chosen direction", and stop again for stage 2.
- **The user picks one** (AskUserQuestion: a, b, c, or "none — redo, with this feedback"). A redo
  carries their feedback and never a direction of the agent's own. Validation point.

### B4 — The showcases
Internal: the tool produces the contract in the chosen direction. External: the brief already
asks for it. Check it against the contract; a missing section goes back to the tool (Case A, 2).

## Implementation in the product (both cases)

Every step starts from what the code already has: present and conforming → say so and move on;
present but partial → complete it; absent → create it. Never redo what exists, never replace a
theme already in the code without the user's go. Each step is rendered the way `UI check` says
before its validation point.

### 1 — The tokens ✋
CSS variables for colors, typography, spacing and radius, the light and dark themes, the fonts
loaded — in the stylesheet the architecture names (e.g. app/globals.css). Values taken from the
chosen showcase, never retouched by eye. Validation point.

### 2 — The CSS framework
Its configuration wired to those tokens (e.g. Tailwind): the utilities resolve to the variables,
never to hard-coded values.

### 3 — The component library ✋
Its theme wired to the tokens, and the base components the project needs installed with the
library's own tool (e.g. button, input, table, dialog with shadcn). "Needs" comes from
docs/stories.md and the showcase's blocks, not from the library's catalogue. Validation point.

### 4 — The layout and the page templates ✋
The app layout (top bar, menu, main area) and empty page templates — list, detail, form — built
from the installed components. No business content: placeholders name the slot ("list of
items"), they never invent the data. Validation point.

### 5 — docs/design-system.md
Fill @templates/design-system.md: direction, tokens, component inventory (what step 3 installed,
plus what the code already had), the layout and page templates, UI patterns, themes and form
factors, Do / Don't.

### 6 — Measure the contrasts, once, here
**This is the only phase that measures anything.** On the real render — the product running with
its stylesheet, not the showcase — every text/surface pair the system can produce, in every theme
it declares, is **measured** rather than judged by eye: a pair at 4.2:1 and one at 4.8:1 look
identical, and only one passes. A failing pair is fixed in the tokens — the stylesheet and
docs/design-system.md — never as a per-story exception, and the tool regenerates the showcases.

Done here on a system that does not move between stories, it holds for every screen that
system can build — which is why no later phase repeats it. Beware a browser forcing dark mode:
it repaints light frames dark whatever the page does.

### 7 — Verify, then commit
Run `Typecheck`, `Test` and `Build` from AGENTS.local.md: the foundations leave the project
green, as /ztp-architect left it. A command at `—` is reported, never guessed. Then commit on the
default branch: `chore: design system foundations` (stylesheet, framework configuration,
components, layout, templates), then `docs: design system` (docs/design-system.md, docs/design/).

The HTML files are reference showcases, not code to copy. When docs/design-system.md changes,
the tool regenerates them; they never become the source.

If a zone rule of the UI layer (.claude/rules/) anchors on a file these foundations replaced or
made obsolete, say so in the recap; it is the project's rule to update, not this command's.

End with: "Design system implemented: tokens, components, layout and page templates (details in
docs/design-system.md, showcases in docs/design/). Design source: <value>. Each story's screen
starts from it via /ztp-design <story>."
