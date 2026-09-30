# Step 4. Validate the frozen Data Contract

**Use the same `02_pipeline` to prove the complete governed path: first every Guardrail passes, then controlled source and target mutations exercise Freshness, Schema, Source Drift, Sensitive Data, every DQ behavior, and Guardrail Coverage without publishing a validation target.**

The selector defaults every table to **Enforce**. For this step, put only `curated_orders` into **Validate** mode and select the exact frozen version from Step 3.

## 1. Select Validate for `curated_orders`

In the Data Contract selector at the top of `02_pipeline`:

1. select the exact frozen Step 3 contract for all three sources,
2. select the exact frozen Step 3 contract for both targets,
3. choose **Validate** for `curated_orders` while running its validation exercise.

All participating tables need selected contracts because Guardrail Coverage checks the complete source → target relationship once any contract is selected.

The frozen-version picker appears only for a target in Validate mode. There is no separate contract dictionary to edit.

## 2. Prove the happy path first

Run the normal visible **Read → Transform → Write** sequence without changing `transformed_df`.

The `curated_orders` Write block evaluates the frozen contract but does not publish the target. The notebook exits after the successful validation gate, so the second Write block is intentionally not reached on this run.

Confirm:

- `published=False`
- `validation_passed=True`
- Freshness, Schema, Source Drift, Sensitive Data, Data Quality, and Guardrail Coverage all report successful evidence where applicable
- the configured `customer_id` Sensitive Data treatment is applied in the prepared DataFrame
- every DQ check is passed
- `pipeline_write()` was not reached

This proves the contract describes the canonical target before we deliberately break it.

## 3. Exercise the source-side Guardrails

Source Guardrails are evaluated from the real source read and Source Observation metadata, so changing only `transformed_df` cannot test them. Use a controlled mutation of the Development `orders` table, then restore it from the canonical fixture.

Before changing anything, the happy-path run above establishes the accepted source → target baseline used by Source Drift.

Create a temporary dirty copy of the Development Orders source with two deliberate changes:

- set every `modified_datetime` to an old enough value to exceed the Freshness maximum age,
- add an unexpected column such as `unexpected_demo_column` so Schema detects drift from the frozen source schema.

Overwrite only the **Development Bronze Orders table** with that temporary DataFrame, then rerun the Orders Read block and the `curated_orders` Write validation.

Expected source-side evidence:

| Guardrail | Deliberate condition | Expected |
| --- | --- | --- |
| Freshness | latest `modified_datetime` exceeds the governed maximum age | Warn/fail evidence |
| Schema | `unexpected_demo_column` is not in the frozen schema | Warn/fail evidence |
| Source Drift | current Orders observation differs from the last successfully consumed baseline | changed/drift evidence |

Keep these rules on Warn for this run so the pipeline can reach the later target checks.

!!! warning "Restore the canonical source immediately after the source test"
    Rerun Step 00C's canonical Orders load before continuing. Do not carry the dirty Bronze source into later demo steps. The mutation is intentionally confined to Development and the canonical CSV remains unchanged.

After restoration, rerun the Orders Read block so the notebook is again holding the canonical source DataFrame.

## 4. Build a deterministic dirty target

Rerun the notebook through the normal Transform cell. Immediately after that cell, add this temporary validation cell:

```python
dirty_transformed_df = (
    transformed_df
    # completeness: customer_id must be present
    .withColumn(
        "customer_id",
        F.when(F.col("order_id") == "O0001", F.lit(None))
        .otherwise(F.col("customer_id")),
    )
    # uniqueness: duplicate O0001
    .withColumn(
        "order_id",
        F.when(F.col("order_id") == "O0002", F.lit("O0001"))
        .otherwise(F.col("order_id")),
    )
    # whitelist: order_status must use the governed status list
    .withColumn(
        "order_status",
        F.when(F.col("order_id") == "O0003", F.lit("INVALID"))
        .when(F.col("order_id") == "O0008", F.lit("DELIVERED"))
        .when(F.col("order_id") == "O0009", F.lit("SHIPPED"))
        .otherwise(F.col("order_status")),
    )
    # blacklist + conditional completeness
    .withColumn(
        "shipping_country",
        F.when(F.col("order_id") == "O0004", F.lit("UNKNOWN"))
        .when(F.col("order_id") == "O0008", F.lit(None))
        .when(F.col("order_id") == "O0009", F.lit("SG"))
        .otherwise(F.col("shipping_country")),
    )
    # range: quantity must remain between 1 and 4
    .withColumn(
        "quantity",
        F.when(F.col("order_id") == "O0005", F.lit(0))
        .otherwise(F.col("quantity")),
    )
    # pattern: order_id must be O + exactly four digits
    .withColumn(
        "order_id",
        F.when(F.col("order_id") == "O0006", F.lit("BAD-006"))
        .otherwise(F.col("order_id")),
    )
    # column relationship: modified_datetime >= order_datetime
    .withColumn(
        "modified_datetime",
        F.when(
            F.col("order_id") == "O0007",
            F.to_timestamp("order_datetime") - F.expr("INTERVAL 1 HOUR"),
        ).otherwise(F.col("modified_datetime")),
    )
    # custom expression: net amount <= quantity * unit price
    .withColumn(
        "order_net_amount",
        F.when(
            F.col("order_id") == "O0010",
            F.col("quantity") * F.col("unit_price") + F.lit(999.0),
        ).otherwise(F.col("order_net_amount")),
    )
)
```

This DataFrame exists only in the notebook session. It does not overwrite Bronze, Silver, or the canonical demo files.

For this validation run, change only the first argument of the `curated_orders` Write block:

```python
write_result = orchestrate_write(
    dirty_transformed_df,
    # keep the rest of the existing Write block unchanged
)
```

Do not change the reusable `02_pipeline` template itself.

## 5. Run the dirty target with every DQ rule on Warn

Run the `curated_orders` Write block again.

Because Step 3 left **Block on failure** off, the DQ guardrail can evaluate the complete ruleset and report warnings instead of terminating on the first deliberate violation. Validate mode still prevents publication.

Use the returned DQ result to compare actual behavior with this matrix:

| DQ behavior | Dirty row | Deliberate violation | Expected runtime rule |
| --- | --- | --- | --- |
| Completeness | original `O0001` | `customer_id = null` | `completeness` |
| Uniqueness | original `O0002` | changed to duplicate `order_id = O0001` | `uniqueness` |
| Whitelist | `O0003` | `order_status = INVALID` | `value_set / allow` |
| Blacklist | `O0004` | `shipping_country = UNKNOWN` | `value_set / block` |
| Range | `O0005` | `quantity = 0` | `range` |
| Pattern | original `O0006` | `order_id = BAD-006` | `pattern` |
| Column Relationship | `O0007` | `modified_datetime < order_datetime` | `column_relationship` |
| Conditional Completeness | `O0008` | DELIVERED row with null `shipping_country` | `conditional_completeness` |
| Conditional Values | `O0009` | SG row with `order_status = SHIPPED` | `conditional_values` |
| Custom Expression | `O0010` | net amount greater than quantity × unit price | `custom_expression` |

The expected integration result is:

```text
Happy target
    → all DQ rules PASS
    → validation_passed=True
    → published=False

Dirty target + Warn
    → every deliberate DQ behavior reports a warning
    → validation can continue
    → published=False
```

Inspect the rule-level checks rather than relying only on the aggregate DQ status. Each row in the matrix should have a corresponding failed/warning rule result.

## 6. Prove Sensitive Data treatment

The walkthrough uses Warn first because a blocking rule can stop orchestration before later stages are visible.

To prove enforcement:

1. return to `01_governance`,
2. create/refine a new contract version,
3. turn **Block on failure** on for any one of the DQ rules above,
4. save and freeze the new version,
5. select that version for `curated_orders` in Validate mode,
6. rerun the dirty path.

The selected violation should now stop the orchestration as a blocking DQ failure. You can repeat this with any other rule if you want to exercise each Block path individually.

## 8. Prove Guardrail Coverage

Guardrail Coverage is not another Warn/Block rule. It is the pre-publication readiness gate that verifies every selected participant has an applicable contract and that every applicable Guardrail produced current-activity evidence.

The normal complete run should return `coverage_result.status == "passed"`.

For the negative exercise, temporarily deselect one participating source contract (or disable its only applicable Guardrail) and rerun the target validation. Guardrail Coverage should stop the orchestration with a clear missing-contract/no-applicable-guardrail or not-evaluated reason. Restore the selection immediately afterward.

This gate intentionally blocks rather than warns: publishing without the required Guardrail evidence would defeat the coverage check.

## 9. Restore the happy path before activation

Remove the temporary dirty-target cell or switch the Write block back to `transformed_df`, then rerun the normal target validation using the contract version you intend to activate.

Require a clean validation result before continuing to Step 5.

Because the dirty path never modifies the source or target tables, restoration is simply a normal rerun of the Transform and Write blocks.

## What this proves

This is an integration test of the complete Fabric path, not only the individual DQ functions:

```text
Data Contract UI
    → persisted frozen contract
    → contract selection
    → orchestrate_write()
    → DQ rule resolution
    → Spark evaluation
    → Guardrail results
    → Warn / Block behavior
```

The exercise now covers both orchestrator boundaries: Read-side Freshness/Schema/DQ evidence, Write-side Schema/Sensitive Data/Source Drift/DQ, and the final Guardrail Coverage readiness gate. Source mutations are restored from the canonical fixture; target mutations remain in-session only.

## Expected result

The frozen pipeline contracts have:

1. passed against the canonical sources and targets,
2. detected deliberate Freshness, Schema, and Source Drift conditions,
3. applied the configured Sensitive Data treatment,
4. detected every deliberately broken DQ behavior in the dirty target,
5. demonstrated that Warn allows broad failure evidence collection,
6. demonstrated that a selected Block rule stops orchestration,
7. demonstrated Guardrail Coverage both passing and rejecting an incomplete governed pipeline,
8. passed again on the fully restored happy path before activation.

No validation run publishes the target.

**Next:** [Step 5. Link the Data Agreement and activate](05-activate-data-contract-and-promote.md)
