# Optional: Explore metadata outputs

`99_explore` is optional and outside the required Step 0 through Step 6 production workflow. Use it in Engineering Development for one-off exploration, analysis, troubleshooting, and transformation development. It supports exploring datasets, testing assumptions, investigating data-quality issues, developing transformation logic, producing one-off analytical outputs, and deciding whether work should become a repeatable `02_pipeline`. It must not change governed agreement, contract, enrichment, or guardrail state.

## What to do

1. Start with the generated [List of Metadata Tables](../reference/metadata.md).
2. Open individual metadata table pages to inspect implemented schemas and related functions.
3. Use `99_explore` when you need notebook-side exploration of datasets, agreement context, configured targets, helper behavior, data-quality issues, or transformation logic.
4. Keep any scratch analysis separate from governed metadata unless a later guided step explicitly writes reviewed evidence.

## Expected evidence

Users can trace agreement context, catalogue profiles, guardrail rules, runtime results, lineage, and pipeline summaries without relying on hidden notebook state. `99_explore` creates no required production workflow metadata; its normal outputs are ad hoc analysis and notebook displays.

Return to the required workflow through the [Guided Demo overview](../guided-demo.md).

See also: [List of Functions](../reference/index.md).
