---
name: codebase-analysis
description: Analyzes existing code you didn't write — structure, conventions, patterns. Use during the Architecture and Research phases of the zero-to-prod pipeline, and to map an existing codebase or a freshly built foundation.
---
# Codebase analysis

Goal: understand inherited code before touching it, and extract the conventions to follow.

Sequence — breadth first, then one deep cut:
1. Map the structure: folders, entry points, layers, build and config files.
2. Follow ONE representative feature end to end (entry point → handler → data access → output): that walk exposes the real conventions faster than any doc.
3. Spot the recurring patterns: naming, organization, error handling, data access, tests.
4. Identify the implicit conventions: what the code always does the same way is law, even if written nowhere.
5. Locate the anchor points: where a new feature plugs in.
6. Report in an actionable form — conventions as rules ("services live in src/services, one file per domain"), not observations ("there are some services"). This is what feeds AGENTS.md and the architecture doc.

Rules:
- Verify, don't assume: name a file, a function or a signature only after opening it.
- Don't propose rewrites. An existing codebase is imposed: conform to it.
