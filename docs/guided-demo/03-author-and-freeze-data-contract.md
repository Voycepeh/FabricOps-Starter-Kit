# Step 3. Author and freeze the Data Contracts

**Return to `01_governance`, author the source and target contracts used by the real pipeline, then freeze the exact versions Engineering will exercise in Step 4.**

Freezing creates an **immutable Data Contract** candidate for validation. It does not activate the contract for Production.

!!! warning "Enable Fabric AI Functions for the full DQ integration exercise"
    The four direct Column data quality families can be authored without AI. The remaining Business Rules are resolved from business language, so the full nine-rule integration exercise requires AI-assisted authoring.

    Meet the [AI Functions prerequisites](https://learn.microsoft.com/en-us/fabric/data-science/ai-functions/overview) and set `GOVERNANCE_CONFIG.ai_enrichment.enabled = True` in `00_env_config`.

    Learn more: [Sensitive Data Classification & Treatment](../solutions/ai-assisted-data-contract-authoring.md).

!!! note "Scheduled Refresh not showing?"
    FabricOps reads the current notebook schedule from Microsoft Fabric using the notebook or pipeline execution identity. In the normal Guided Demo setup, the person developing the pipeline should already have **Contributor, Member, or Admin** access to the Engineering workspace. If Scheduled Refresh shows `Unavailable`, confirm that the execution identity can access the notebook and can read its schedule through the Fabric API. `Unavailable` means FabricOps could not observe the schedule; it does not mean that no schedule exists.

    See Microsoft's [workspace roles](https://learn.microsoft.com/en-us/fabric/fundamentals/roles-workspaces) and [List Item Schedules API](https://learn.microsoft.com/en-us/rest/api/fabric/core/job-scheduler/list-item-schedules) for the underlying access requirements.

## 1. Cover the whole pipeline, not only the target

Step 4 validates the complete governed path, so every participating table needs a frozen contract:

| Pipeline role | Table | Guardrails exercised |
| --- | --- | --- |
| Source | `orders` | Freshness, Schema, Source Drift |
| Source | `products` | Schema |
| Source | `order_history` | Schema |
| Target | `curated_orders` | Schema, Sensitive Data, Data Quality |

Guardrail Coverage then proves that every selected source/target contract has applicable rules and that every applicable rule produced evidence in the current activity.

Open `01_governance`, run the setup cells, select each table above, then run [`widget_data_contract()`](../api/reference/widget_data_contract.md):

```python
widget_data_contract()
```

The editor uses the selected table's Catalogue and latest Profile as authoring evidence.

For `orders`, enable **Freshness**, **Schema**, and **Source Drift**. Use `modified_datetime` as the Freshness evidence column and keep the allowed age comfortably above the canonical baseline's normal age. Configure Source Drift for the source's normal overwrite behavior. Keep these rules on **Warn** for the first integration run.

For `products` and `order_history`, a Schema rule is sufficient for this exercise. Their purpose is to make the complete `curated_orders` source → target path Guardrail-ready without inventing unrelated business rules.

For `curated_orders`, enable **Schema**, add one **Sensitive Data** treatment on `customer_id` (Mask is the easiest treatment to inspect), and author the complete DQ rules below. Keep Schema and DQ on **Warn** for the first dirty run. Sensitive Data is a treatment guardrail: the integration proof is that the treatment is actually applied before DQ/publication, not that valid sensitive data is rejected.

For this walkthrough, keep every DQ rule **Enabled** but leave **Block on failure** off. Step 4 intentionally breaks every DQ behavior in one validation run; Warn lets FabricOps report all of them instead of stopping at the first blocking failure.

## 2. Table

Open **Table** and review:

* Description and Classification
* Grain & Row Key — use `order_id`
* Processing
* Freshness, when applicable
* Source Drift, when applicable

Use AI suggestions where useful, then review them before applying. Profile statistics are evidence only; they do not become contract requirements unless Governance authors a rule from them.

## 3. Columns — author the direct DQ rules

Open **Columns** and configure these rules for the integration exercise:

| UI | Column | Configuration | Runtime rule |
| --- | --- | --- | --- |
| **Completeness** | `customer_id` | Maximum missing = **0%**; treat blank as missing | [`completeness`](../reference/dq-rules/completeness.md) |
| **Uniqueness** | `order_id` | Minimum unique = **100%** | [`uniqueness`](../reference/dq-rules/uniqueness.md) |
| **Value Lists → Whitelist** | `order_status` | `NEW, PROCESSING, SHIPPED, DELIVERED, CANCELLED` | [`value_set`](../reference/dq-rules/value-set.md) / `allow` |
| **Value Lists → Blacklist** | `shipping_country` | `UNKNOWN` | [`value_set`](../reference/dq-rules/value-set.md) / `block` |
| **Value Rules** | `quantity` | Lower bound **1**, upper bound **4**, include both bounds | [`range`](../reference/dq-rules/range.md) |

Keep **Block on failure** off for each rule.

Whitelist and Blacklist are separate rules even though both persist using the `value_set` runtime type. The [DQ rule reference](../reference/dq-rules/index.md) maps every authoring control to its persisted rule.

## 4. DQ Rules — exercise every Business Rule path

Open **DQ Rules** and resolve each requirement below. Review the proposed rule before choosing **Add DQ Rule**.

| Business requirement to enter | Expected resolved rule | Why the clean target passes |
| --- | --- | --- |
| Order ID must start with O followed by exactly four digits. | [`pattern`](../reference/dq-rules/pattern.md) | Canonical IDs use `O0001` through `O0120`. |
| Modified datetime must be on or after order datetime. | [`column_relationship`](../reference/dq-rules/column-relationship.md) | Every canonical order is modified after it is created. |
| When order status is DELIVERED, shipping country is required. | [`conditional_completeness`](../reference/dq-rules/conditional-completeness.md) | Delivered baseline rows have a shipping country. |
| When shipping country is SG, order status must be NEW. | [`conditional_values`](../reference/dq-rules/conditional-values.md) | The canonical demo data uses NEW for SG rows. |
| Order net amount must not exceed quantity multiplied by unit price. | [`custom_expression`](../reference/dq-rules/custom-expression.md) | A non-negative discount makes net amount less than or equal to gross amount. |

For each proposal:

1. confirm the **Expected resolved rule** above,
2. keep the rule **Enabled**,
3. leave **Block on failure** off,
4. add it to the draft.

!!! important "Custom Expression must remain the fallback"
    The final requirement deliberately contains arithmetic that the structured rule types cannot preserve. Confirm that FabricOps resolves it to `custom_expression`, review the constrained PySpark expression, and complete the required **Engineering review** before freeze.

If AI resolves one of these requirements to a different rule, do not accept it just to continue the demo. Refine the business wording until the intended deterministic rule is produced.

## 5. Confirm the complete DQ contract

Before freezing, the contract should exercise all nine supported runtime DQ types and both Value List behaviors:

| Coverage | Expected |
| --- | --- |
| Completeness | ✓ |
| Uniqueness | ✓ |
| Whitelist | ✓ `value_set / allow` |
| Blacklist | ✓ `value_set / block` |
| Range | ✓ |
| Pattern | ✓ |
| Column Relationship | ✓ |
| Conditional Completeness | ✓ |
| Conditional Values | ✓ |
| Custom Expression | ✓ |

This is intentionally broader than a normal contract. The Guided Demo uses it as the canonical Fabric integration exercise for the complete DQ authoring and execution path.

## 6. Freeze every participating contract

Freeze the three source contracts and the `curated_orders` target contract. Step 4 must select the exact frozen versions for all four participating tables; otherwise Guardrail Coverage correctly reports that the governed source → target path is not ready.

## 7. Manifest & Freeze

Open **Manifest & Freeze** and review the complete contract, including the DQ rules above.

Choose **Save Data Contract** while the version is still a draft. When it is ready for Engineering validation, choose **Freeze**.

The frozen version is immutable and becomes the exact candidate Engineering selects in Step 4. Freezing does not activate it for Production.

## Expected result

You now have frozen contracts for the complete demo pipeline. `curated_orders` represents all nine DQ rule types, `orders` supplies the source-side Freshness and Source Drift expectations, Schema is represented across the pipeline, and Sensitive Data treatment is configured on the governed target. Step 4 can now exercise every Guardrail stage that the orchestrators actually run.

**Previous:** [Step 2. Run the Development pipeline](02-build-and-run-etl.md)  
**Next:** [Step 4. Select and validate the Data Contract](04-validate-frozen-data-contract.md)
