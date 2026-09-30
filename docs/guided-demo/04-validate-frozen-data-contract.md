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
- Validate mode runs the transformed target through the exact same Schema, [Sensitive Data](../reference/sensitive-data-treatments.md), Source Drift, Data Quality, and Guardrail Coverage functions as Enforce.
- The modes differ only after every applicable Guardrail passes: Validate returns `published=False` and `validation_passed=True`, while Enforce reaches `pipeline_write()` and profiles the persisted target.
- A blocking Guardrail fails at the same stage with the same evidence and exception behaviour in either mode.

| Step 2 default | Step 4 selected target |
| --- | --- |
| Enforce mode | Validate mode |
| Existing checks stop on the first blocking failure, then publish | The same checks stop on the first blocking failure, then a successful dry run exits |
| No contract-backed rule before authoring | Applicable Schema, DQ, and Sensitive Data rules evaluate |
| Target write is allowed only after checks pass | `pipeline_write()` is never reached |

## Review the validation result

The target orchestration result identifies the table and exposes every standard Guardrail result. Review:

- `published=False`,
- `validation_passed=True`,
- the Schema, Sensitive Data, Source Drift, Data Quality, and Guardrail Coverage results,
- skipped, warning, and blocking outcomes plus caller-visible DQ failure details where present.

Because Validate uses the enforcement functions rather than a separate callback, existing Guardrail evidence persistence remains unchanged. Any Sensitive Data token support mapping remains caller-owned and is not persisted automatically. No target Profile is created because Validate does not publish a new target state.

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

**Next:** [Step 5. Link the Data Agreement and activate](05-activate-data-contract-and-promote.md)
