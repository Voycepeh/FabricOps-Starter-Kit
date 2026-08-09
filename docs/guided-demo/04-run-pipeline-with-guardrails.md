# Step 4: Rerun the Development pipeline with guardrails

Rerun `02_pipeline` in the Engineering Development workspace after Step 3 has defined guardrails. This workflow starts with the same read, profile, transform, profile, and write pattern described in [Step 2: Run the first Development pipeline](02-run-pipeline.md). It then adds active guardrail retrieval, evaluation, severity handling, and continuation decisions before critical publication steps.

Use this step to wire in the guardrail rules defined in Step 3, run the pipeline, and verify that the configured guardrails warn users or fail the pipeline as intended.

## Prerequisite pipeline evidence

The guarded pipeline still records the same standard evidence described in [Step 2: Run the first Development pipeline](02-run-pipeline.md):

- `METADATA_DATA_CATALOGUE` for physical table and column identity snapshots;
- `METADATA_DATA_PROFILED` for statistical, frequency, and schema evidence per column; and
- `METADATA_DATA_LINEAGE` for runtime source and target participation evidence.

Guardrails add enforcement evidence. They do not replace the normal profiling, catalogue, schema, frequency, or lineage records.

## Guardrail workflow

```text
read
→ profile source
→ load active source guardrails
→ evaluate source guardrails
→ transform
→ profile target
→ load active target guardrails
→ evaluate target guardrails
→ make continuation decision
→ write target when allowed
→ register guardrail results and lineage evidence
```

1. Read the source DataFrame.
2. Profile and register the source.
3. Load the active source guardrails defined by Governance.
4. Evaluate source guardrails.
5. Stop or continue based on severity and continuation results.
6. Apply transformation logic.
7. Profile and register the target.
8. Load active target guardrails.
9. Evaluate target guardrails before publication.
10. Write the target only when blocking checks permit continuation.
11. Persist guardrail results and runtime evidence.

## Where rules come from

Runtime does not invent rules. It retrieves the active guardrail definitions created through the Governance workflow in `METADATA_GUARDRAIL`.

Those records describe rule identity, rule type, table or column scope, parameters, severity, activation state, and audit context. `02_pipeline` uses active rules as the executable expectations for the current source or target evaluation point.

## Profile mode and enforcement mode

| Mode | User outcome |
| ---- | ------------ |
| Profile mode | Records visibility and observations without blocking publication. |
| Enforcement mode | Evaluates continuation and can block publication when required. |

Typical severity behavior:

- **Warning** records an issue but normally allows continuation.
- **Error** blocks the next critical step when the guardrail fails.

The runtime continuation decision is recorded with the result, including whether the notebook can continue past the guarded point.

## Source and target enforcement points

| Run point | What happens | Why it matters |
| --------- | ------------ | -------------- |
| After source read and profiling | Evaluate active source schema, freshness, profile-behavior, and DQ expectations. | Catch upstream issues before transformation. |
| Transformation | Apply deterministic business logic in visible notebook cells. | Keep the output explainable and repeatable. |
| Before target write | Evaluate active target expectations. | Prevent unsafe or non-compliant publication. |
| After checks pass | Write outputs and persist metadata evidence. | Preserve a reviewable execution trail. |

## Guardrail results

`METADATA_GUARDRAIL_RESULTS` records runtime outcomes for evaluated guardrails. It captures items such as:

- rule identity, including `guardrail_result_id`, `guardrail_rule_id`, `result_id`, and `rule_key`;
- execution scope, including `metadata_table_key`, `environment_name`, `dataset_name`, `table_name`, and `column_name`;
- guardrail classification, including `guardrail_type` and `rule_type`;
- outcome fields, including `status`, `can_continue`, `severity`, and `reason`;
- comparison and diagnostic payloads, including `expected_value_json`, `actual_value_json`, and `result_payload_json`; and
- standard runtime audit information.

Statuses may represent pass, warning, fail, or skipped outcomes depending on the evaluated rule and severity. The important operational field is the continuation result: blocking checks can deny continuation before an unsafe target publication step.

## Relationship to normal pipeline evidence

A guarded run produces the normal pipeline evidence plus guardrail results:

| Evidence area | What it contributes |
| ------------- | ------------------- |
| `METADATA_DATA_CATALOGUE` | Physical table and column identity snapshots. |
| `METADATA_DATA_PROFILED` | Statistical, frequency, and schema evidence per column. |
| `METADATA_DATA_LINEAGE` | Runtime source and target participation evidence. |
| `METADATA_GUARDRAIL_RESULTS` | Evaluation outcomes, severity, continuation decisions, and result payloads. |

The additional behavior is that continuation may be denied before unsafe publication.

Previous: [Step 3: Enrich the Data Catalogue and define guardrails](03-enrich-guardrails.md).

Next, continue to [Step 5: Create the Data Contract and record steward sign-off](05-create-data-contract.md).
