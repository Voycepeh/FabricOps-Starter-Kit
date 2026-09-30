# Step 3. Author and freeze the Data Contract

**Return to `01_governance`, author a complete contract for `curated_orders`, then freeze the exact version Engineering will exercise in Step 4.**

Freezing creates an **immutable Data Contract** candidate for validation. It does not activate the contract for Production.

!!! warning "Enable Fabric AI Functions for the full DQ integration exercise"
    The four direct Column data quality families can be authored without AI. The remaining Business Rules are resolved from business language, so the full nine-rule integration exercise requires AI-assisted authoring.

    Meet the [AI Functions prerequisites](https://learn.microsoft.com/en-us/fabric/data-science/ai-functions/overview) and set `GOVERNANCE_CONFIG.ai_enrichment.enabled = True` in `00_env_config`.

    Learn more: [AI-assisted Data Contract Authoring](../solutions/ai-assisted-data-contract-authoring.md).

## 1. Open the Data Contract editor

Open `01_governance`, run the setup cells, select the `curated_orders` target produced in Step 2, then run:

```python
widget_data_contract()
```

The editor uses the selected table's Catalogue and latest Profile as authoring evidence.

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
| **Completeness** | `customer_id` | Maximum missing = **0%**; treat blank as missing | `completeness` |
| **Uniqueness** | `order_id` | Minimum unique = **100%** | `uniqueness` |
| **Value Lists → Whitelist** | `order_status` | `NEW, PROCESSING, SHIPPED, DELIVERED, CANCELLED` | `value_set` / `allow` |
| **Value Lists → Blacklist** | `shipping_country` | `UNKNOWN` | `value_set` / `block` |
| **Value Rules** | `quantity` | Lower bound **1**, upper bound **4**, include both bounds | `range` |

Keep **Block on failure** off for each rule.

Whitelist and Blacklist are separate rules even though both persist using the `value_set` runtime type. The [DQ rule reference](../reference/dq-rules/index.md) maps every authoring control to its persisted rule.

## 4. DQ Rules — exercise every Business Rule path

Open **DQ Rules** and resolve each requirement below. Review the proposed rule before choosing **Add DQ Rule**.

| Business requirement to enter | Expected resolved rule | Why the clean target passes |
| --- | --- | --- |
| Order ID must start with O followed by exactly four digits. | `pattern` | Canonical IDs use `O0001` through `O0120`. |
| Modified datetime must be on or after order datetime. | `column_relationship` | Every canonical order is modified after it is created. |
| When order status is DELIVERED, shipping country is required. | `conditional_completeness` | Delivered baseline rows have a shipping country. |
| When shipping country is SG, order status must be NEW. | `conditional_values` | The canonical demo data uses NEW for SG rows. |
| Order net amount must not exceed quantity multiplied by unit price. | `custom_expression` | A non-negative discount makes net amount less than or equal to gross amount. |

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

## 6. Manifest & Freeze

Open **Manifest & Freeze** and review the complete contract, including the DQ rules above.

Choose **Save Data Contract** while the version is still a draft. When it is ready for Engineering validation, choose **Freeze**.

The frozen version is immutable and becomes the exact candidate Engineering selects in Step 4. Freezing does not activate it for Production.

## Expected result

You now have one frozen `curated_orders` Data Contract with all nine DQ rule types represented and all DQ rules initially configured to warn so Step 4 can observe every deliberate failure in one run.

**Previous:** [Step 2. Run the Development pipeline](02-build-and-run-etl.md)  
**Next:** [Step 4. Select and validate the Data Contract](04-validate-frozen-data-contract.md)
