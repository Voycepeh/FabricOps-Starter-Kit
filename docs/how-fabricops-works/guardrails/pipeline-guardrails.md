# Pipeline Guardrails

Pipeline guardrails are the runtime checks that `02_pipeline` uses to compare approved expectations with observed source and target data before publishing pipeline outputs.

Use [`guardrail orchestration`](../../api/reference/run_table_guardrails.md) when a pipeline needs to evaluate schema, freshness, profile behaviour, and active data quality rules as one governed workflow step. The function writes runtime evidence to the configured metadata lakehouse and returns results that notebook authors can inspect or display.

For the end-to-end notebook flow, see [`02 Pipeline Execution`](../notebook-templates/pipeline-execution.md).
