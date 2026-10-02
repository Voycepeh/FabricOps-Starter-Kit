# Step 7. Consume and productize governed data

**Use the governed consumer handoff to turn approved Production data and its FabricOps context into useful analytics and AI consumption products.**

Step 6 already completed the engineering handoff: the Production pipeline ran, governed outputs exist, and approved consumers can access them through native Fabric permissions and interfaces.

Step 7 adds a consumer and analytics-engineering interface over that foundation.

## Review the governed context

The consumer should be able to select approved Production table(s) and see the useful context FabricOps already captured: purpose, grain/key evidence, column meaning, business rules, Data Quality expectations, sensitivity/classification decisions, lineage, freshness, access information, and known limitations.

This is derived from authoritative FabricOps metadata rather than maintained again in the consumption notebook.

## Create a single-table Data Agent

FabricOps V1 exposes a thin programmatic handoff:

```python
from fabricops_kit import build_consumer_context, create_data_agent

consumer_context = build_consumer_context(table_id=production_table_id)
display(consumer_context)

result = create_data_agent(
    table_id=production_table_id,
    target_workspace_id=consumer_workspace_id,
    display_name="Governed orders",
)
display(result)
```

The context is derived deterministically from the active frozen Data Contract, `METADATA_DATA_CATALOGUE`, Enrichment, Guardrails, and configured Production store. It excludes credentials, tokens, profile samples, and raw sensitive values. The creator then creates a native Data Agent, adds its staging Lakehouse or Warehouse datasource, selects the governed table, and applies separate agent and datasource instructions.

The target flow is:

```text
Approved Production table
        +
FabricOps governed context
        |
        v
99_explore or another consumer notebook
        |
        +--> generate Data Agent context
        |
        +--> create/configure Data Agent
        |
        v
Test and consume
```

!!! note "Feature implementation status"

    The single-table API is Preview. Multi-table agents, relationship authoring, product registration and overlap detection, evaluation, and automatic publication remain deliberately out of scope.

## Prerequisites

- Run on a [Fabric capacity that supports Data Agents](https://learn.microsoft.com/fabric/data-science/data-agent-concept).
- Give the caller access to the governed Production Lakehouse or Warehouse and permission to create and configure items in the target workspace.
- Configure both physical source identifiers through `00_env_config`; the flow does not infer a default Lakehouse.
- Activate one frozen Production Data Contract linked to an exact Data Agreement version.
- Use the current [Fabric Data Agent REST APIs](https://learn.microsoft.com/rest/api/fabric/data-agent/items) for item creation and the documented staging datasource and instruction resources. These APIs may remain Preview; review Microsoft's current limitations before production adoption.

FabricOps acquires the Fabric API token from `notebookutils`; do not paste or persist bearer tokens. Permission failures retain the underlying Fabric HTTP status and response details.

## Multi-table extension

The same handoff later supports multiple governed tables. An analytics engineer selects tables, confirms explicit relationships using deterministic evidence from FabricOps, and reuses those relationships as consumption context.

That context can ground a multi-table Data Agent without turning FabricOps into a general-purpose semantic-modelling engine.

## Other consumption paths

A Data Agent is the first automated consumption accelerator, not the definition of Step 7.

Consumers can continue using notebooks, SQL, Lakehouses, Warehouses, and other native Fabric interfaces through the access established in Step 6. Power BI, reporting, and future consumption products can reuse the same governed context as parallel paths.

The maintainer-facing product direction is recorded in the [FabricOps product definition](../maintainer/product-definition.md).

**Complete:** return to the [Guided Demo overview](../guided-demo.md).
