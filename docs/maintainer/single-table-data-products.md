# Publish Governed Data to a Fabric Data Agent

FabricOps should make an activated, governed table immediately useful as a Fabric data product without inventing another semantic layer.

This feature defines the first consumption accelerator after governed Production data exists. It reuses FabricOps metadata as an AI-ready context package and publishes selected governed tables into a native Fabric Data Agent. The single-table path is the first implementation; explicit cross-table relationships extend the same contract to multi-table agents.

## Product decision

The first-class Step 7 consumption interface is a **Fabric Data Agent**.

FabricOps should not introduce a Power BI semantic layer or report-generation dependency into this feature. Power BI consumption can evolve independently.

For one governed table, FabricOps already owns the useful context: table identity and purpose, schema, column descriptions, grain/key evidence, profile evidence, classification, sensitive-data decisions, business rules, Data Quality expectations, lineage, and the activated Data Contract.

For multiple governed tables, the important additional context is explicit relationship intent: which column is a primary or referenced key, which column is a foreign key, and which governed table/column it references. FabricOps should capture that relationship as governed context rather than infer a semantic model.

The downstream source of truth for the consumption experience remains the native Fabric Data Agent. FabricOps assembles and publishes the context needed for the agent to query the governed data accurately.

## V1: one-shot single-table Data Agent

Target experience:

1. Select one activated Production `table_id`.
2. Resolve the approved Production table and its active Data Contract.
3. Build a compact FabricOps context package from existing authoritative metadata.
4. Create a Fabric Data Agent in the target consumer workspace.
5. Attach the Production Lakehouse or Warehouse datasource.
6. Select the governed table rather than exposing unrelated tables from the same item.
7. Apply FabricOps context as datasource instructions and, where useful, agent-level instructions.
8. Leave the created agent ready for review, test, and publication.

The context should explain the table's purpose and grain, important columns, governed terminology, business rules, relevant Data Quality expectations, sensitivity/classification context that is safe for the consumer, and known usage constraints. It must not copy FabricOps metadata into a second independently maintained source of truth.

Microsoft Fabric's Data Agent REST API can create a Data Agent, create staging datasources, select datasource elements, update datasource instructions, and update agent-level AI instructions. Configuration-management endpoints are currently Preview, so implementation must isolate those calls behind a small integration boundary and document that lifecycle status.

## V2: relationship-aware multi-table Data Agent

The multi-table path extends the same publishing flow rather than introducing a separate semantic product.

A Governance/Engineering UI should allow an expert to select governed tables and explicitly define relationships such as:

```text
Customers.customer_id  <-  Orders.customer_id
primary/reference key      foreign key
```

The relationship definition should identify at minimum:

- source/foreign-key `table_id` and column;
- referenced `table_id` and column;
- key role or relationship role needed to render the context unambiguously;
- validation evidence such as datatype compatibility, referenced-key uniqueness, foreign-key nullability, and referential coverage.

FabricOps can pre-compute deterministic evidence and warnings, but an expert confirms the relationship. Statistical similarity alone must never silently become a governed relationship.

Once confirmed, the publisher renders those relationships into the Data Agent datasource instructions together with the existing table and column context. Microsoft explicitly supports datasource instructions containing table descriptions, relationships, key-column details, business terminology, and query guidance, so this is the natural native destination for FabricOps relationship context.

The intended flow becomes:

```text
Governed tables
    + table context
    + confirmed PK/FK relationships
            |
            v
    FabricOps context builder
            |
            v
    Data Agent instructions
            |
            v
    one-shot create/configure
            |
            v
    Fabric Data Agent
            |
            v
       Step 7 consumption
```

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
publish_data_agent(
    table_ids=["..."],
    workspace="Consumer Development",
)
```

For the first implementation, `table_ids` contains one activated table. The same contract can later accept multiple tables once explicit relationship context is available.

This is a **feature contract**, not yet a commitment to this exact Python signature. Before exposing a public API, implementation work must validate authentication, permissions, idempotency, naming, update behavior, error surfaces, publication behavior, and Preview dependencies in a real Fabric workspace.

Internally, keep deterministic context assembly separate from the Fabric adapter:

```text
active table_id(s)
    -> build Data Agent context
    -> create/configure Data Agent
```

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

Step 7 should become an actual consumption outcome rather than stopping at `99_explore`.

The first demo should prove the single-table path end to end:

1. select the approved Production demo table;
2. build its FabricOps context automatically;
3. create and configure a Fabric Data Agent programmatically;
4. select only the governed table;
5. inject the generated instructions;
6. publish/test the agent;
7. ask representative business questions without manually rewriting table documentation.

`99_explore` can remain as a direct technical consumption option, but the Data Agent becomes the showcase consumption interface.

A later Guided Demo extension should select multiple governed tables, confirm PK/FK relationships in the relationship-authoring UI, publish the combined context to a Data Agent, and demonstrate questions that require joins.

## Scope boundary

This feature does **not** require FabricOps to build a Power BI semantic model, generate a dashboard, or own BI measures and visuals. Those can be explored as a parallel consumption track.

For multi-table Data Agents, FabricOps owns governed relationship context and deterministic validation evidence. It does not attempt to become a general-purpose dimensional-modelling engine. More complex analytical modelling decisions can still require a BI/data architect.

## Implementation phases

**Phase 1: single-table context contract.** Implement and test deterministic Data Agent context assembly from existing metadata.

**Phase 2: one-shot Data Agent publisher.** Create/configure a single-table Data Agent through supported Fabric REST APIs, with Preview configuration calls clearly isolated.

**Phase 3: Step 7 Guided Demo.** Make the Data Agent the showcase consumption outcome and retain `99_explore` as a technical direct-data option.

**Phase 4: relationship metadata and UI.** Add explicit PK/FK/reference authoring between governed tables with deterministic validation evidence.

**Phase 5: multi-table Data Agent publishing.** Render confirmed relationships into the same context contract and publish selected related tables into one Data Agent.

