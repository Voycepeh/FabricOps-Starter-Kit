# Step 5: Create and activate the Data Contract

**Use `01_governance` to freeze one immutable Data Contract version for one governed table, optionally test that frozen version in Development, then activate the exact version Production is authorised to resolve.**

!!! info "Key concepts for this step"

    **Data Agreement**, **Data Contract**, **Guardrails**, and **Governance as Code** explain what is being frozen and why Production should resolve a saved version rather than mutable authoring.

    A Data Agreement records the provider-to-recipient Data Steward relationship. A Data Contract is table-centric: one contract lifecycle is tied to one governed `table_id` under one exact Data Agreement version. Hover over a glossary term for its canonical definition, or open the [Glossary](../glossary.md) for the full entry.

## Freeze, test, activate, then run

Freezing a Data Contract and promoting a notebook are separate lifecycle concerns. A frozen contract version can be selected and tested by `02_pipeline` in Engineering Development without being active. Activation only selects which frozen version Engineering Production is authorised to resolve.

```mermaid
flowchart LR
    AUTHOR["Mutable Development<br/>Governance authoring"] --> FREEZE["Create Data Contract vN<br/>Frozen + immutable"]

    FREEZE --> TEST["Development 02_pipeline<br/>select and test vN"]
    FREEZE --> ACTIVATE["Activate vN"]

    ACTIVATE --> PROD["Engineering Production<br/>02_pipeline"]
    PROD --> RESOLVE["Resolve exactly one<br/>active Data Contract"]
    RESOLVE --> RUN["Frozen Guardrails<br/>+ frozen target load strategy"]
```

**Freeze** creates an immutable Data Contract version. **Activate** selects one frozen version as the version Production may resolve. **Promote** moves the approved notebook/runtime artefact into Engineering Production using the organisation's deployment process; FabricOps does not currently perform that deployment step.

## Before you begin

Confirm that the relevant Data Agreement exists, the table is registered in the Data Catalogue, Enrichment has been added where needed, and Guardrails plus target load strategy and parameters have been authored and re-validated in Engineering Development.

???+ success "Live — Create a versioned Data Contract"

    1. Open `01_governance` in the Governance workspace.
    2. Run `00_env_config`.
    3. Open `widget_register_data_contract()`.
    4. Select the exact Data Agreement version and one governed table.
    5. Review the frozen contract preview, including table structure, Enrichment, Guardrails, target load strategy and parameters, Data Stewards, and governed usages.
    6. Save the Data Contract. FabricOps appends a new draft version for that table lifecycle.

### What a Data Contract freezes

`widget_register_data_contract()` assembles the contract from the current `METADATA_DATA_AGREEMENT`, `METADATA_DATA_STEWARD`, `METADATA_DATA_CATALOGUE`, `METADATA_ENRICHMENT`, and active `METADATA_GUARDRAIL` records for the selected table.

| Frozen item | What is captured |
| --- | --- |
| Exact Data Agreement version | Agreement identity and version plus its name, domain, business purpose, validity dates, provider and recipient Steward IDs, and approved usages. |
| Provider and recipient Data Stewards | The selected Stewards' IDs, names, roles, and contacts. |
| Governed `table_id` and physical identity | The canonical `table_id` plus environment, store type, layer, schema, and table name from `METADATA_DATA_CATALOGUE`. |
| Table structure / schema | The active Catalogue columns with their `column_id`, column name, and data type. |
| Enrichment | Current table- and column-level `METADATA_ENRICHMENT` values, including enrichment level, type, and value. |
| Active Guardrails | Active `METADATA_GUARDRAIL` rules, including the exact Guardrail version, type, rule identity, severity, and rule parameters. |
| Target load strategy | The Catalogue `load_strategy`, such as `overwrite`, `append`, `scd1`, or `scd2`, when configured. |
| Load-strategy parameters | The configured `load_strategy_parameters_json` values required by the selected target strategy. |
| Governed usages | The selected approved-usage subset, which must remain within the parent Data Agreement's approved usages. |

Runtime records are not part of the frozen definition. `METADATA_GUARDRAIL_RESULTS`, `METADATA_GUARDRAIL_ROW_RESULTS`, source observations, successful-processing checkpoints, and run/audit state continue to describe individual executions rather than the immutable contract.

???+ success "Live — Understand the one-table contract boundary"

    Each Data Contract lifecycle governs one canonical `table_id`. Multiple historical versions may exist for that table, and one Data Agreement can support multiple table-level Data Contracts.

    Saving a new version does not mutate historical versions. The saved contract contains the exact governed definition shown above for that point in the lifecycle.

??? info "Preview — Test one frozen version in Development"

    After the contract exists, return to `02_pipeline` in Engineering Development and use `widget_select_data_contract()` for the same table.

    **Current authoring** uses mutable Governance Guardrails plus the Development-authored target load strategy and parameters.

    **Data Contract vN** makes the same checks and target-write preparation use the frozen Guardrails, target load strategy, and load-strategy parameters from that exact contract version.

    The selector is read only. It does not activate or change the Data Contract.

??? info "Preview — Manually activate the Production Data Contract"

    Open `widget_activate_data_contract()` and activate the exact saved version that Production should use.

    Manual activation is the current interim lifecycle mechanism. It selects the frozen version FabricOps Production runtime should resolve, but it does not copy notebooks, move data, or implement the external approval/promotion workflow.

??? note "Planned — Notebook/runtime promotion"

    FabricOps currently separates Data Contract freezing and activation from promotion into Engineering Production. The standardised promotion mechanism is planned and may use Fabric deployment or pipeline approval, Git-based CI/CD, or a controlled manual approval-and-ferry process.

## Expected result

You should now understand the Live Data Contract freeze flow plus the Preview frozen Development-test and activation paths. A saved contract version is immutable and can be tested in Development without being active; activation designates the frozen version Production is authorised to resolve, while notebook/runtime promotion remains a separate lifecycle concern.

**Previous:** [Step 4: Rerun the Development pipeline with Guardrails](04-run-pipeline-with-guardrails.md)  
**Next:** [Step 6: Run Production with the active Data Contract](06-promote-to-production.md)

See also: [`widget_register_data_contract()`](../api/reference/widget_register_data_contract.md), [`widget_activate_data_contract()`](../api/reference/widget_activate_data_contract.md), and [METADATA_DATA_CONTRACT](../reference/metadata/metadata_data_contract.md).
