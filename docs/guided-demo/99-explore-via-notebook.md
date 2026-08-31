# Step 7: Consume approved Production data with FabricOps IO and profiling

**Use `99_explore` in a Project-Specific Consumer workspace to consume only approved Engineering Production data without changing or duplicating the governed Production pipeline.**

!!! info "Key concepts for this step"

    [**Data Access**](../glossary.md#data-access) — the governed definition of who may access data and under what conditions.  
    [**Workspace**](../glossary.md#workspace) — the Fabric boundary that keeps project-specific exploration separate from Engineering Production.  
    [**Profile**](../glossary.md#profile) — a point-in-time summary you can generate when the project needs to inspect the returned data.

    These concepts are enough to understand the consumer boundary in this step.

## High-level flow

```text
Engineering Production
→ 99_explore in Project-Specific Consumer workspace
→ Read approved Production data
→ Power BI / AI / Data Science / exploration
```

???+ success "Live — Keep the consumer workspace downstream"

    - Read approved data only from Engineering Production.
    - Keep project-specific Power BI, AI, data science, exploration, experiments, models, reports, and notebook outputs in the consumer workspace.
    - Do not use Engineering Development as a downstream consumer source.
    - Do not modify governed Data Agreement, Data Contract, Enrichment, Guardrail, or Production pipeline state.
    - Do not write back into governed Production source, unified, or product stores as part of this walkthrough.
    - Move stable, recurring preparation into the governed `02_pipeline` workflow.

???+ success "Live — Resolve and read approved Production data"

    1. Create or open the Project-Specific Consumer workspace.
    2. Attach the Fabric Environment containing the FabricOps wheel.
    3. Configure the workspace so `99_explore` can resolve the Engineering Production targets.
    4. Open `99_explore`.
    5. Read an approved Production table, file, or query result using the relevant FabricOps IO helper.

    | Helper | What it demonstrates |
    | --- | --- |
    | `read_lakehouse_csv`, `read_lakehouse_excel`, `read_lakehouse_parquet` | Read files from a configured Production Lakehouse target. |
    | `read_lakehouse_table` | Read Delta tables from Engineering Production. |
    | `read_warehouse_table`, `read_warehouse_query` | Read Production Warehouse tables or query results. |

???+ success "Live — Inspect and profile the returned DataFrame"

    Display and inspect the returned Spark DataFrame. Run `profile_dataframe()` when a column-level profile is useful for the project.

    FabricOps IO exists so a consumer notebook can resolve configured Production items without switching its default attachment or hardcoding cross-workspace paths throughout the notebook.

???+ success "Live — Keep consumption project-specific"

    Use the approved Production data for project-specific Power BI reporting, AI and machine learning, data science, exploration, and other downstream analysis. Keep those project outputs within the consumer workspace.

    Route stable or recurring transformation work back into Engineering Development rather than turning `99_explore` into an alternative Production pipeline.

## Expected result

The consumer team can use `99_explore` to consume only approved Engineering Production data through configured FabricOps targets for Power BI, AI, data science, exploration, and other project-level use without changing governed Production state or duplicating the Production pipeline.

**Previous:** [Step 6: Promote and run Production with the active Data Contract](06-promote-to-production.md)  
**Return:** [Guided Demo overview](../guided-demo.md)
