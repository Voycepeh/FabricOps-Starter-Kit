# Step 4. Validate the frozen Data Contract

**Use the same `02_pipeline` to prove the complete governed path: first every Guardrail passes, then controlled source and target mutations exercise Freshness, Schema, Source Drift, Sensitive Data, every DQ behavior, and Guardrail Coverage without publishing a validation target.**

The selector defaults every table to **Enforce**. For this step, put only `curated_orders` into **Validate** mode and select the exact frozen version from Step 3.

## 1. Select Validate for `curated_orders`

In the Data Contract selector at the top of `02_pipeline`:

1. leave every source table in **Enforce** mode and select its exact frozen Step 3 contract,
2. choose **Validate** only for the target, `curated_orders`,
3. select the exact frozen candidate version from Step 3 for `curated_orders`.

All participating tables need selected contracts because Guardrail Coverage checks the complete source → target relationship once any contract is selected.

The frozen-version picker appears only for a target in Validate mode. There is no separate contract dictionary to edit.

## 2. Prove the happy path first

Run the normal visible **Read → Transform → Write** sequence without changing `transformed_df`.

The `curated_orders` Write block evaluates the frozen contract but does not publish the target.

Validate returns `published=False` and `validation_passed=True` when the frozen contract passes. This provides validation evidence before the business target can be written under Enforce. The notebook exits after the successful validation gate, so [`pipeline_write()`](../api/reference/pipeline_write.md) is never reached and the second Write block is intentionally not reached on this run.

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

```python
from fabricops_kit import write_lakehouse_table

dirty_orders_source_df = (
    orders_df
    .withColumn("modified_datetime", F.to_timestamp(F.lit("2025-01-01 00:00:00")))
    .withColumn("unexpected_demo_column", F.lit("schema-drift"))
)

write_lakehouse_table(
    dirty_orders_source_df,
    "orders",
    store="Bronze",
    schema="demo",
    mode="overwrite",
)
```

This makes Freshness deterministically stale and adds a column that is absent from the frozen Schema. Overwrite only the **Development Bronze Orders table**, then rerun the Orders Read block and the `curated_orders` Write validation.

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
    # target schema: add a column absent from the frozen contract
    .withColumn("unexpected_target_column", F.lit("schema-drift"))
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

For this validation run, change only the first argument of the `curated_orders` Write block. The boundary is handled by [`orchestrate_write()`](../api/reference/orchestrate_write.md):

```python
write_result = orchestrate_write(
    dirty_transformed_df,
    # keep the rest of the existing Write block unchanged
)
```

Do not change the reusable `02_pipeline` template itself.

## 5. Run the dirty target with every DQ rule on Warn

Run the `curated_orders` Write block again.

Because Step 3 left **Block on failure** off, the DQ guardrail can evaluate the complete ruleset and report warnings instead of terminating on the first deliberate violation. Validate mode uses the exact same Schema, Sensitive Data, Source Drift, Data Quality, and Guardrail Coverage path as Enforce, but still prevents publication. See [Sensitive Data Treatments](../reference/sensitive-data-treatments.md) for the treatment behavior used by this check.

Use the returned DQ result to compare actual behavior with this matrix:

| DQ behavior | Dirty row | Deliberate violation | Expected runtime rule |
| --- | --- | --- | --- |
| Completeness | original `O0001` | `customer_id = null` | [`completeness`](../reference/dq-rules/completeness.md) |
| Uniqueness | original `O0002` | changed to duplicate `order_id = O0001` | [`uniqueness`](../reference/dq-rules/uniqueness.md) |
| Whitelist | `O0003` | `order_status = INVALID` | [`value_set`](../reference/dq-rules/value-set.md) / `allow` |
| Blacklist | `O0004` | `shipping_country = UNKNOWN` | [`value_set`](../reference/dq-rules/value-set.md) / `block` |
| Range | `O0005` | `quantity = 0` | [`range`](../reference/dq-rules/range.md) |
| Pattern | original `O0006` | `order_id = BAD-006` | [`pattern`](../reference/dq-rules/pattern.md) |
| Column Relationship | `O0007` | `modified_datetime < order_datetime` | [`column_relationship`](../reference/dq-rules/column-relationship.md) |
| Conditional Completeness | `O0008` | DELIVERED row with null `shipping_country` | [`conditional_completeness`](../reference/dq-rules/conditional-completeness.md) |
| Conditional Values | `O0009` | SG row with `order_status = SHIPPED` | [`conditional_values`](../reference/dq-rules/conditional-values.md) |
| Custom Expression | `O0010` | net amount greater than quantity × unit price | [`custom_expression`](../reference/dq-rules/custom-expression.md) |

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

Inspect `write_result["sensitive_result"]` from the target validation. Confirm the configured `customer_id` treatment was evaluated and that the prepared DataFrame contains the treated representation.

Sensitive Data is intentionally different from a validation rule: valid sensitive values are **transformed**, not failed merely because they exist. A treatment failure can Warn or Block, but manufacturing an invalid treatment configuration is not a useful data-quality scenario.

Also confirm the dirty target's `unexpected_target_column` produces target **Schema** warning evidence. This is separate from the source Schema exercise above and proves the Write boundary validates the DataFrame before publication.

## 7. Try Block on failure

The walkthrough uses Warn first because a blocking rule can stop orchestration before later stages are visible.

To prove enforcement:

1. return to `01_governance`,
2. create/refine a new contract version,
3. turn **Block on failure** on for any one of the deliberately failing Freshness, Schema, or DQ rules,
4. save and freeze the new version,
5. select that version for the relevant table,
6. rerun its dirty path.

The selected violation should now stop the orchestration at that Guardrail stage. You can repeat this with other rules if you want to exercise each Block path individually.

Do not edit a frozen version in place. Refine the draft, freeze a new immutable version, and select that version for validation.

## 8. Prove Guardrail Coverage

[Guardrail Coverage](../api/reference/check_guardrail_coverage.md) is not another Warn/Block rule. It is the pre-publication readiness gate that verifies every selected participant has an applicable contract and that every applicable Guardrail produced current-activity evidence.

The normal complete run should return `coverage_result.status == "passed"`.

For the negative exercise, temporarily deselect one participating source contract (or disable its only applicable Guardrail) and rerun the target validation. Guardrail Coverage should stop the orchestration with a clear missing-contract/no-applicable-guardrail or not-evaluated reason. Restore the selection immediately afterward.

This gate intentionally blocks rather than warns: publishing without the required Guardrail evidence would defeat the coverage check.

## 9. Restore the happy path before activation

Remove the temporary dirty-target cell or switch the Write block back to `transformed_df`, then rerun the normal target validation using the contract version you intend to activate.

Require a clean validation result before continuing to Step 5.

Step 3's source-side exercise temporarily overwrites only the Development Bronze Orders table and explicitly restores it from Step 00C. The dirty target remains in-session only. After restoring Bronze, rerun the normal Reads, Transform, and Write validation so every Guardrail is green again.

## What this proves

This is an integration test of the complete Fabric path, not only the individual DQ functions:

```text
Data Contract UI
    → persisted frozen contract
    → contract selection
    → orchestrate_read() / orchestrate_write()
    → Guardrail + DQ rule resolution
    → Spark / observation evaluation
    → Guardrail results
    → Warn / Block behavior
```

The exercise now covers both orchestrator boundaries ([`orchestrate_read()`](../api/reference/orchestrate_read.md) and [`orchestrate_write()`](../api/reference/orchestrate_write.md)): Read-side Freshness/Schema/DQ evidence, Write-side Schema/Sensitive Data/Source Drift/DQ, and the final [Guardrail Coverage](../api/reference/check_guardrail_coverage.md) readiness gate. Source mutations are restored from the canonical fixture; target mutations remain in-session only.

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
