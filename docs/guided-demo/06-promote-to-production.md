# Step 6: Run Production with the active Data Contract

**Run `02_pipeline` in Engineering Production and let FabricOps resolve the one active Data Contract for each governed table automatically.**

This step demonstrates the implemented Production validation behaviour. It does not implement the external approval or Development-to-Production promotion workflow.

## Before you begin

Confirm that:

- the governed table has exactly one active Data Contract version
- the required `02_pipeline` and Production data are already available in Engineering Production through your current Fabric process
- the notebook uses the Production `00_env_config`

## What to do

1. Open `02_pipeline` in Engineering Production.
2. Confirm the source, unified, and product targets resolve to the expected Production Fabric items.
3. Run the Data Contract selector area. In Production it is read only and shows the active Data Contract version for the table.
4. Run `observe_table()` and the source Guardrails.
5. Run the source DQ checks after the full read.
6. Apply the visible transformation logic.
7. Run target Schema and DQ checks before changing an existing Production target.
8. Continue with the Production write only when the Guardrail continuation decisions allow it.

## Production rule source

**Production never falls back to mutable authoring Guardrails.**

For each governed table FabricOps resolves:

```text
physical Production table
→ canonical Data Catalogue table_id
→ exactly one active Data Contract
→ frozen Guardrails in contract_payload_json
→ check_schema / check_freshness / check_changes / check_dq
```

If no active Data Contract exists, the governed Production check fails. If more than one active version exists for the same table, FabricOps treats that as a Data Contract integrity error.

!!! important "Production selection is automatic"

    Do not manually choose a draft, superseded, or other historical Data Contract version in Production. Manual contract selection exists only for Development testing.

## Expected result

You should now have a Production run where the same Guardrail check functions automatically evaluate the frozen expectations from the table's active Data Contract.

!!! note "Approval and promotion are still deferred"

    This demo assumes the Production notebook and data are already available through your current Fabric process. The end-to-end Fabric approval and promotion workflow will be added later when it can be configured and demonstrated in the Fabric GUI.

**Previous:** [Step 5: Create and activate the Data Contract](05-create-data-contract.md)  
**Next:** [Step 7: Consume Production data](99-explore-via-notebook.md)

See also: [`widget_select_data_contract()`](../api/reference/widget_select_data_contract.md), [ETL Guardrails](../solutions/etl-guardrails.md), and [METADATA_DATA_CONTRACT](../reference/metadata/metadata_data_contract.md).
