# Improvement reports

A run of the method that looks long, expensive or odd gets a report here. One file per run,
numbered, never rewritten — it is a trace, not living documentation. The improvements that are
retained then go into `src/`; the report stays to say where they came from and what they were
worth.

## Asking for a report

> "Analyze the <project> run and write an improvement report in `docs/improvements/`."

The agent reads the transcripts, measures, then writes. **It proposes nothing it has not
measured**: an axis without a number next to it is an opinion, and an opinion does not deserve
a file.

## Format

A report carries, in this order:

| Section | Content |
| --- | --- |
| Header | project, dates, duration, perimeter delivered, track used |
| Volume | calls, tokens per item, API-equivalent cost, ratios |
| Question | the question asked, in one sentence |
| Analysis | what the data says — tables, not prose |
| Axes | five at most, ranked by **measured** impact, each with its estimated gain |
| Measurement method | how to reproduce the numbers |

## Where the data is

Claude Code transcripts, in JSONL:

```
~/.claude/projects/<slugified-project-path>/**/*.jsonl
```

Every line carrying `message.usage` is an API call: `input_tokens`, `output_tokens`,
`cache_creation_input_tokens`, `cache_read_input_tokens`.

**Two traps:**

1. **The same call appears on several lines** — separate content blocks, forks, resumed
   sessions. Deduplicate on `message.id`, or the total is nearly doubled.
2. **The lines of one `message.id` do not all carry the same values.** They are streaming
   snapshots: `output_tokens` grows from one line to the next, input and cache do not move.
   Keep the **maximum occurrence**, not the first — or output is undercounted by half.

## Reference pricing ($/MTok)

Use the current published pricing of the model the run used: input, output, cache write,
cache read. The cost given in a report is an **API equivalent**. On a subscription nothing is
billed that way — it is a unit to compare two runs, not an invoice.

## Reports

| # | Project | Date | Volume | Verdict |
| --- | --- | --- | --- | --- |
