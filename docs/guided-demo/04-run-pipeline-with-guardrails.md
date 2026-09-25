# Step 4. Validate the frozen Data Contract

**Return to the same `02_pipeline`, choose Validate for the governed target, select the frozen version from Step 3, and evaluate the transformed target without publishing it.**

The selector defaults every table to **Enforce**, so the normal Guided Demo flow remains unchanged until you explicitly put a target into **Validate** mode.

## Select Validate for the target

In the Data Contract selector at the top of `02_pipeline`:

1. leave every source table in **Enforce** mode,
2. choose **Validate** only for the target whose frozen candidate you are reviewing,
3. select the exact frozen candidate version from Step 3.

The frozen-version picker appears only for a target in Validate mode. The selector keeps the candidate identity with that target, so there is no separate contract dictionary to edit in the notebook.

## Add the Day 2 Orders rows

Before this run, append `orders_incremental.csv` to `source.demo.orders` using the setup notebook from 0B.

The source now contains 132 rows instead of 120. This produces a changed transformed target for a meaningful candidate validation rather than merely repeating the original input.

## Rerun `02_pipeline`

Run the same visible **Read → Transform → Write-block** sequence.

- The Read blocks continue enforcing their own current contract state.
- Transform remains ordinary PySpark.
- The selected target Write block reads `CONTRACTS["tables"][target_table_id]`.
- Validate mode evaluates the transformed target against the exact frozen candidate and records aggregate evidence.
- Validate is a small pre-write exit gate: it evaluates the exact frozen candidate, records the evidence, and exits the notebook before the existing Enforce checks and `pipeline_write()` path.
- Enforce does not need a second branch. Its existing checks remain flat and stop naturally at the first blocking failure; only a successful Enforce run reaches `pipeline_write()`.

| Step 2 default | Step 4 selected target |
| --- | --- |
| Enforce mode | Validate mode |
| Existing checks stop on the first blocking failure, then publish | Exact frozen candidate evaluation, then notebook exit |
| No contract-backed rule before authoring | Applicable Schema, DQ, and Sensitive Data rules evaluate |
| Target write is allowed only after checks pass | `pipeline_write()` is never reached |

## Review the validation result

The target validation result identifies the exact table, contract version, environment, and run. Review:

- `validation_passed`,
- passed, warning, and blocked counts,
- `not_applicable` outcomes for Guardrails that require enforcement pipeline context,
- caller-visible DQ failure details when present.

Sensitive Data is evaluated against the exact frozen candidate using the same treatment core as Enforce; any token support mapping remains caller-owned and is not persisted automatically. Freshness and Source Drift require enforcement observation context, so validation keeps those outcomes visible as `not_applicable` rather than falsely recording them as PASS.

Only aggregate evidence is appended to `METADATA_GUARDRAIL_RESULTS` with `execution_type = validate`.

## Iterate if needed

If validation shows that the Governance definition is wrong or incomplete:

1. return to `01_governance`,
2. refine the draft definition,
3. freeze a new immutable version,
4. select that new target candidate in Validate mode,
5. rerun `02_pipeline`.

Do not edit a frozen version in place.

## Expected result

The exact frozen target contract has successful validation evidence for the Development environment, and the notebook exits at the validation gate before the business target can be written. This evidence is one prerequisite for the later Governance activation decision; it does not activate the contract by itself.

**Next:** [Step 5. Link the Data Agreement and activate](05-create-data-contract.md)
