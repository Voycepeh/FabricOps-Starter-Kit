# Step 4. Validate the frozen Data Contract

### Before you begin

Complete [Step 3](03-author-and-freeze-data-contract.md) and select the frozen contract versions.

<div class="fabricops-section-banner" markdown="1">
<img src="/FabricOps-Starter-Kit/assets/mascots/robot-validate.png" alt="" loading="lazy">
<div class="fabricops-section-content" markdown="1">

## Select Validate for `curated_orders`

Use the same `02A_full_refresh_demo` notebook from Step 2A. In its Data Contract selector:

The selector defaults every table to **Enforce**. Switch only the `curated_orders` target to **Validate**:

</div>
</div>






1. leave every source table in **Enforce** mode and select its exact frozen Step 3 contract,
2. choose **Validate** only for the target, `curated_orders`,
3. select the exact frozen candidate version from Step 3 for `curated_orders`.

All participating tables need selected contracts because Guardrail Coverage checks the complete source → target relationship once any contract is selected.

In Development, sources show a frozen-version picker while remaining in **Enforce** mode; activation is not required to select a frozen source candidate. Targets show their frozen-version picker in **Validate** mode. Production resolves active frozen versions automatically. There is no separate contract dictionary to edit.

After all Read/Write checks and Guardrail Coverage pass, the validation run appends a completion record for each participating exact contract version to `METADATA_GUARDRAIL_RESULTS`. These runtime completion records have `guardrail_type=guardrail_coverage` and `rule_type=contract_validation`; they are not another authorable Guardrail or a new metadata table. They enable activation for sources as well as targets. Partial check results do not enable activation.

<div class="fabricops-section-banner" markdown="1">
<img src="/FabricOps-Starter-Kit/assets/mascots/robot-validate.png" alt="" loading="lazy">
<div class="fabricops-section-content" markdown="1">

## Prove the happy path first

Run the normal visible **Read → Transform → Write** sequence without changing `transformed_df`.

</div>
</div>



The `curated_orders` Write block evaluates the frozen contract but does not publish the target.

Validate returns `published=False` and `validation_passed=True` when the frozen contract passes. This provides validation evidence before the business target can be written under Enforce. The notebook exits after the successful validation gate, so the internal publication stage is never reached and the second Write block is intentionally not reached on this run.

Confirm:

- `published=False`
- `validation_passed=True`
- Freshness, Schema, Source Drift, Sensitive Data, Data Quality, and Guardrail Coverage all permit continuation where applicable; Grain is skipped until explicitly enabled
- the configured `customer_id` Sensitive Data treatment is applied in the prepared DataFrame
- every DQ check is passed
- the physical Write stage was not reached

This proves the contract describes the canonical target before we deliberately break it.

<div class="fabricops-section-banner" markdown="1">
<img src="/FabricOps-Starter-Kit/assets/mascots/robot-validate.png" alt="" loading="lazy">
<div class="fabricops-section-content" markdown="1">

## Exercise the source-side Guardrails

Test Freshness and Schema at the governed Read boundary, then inspect Source Drift during target Write validation.

</div>
</div>

Source Guardrails are evaluated from the real source read and Source Observation metadata, so changing only `transformed_df` cannot test them. Use a controlled mutation of the Development `orders` table, then restore it from the canonical fixture.

The happy-path Validate run does **not** commit an accepted source → target baseline. Source Drift compares against `drift_committed` Source Observation history from a successful Enforce publication. Without that history, expect `first_observation=True` and `status=baseline_created`; this permits continuation but does not demonstrate a historical comparison.

??? info "Exercise historical Source Drift after the first accepted publication"

    After Step 5 activates the tested versions, run the clean **Development** pipeline in Enforce mode once to publish `curated_orders` and commit its accepted source observations. Then select Validate for that target and repeat the controlled Development source mutation below. Do not mutate Production sources. Validate compares against the accepted baseline without advancing it. Restore the canonical source and rerun clean validation afterward.

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
| Schema | `unexpected_demo_column` is not in the frozen schema | Warning; execution continues |
| Source Drift | current Orders observation differs from a committed baseline for this source → target | change details in the Write result; `baseline_created` if no accepted baseline exists |

Inspect `write_result["source_drift_results"]` after the target validation. Overwrite can reconcile historical mutation, so change details can coexist with a passing result. Append cannot reconcile historical mutation; its configured Warn/Block policy determines continuation. See [Read & Write Modes](../reference/read-and-load-strategies.md).

Keep Freshness and Source Drift on Warn for this run so the pipeline can reach the later target checks. Schema permits additional columns automatically; missing Required columns or wrong contracted datatypes would block.

!!! warning "Restore the canonical source immediately after the source test"
    Rerun Step 00C's canonical Orders load before continuing. Do not carry the dirty Bronze source into later demo steps. The mutation is intentionally confined to Development and the canonical CSV remains unchanged.

After restoration, rerun the Orders Read block so the notebook is again holding the canonical source DataFrame.

<div class="fabricops-section-banner" markdown="1">
<img src="/FabricOps-Starter-Kit/assets/mascots/robot-validate.png" alt="" loading="lazy">
<div class="fabricops-section-content" markdown="1">

## Build a deterministic dirty target

Rerun the notebook through the normal Transform cell. Immediately after that cell, add this temporary validation cell:

</div>
</div>



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

Do not change the reusable `02_pipeline` template itself; make validation mutations only in your imported 02A demo copy.

### Run the dirty target with every DQ rule on Warn

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

### Prove Sensitive Data treatment

Inspect `write_result["sensitive_result"]` from the target validation. Confirm the configured `customer_id` treatment was evaluated and that the prepared DataFrame contains the treated representation.

Sensitive Data is intentionally different from a validation rule: valid sensitive values are **transformed**, not failed merely because they exist. A failed treatment always blocks publication; the same treatment behavior runs in Validate and Enforce modes.

Also confirm the dirty target's `unexpected_target_column` produces target **Schema** warning evidence. This is separate from the source Schema exercise above and proves the Write boundary validates the DataFrame before publication.

### Exercise Grain independently of DQ Uniqueness

The main walkthrough leaves Grain enforcement off so the broad DQ exercise can report every rule. To cover Grain as well:

1. Create new drafts for `orders` and `curated_orders`, select `order_id` in **Grain & Row Key**, and enable **Enforce Grain** with **Warn**. Keep the existing DQ Uniqueness rule; it is independent.
2. Save, freeze, and select those exact new versions, leaving `orders` in Enforce and `curated_orders` in Validate.
3. Run the clean Reads, Transform, and target validation. Inspect `sources["orders"]["grain_result"]` and `write_result["grain_result"]`; both should pass.
4. For the Read check, use a temporary Development Orders copy that changes `O0002` to `O0001`, then rerun the Orders Read. Duplicate key rows should produce Grain warnings. Restore Orders from Step 00C immediately and rerun all clean Reads and Transform.
5. For the Write check, use the dirty-target cell above, which duplicates `order_id`. Reassign `transformed_df` to that dirty DataFrame as shown, then rerun only the target validation. Inspect the separate Grain and DQ results; Warn permits both to be collected without publishing.
6. Choose Block in a new draft to demonstrate a Grain failure stopping execution before DQ. A null key also fails Grain; missing or invalid key configuration blocks even with Warn. Restore the clean transform and validate the exact version intended for activation afterward.

Grain checks the returned Read batch or prepared Write input. It does not prove uniqueness against an existing Append or SCD target. See [Step 3's Grain scope table](03-author-and-freeze-data-contract.md#grain-enforcement-and-the-orchestration-sidebar).

### Try Block on failure

The walkthrough uses Warn first because a blocking rule can stop orchestration before later stages are visible.

To prove enforcement:

1. return to `01_governance`,
2. create/refine a new contract version,
3. turn **Block on failure** on for any one of the deliberately failing Freshness or DQ rules,
4. save and freeze the new version,
5. select that version for the relevant table,
6. rerun its dirty path.

The selected violation should now stop the orchestration at that Guardrail stage. You can repeat this with other rules if you want to exercise each Block path individually.

Do not edit a frozen version in place. Refine the draft, freeze a new immutable version, and select that version for validation.

### Prove Guardrail Coverage

[Guardrail Coverage](../api/reference/orchestrate_write.md) is not another Warn/Block rule. It is the pre-publication readiness gate that verifies every selected participant has an applicable contract and that every applicable Guardrail produced current-activity evidence.

The normal complete run should return `coverage_result.status == "passed"`.

For the negative exercise before activation, temporarily clear one participating source's frozen-version selection, then rerun all Reads and the target validation. Use a source with no active contract fallback: clearing a Development candidate does not disable an already active version. Guardrail Coverage should stop the orchestration with a missing-contract or not-evaluated reason. Restore the exact selection and rerun the complete validation afterward.

This gate intentionally blocks rather than warns: publishing without the required Guardrail evidence would defeat the coverage check.

<div class="fabricops-section-banner" markdown="1">
<img src="/FabricOps-Starter-Kit/assets/mascots/robot-validate.png" alt="" loading="lazy">
<div class="fabricops-section-content" markdown="1">

## Restore the happy path before activation

Remove the temporary dirty-target cell or switch the Write block back to `transformed_df`, then rerun the normal target validation using the contract version you intend to activate.

</div>
</div>



Require a clean validation result before continuing to Step 5.

This step's source-side exercise temporarily overwrites only the Development Bronze Orders table and explicitly restores it from Step 00C. The dirty target remains in-session only. After restoring Bronze, rerun the normal Reads, Transform, and Write validation so every configured Guardrail permits continuation again.

### Validate the second target separately

The Full Refresh notebook also writes `customer_summary`. Its Validate run must complete before promoting the full notebook:

1. Select the frozen `customer_summary` contract from Step 3 in **Validate**, retaining the same exact three source versions.
2. Run the environment/selection cells, all three Reads, and the clean Transform to recreate `customer_summary_df`.
3. Initialize `writes = {}`, skip **WRITE 1 — Lakehouse Curated Orders**, and execute **WRITE 2 — Warehouse Customer Summary** directly. Running WRITE 1 in Validate would exit the notebook before WRITE 2.
4. Confirm `write_result["validation_passed"]` is true and `write_result["published"]` is false. This target and its participating source versions now have completed validation records.

No template changes are needed: run the appropriate cells in the imported demo copy. Keep both target versions and all three source versions recorded for Step 5. If a source version changes, rerun validation for both targets with that source version.

### What this proves

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

The exercise covers both orchestrator boundaries ([`orchestrate_read()`](../api/reference/orchestrate_read.md) and [`orchestrate_write()`](../api/reference/orchestrate_write.md)): four applicable Read checks (Freshness, Schema, Grain, Data Quality), five applicable Write checks (Schema, Sensitive Data, Source Drift, Grain, Data Quality), and Guardrail Coverage. Only configured checks run; the focused Grain exercise enables Grain explicitly. Source mutations are restored from the canonical fixture; target mutations remain in-session only.

### Expected result

The frozen pipeline contracts have:

1. passed against the canonical sources and targets,
2. detected deliberate Freshness and Schema conditions, and recorded Source Drift change details where a committed baseline exists,
3. applied the configured Sensitive Data treatment,
4. detected every deliberately broken DQ behavior in the dirty target,
5. demonstrated that Warn allows broad failure evidence collection,
6. demonstrated that a selected Block rule stops orchestration,
7. demonstrated Guardrail Coverage both passing and rejecting an incomplete governed pipeline,
8. passed again on the fully restored happy path before activation,
9. completed separate validation for both `curated_orders` and `customer_summary`, plus Grain checks when enabled.

No validation run publishes the target.

**Next:** [Step 5. Link the Data Agreement and activate](05-activate-data-contract-and-promote.md)
