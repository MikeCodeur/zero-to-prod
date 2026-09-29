---
description: Frame the product — idea validation, starting point, perimeter, the WHAT and the WHY
argument-hint: <product idea, or the product to replace>
allowed-tools:
  - Read
  - Write
  - Bash
  - AskUserQuestion
---
You are framing an zero-to-prod project. Subject: $ARGUMENTS

Use this template as the output structure:
@templates/prd.md

## Step 0 — The project's settings (fail-closed)
`AGENTS.local.md` must exist. Missing → STOP: "This project has no settings yet. Run /ztp-setup, then rerun /ztp-prd." Nothing below runs without it.

Present → read `Merge mode`, `Target branch`, `Plan validation` and `Design source`, and repeat them in the final recap: whoever writes the PRD should see what they are committing to before writing it.

The PRD fixes the WHAT and the WHY, never the HOW. Everything downstream — stories, their review, every plan — is measured against its perimeter.

Proceed as follows, asking me one question at a time:
1. **Idea validation** — the section that stands in for a reference when there is none:
   - Problem: what need, for whom, what do they do today instead, and what does that cost them?
   - Users: who uses it, in what context. An internal tool names the actual team; a product names its segment.
   - Hypothesis to verify: the one belief the project stands on that is not yet proven, and how it will be checked (a measurable signal, not an intention). Say plainly if it has not been verified before building.
2. **Starting point** — new project, existing codebase, or replacement of an existing product or system. And the **product type**: web application, mobile application, desktop application, API or service, CLI, library, internal tool, system or embedded software, other. Both decide what the architecture phase does.
3. **Reference (optional)** — an existing product, a legacy system or mockups that act as a living spec. If there is one: what it does in one line, and what we explicitly do not need from it. If there is none, write "None" — the idea validation above carries the frame alone.
4. **Perimeter** — never the whole idea at once. Which core loop delivers the real value — the smallest set of features that makes the product useful? Score each in-scope feature for complexity 1-5 (scale in the template). A 4-5 must earn its place — the default home of heavy features is out of scope.
5. **Out of scope** — what stays explicitly out. Be exhaustive: this list is what stops scope creep.
6. **Differentiation (optional)** — what this does differently or better than the reference or the current way of working.
7. **Constraints** — technical, time, budget, regulatory, dependencies.
8. **Success criteria** — the perimeter delivered and working in production, plus the hypothesis signal. Measurable.
9. Fill each section of the template with my answers. Fill nothing you haven't validated with me.
10. Write the result to `docs/prd.md` and commit it on the default branch (docs: prd).

End with: "PRD ready in docs/prd.md. Next step: /ztp-stories"
