# Step 4. Validate the frozen Data Contract

**Use the same `02_pipeline` to prove both sides of the contract: the normal transformed target passes, then a deterministic dirty target trips every DQ behavior authored in Step 3 without publishing either validation run.**

The selector defaults every table to **Enforce**. For this step, put only `curated_orders` into **Validate** mode and select the exact frozen version from Step 3.

## 1. Select Validate for `curated_orders`

In the Data Contract selector at the top of `02_pipeline`:

1. leave every source table in **Enforce** mode,
2. choose **Validate** only for `curated_orders`,
3. select the exact frozen candidate version from Step 3.

The frozen-version picker appears only for a target in Validate mode. There is no separate contract dictionary to edit.

## 2. Prove the happy path first

Run the normal visible **Read → Transform → Write** sequence without changing `transformed_df`.

The `curated_orders` Write block evaluates the frozen contract but does not publish the target. The notebook exits after the successful validation gate, so the second Write block is intentionally not reached on this run.

Confirm:

- `published=False`
- `validation_passed=True`
- every DQ check is passed
- `pipeline_write()` was not reached

This proves the contract describes the canonical target before we deliberately break it.

## 3. Build a deterministic dirty target

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

## 4. Run the dirty path with every rule on Warn

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

## 5. Try Block on failure

The walkthrough uses Warn first because a blocking rule can stop orchestration before later stages are visible.

To prove enforcement:

1. return to `01_governance`,
2. create/refine a new contract version,
3. turn **Block on failure** on for any one of the DQ rules above,
4. save and freeze the new version,
5. select that version for `curated_orders` in Validate mode,
6. rerun the dirty path.

The selected violation should now stop the orchestration as a blocking DQ failure. You can repeat this with any other rule if you want to exercise each Block path individually.

## 6. Restore the happy path before activation

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

The same Write-side orchestration also evaluates applicable Schema, Sensitive Data, Source Drift, and Guardrail Coverage checks. Those results remain visible alongside DQ; this exercise deliberately mutates only the target values so each of the nine DQ runtime types can be tested deterministically without corrupting the reusable demo environment.

## Expected result

The exact frozen contract has:

1. passed against the canonical `curated_orders` target,
2. detected every deliberately broken DQ behavior in the dirty target,
3. demonstrated that Warn allows complete evidence collection,
4. optionally demonstrated that changing a rule to Block stops orchestration,
5. passed again on the restored happy path before activation.

No validation run publishes the target.

**Next:** [Step 5. Link the Data Agreement and activate](05-activate-data-contract-and-promote.md)
