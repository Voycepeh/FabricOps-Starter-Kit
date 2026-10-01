# Governed Consumption and Data Agent Publishing

FabricOps should carry governed Production data across the handoff from Data Engineering into analytics and AI consumption without replacing the native Microsoft Fabric experiences that already serve those consumers.

Step 7 is therefore **governed consumption**, not a Data Agent-specific stage. The planned `03_consumption` notebook is the consumer and analytics-engineering handoff interface. One-shot Fabric Data Agent publishing is the first productized consumption accelerator built on that interface.

## Product decision

The governed Production table and its FabricOps context are reusable assets. A Data Agent is one destination for those assets, not their definition.

The operating boundary is:

```text
01_governance
      |
      v
02_pipeline
      |
      v
Governed Production data
      |
      v
03_consumption
      |
      +--> Direct Fabric consumption
      +--> Fabric Data Agent
      +--> Power BI / reporting context (later)
      +--> future consumption products
```

Consumers do not need FabricOps merely to query data they are permitted to access. Step 6 grants the appropriate native Fabric access. `03_consumption` adds value by presenting governed consumer-facing context and reusable accelerators at the handoff.

The existing `99_explore` notebook is the predecessor of this role. Renaming and revamping the actual template to `03_consumption` is implementation work and should update its directly affected tests and generated references together.

## Consumer handoff

`03_consumption` should let an analyst or analytics engineer select approved Production table(s) and see the context needed to use them safely without understanding the engineering implementation.

Useful context includes:

- table purpose, description, location, and ownership;
- grain and key evidence;
- columns, data types, descriptions, and business terminology;
- approved classification and sensitivity/treatment outcome;
- business rules and Data Quality expectations that affect interpretation;
- useful profile evidence and freshness context;
- lineage/provenance where relevant;
- access information and known usage limitations.

This context is a **projection of existing authoritative metadata**, not a second independently maintained source of truth.

The same context can then be rendered for a specific consumption target. Data Agent instructions are the first implementation target. Power BI, reporting, notebooks, SQL, and future consumers can reuse the same governed foundation without being coupled to the Data Agent implementation.

## V1: one-shot single-table Data Agent

The first consumption accelerator should make one activated Production table immediately useful through a native Fabric Data Agent.

Target experience:

1. Open `03_consumption` and select one activated Production `table_id`.
2. Resolve the approved Production table and its active Data Contract.
3. Build the compact consumer context from existing FabricOps metadata.
4. Check whether an existing registered consumption product already uses the same governed scope.
5. Generate the Data Agent-ready instructions.
6. Create/configure a Fabric Data Agent in the target consumer workspace.
7. Attach the Production Lakehouse or Warehouse datasource and select the governed table.
8. Apply the generated datasource and agent instructions.
9. Leave the agent ready for review, testing, and publication.

A user should not have to manually rewrite the Data Contract or catalogue documentation into agent instructions.

Microsoft Fabric's Data Agent configuration APIs are currently a Preview dependency. Implementation should isolate Fabric-specific publishing calls behind a small integration boundary and document their lifecycle status.

## V2: relationship-aware multi-table consumption

The multi-table path extends the same governed consumption flow.

`03_consumption` should allow an analytics engineer or other qualified owner to select governed tables and explicitly define relationships such as:

```text
Customers.customer_id  <-  Orders.customer_id
referenced key             foreign key
```

FabricOps can provide deterministic evidence and warnings, including datatype compatibility, referenced-key uniqueness, foreign-key nullability, and referential coverage. A human confirms the intended relationship; statistical similarity alone must not silently become governed relationship truth.

The relationship-authoring UI can live in `03_consumption`, while reusable confirmed relationship metadata should be persisted centrally rather than trapped inside the notebook or a Data Agent prompt.

Confirmed relationships then become reusable consumption context:

```text
Governed tables
    + table context
    + confirmed relationships
             |
             v
       03_consumption
             |
      +------+------+
      |             |
      v             v
 Data Agent      other consumers
```

FabricOps does not become a general-purpose dimensional-modelling engine. More complex analytical modelling decisions can still require BI/data-architecture judgement.

## Consumption-product reuse

FabricOps should discourage accidental duplication without assuming that overlapping products are always duplicates.

Before creating a new consumption artifact, `03_consumption` should surface existing registered products that use the same or overlapping governed tables.

For example:

```text
Requested
Customers + Orders + Products

Existing: Sales Analysis
Customers + Orders
2 of 3 tables overlap
```

An exact table set is a strong reuse signal, but it is not sufficient to declare two products equivalent. Purpose, owner, audience, confirmed relationships, and product type can make separate products legitimate.

The user should be able to reuse or extend an existing product, or intentionally create another product with a clear purpose.

This requires a small **Consumption Product registry**, not a Data Agent-specific registry. Its eventual schema is an implementation decision, but conceptually it needs to record:

- product identity, name, purpose, owner, type, and lifecycle status;
- the governed `table_id` values used by the product;
- the confirmed relationship scope where applicable;
- the deployed Fabric artifact identity where applicable.

A canonical scope signature can make exact-set lookup deterministic, but the registry must preserve the underlying table and relationship records so overlap and lineage remain queryable.

A Data Agent is then one deployed artifact of a governed consumption product. Power BI or another future target can reuse the same registry and context model.

## Context package

The context package remains derived from authoritative FabricOps records: the active Data Contract plus relevant Catalogue, profile, lineage, Data Agreement, access, and other governed metadata for the selected tables.

Do not expose secrets, credentials, tokens, unnecessary profile values, or metadata that the downstream consumer does not need.

Keep deterministic context assembly separate from target-specific rendering:

```text
approved table_id(s)
      + confirmed relationships
              |
              v
     consumer context
              |
       +------+------+
       |             |
       v             v
 Data Agent       future target
 instructions
```

## Guided Demo acceptance target

Step 7 should demonstrate the handoff into governed consumption through `03_consumption`.

The first showcase path should prove:

1. select the approved Production demo table;
2. see its consumer-facing FabricOps context;
3. check for existing consumption products;
4. generate the Data Agent context automatically;
5. create/configure the Data Agent;
6. test representative business questions without manually recreating table documentation.

Direct notebook, SQL, Lakehouse, and Warehouse consumption remains available through the native access granted in Step 6.

A later demo should select multiple governed tables, confirm relationships, show overlapping existing consumption products, and publish the combined context into a Data Agent.

## Scope boundary

This feature does not require FabricOps to build a Power BI semantic model, generate dashboards, or own BI measures and visuals. Those are parallel consumption paths.

The reusable asset is the governed Production data plus its consumption context. Data Agent publishing is simply the first automated destination.

## Implementation phases

**Phase 1: consumer context contract.** Implement deterministic consumer-facing context assembly from existing metadata.

**Phase 2: revamp `99_explore` into `03_consumption`.** Make it the consumer/analytics-engineering handoff interface and update directly affected tests and generated references.

**Phase 3: one-shot Data Agent publisher.** Generate instructions and create/configure a single-table Data Agent through the supported Fabric APIs.

**Phase 4: Consumption Product registry and reuse checks.** Record product purpose, ownership, governed table scope, deployed artifacts, and exact/overlapping scope discovery.

**Phase 5: relationship metadata and authoring UI.** Add explicit reusable PK/FK/reference relationships with deterministic validation evidence.

**Phase 6: multi-table Data Agent publishing.** Render confirmed relationships into the same context contract and publish selected related tables into one Data Agent.
