# Run Pipeline

Run `example_pipeline_demo` to seed deterministic demo source tables, then run `02_pipeline` for governed source-to-target execution.

## What to do

1. Generate the `demo_` source tables in the configured source lakehouse.
2. Open `02_pipeline` and select the agreement context.
3. Read source data, apply the visible transform cells, run guardrails, and write outputs.
4. Write lineage and pipeline run summary evidence.

## Expected evidence

The workflow writes profile evidence, guardrail outcomes, lineage rows, pipeline summary rows, and governed output tables.

See also: [List of Templates](../notebook-templates-implementation-guide/index.md) and [List of DQ Rules](../reference/dq-rules/index.md).
