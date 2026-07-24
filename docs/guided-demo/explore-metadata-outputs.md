# Optional: Explore metadata outputs

Use generated reference pages, `99_explore`, or dashboard-internal pages to inspect what the required Step 0 through Step 6 workflow wrote. `99_explore` is optional and read-only for the governed workflow: use it for discovery, scratch profiling, troubleshooting, or support investigation without changing agreement, pipeline, or governance state.

## What to do

1. Start with the generated [List of Metadata Tables](../reference/metadata.md).
2. Open individual metadata table pages to inspect implemented schemas and related functions.
3. Use `99_explore` when you need notebook-side inspection of a table, agreement context, configured target, or helper behavior.
4. Keep any scratch analysis separate from governed metadata unless a later guided step explicitly writes reviewed evidence.

## Expected evidence

Users can trace agreement context, catalogue profiles, guardrail rules, runtime results, lineage, and pipeline summaries without relying on hidden notebook state. `99_explore` creates no required production metadata; its normal outputs are ad hoc notebook displays.

Return to the required workflow through the [Guided Demo overview](../guided-demo.md).

See also: [List of Functions](../reference/index.md).
