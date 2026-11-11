# Step 3. Author and freeze the Data Contracts

### Before you begin

Complete [Step 2A](02A-full-refresh-demo.md) before authoring and freezing the contracts.

!!! warning "Enable Fabric AI Functions for the AI-assisted DQ exercise"
    All nine deterministic Data Quality rule types can be authored manually. This walkthrough also exercises natural-language generation, so enable AI to follow that assisted path; AI is not required for ordinary rule creation or enforcement.

    Meet the [AI Functions prerequisites](https://learn.microsoft.com/en-us/fabric/data-science/ai-functions/overview) and set `GOVERNANCE_CONFIG.ai_enrichment.enabled = True` in `00_env_config`.

    Learn more: [Sensitive data discovery, classification and treatment](../governance.md#sensitive-data-discovery-classification-and-treatment).

### Choose the AI settings or author manually

The default is **GPT-5-mini with low reasoning** and provider-default verbosity.
In `00_env_config`, keep existing project prompts and add these keys to the existing
`GOVERNANCE_CONFIG = GovernanceConfig(..., ai_enrichment={...})` declaration:

```python
ai_enrichment={
    "enabled": True,
    "model_deployment_name": "gpt-5-mini",  # Or "gpt-5.1".
    "reasoning_effort": "low",
    "verbosity": None,
    # Keep your existing table, column, Sensitive Data, Grain and Business Rule prompts.
}
```

For a complex governance exercise, override the settings for one widget instance:

```python
contract_state = widget_data_contract(
    ai_model="gpt-5.1",
    ai_reasoning_effort="high",  # "medium" also supported.
    ai_verbosity="medium",
)
```

Explicit widget values take precedence over `00_env_config`, then package defaults.
The selector and editor show the effective model, reasoning and verbosity before any request.
Stronger models and higher reasoning can increase consumption and latency; see
[AI consumption and monitoring](../governance.md#optional-ai-authoring-and-consumption).

Choose **Open Data Contract** to open the manual-first editor. Opening, switching
sections or columns, and lifecycle actions make zero AI requests and do not initialize
AI Functions. To disable all AI actions, set `ai_enrichment.enabled=False`. Author Description, Grain and Row Key, Sensitive Data
and all nine Data Quality rule types manually, then use the same Save, Freeze and
activation steps. Each contextual **Generate**, **Suggest** or **Re-run** requests only
that suggestion and consumes Fabric AI capacity. Suggestions remain in the authoring
session during navigation and require explicit human review before addition.

Use the persistent left sidebar to switch between **Table**, **Columns**, **Data Quality**,
**Review** and **AI Settings**. It shows the contract identity and collapsed Read/Write
Guardrail summaries. **Save draft**, **Discard changes**, **Freeze** and **Exit** are in
the same sidebar, together with action feedback. The main content scrolls independently;
long column and rule lists retain bounded selection controls. Discard and Exit confirm
unsaved changes; Freeze confirms and saves staged changes before freezing the version.

??? info "Inspect a failure from the widget you actually opened"

    Keep `contract_state` from the call above. Inspect `contract_state["_ai_diagnostics"]`
    for failures keyed by contract/version and authoring operation, and `contract_state["ai_usage"]`
    for available measured statistics. Retry the affected action to clear its failure.
    Do not create a second widget to retrieve diagnostics. Raw exception chains can contain
    provider context; review them before sharing. The UI only shows safe failure categories and guidance.

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
| Source | `orders` | Freshness, Schema |
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

For `orders`, enable **Freshness** and **Schema**. Choose **Column-based** evidence, **Full dataset** scope, and `modified_datetime` as the Freshness evidence column and keep the allowed age comfortably above the canonical baseline's normal age. Keep Freshness on **Warn** for the first integration run. Engineering configures optional Source Drift in `setup_pipeline()`, independently of the Contract. Schema blocks missing Required columns and contracted datatype mismatches.

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
* Freshness, when applicable

Use AI suggestions where useful, then review them before applying. Profile statistics are evidence only; they do not become contract requirements unless Governance authors a rule from them.

### Grain enforcement and the orchestration sidebar

**Grain enforcement is one managed Data Quality uniqueness rule.** The description remains table Enrichment; selected key columns and enforcement policy are separate choices. Selecting a profiled key or entering a description does not enable enforcement. **Enforce Grain** defaults to **Block** when enabled; choose **Warn** to record violations and continue. Turn it off to retain the description and keys without runtime validation or required Grain Results.

A composite key is unique as a combination. Any SQL null in any key component fails that row; blank strings are ordinary values. All rows sharing a duplicate combination fail. An empty input passes only with a valid configured key and all configured columns present. Missing columns, duplicate/blank key names, unknown contract columns, and invalid configuration cannot pass; invalid configuration blocks even under Warn. The Data Quality section displays **GRAIN — Uniqueness**, selected columns, Warn/Block policy and enabled status. Edit it only through the Table controls. An active authored uniqueness rule for the same key is rejected as a duplicate.

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

The sidebar groups configured rules under **When this table is read** (`orchestrate_read()`: Freshness, Schema, Data Quality) and **Before this table is written** (`orchestrate_write()`: Schema, Sensitive Data, Data Quality). Pipeline-owned Source Drift observes complete sources during Read and consolidates decisions before any Write. The same Schema, Grain, and DQ configuration applies to both paths; there are no separate Read/Write policies.

Expand a Guardrail to inspect its columns, rules, parameters, and policy, then click a rule to open its existing editor. Use **Table**, **Column**, and **Data Quality** to author or edit settings, including unconfigured Guardrails. Disabled Grain remains visible with its disabled state; its description and key selection remain editable in **Grain & Row Key**. Summaries update as edits are staged, before Save.

**Warn/Block is policy, not an execution result.** The sidebar does not execute validation. `METADATA_GUARDRAIL_RESULTS` records the managed Grain DQ evaluation with `guardrail_type=data_quality`, the exact contract version, continuation decision, counts, and validation scope. Configured Grain checks validate Read rows and prepared Write input independently; their authored Warn or Block action determines continuation. Sensitive Data treatments must succeed before continuation. Profiling supplies observations and suggestions, not Guardrails.


<div class="fabricops-section-banner" markdown="1">
<img src="/FabricOps-Starter-Kit/assets/mascots/robot-writing.png" alt="" loading="lazy">
<div class="fabricops-section-content" markdown="1">

## Data Quality — add rules manually

Open **Data Quality**, use **Add Rule Manually**, and configure these rules for the integration exercise:

The rule inventory at the top shows status, type, columns, Warn/Block policy, and the accepted failure limit. Choose a rule in **Review and Edit** to use the same guided controls for existing or AI-generated rules. Relationship and conditional rules use explicit column roles such as **Left column**, **Right column**, **Condition column**, and **Target column**; advanced JSON is available only as a collapsed inspection option.

For Completeness, Uniqueness, Value set, Range, and Pattern, select several columns to add the same configuration as independent rules in one action. Uniqueness also offers **Columns together** when the selected columns form one composite key. The preview lists every rule that will be added before confirmation.

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

Choose **Save draft** in the sidebar while the version is still a draft. Close and reopen that exact draft to confirm its descriptions, classifications, key selection and configured Guardrails hydrate from the saved payload. Pending sidebar edits are not saved until Save succeeds. When it is ready for Engineering validation, choose **Freeze** and reopen the exact frozen version to review its immutable manifest.

`METADATA_DATA_CONTRACT.contract_payload_json` stores authored Enrichment and Guardrails for an exact version. Grain description and key authoring remain in Table; enabled Grain is evaluated once by DQ. Read runs Freshness, Schema and DQ. Write runs Schema, Sensitive Data and DQ after the independent Source Drift decision. Save replaces the draft payload and Freeze makes the exact version immutable. Evaluations are retained in `METADATA_GUARDRAIL_RESULTS`.

### Processing and source identity

Engineering authors `read_mode`, `read_parameters`, `write_mode`, `write_parameters`, source-to-target associations and `repartition_by` in the pipeline. Pipeline Activation retains the exact configuration and runtime compares it before execution. Changing approved parameters requires a new pipeline submission and approval. Contracts contain no Processing controls or executable processing definition.

Physical tables keep canonical Table IDs. File-backed contracts use a stable `source_id` based on physical workspace, Lakehouse item and case-sensitive relative Files selector. Reader format/options are frozen and reviewed separately; folders and wildcards retain selector identity as membership changes. The shared authoring service accepts an explicit observed file schema. File Contract Activation verifies the configured physical source, frozen payload and Agreement association. Pipeline approval packages can retain exact `file_authorizations`.

The current authoring widget selects registered tables. A file selector in that widget and a file orchestration boundary are separate implementation work. Approved file declarations alone cannot authorize execution: deployment rejects packages with file authorizations until that boundary exists. No artificial Table IDs or file checkpoints are introduced.

### Freshness evidence

Choose an explicit method and age threshold, then select Warn or Block:

| Method | Meaning and scope |
| --- | --- |
| Metadata-based | Full physical dataset only. Supported Lakehouse Delta sources use the latest data-changing history entry, excluding maintenance. Unsupported Warehouse metadata is unavailable. Files use modification timestamps from the resolved selector; folder/wildcard data members expand recursively, exclude hidden control files, and use the oldest member so a new file cannot hide stale members. |
| Column-based | Latest non-null value in the configured timestamp column. Select Full dataset or Incremental batch explicitly. The aggregation scans data and checks invalid values; it is not metadata-only. An empty batch does not prove full-dataset freshness. |

Every evaluated result retains the method, scope, observation time, source identity, threshold, continuation decision and current evidence in `METADATA_GUARDRAIL_RESULTS`. File evidence includes member timestamps and a membership hash. Missing metadata, failed access, no matched files and empty/all-null datasets are unavailable; invalid or future timestamps are invalid. Both follow Warn/Block. Reader options that change membership require an actual reader-resolved file set; until that boundary exists, metadata evidence reports unavailable rather than ignoring those filters. Freshness never switches methods or falls back to historical profiles. File modification time describes storage updates, not business-event time.

No metadata tables are added. Nullable `source_id` fields distinguish file contracts and activations; a file row has no Table ID. Run operation JSON adds typed read/write parameters and repartitioning so approval can compare actual settings. Existing physical Run JSON storage and retained historical content hashes are preserved.


The frozen version is an immutable data contract and becomes the exact candidate Engineering selects in Step 4. Freezing does not activate it for Production.

!!! warning "Breaking workspace architecture"
    Contract definitions are global and immutable when frozen. Physical workspace/Table ID activations select exact versions independently; authoring observations and profile snapshots do not mutate frozen payloads.

**Next:** [Step 4. Preview and enforce the frozen Data Contract](04-validate-frozen-data-contract.md).
