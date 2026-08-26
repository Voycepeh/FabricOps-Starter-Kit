# Step 5: Create and activate the Data Contract

**Use `01_governance` to assemble one versioned Data Contract for one governed table, then use the current interim activation mechanism to choose the version Production is authorised to resolve.**

!!! info "Key concepts for this step"

    [**Data Agreement**](../glossary.md#data-agreement) — the governed relationship and intent established before Engineering begins.  
    [**Data Contract**](../glossary.md#data-contract) — the approved Production-facing definition frozen for one governed table.  
    [**Guardrails**](../glossary.md#guardrails) — the governed rules included in the contract definition.  
    [**Governance as Code**](../glossary.md#governance-as-code) — the broader idea behind freezing governed rules and expectations into structured, reviewable form.

    These concepts explain what is being frozen and why Production should resolve a saved version rather than mutable authoring.

## High-level flow

```text
Review governed metadata → Freeze Data Contract version → Activate Production version → Optional frozen Development test
```

## Before you begin

Confirm that the relevant Data Agreement exists, the table is registered in the Data Catalogue, Enrichment has been added where needed, and Guardrails plus target processing have been authored and re-validated in Engineering Development.

???+ success "Live — Create a versioned Data Contract"

    1. Open `01_governance` in the Governance workspace.
    2. Run `00_env_config`.
    3. Open `widget_register_data_contract()`.
    4. Select the exact Data Agreement version and one governed table.
    5. Review the frozen contract preview, including table structure, Enrichment, Guardrails, target processing definition, Data Stewards, and governed usages.
    6. Save the Data Contract. FabricOps appends a new draft version for that table lifecycle.

    The Data Contract freezes the selected Data Agreement version, Data Stewards, one governed `table_id` and structure, Enrichment, Guardrails and exact versions, target load strategy and parameters, and governed usages.

    Guardrail Results and row-level failure records remain runtime records and are not frozen into the contract.

???+ success "Live — Understand the one-table contract boundary"

    Each Data Contract lifecycle governs one canonical `table_id`. Multiple historical versions may exist for that table.

    ```text
    Data Agreement
    + Data Stewards
    + Data Catalogue structure
    + Enrichment
    + Guardrails
    + target processing
    + governed usages
            ↓
    versioned Data Contract
    ```

    Production uses a frozen contract definition rather than mutable Governance authoring.

??? info "Preview — Manually activate the Production Data Contract"

    Open `widget_activate_data_contract()` and activate the exact saved version that Production should use.

    Manual activation is the current interim lifecycle mechanism. It selects the frozen version FabricOps Production runtime should resolve, but it does not copy notebooks, move data, or implement the external approval/promotion workflow.

??? info "Preview — Test one frozen version in Development"

    After the contract exists, return to `02_pipeline` in Engineering Development and use `widget_select_data_contract()` for the same table.

    - **Current authoring** uses mutable Governance Guardrails plus the Development-authored target processing definition.
    - **Data Contract vN** makes the same checks and processing preparation use the frozen Guardrails and processing definition from that exact contract version.

    The selector is read only. It does not activate or change the Data Contract.

??? note "Planned — Approval and promotion"

    FabricOps currently separates contract activation from promotion. The standardised promotion mechanism is planned and may use Fabric deployment or pipeline approval, Git-based CI/CD, or a controlled manual approval-and-ferry process.

## Expected result

You should now understand the Live Data Contract creation flow plus the Preview interim activation and frozen Development-test paths. A saved contract version contains a self-contained governed definition for one table, while Production activation and promotion remain separate lifecycle concerns.

**Previous:** [Step 4: Rerun the Development pipeline with Guardrails](04-run-pipeline-with-guardrails.md)  
**Next:** [Step 6: Run Production with the active Data Contract](06-promote-to-production.md)

See also: [`widget_register_data_contract()`](../api/reference/widget_register_data_contract.md), [`widget_activate_data_contract()`](../api/reference/widget_activate_data_contract.md), and [METADATA_DATA_CONTRACT](../reference/metadata/metadata_data_contract.md).
