# Run Pipeline

Run `example_pipeline_demo` to seed deterministic demo source tables, then run `02_pipeline` for governed source-to-target execution. The pipeline notebook is where engineering users select an agreement, keep source and target settings visible, read data, apply transformations, run guardrails, write outputs, and record evidence for governance review.

## Seed demo source data with `example_pipeline_demo`

Use `example_pipeline_demo` only for demos, training, and smoke testing. It creates repeatable `demo_` source tables in the configured source lakehouse and can prepare demo-scoped guardrail intent for the guided run. It is not a production delivery notebook.

Keep the default demo schema and table prefix for the first run so the later `02_pipeline` cells match the generated source tables.

## Run `02_pipeline`

1. Open `02_pipeline` after `00_env_config`, `01_agreement`, and the demo seed notebook have run.
2. Start the pipeline context and select the agreement created in `01_agreement`.
3. Review the source and target table settings. These are the main values users normally edit for a real workflow: source table names, target table names, read settings, write modes, run labels, operational notes, and transformation cells.
4. Read source data from configured Fabric targets rather than relying on an attached default Lakehouse.
5. Apply the visible transformation cells so the output remains explainable to reviewers.
6. Run profile and enforcement guardrails for source and target tables.
7. Write governed outputs only after blocking checks allow continuation.
8. Write lineage and pipeline run summary evidence.

## Guardrails and continuation decisions

Guardrails turn agreement and rule expectations into runtime pass, warning, fail, or skipped results. `02_pipeline` evaluates schema, freshness, profile behavior, and active DQ rules before unsafe outputs are published.

| Run point | What happens | Why it matters |
| --------- | ------------ | -------------- |
| After source read | Validate source schema, freshness, profile behavior, and active source DQ rules. | Catch upstream structure, recency, behavior, and quality issues before transformation. |
| Transformation | Apply deterministic business logic in visible cells. | Keep outputs repeatable and explainable. |
| Before target write | Validate target schema, freshness, profile behavior, and active target DQ rules. | Avoid publishing stale, unexpected, or DQ-failing outputs. |
| After successful checks | Write outputs, lineage, profiles, guardrail results, and run summary. | Give governance and support teams evidence of what actually ran. |

Profile-mode checks are non-blocking visibility by default. Enforcement checks stop publication when error-severity checks fail. A Warning-severity failure records an observability issue without blocking continuation. An Error-severity failure blocks before the next critical step so unsafe publication does not continue.

## Expected evidence

The workflow writes governed output tables plus metadata rows for catalogue profiles, guardrail results, lineage, and run summaries. `03_governance` depends on these observed profiles and proposed guardrails to review enrichment and guardrail intent. Later `02_pipeline` runs use active approved rules from governance metadata.

| Metadata area | Why it matters |
| ------------- | -------------- |
| `METADATA_DATA_CATALOGUE` | Stores observed table and column profiles for comparison, review, and troubleshooting. |
| `METADATA_GUARDRAIL_RULES` | Stores schema, freshness, profile-behavior, and DQ rule intent that runtime enforcement loads. |
| `METADATA_GUARDRAIL_RESULTS` | Stores pass/warn/fail/skipped outcomes, severity, continuation decisions, and result payloads. |
| `METADATA_PIPELINE_RUNS` | Summarizes source/target counts, guardrail rollups, lineage/catalogue write status, and run details. |
| `METADATA_DATA_LINEAGE_TABLE` | Records source-to-target relationships for handover, dashboarding, and review context. |

Next, continue to [Review Guardrails](review-guardrails.md).

See also: [Templates](../notebook-templates-implementation-guide/index.md) and [List of DQ Rules](../reference/dq-rules/index.md).
