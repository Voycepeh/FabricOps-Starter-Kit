# Step 7: Consume approved Production data with FabricOps IO and profiling

Run `99_explore` in a Project-Specific Consumer workspace after approved outputs are available from Engineering Production.

This step demonstrates how a consumer team can use FabricOps IO helpers to read approved Lakehouse or Warehouse data through configured targets, inspect the resulting Spark dataframes, and use `profile_dataframe` for project-level exploration, AI, or BI work without modifying or duplicating the governed production pipeline.

## Consumer workspace boundaries

- Read approved data from Engineering Production.
- Keep project-specific analysis, experiments, models, reports, and notebook outputs in the consumer workspace.
- Do not modify governed agreement, contract, enrichment, guardrail, or production pipeline state.
- Do not write back into governed Production source, unified, or product stores as part of this walkthrough.
- Move any preparation that must become stable, recurring, or operational into the governed `02_pipeline` workflow.

## Why FabricOps IO exists

Fabric notebooks can attach one Lakehouse or Warehouse, making it convenient to select tables or files through the native UI. A notebook that needs data from another item, however, should not depend on switching attachments, hardcoded paths, or broad item-level access.

FabricOps standardizes this access pattern. Its IO helpers resolve the configured Lakehouse or Warehouse target established through `00_env_config`, so consumers can read through approved targets with consistent function calls even when the target is not the item attached to the notebook.

## Key functions that support this notebook flow

| Helper | What it demonstrates |
| --- | --- |
| `read_lakehouse_csv`, `read_lakehouse_excel`, `read_lakehouse_parquet` | Read approved files from a configured Production Lakehouse target when file access is part of the approved interface. |
| `read_lakehouse_table` | Read approved Delta tables from a configured Engineering Production Lakehouse target. |
| `read_warehouse_table`, `read_warehouse_query` | Read approved tables or query results from a configured Engineering Production Warehouse target. |
| `profile_dataframe` | Profile a Spark dataframe returned from an approved Lakehouse or Warehouse read. |

## What to do

1. Create or open the Project-Specific Consumer workspace for the relevant project, analytical product, AI use case, or BI use case.
2. Attach the Fabric Environment containing the FabricOps wheel.
3. Configure the consumer workspace so `99_explore` can resolve the approved Engineering Production Lakehouse or Warehouse targets.
4. Open `99_explore`.
5. Read an approved Production table, file, or query result using the relevant FabricOps IO helper.
6. Display and inspect the returned Spark dataframe.
7. Run `profile_dataframe` when a column-level profile is useful for the project.
8. Keep all project-specific analysis and outputs within the consumer workspace.
9. Route any transformation that must become stable or recurring back into the governed Engineering Development workflow.

## Expected outcome

The consumer team can read approved Engineering Production data through configured FabricOps targets, inspect it as a Spark dataframe, and generate a project-level profile where needed.

The walkthrough does not create or update governed agreement, contract, enrichment, guardrail, lineage, or production pipeline state. Its normal outputs are project-specific analysis, experiments, models, reports, profiles, and notebook displays.

Previous: [Step 6: Promote the validated pipeline to Production](06-promote-to-production.md).

Supporting guide: [Understand FabricOps widgets and metadata outputs](99-explore-via-notebook.md).

Return to the [Guided Demo overview](../guided-demo.md).
