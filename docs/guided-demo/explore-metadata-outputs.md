# Explore Metadata Outputs

Use generated reference pages, `99_explore`, or dashboard-internal pages to inspect what the notebooks wrote. `99_explore` is optional and read-only for the governed workflow: use it for discovery, scratch profiling, troubleshooting, or support investigation without changing agreement, pipeline, or governance state.

## What to do

1. Start with the generated [List of Metadata Tables](../reference/metadata.md).
2. Open individual metadata table pages to inspect implemented schemas and related functions.
3. Use `99_explore` when you need notebook-side inspection of a table, agreement context, configured target, or helper behavior.
4. Keep any scratch analysis separate from governed metadata unless a later guided step explicitly writes reviewed evidence.

## Expected evidence

Users can trace steward and agreement context, catalogue identities, profile evidence, lineage participation, enrichment, guardrail intent, and runtime guardrail results without relying on hidden notebook state. `99_explore` creates no required production metadata; its normal outputs are ad hoc notebook displays.

See also: [List of Functions](../reference/index.md).
