# Step 3. Author and freeze the Data Contracts

### Before you begin

Complete [Step 2A](02A-full-refresh-demo.md) before authoring and freezing the contracts.

!!! warning "Enable Fabric AI Functions for the AI-assisted DQ exercise"
    All nine deterministic Data Quality rule types can be authored manually. This walkthrough also exercises natural-language generation, so enable AI to follow that assisted path; AI is not required for ordinary rule creation or enforcement.

    Meet the [AI Functions prerequisites](https://learn.microsoft.com/en-us/fabric/data-science/ai-functions/overview) and set `GOVERNANCE_CONFIG.ai_enrichment.enabled = True` in `00_env_config`.

    Learn more: [Sensitive Data Classification & Treatment](../solutions/ai-assisted-data-contract-authoring.md).

Scheduled Refresh is operational metadata in `METADATA_DATA_CATALOGUE`, captured by the writer pipeline. If discovery is unavailable, the writer records `unavailable` and continues. Data Contract authoring and freezing do not depend on it. Freshness Guardrails retain their independently authored source-data arrival expectations.

<div class="fabricops-section-banner" markdown="1">
<img src="/FabricOps-Starter-Kit/assets/mascots/robot-writing.png" alt="" loading="lazy">
<div class="fabricops-section-content" markdown="1">

## Cover the whole pipeline, not only the target

This walkthrough validates frozen contracts for every participating table in the governed path:

</div>
</div>






| Pipeline role | Table | Guardrails exercised |
| --- | --- | --- |
| Source | `orders` | Freshness, Schema, Source Drift |
| Source | `products` | Schema |
| Source | `order_history` | Schema |
| Target | `curated_orders` | Schema, Sensitive Data, Data Quality |
| Target | `customer_summary` | Schema |

The selected Data Contract determines which Guardrails run; empty or intentionally disabled optional checks impose no additional requirement. Governed execution requires configured checks to execute successfully or return a Warn decision before publication.

Open `01_governance`, run the setup cells, select each table above, then run [`widget_data_contract()`](../api/reference/widget_data_contract.md):

```python
widget_data_contract()
```

The editor uses the selected table's Catalogue and latest Profile as authoring evidence.

For `orders`, enable **Freshness**, **Schema**, and **Source Drift**. Use `modified_datetime` as the Freshness evidence column and keep the allowed age comfortably above the canonical baseline's normal age. Configure Source Drift for the source's normal overwrite behavior. Keep Freshness and Source Drift on **Warn** for the first integration run. Schema blocks missing Required columns and contracted datatype mismatches.

For `products`, `order_history`, and the `customer_summary` target, a Schema rule is sufficient for this exercise. Their purpose is to make both source → target paths Guardrail-ready without inventing unrelated business rules.

For `curated_orders`, enable **Schema**, add one **Sensitive Data** treatment on `customer_id` (Mask is the easiest treatment to inspect), and author the complete DQ rules below. Keep DQ on **Warn** for the first dirty run. Schema always blocks missing Required columns, uncontracted additional columns and normalized datatype mismatches. Sensitive Data treatment failures always block. Sensitive Data is a treatment guardrail: the integration proof is that the treatment is actually applied before DQ/publication, not that valid sensitive data is rejected.

For this walkthrough, keep every DQ rule **Enabled** but leave **Block on failure** off. Step 4 intentionally breaks every DQ behavior in one validation run; Warn lets FabricOps report all of them instead of stopping at the first blocking failure.

<div class="fabricops-section-banner" markdown="1">
<img src="/FabricOps-Starter-Kit/assets/mascots/robot-writing.png" alt="" loading="lazy">
<div class="fabricops-section-content" markdown="1">

## Table

Open **Table** and review:

</div>
</div>



* Description and Classification
* Grain & Row Key — describe one row and select the actual table key: `order_id` for Orders/Curated Orders, `product_id` for Products, `historical_order_id` for Order History, and `customer_id` for Customer Summary. Leave **Enforce Grain** off for the main DQ exercise; Step 4 adds a focused Grain check separately.
* Processing
* Freshness, when applicable
* Source Drift, when applicable

Use AI suggestions where useful, then review them before applying. Profile statistics are evidence only; they do not become contract requirements unless Governance authors a rule from them.

### Grain enforcement and the orchestration sidebar

**Grain is a singular table Guardrail, independent of Data Quality.** The description remains table Enrichment; selected key columns and enforcement policy are separate choices. Selecting a profiled key or entering a description does not enable enforcement. **Enforce Grain** defaults to **Block** when enabled; choose **Warn** to record violations and continue. Turn it off to retain the description and keys without runtime validation or required Grain Results.

A composite key is unique as a combination. Any SQL null in any key component fails that row; blank strings are ordinary values. All rows sharing a duplicate combination fail. An empty input passes only with a valid configured key and all configured columns present. Missing columns, duplicate/blank key names, unknown contract columns, and invalid configuration cannot pass; invalid configuration blocks even under Warn. No duplicate DQ Uniqueness rule is created for declared Grain. Existing authored DQ Uniqueness rules remain independent rules.

| Boundary or strategy | Grain validation scope |
| --- | --- |
| Full Read | The returned DataFrame, including any query restriction. |
| Incremental Read | The returned incremental batch only. |
| Overwrite | Prepared Write input after Sensitive Data treatment; these rows replace the target. |
| Append | Prepared incoming rows only; collisions with existing target rows are not checked. |
| SCD1 | Prepared incoming rows only; existing target uniqueness is not established. Existing strategy business-key checks still apply. |
| SCD2 | Prepared incoming rows only. On full Read, history needs a version-aware row key such as business key plus effective timestamp. Business keys may repeat across history; Grain does not change SCD2 merge keys or restrict Read to current rows. |

??? info "Resulting-table uniqueness is outside this validation scope"

    Grain does not read existing targets or simulate merges. Append, SCD1, and SCD2 can therefore produce a different table state from the checked input. Resulting-table uniqueness would require strategy-specific validation and concurrency handling beyond this change. Configure physical row Grain appropriately; a business key alone is not a unique physical row key for SCD2 history. Existing SCD processing still requires unique incoming business keys.

The sidebar groups configured rules under **When this table is read** (`orchestrate_read()`: Freshness, Schema, Grain, Data Quality) and **Before this table is written** (`orchestrate_write()`: Schema, Sensitive Data, Source Drift, Grain, Data Quality). Source Drift belongs to the source → consuming target relationship and runs during that target's Write orchestration. The same Schema, Grain, and DQ configuration applies to both paths; there are no separate Read/Write policies.

Expand a Guardrail to inspect its columns, rules, parameters, and policy, then click a rule to open its existing editor. Use **Table**, **Column**, and **Data Quality** to author or edit settings, including unconfigured Guardrails. Disabled Grain remains visible with its disabled state; its description and key selection remain editable in **Grain & Row Key**. Summaries update as edits are staged, before Save.

**Warn/Block is policy, not an execution result.** The sidebar does not execute validation. `METADATA_GUARDRAIL_RESULTS` records actual Grain evaluations with `guardrail_type=grain`, the exact contract version, continuation decision, counts, and validation scope. Configured Grain checks validate Read rows and prepared Write input independently; their authored Warn or Block action determines continuation. Sensitive Data treatments must succeed before continuation. Profiling supplies observations and suggestions, not Guardrails.


<div class="fabricops-section-banner" markdown="1">
<img src="/FabricOps-Starter-Kit/assets/mascots/robot-writing.png" alt="" loading="lazy">
<div class="fabricops-section-content" markdown="1">

## Data Quality — add rules manually

Open **Data Quality**, use **Add Rule Manually**, and configure these rules for the integration exercise:

The rule inventory at the top shows status, type, columns, Warn/Block policy, and the accepted failure limit. Choose a rule in **Review and Edit** to use the same guided controls for existing or AI-generated rules. Relationship and conditional rules use explicit column roles such as **Left column**, **Right column**, **Condition column**, and **Target column**; advanced JSON is available only as a collapsed inspection option.

</div>
</div>



| UI | Column | Configuration | Runtime rule |
| --- | --- | --- | --- |
| **Completeness** | `customer_id` | Maximum missing = **0%**; treat blank as missing | [`completeness`](../reference/dq-rules/completeness.md) |
| **Uniqueness** | `order_id` | Accepted failure rate = **0%** | [`uniqueness`](../reference/dq-rules/uniqueness.md) |
| **Value set → Allow listed values** | `order_status` | `NEW, PROCESSING, SHIPPED, DELIVERED, CANCELLED` | [`value_set`](../reference/dq-rules/value-set.md) / `allow` |
| **Value set → Block listed values** | `shipping_country` | `UNKNOWN` | [`value_set`](../reference/dq-rules/value-set.md) / `block` |
| **Range** | `quantity` | Lower bound **1**, upper bound **4**, include both bounds | [`range`](../reference/dq-rules/range.md) |

Keep **Block on failure** off for each rule.

Allowed and blocked value sets are separate rules even though both persist using the `value_set` runtime type. The [DQ rule reference](../reference/dq-rules/index.md) maps every authoring control to its persisted rule.

<div class="fabricops-section-banner" markdown="1">
<img src="/FabricOps-Starter-Kit/assets/mascots/robot-writing.png" alt="" loading="lazy">
<div class="fabricops-section-content" markdown="1">

## Data Quality — generate rules with AI

In **Generate Rules with AI**, resolve each requirement below. Review and edit the proposal before choosing **Add DQ Rule**. Generated proposals do not become draft rules until you add them.

</div>
</div>



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

### Confirm the complete DQ contract

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

<div class="fabricops-section-banner" markdown="1">
<img src="/FabricOps-Starter-Kit/assets/mascots/robot-writing.png" alt="" loading="lazy">
<div class="fabricops-section-content" markdown="1">

## Freeze every participating contract

Freeze the source and target contracts that the next validation step will test.

</div>
</div>

Freeze the three source contracts and both target contracts (`curated_orders` and `customer_summary`): five contracts in total. Step 4 validates each target separately with the same three sources. Each target run needs those four exact participating versions; the full notebook needs both targets ready before Production.

### Manifest & Freeze

Open **Review** and inspect the complete contract, including the DQ rules above, before freezing it.

A saved draft keeps the schema captured when it was created. A new draft excludes columns removed from the latest workspace observation. In the **Table** workspace, review the unavailable definitions and choose **Remove unavailable definitions** to stage their removal. Correct any remaining references, such as Grain keys, before saving. Frozen versions remain unchanged. If another session freezes the draft before Save or Freeze completes, the operation reports a conflict and retains pending edits.

Choose **Save Data Contract** while the version is still a draft. Close and reopen that exact draft to confirm its descriptions, classifications, key selection, Processing, and configured Guardrails hydrate from the saved payload. Pending sidebar edits are not saved until Save succeeds. When it is ready for Engineering validation, choose **Freeze** and reopen the exact frozen version to review its immutable manifest.

`METADATA_DATA_CONTRACT.contract_payload_json` is the single source of authored table and column Enrichment and the configured Guardrails. Source contracts support five Guardrails: Schema, Grain, Freshness, Source Drift, and Data Quality. Target contracts support four: Schema, Grain, Data Quality, and Sensitive Data. `orchestrate_read` runs four checks (Freshness, Schema, Grain, Data Quality); `orchestrate_write` runs five (Schema, Sensitive Data, Source Drift on sources, Grain, Data Quality). Grain description is descriptive Enrichment; key selection and optional enforcement are stored as the Grain Guardrail in the same payload. Save replaces the draft payload, Freeze makes that exact version immutable, and the next draft inherits the previous frozen definition. Runtime checks and exports resolve the selected payload; actual evaluations remain in `METADATA_GUARDRAIL_RESULTS`.

The frozen version is an immutable data contract and becomes the exact candidate Engineering selects in Step 4. Freezing does not activate it for Production.

!!! warning "Breaking workspace architecture"
    This Unreleased architecture uses workspace-scoped metadata and intentionally breaks earlier layouts. Start with fresh Metadata for this design; no compatibility layer or in-place migration is supplied. Frozen release documentation retains the earlier contracts.

**Next:** [Step 4. Preview and enforce the frozen Data Contract](04-validate-frozen-data-contract.md).
