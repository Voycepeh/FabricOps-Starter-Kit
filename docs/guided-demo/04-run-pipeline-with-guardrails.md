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
- The Validate branch cannot call `pipeline_write()`, so the governed business target is not changed.
- Any other target left in Enforce mode continues through its normal checks and write path independently.

| Step 2 default | Step 4 selected target |
| --- | --- |
| Enforce mode | Validate mode |
| Normal checks and publication path | Exact frozen candidate evaluation |
| No contract-backed rule before authoring | Applicable Schema and DQ rules evaluate |
| Target write is allowed | Target write is structurally blocked |

## Review the validation result

The target validation result identifies the exact table, contract version, environment, and run. Review:

- `validation_passed`,
- passed, warning, and blocked counts,
- `not_applicable` outcomes for Guardrails that require enforcement pipeline context,
- caller-visible DQ failure details when present.

Freshness, Source Drift, and Sensitive Data can depend on enforcement observations or transformations. Validation keeps these outcomes visible as `not_applicable`; it does not falsely record them as PASS and does not persist raw rows, sensitive values, or token mappings.

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

The exact frozen target contract has successful validation evidence for the Development environment, while the business target remains unchanged. This evidence is one prerequisite for the later Governance activation decision; it does not activate the contract by itself.

**Next:** [Step 5. Link the Data Agreement and activate](05-create-data-contract.md)
