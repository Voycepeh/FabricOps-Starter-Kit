# Step 6: Run Production with the active Data Contract

**Run `02_pipeline` in Engineering Production and let FabricOps resolve the one active Data Contract for each governed table automatically.**

The Production runtime behaviour below is implemented but remains **Preview** in the Guided Demo until the complete promotion-to-run path is revalidated end to end in Fabric.

## High-level flow

```text
Production environment
→ Resolve active Data Contract
→ Resolve frozen Guardrails + processing
→ Prepare source scope
→ Validate source
→ Transform
→ Validate target
→ Governed write
→ Full read-back + profile
```

## Before you begin

Confirm that the governed table has exactly one active Data Contract version, the required `02_pipeline` and Production data are already available in Engineering Production through the organisation's current Fabric process, and the notebook uses the Production `00_env_config`.

??? info "Preview — Resolve the active Data Contract automatically"

    Open `02_pipeline` in Engineering Production and confirm the source, unified, and product targets resolve to the expected Production Fabric items.

    Run the Data Contract selector area. In Production it is read only and shows the active Data Contract version for the table.

    Production never falls back to mutable authoring metadata.

    ```text
    physical Production table
    → canonical Data Catalogue table_id
    → exactly one active Data Contract
    → frozen Guardrails + frozen target processing
    ```

    If no active contract exists, or more than one active version exists for the same table, the governed Production run fails.

??? info "Preview — Prepare and validate the Production source"

    Use `read_pipeline_prep()` so FabricOps resolves the active contract's frozen processing definition and prepares the source scope as `skip`, `full`, or `incremental`.

    Run source Schema, Freshness, and Changes Guardrails before the business-data read. Read the source using the prepared scope and run DQ on the DataFrame being processed.

    Register a source profile only when that DataFrame represents the complete physical source table.

???+ success "Live — Apply the visible transformation"

    Apply the normal project-owned transformation logic. The Production runtime uses the same visible transformation section as Development.

??? info "Preview — Validate and write the Production target"

    Run target Schema and DQ checks before changing the Production target.

    Use `write_pipeline_prep()` and continue with the Production write only when the Guardrail continuation decisions allow it. The same frozen processing definition resolved for the source scope is reused for target-write preparation.

??? info "Preview — Read back and register the complete target"

    Read the persisted target back in full and profile/register the complete persisted target.

    The active contract therefore controls the governed runtime boundary while the physical read, transformation, writer, and persisted target remain visible in `02_pipeline`.

??? note "Planned — Promotion into Engineering Production"

    This demo currently assumes the Production notebook and data are already available through the organisation's current Fabric process.

    The canonical **Promote** stage is planned to use an approved organisational mechanism, which may be Fabric deployment or pipeline approval, Git-based CI/CD, or a controlled manual approval-and-ferry process.

## Expected result

You should understand how the Preview Production runtime resolves one active frozen Data Contract and applies that contract's Guardrails and processing definition around the same canonical ETL lifecycle.

**Previous:** [Step 5: Create and activate the Data Contract](05-create-data-contract.md)  
**Next:** [Step 7: Consume Production data](99-explore-via-notebook.md)

See also: [`widget_select_data_contract()`](../api/reference/widget_select_data_contract.md), [`read_pipeline_prep()`](../api/reference/read_pipeline_prep.md), [`write_pipeline_prep()`](../api/reference/write_pipeline_prep.md), and [METADATA_DATA_CONTRACT](../reference/metadata/metadata_data_contract.md).
