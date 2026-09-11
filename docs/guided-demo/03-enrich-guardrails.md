# Step 3: Author and Freeze the Data Contract

**Return to `01_governance`, select the governed `table_id`, and use one unified editor to author and freeze its Data Contract definition.**

## High-level flow

```text
METADATA_DATA_CATALOGUE + METADATA_DATA_PROFILED
                         ↓
                 governed table_id
                         ↓
             Data Contract version
             ├── Enrichment
             ├── Guardrails
             └── immutable schema / processing definition
                         ↓
                  Review → Freeze
```

!!! important "The Data Agreement is not linked in this step"

    Step 3 is table-centric. It binds descriptive Enrichment and executable Guardrails to one governed `table_id` and freezes that definition. Governance explicitly links the tested version to the required Data Agreement later in Step 5, together with the activation decision.

## Before you begin

Complete Step 2 so `02_pipeline` has registered the target in `METADATA_DATA_CATALOGUE` and written its latest `METADATA_DATA_PROFILED` snapshot to the metadata target configured by `00_env_config`.

## What to do

1. Open `01_governance` in the Governance workspace and run `00_env_config`.
2. Review the Catalogue and Profiled records produced by Engineering, then select the target's canonical `table_id`.
3. Run `widget_author_data_contract(table_id=TABLE_ID, spark_session=spark)`. The unified editor creates or reopens the agreement-free draft for that table and environment.
4. In **Enrichment**, author descriptive table and column context and classifications. Enrichment is descriptive metadata only; it does not enforce runtime behavior.
5. In **Guardrails**, author the enforced Schema, Freshness, Source Stability, Data Quality, and Sensitive Data requirements that apply to the table.
6. Open **Review** and confirm the table identity, schema, Enrichment, Guardrails, and processing definition.
7. Freeze the version. The saved definition is immutable; later revisions require a new version.

`widget_author_data_contract(...)` is the normal authoring UX. Enrichment, Guardrail, DQ-rule, and contract-registration widgets are not separate journeys in the canonical workflow.

??? info "Sensitive Data and DQ ownership"

    Sensitive Data treatment can tokenize, mask, bucket, or remove an explicitly governed column. Token support mappings remain caller-owned and outside FabricOps metadata; they are not persisted automatically.

    DQ is authored as a Guardrail. At runtime, `check_dq()` returns row-level failed values as a caller-owned DataFrame, while `METADATA_GUARDRAIL_RESULTS` stores the evaluation summary and continuation decision.

## Expected result

One frozen Data Contract version binds the reviewed Enrichment and Guardrails to the selected `table_id`. It has **not** been selected for Development, linked to a Data Agreement, activated for Production, or deployed.

**Previous:** [Step 2: Run the Development pipeline](02-run-pipeline.md)
**Next:** [Step 4: Select and validate the Data Contract](04-run-pipeline-with-guardrails.md)
