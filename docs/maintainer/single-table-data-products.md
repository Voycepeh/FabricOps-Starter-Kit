# Publish a Single-Table Data Product

FabricOps should make an activated, governed table immediately useful as a Fabric data product without inventing another semantic layer.

This feature defines the first consumption accelerator after the governed Production table exists. It reuses FabricOps metadata as an AI-ready context package, then hands the table to native Microsoft Fabric capabilities.

## Product decision

For a **single governed table**, FabricOps already owns the useful source context: table identity and purpose, schema, column descriptions, grain/key evidence, profile evidence, classification, sensitive-data decisions, business rules, Data Quality expectations, lineage, and the activated Data Contract.

FabricOps therefore should not create its own metric, dimension, relationship, or visualization metadata model.

The downstream source of truth remains the native Fabric artifact:

- a **Fabric Data Agent** owns its AI instructions and datasource configuration;
- a **Power BI semantic model** owns measures and analytical semantics;
- a **Power BI report** owns pages, visuals, filters, slicers, and presentation.

FabricOps provides governed context to accelerate creation of those artifacts.

## V1 scope: one table

The user selects one activated Production `table_id` and one target consumption path.

### Data Agent path

Target experience:

1. Resolve the approved Production table and its active Data Contract.
2. Build a compact FabricOps context package from existing authoritative metadata.
3. Create a Fabric Data Agent in the target consumer workspace.
4. Attach the Lakehouse or Warehouse datasource.
5. Select the governed table rather than exposing unrelated tables from the same item.
6. Apply FabricOps context as datasource instructions and, where useful, agent-level instructions.
7. Leave the created agent ready for review, test, and publication.

The context should explain the table's purpose and grain, important columns, governed terminology, business rules, relevant Data Quality expectations, sensitivity/classification context that is safe for the consumer, and known usage constraints. It must not copy FabricOps metadata into a second independently maintained source of truth.

Microsoft Fabric's Data Agent REST API can create a Data Agent, create staging datasources, select datasource elements, update datasource instructions, and update agent-level AI instructions. Configuration-management endpoints are currently Preview, so implementation must isolate those calls behind a small integration boundary and document that lifecycle status.

### Power BI path

Target experience:

1. Resolve the same governed table and FabricOps context package.
2. Create or select a Power BI semantic model over the governed Production table.
3. Give native Power BI AI authoring the FabricOps context and a bounded authoring request.
4. Ask it to create useful measures, descriptions, formatting, and other single-table model improvements.
5. Build an initial report with useful pages and visuals from that semantic model.
6. Leave the semantic model and report as native Power BI artifacts for a BI owner to review and continue editing.

The first version should prefer **native Power BI authoring capabilities** rather than FabricOps generating DAX, TMDL, PBIR, visual JSON, or a second semantic specification itself.

Fabric exposes REST creation for semantic-model and report items. Natural-language semantic-model authoring is available through the Power BI Authoring MCP server, while the Power BI Report Authoring skill covers report pages, visuals, filters, slicers, formatting, and themes. Where a fully unattended supported API path is not available, FabricOps should generate the exact bounded authoring instruction and hand off to the native authoring experience rather than pretending the operation is automated.

## Context package

The context package is a **projection**, not new governance metadata.

Its authoritative inputs are the active Data Contract and the existing Catalogue, profile, lineage, Data Agreement, and other relevant FabricOps records for the selected `table_id`.

A single-table package should contain only information useful to the downstream consumer, for example:

- table identity, business name, description, and governed purpose;
- grain and key evidence;
- columns, data types, descriptions, and business terminology;
- approved classification and sensitivity/treatment outcome;
- business rules and Data Quality expectations that affect interpretation;
- profile evidence useful for understanding the table;
- source/lineage summary where it helps explain provenance;
- known limitations or governed usage notes;
- the Production Fabric item/table reference required to bind the downstream artifact.

Do not expose secrets, credentials, internal tokens, unnecessary profile values, or metadata that the downstream consumer does not need.

The same package should be renderable into target-specific forms, initially:

- Data Agent datasource instructions;
- Data Agent global instructions when table-level context alone is insufficient;
- Power BI semantic-model authoring context;
- Power BI report-authoring context.

## Proposed public interaction

The user-facing workflow should feel like one publish action even if the implementation uses several Fabric APIs.

Conceptually:

```python
publish_data_product(
    table_id="...",
    target="data_agent",
    workspace="Consumer Development",
)
```

or:

```python
publish_data_product(
    table_id="...",
    target="power_bi",
    workspace="Consumer Development",
)
```

This is a **feature contract**, not yet a commitment to this exact Python signature. Before exposing a public API, implementation work must validate authentication, permissions, supported Fabric item types, idempotency, naming, update behavior, error surfaces, and Preview dependencies in a real Fabric workspace.

A first implementation may separate deterministic context assembly from target adapters internally:

```text
active table_id
    -> build consumer context
    -> Data Agent adapter
       or
    -> Power BI authoring adapter
```

The context builder must remain target-neutral. Target adapters own Fabric-specific payloads and lifecycle behavior.

## Development to Production

Build and validate downstream artifacts in a Development consumer workspace first.

FabricOps should not bind consumer products to Engineering Development outputs. Development artifacts use Development data while being authored and tested; promoted Production artifacts must resolve approved Production data.

Deployment behavior, rebinding rules, supported item types, and Preview limitations must be validated per artifact before FabricOps claims end-to-end promotion support.

The intended lifecycle is:

```text
Engineering Development -> governed table
                         -> consumer product Development
                         -> review
                         -> Fabric deployment
                         -> consumer product Production
                         -> approved Production data
```

## Guided Demo acceptance target

The Guided Demo should eventually prove two outcomes from the same governed single table.

**Data Agent:** select the demo table, create/configure an agent from FabricOps context, then ask representative business questions without manually rewriting the table documentation into the agent.

**Power BI:** select the same table, use the generated context with native Power BI authoring to create useful measures and an initial report page, then review the generated model and visuals.

The demo should clearly distinguish what FabricOps executes from what native Fabric AI authoring executes.

## Out of scope for V1

V1 does not attempt to infer or own a multi-table semantic model.

FabricOps does not automatically decide:

- foreign-key relationships between governed tables;
- relationship cardinality or filter direction;
- active versus inactive role-playing date relationships;
- fact versus dimension design;
- bridge tables or many-to-many modelling;
- cross-table business measures;
- star/snowflake redesign;
- whether an arbitrary set of tables forms a useful analytical model.

These are real data-modelling decisions and should remain reviewable work for a BI/data architect.

## Next phase: multi-table product design

The next useful structural context is an explicit governed reference such as:

```text
Orders.customer_id
    references Customers.customer_id
```

FabricOps can later combine explicit foreign-key/reference metadata with deterministic evidence such as grain, uniqueness, nullability, datatype compatibility, referential coverage, lineage, and table descriptions.

That evidence can help a BI/data architect assess a selected group of tables and can ground Power BI authoring, but FabricOps should not silently convert statistical similarity into a semantic relationship.

A future multi-table workflow should therefore:

1. let an expert select candidate governed tables;
2. show deterministic relationship evidence and modelling warnings;
3. capture or confirm explicit foreign-key/reference intent;
4. produce model-authoring context for Power BI;
5. let native Power BI own the resulting relationships, measures, and semantic model;
6. reuse that semantic model for both reports and Data Agents where appropriate.

This keeps FabricOps focused on governed evidence and context while leaving analytical modelling in the platform built for it.

## Implementation phases

**Phase 1: context contract.** Implement and test deterministic single-table context assembly from existing metadata.

**Phase 2: Data Agent adapter.** Create/configure a single-table Data Agent through supported Fabric REST APIs, with Preview configuration calls clearly isolated.

**Phase 3: Power BI authoring handoff.** Generate bounded semantic-model and report-authoring instructions, validate the Power BI Authoring MCP/report-authoring path in Fabric, and automate only the parts supported by stable programmatic interfaces.

**Phase 4: Guided Demo.** Add the single-table Data Agent and Power BI outcomes to the consumption step.

**Phase 5: multi-table design.** Specify foreign-key/reference metadata and deterministic model-assessment guidance separately after the single-table path is proven.
