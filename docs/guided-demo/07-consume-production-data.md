# Step 7. Publish governed data to a Fabric Data Agent

**Turn approved Production data and its FabricOps governance context into a native Fabric Data Agent for actual consumption.**

Step 6 already completed the engineering handoff: the Production pipeline ran, the governed outputs exist, and approved consumers can access those tables through native Fabric permissions and interfaces.

Step 7 is therefore not another exploration notebook. Its purpose is to create a consumption product from the governed data.

!!! note "Feature implementation status"

    One-shot Data Agent publishing is the next FabricOps consumption feature and is not yet part of the released public API. This page defines the Guided Demo target while the publisher is implemented.

## Single-table path

For one governed table, FabricOps already has the context needed to ground a useful Data Agent: table purpose, grain/key evidence, column meaning, classification and sensitivity decisions, business rules, Data Quality expectations, profile evidence, lineage, and the active Data Contract.

The target flow is:

```text
Approved Production table
        +
FabricOps governed context
        |
        v
Create/configure Data Agent
        |
        v
Select governed table
        |
        v
Apply generated instructions
        |
        v
Test and consume through the agent
```

The user should not have to manually rewrite FabricOps documentation into Data Agent instructions.

## Multi-table extension

The same flow later expands to multiple governed tables once FabricOps can capture explicit primary-key and foreign-key/reference relationships between them.

FabricOps can provide deterministic relationship evidence and warnings, while a BI/data architect confirms the intended relationship. The confirmed relationships are then rendered into the Data Agent context together with each table's existing governed metadata.

This keeps FabricOps focused on governed data and relationship context rather than creating a separate semantic modelling platform.

## Direct data consumption still exists

A Data Agent is the showcase Step 7 consumption interface, not the only way to use Production data.

Consumers who need direct access can use the native Fabric permissions and interfaces established in Step 6. FabricOps does not require a dedicated `99_explore` notebook for that path.

For the full feature contract and implementation phases, see [Publish Governed Data to a Fabric Data Agent](../maintainer/single-table-data-products.md).

**Complete:** return to the [Guided Demo overview](../guided-demo.md).
