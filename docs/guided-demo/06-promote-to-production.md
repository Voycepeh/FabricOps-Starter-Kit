# Step 6: Run Production with the active Data Contract

**Run `02_pipeline` in Engineering Production and let FabricOps resolve the one active Data Contract for each governed table automatically.**

This step demonstrates the implemented Production validation and processing behaviour. It does not implement the external approval or Development-to-Production promotion workflow.

## Before you begin

Confirm that:

- the governed table has exactly one active Data Contract version
- the required `02_pipeline` and Production data are already available in Engineering Production through your current Fabric process
- the notebook uses the Production `00_env_config`

## What to do

1. Open `02_pipeline` in Engineering Production.
2. Confirm the source, unified, and product targets resolve to the expected Production Fabric items.
3. Run the Data Contract selector area. In Production it is read only and shows the active Data Contract version for the table.
4. Use `read_pipeline_prep()` so FabricOps resolves the active contract's frozen processing definition and prepares the source scope as `skip`, `full`, or `incremental`.
5. Run the source Schema, Freshness, and Changes Guardrails before the business-data read.
6. Read the source using the prepared scope and run source DQ on the DataFrame being processed.
7. Register a source profile only when the DataFrame represents the complete physical source table.
8. Apply the visible transformation logic.
9. Run target Schema and DQ checks before changing the Production target.
10. Use `write_pipeline_prep()` and continue with the Production write only when the Guardrail continuation decisions allow it.
11. Read the persisted target back in full and profile/register the complete persisted target.

## Production rule and processing source

**Production never falls back to mutable authoring metadata.**

For each governed table FabricOps resolves:

```text
physical Production table
→ canonical Data Catalogue table_id
→ exactly one active Data Contract
→ frozen Guardrails + frozen target processing
→ checks + governed read/write preparation
```

If no active Data Contract exists, the governed Production run fails. If more than one active version exists for the same table, FabricOps treats that as a Data Contract integrity error.

!!! important "Production selection is automatic"

    Do not manually choose a draft, superseded, or other historical Data Contract version in Production. Manual contract selection exists only for Development testing.

??? info "Why Production fails closed instead of falling back to current authoring"

    Current Governance authoring may already contain changes intended for a future contract version. Silently falling back to that mutable state would allow Production behaviour to change without activating a new frozen contract.

    FabricOps therefore requires exactly one active contract and fails when that invariant is not satisfied. The failure is intentional: an explicit governance/configuration problem is safer than an implicit change to Production policy.

??? info "Why the same frozen processing definition controls both read and write preparation"

    The active contract freezes not only Guardrails but also the governed target processing definition. FabricOps resolves that definition once when preparing the run and reuses it for target-write preparation.

    This keeps the source scope and target maintenance behaviour aligned under the same approved contract version. Unsupported combinations are rejected rather than being silently translated into a different write strategy.

## Expected result

You should now have a Production run where the same Guardrail functions and processing-preparation functions automatically use the frozen definition from the table's active Data Contract.

!!! note "Approval and promotion are still deferred"

    This demo assumes the Production notebook and data are already available through your current Fabric process. The end-to-end Fabric approval and promotion workflow will be added later when it can be configured and demonstrated in the Fabric GUI.

**Previous:** [Step 5: Create and activate the Data Contract](05-create-data-contract.md)  
**Next:** [Step 7: Consume Production data](99-explore-via-notebook.md)

See also: [`widget_select_data_contract()`](../api/reference/widget_select_data_contract.md), [`read_pipeline_prep()`](../api/reference/read_pipeline_prep.md), [`write_pipeline_prep()`](../api/reference/write_pipeline_prep.md), and [METADATA_DATA_CONTRACT](../reference/metadata/metadata_data_contract.md).
