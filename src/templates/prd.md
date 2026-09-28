# PRD — <product name>

## Idea validation
### Problem
<what need, for whom, what they do today instead, and what it costs them>

### Target users
<profiles, usage context. Internal tool: the actual team. Product: the segment.>

### Hypothesis to verify
<the one unproven belief the project stands on, and the measurable signal that will confirm or refute it — and whether it was checked before building>

## Starting point
- Situation: <new project | existing codebase | replacement of an existing product or system>
- Product type: <web application | mobile application | desktop application | API or service | CLI | library | internal tool | system or embedded software | other>

## Reference
<existing product, legacy system or mockups used as a living spec — what it does in one line, and what we do NOT need from it. "None" if there is none.>

## Perimeter
### In scope (core loop)
| Feature | Complexity (1-5) | Why this score |
|---|---|---|
| <feature> | <n> | <...> |

Scale: 1 trivial CRUD · 2 form + persistence + list · 3 business logic / several states · 4 integrations, payments, roles · 5 real-time, migrations, external systems. A 5 is an out-of-scope candidate — keep it only if it IS the core value.

### Out of scope
<what we deliberately leave out — be exhaustive, this list stops scope creep>

### Differentiation
<optional — what we do differently or better than the reference or the current way of working>

## Constraints
<technical, time, budget, regulatory, dependencies>

## Success criteria
<the in-scope perimeter delivered and working in production + the hypothesis signal. Measurable.>
