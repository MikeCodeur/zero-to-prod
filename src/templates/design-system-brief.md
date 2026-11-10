# Design System Brief — <product>

> Send this brief to your design tool. Drop what it returns into docs/design/, then rerun
> /ztp-design-system. It is self-contained.

## Product and audience
<what the product does, for whom — from docs/prd.md>

## Mood
<the mood sought, in the user's words>

## References
<3 to 5 real products or sites, and what to take from each>

## Constraints
- Brand charter: <existing — attached / none>
- Component base: <e.g. shadcn — the system must be expressible in it>
- Themes and form factors: <light and dark, desktop and mobile…>

## Witness screen
<the story id and its screen, from the initial batch of docs/stories.md: purpose, real content,
actions, states — real copy, never lorem ipsum>

## Expected deliverables
**Stage 1 — three directions.** Three genuinely distinct directions on the witness screen, one
HTML file each: docs/design/directions/a.html, b.html, c.html. The user picks one.

**Stage 2 — the design system, in the chosen direction.**
1. Visible tokens — colors, typography, spacing, radius, light and dark → docs/design/design-system.html
2. Blocks, each in its states: empty, loading, error, filled → docs/design/blocks.html
3. The app — the layout and these 2–3 screens, linked and clickable: <screens> → docs/design/app.html

One file holding the three sections is accepted. These showcases are references: the foundations
are implemented in the code from them, so use the component base named above and let every
block map to a real component.

## Chosen direction
<filled when only stage 1 came back: a, b or c, and the user's remarks>
