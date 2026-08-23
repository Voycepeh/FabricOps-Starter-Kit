# Step 7: Consume Production data with FabricOps IO and profiling

**Use `99_explore` in a Project-Specific Consumer workspace to read Engineering Production data without changing or duplicating the governed Production pipeline.**

## High-level flow

```text
Consumer workspace → Resolve Production target → Read → Inspect / profile → Analyse downstream
```

???+ success "Live — Keep the consumer workspace downstream"

    - Read data from Engineering Production.
    - Keep project-specific analysis, experiments, models, reports, and notebook outputs in the consumer workspace.
    - Do not modify governed Data Agreement, Data Contract, Enrichment, Guardrail, or Production pipeline state.
    - Do not write back into governed Production source, unified, or product stores as part of this walkthrough.
    - Move stable, recurring preparation into the governed `02_pipeline` workflow.

???+ success "Live — Resolve and read Production data"

    1. Create or open the Project-Specific Consumer workspace.
    2. Attach the Fabric Environment containing the FabricOps wheel.
    3. Configure the workspace so `99_explore` can resolve the Engineering Production targets.
    4. Open `99_explore`.
    5. Read a Production table, file, or query result using the relevant FabricOps IO helper.

    | Helper | What it demonstrates |
    | --- | --- |
    | `read_lakehouse_csv`, `read_lakehouse_excel`, `read_lakehouse_parquet` | Read files from a configured Production Lakehouse target. |
    | `read_lakehouse_table` | Read Delta tables from Engineering Production. |
    | `read_warehouse_table`, `read_warehouse_query` | Read Production Warehouse tables or query results. |

???+ success "Live — Inspect and profile the returned DataFrame"

    Display and inspect the returned Spark DataFrame. Run `profile_dataframe()` when a column-level profile is useful for the project.

    FabricOps IO exists so a consumer notebook can resolve configured Production items without switching its default attachment or hardcoding cross-workspace paths throughout the notebook.

???+ success "Live — Keep analysis project-specific"

    Keep project-specific analysis and outputs within the consumer workspace. Route stable or recurring transformation work back into Engineering Development rather than turning `99_explore` into an alternative Production pipeline.

## Expected result

The consumer team can read Engineering Production data through configured FabricOps targets, inspect it as a Spark DataFrame, and generate project-level profiles where useful without changing governed Production state.

**Previous:** [Step 6: Run Production with the active Data Contract](06-promote-to-production.md)  
**Return:** [Guided Demo overview](../guided-demo.md)
