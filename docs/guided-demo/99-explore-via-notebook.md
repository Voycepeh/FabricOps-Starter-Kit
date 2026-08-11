# Step 7: Consume approved Production data with FabricOps IO and profiling

**Use `99_explore` in a Project-Specific Consumer workspace to read approved Engineering Production data without changing or duplicating the governed production pipeline.**

This step demonstrates project-level exploration, AI, BI, and profiling using configured FabricOps IO targets.

## Consumer workspace boundaries

- Read approved data from Engineering Production.
- Keep project-specific analysis, experiments, models, reports, and notebook outputs in the consumer workspace.
- Do not modify governed Data Agreement, Data Contract, Enrichment, Guardrail, or Production pipeline state.
- Do not write back into governed Production source, unified, or product stores as part of this walkthrough.
- Move stable, recurring preparation into the governed `02_pipeline` workflow.

## Why FabricOps IO exists

A Fabric notebook can attach one Lakehouse or Warehouse for convenient native access. When data lives in another configured item, FabricOps IO provides a consistent way to resolve the approved target without switching attachments or hardcoding paths throughout the notebook.

| Helper | What it demonstrates |
| --- | --- |
| `read_lakehouse_csv`, `read_lakehouse_excel`, `read_lakehouse_parquet` | Read approved files from a configured Production Lakehouse target. |
| `read_lakehouse_table` | Read approved Delta tables from Engineering Production. |
| `read_warehouse_table`, `read_warehouse_query` | Read approved Warehouse tables or query results. |
| `profile_dataframe` | Profile a Spark DataFrame returned from an approved read. |

## What to do

1. Create or open the Project-Specific Consumer workspace.
2. Attach the Fabric Environment containing the FabricOps wheel.
3. Configure the workspace so `99_explore` can resolve the approved Engineering Production targets.
4. Open `99_explore`.
5. Read an approved Production table, file, or query result using the relevant FabricOps IO helper.
6. Display and inspect the returned Spark DataFrame.
7. Run `profile_dataframe` when a column-level profile is useful.
8. Keep project-specific analysis and outputs within the consumer workspace.
9. Route stable or recurring transformation work back into Engineering Development.

!!! note "Consumer work stays downstream"

    `99_explore` supports analysis and experimentation. It should not become an alternative Production pipeline.

## Expected result

The consumer team can read approved Engineering Production data through configured FabricOps targets, inspect it as a Spark DataFrame, and generate project-level profiles where useful.

The normal outputs are project-specific analysis, experiments, models, reports, profiles, and notebook displays rather than changes to governed Production state.

**Previous:** [Step 6: Promote the validated pipeline to Production](06-promote-to-production.md)  
**Return:** [Guided Demo overview](../guided-demo.md)
