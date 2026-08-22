# Step 5: Create and activate the Data Contract

**Use `01_governance` to assemble one versioned Data Contract for one governed table, then manually activate the version that Production is authorised to use.**

## Before you begin

Confirm that:

- the relevant Data Agreement exists
- the table is registered in the Data Catalogue
- Enrichment has been added where needed
- Guardrails and target processing have been authored and re-validated in Engineering Development

## What to do

1. Open `01_governance` in the Governance workspace.
2. Run `00_env_config`.
3. Open `widget_register_data_contract()`.
4. Select the exact Data Agreement version and one governed table.
5. Review the frozen contract preview, including the table structure, Enrichment, Guardrails, target processing definition, Data Stewards, and approved usages.
6. Save the Data Contract. FabricOps appends a new draft version for that table lifecycle.
7. Open `widget_activate_data_contract()` and activate the exact version that Production should use.

## What the Data Contract freezes

**The Data Contract is a self-contained snapshot of the governed definition at the time that version is created.**

It includes the selected:

- Data Agreement version
- Data Stewards
- governed `table_id` and table structure
- Enrichment
- active Guardrails and their exact `guardrail_version`
- target `load_strategy` and its governed parameters
- approved usages

Guardrail Results and row-level failure evidence remain runtime evidence and are not frozen into the contract.

!!! important "One table per Data Contract lifecycle"

    Each Data Contract governs one canonical `table_id`. Multiple historical versions may exist, but Production must resolve exactly one active version for that table.

??? info "Why FabricOps freezes a version instead of reading mutable Governance metadata in Production"

    Governance authoring changes over time. Production needs a stable definition of the expectations and processing behaviour it is authorised to enforce.

    FabricOps therefore keeps mutable authoring metadata available for Development, then freezes the selected governed state into a versioned contract payload:

    ```text
    Data Agreement
    + Data Stewards
    + Data Catalogue structure
    + Enrichment
    + Guardrails
    + target processing
    + approved usages
            ↓
    versioned Data Contract
    ```

    Runtime Guardrail Results remain outside the snapshot because they are evidence about individual executions, not part of the governed definition itself.

??? info "Why activation is separate from notebook promotion"

    Activating a Data Contract tells FabricOps which frozen version Production is authorised to resolve for that table. It does not copy notebooks, move data, or implement the external Fabric deployment/approval process.

    Keeping those concerns separate lets FabricOps enforce the runtime contract without pretending that it owns a Fabric GUI promotion workflow that has not yet been configured and demonstrated end to end.

## Optional Development test

After the contract exists, return to `02_pipeline` in Engineering Development and use `widget_select_data_contract()` for the same table.

- **Current authoring** keeps using mutable Governance Guardrails plus the Development-authored target processing definition.
- **Data Contract vN** makes the same checks and processing preparation use the frozen Guardrails and processing definition from that exact contract version.

This selection is read only. It does not approve, activate, or change the Data Contract.

## Expected result

You should now have:

- a versioned Data Contract for one governed table
- a frozen `contract_payload_json` containing the governed definition and target processing
- exactly one manually activated Data Contract version for Production use
- an optional way to test an exact frozen version in Engineering Development

!!! note "Approval and promotion are not part of this step"

    FabricOps currently provides manual Data Contract activation. The external approval and Development-to-Production promotion workflow is deferred until we are ready to configure and demonstrate the Fabric GUI flow end to end.

**Previous:** [Step 4: Rerun the Development pipeline with Guardrails](04-run-pipeline-with-guardrails.md)  
**Next:** [Step 6: Run Production with the active Data Contract](06-promote-to-production.md)

See also: [`widget_register_data_contract()`](../api/reference/widget_register_data_contract.md), [`widget_activate_data_contract()`](../api/reference/widget_activate_data_contract.md), and [METADATA_DATA_CONTRACT](../reference/metadata/metadata_data_contract.md).
