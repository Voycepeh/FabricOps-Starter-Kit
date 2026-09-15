# Step 4. Select and validate the Data Contract

**Return to the same `02_pipeline`, select the frozen Data Contract version from Step 3, and rerun the real pipeline.**

Do not switch to a special Guardrail notebook. The point of this step is to show that Governance changes the behaviour of the same Engineering flow.

## Select the frozen version

In Development, use the Data Contract selection section in `02_pipeline` to select the immutable version for the governed `table_id`.

The contract context is now different from Step 2. The check functions that previously returned `skipped` can resolve the authored Guardrails and execute them against the real data flow.

## Add the Day 2 Orders rows

Before this rerun, append `orders_incremental.csv` to `source.demo.orders` using the setup notebook from 0B.

The source now contains 132 rows instead of 120.

This gives the validation run an observable data change rather than simply repeating the same input.

## Rerun `02_pipeline`

Run the same full Read → Transform → Write path.

Observe the contrast with Step 2:

| Step 2 | Step 4 |
| --- | --- |
| No selected Data Contract | Frozen Data Contract selected |
| Contract-backed checks safely skip | Authored Guardrails execute |
| Development processing proposal drives the write | Selected contract validates and governs the processing definition |
| 120-row Orders source | 132-row Orders source after Day 2 arrival |

The source is still read in full. FabricOps has not turned the pipeline into a source-side incremental reader.

## Watch each Guardrail in context

The notebook should make it easy to follow where each expectation belongs:

- Freshness, Schema, and source DQ around each Read block,
- target Schema and Sensitive Data before publication,
- Source Drift for each exact source-to-target relationship,
- target DQ before publication,
- Guardrail coverage before the target write,
- `pipeline_write()` only after the target is ready to publish.

Warn outcomes can continue. Blocking outcomes should stop the governed publication according to the configured rule behaviour.

## See the load strategy on changing data

Because the Orders source changed between runs, inspect the persisted target after Step 4.

An overwrite target should now represent the newly recomputed complete result. A target governed with append, SCD1, or SCD2 should reflect the semantics of that strategy and its configured parameters.

This is why the walkthrough separates full source reads from target load strategy. They solve different problems.

## Iterate if needed

If validation shows that the Governance definition is wrong or incomplete:

1. return to `01_governance`,
2. refine the draft definition,
3. freeze a new immutable version,
4. select that new version in Development,
5. rerun `02_pipeline`.

Do not edit a frozen version in place.

## Expected result

You have now seen the same Engineering pipeline operate first without a Data Contract and then with a frozen Data Contract enforcing the Governance definition against changed real data.

**Next:** [Step 5. Link the Data Agreement and activate](05-create-data-contract.md)
