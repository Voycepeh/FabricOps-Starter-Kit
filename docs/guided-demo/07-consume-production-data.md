# Step 7. Consume and productize governed data

**Use the governed consumer handoff to turn approved Production data and its FabricOps context into useful analytics and AI consumption products.**

Step 6 already completed the engineering handoff: the Production pipeline ran, governed outputs exist, and approved consumers can access them through native Fabric permissions and interfaces.

Step 7 adds a consumer and analytics-engineering interface over that foundation.

## Review the governed context

The consumer should be able to select approved Production table(s) and see the useful context FabricOps already captured: purpose, grain/key evidence, column meaning, business rules, Data Quality expectations, sensitivity/classification decisions, lineage, freshness, access information, and known limitations.

This is derived from authoritative FabricOps metadata rather than maintained again in the consumption notebook.

## Reuse before creating

Before creating another consumption artifact, FabricOps should show existing registered products that use the same or overlapping governed tables.

An exact table set is a strong reuse signal, but purpose, owner, audience, relationships, and product type still matter. The user can reuse or extend an existing product or intentionally create another when its purpose is genuinely different.

## First accelerator: Fabric Data Agent

The first automated Step 7 target is one-shot Data Agent publishing.

For one governed table, FabricOps can generate the Data Agent-ready context and configure the native agent without requiring the user to rewrite the Data Contract and catalogue information manually.

The target flow is:

```text
Approved Production table
        +
FabricOps governed context
        |
        v
03_consumption
        |
        +--> discover existing products
        |
        +--> generate Data Agent context
        |
        +--> create/configure Data Agent
        |
        v
Test and consume
```

!!! note "Feature implementation status"

    One-shot Data Agent publishing and the `99_explore` revamp are planned capabilities and are not yet part of the released public API.

## Multi-table extension

The same handoff later supports multiple governed tables. An analytics engineer selects tables, confirms explicit relationships using deterministic evidence from FabricOps, and reuses those relationships as consumption context.

That context can ground a multi-table Data Agent without turning FabricOps into a general-purpose semantic-modelling engine.

## Other consumption paths

A Data Agent is the first automated consumption accelerator, not the definition of Step 7.

Consumers can continue using notebooks, SQL, Lakehouses, Warehouses, and other native Fabric interfaces through the access established in Step 6. Power BI, reporting, and future consumption products can reuse the same governed context as parallel paths.

The maintainer-facing product direction is recorded in the [FabricOps product definition](../maintainer/product-definition.md).

**Complete:** return to the [Guided Demo overview](../guided-demo.md).
