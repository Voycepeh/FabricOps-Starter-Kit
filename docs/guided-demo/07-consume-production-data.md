# Step 7. Consume and productize governed data

### Before you begin

- Run on a [Fabric capacity that supports Data Agents](https://learn.microsoft.com/fabric/data-science/data-agent-concept).
- Give the caller access to the governed Production Lakehouse or Warehouse and permission to create and configure items in the target workspace.
- Configure both physical source identifiers through `00_env_config`; the flow does not infer a default Lakehouse.
- Activate one frozen Production Data Contract linked to an exact Data Agreement version.
- Use the current [Fabric Data Agent REST APIs](https://learn.microsoft.com/rest/api/fabric/data-agent/items) for item creation and the documented staging datasource and instruction resources. These APIs may remain Preview; review Microsoft's current limitations before production adoption.

FabricOps acquires the Fabric API token from `notebookutils`; do not paste or persist bearer tokens. Permission failures retain the underlying Fabric HTTP status and response details.


<div class="fabricops-section-banner" markdown="1">
<img src="/FabricOps-Starter-Kit/assets/mascots/robot-pointing.png" alt="" loading="lazy">
<div class="fabricops-section-content" markdown="1">

## Review the governed context

Review the approved Production table and its governance context before creating a Data Agent.

</div>
</div>


The consumer should be able to select approved Production table(s) and see the useful context FabricOps already captured: purpose, grain/key evidence, column meaning, business rules, Data Quality expectations, sensitivity/classification decisions, lineage, freshness, access information, and known limitations.



This is derived from authoritative FabricOps metadata rather than maintained again in the consumption notebook.

<div class="fabricops-section-banner" markdown="1">
<img src="/FabricOps-Starter-Kit/assets/mascots/robot-pointing.png" alt="" loading="lazy">
<div class="fabricops-section-content" markdown="1">

## Create a single-table Data Agent

FabricOps V1 exposes a thin programmatic handoff:

</div>
</div>



```python
from fabricops_kit import create_data_agent

result = create_data_agent(
    table_id=production_table_id,
    target_workspace_id=consumer_workspace_id,
    display_name="Governed orders",
)
display(result)
```

[`create_data_agent()`](../api/reference/create_data_agent.md) internally derives governed context from the active [Activated Pipeline](../reference/metadata/metadata_activation_state.md) manifest and its exact frozen [Data Contract](../reference/metadata/metadata_data_contract.md), [`METADATA_DATA_CATALOGUE`](../reference/metadata/metadata_data_catalogue.md), Enrichment, Guardrails, and configured Production store. It excludes credentials, tokens, profile samples, and raw sensitive values. The function converts that context into instructions, creates a native Data Agent, adds its staging Lakehouse or Warehouse datasource, selects the governed table, and applies separate agent and datasource instructions.

The target flow is:

```text
Approved Production table
        +
FabricOps governed context
        |
        v
Native Fabric interface or project-specific consumer notebook
        |
        +--> create_data_agent()
                |
                +--> build governed context
                +--> render instructions
                +--> create/configure Data Agent
        |
        v
Test and consume
```

!!! note "Feature implementation status"

    The single-table API is Preview. Multi-table agents, relationship authoring, product registration and overlap detection, evaluation, and automatic publication remain deliberately out of scope.

### Multi-table extension

The same handoff later supports multiple governed tables. An analytics engineer selects tables, confirms explicit relationships using deterministic evidence from FabricOps, and reuses those relationships as consumption context.

That context can ground a multi-table Data Agent without turning FabricOps into a general-purpose semantic-modelling engine.

### Other consumption paths

A Data Agent is the first automated consumption accelerator, not the definition of Step 7.

Consumers can continue using notebooks, SQL, Lakehouses, Warehouses, and other native Fabric interfaces through the access established in Step 6. Power BI, reporting, and future consumption products can reuse the same governed context as parallel paths.

The maintainer-facing product direction is recorded in the [FabricOps product definition](../maintainer/product-definition.md).

### Expected result

Approved Production data can be consumed through the documented Fabric interfaces, with FabricOps governance context available for downstream use.

**Complete:** return to the [Guided Demo overview](../guided-demo.md).
