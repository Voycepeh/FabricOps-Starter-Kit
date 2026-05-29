# Metadata and contracts

This page explains how approved notebook evidence becomes a contract-ready handover artifact.
Use this when you need to understand contract contents, metadata ownership, and where enforcement happens.
Next read: [Quality](../data-quality-rules-system.md), [Notebooks](../notebook-structure.md), [Deploy](../deployment-and-promotion.md).

The data contract is an assembled handover artifact. It is built from approved evidence across agreement, exploration, pipeline contract, and governance notebooks. It is not a standalone YAML file and it is not owned by one notebook; each notebook family contributes evidence that becomes part of the governed contract record.

<figure markdown>
  ![Notebook workflow showing agreement, exploration, pipeline contract, and governance evidence assembled into a FabricOps data contract](../assets/notebook-datacontract-flow.png){ .full-width }
  <figcaption>FabricOps data contracts are assembled from approved evidence across the notebook workflow.</figcaption>
</figure>

## Where the contract comes from

| Notebook family | Role | Evidence contributed | Contract action |
| --- | --- | --- | --- |
| `01_agreement_*` | Capture governance intent and approved scope before delivery work starts. | Agreement terms, domain ownership, data steward curation, usage intent, access boundaries, and handover expectations. | Defines |
| `02_ex_*` | Discover what the data actually contains and prepare contract-ready suggestions for review. | Exploration results, profiling summaries, schema and column evidence, lineage notes, AI-assisted suggestions, and data quality observations. | Discovers |
| `03_pc_*` | Turn approved evidence into operational pipeline behavior. | Pipeline contracts, validation results, DQ checks, write expectations, run evidence, and enforcement outcomes. | Enforces |
| `04_gov_*` | Keep governance evidence current after the contract is operational. | Governance metadata, drift monitoring, classifications, sensitivity labels, compliance review evidence, and approval history. | Monitors |

## What the assembled contract contains

The assembled contract combines approved evidence into a practical handover view that describes:

- **Domain & ownership**: business domain, owning team, accountable owner, and stewardship context.
- **Data assets**: tables, files, lakehouse objects, or other governed assets in scope.
- **Schema & columns**: approved fields, types, required columns, descriptions, and expected structure.
- **DQ rules & expectations**: quality checks, thresholds, acceptable values, and review status.
- **Lineage & sources**: upstream inputs, transformations, downstream consumers, and traceability notes.
- **Stewards & responsibilities**: who approves, maintains, operates, and reviews the contract evidence.
- **Classifications & sensitivity**: classification labels, sensitivity context, and handling requirements.
- **Access & usage**: intended use, access boundaries, sharing expectations, and consumer obligations.
- **Policies & agreements**: agreement terms, governance decisions, policy links, and approval evidence.
- **SLA / refresh expectations**: refresh cadence, timeliness expectations, operational commitments, and drift response.

YAML can be exported as an optional machine-readable representation of this assembled evidence. The governed contract remains the approved evidence set, not the YAML file by itself.

## Standards alignment

FabricOps is designed to align with open metadata and data contract patterns without requiring a separate metadata platform.

The assembled contract model is conceptually aligned with [OpenMetadata](https://github.com/open-metadata/OpenMetadata) because it connects ownership, schema, lineage, quality, classifications, policies, and operational context into a governed metadata record.

It is also compatible in concept with the [Open Data Contract Standard (ODCS)](https://bitol-io.github.io/open-data-contract-standard/v3.1.0/). ODCS defines a YAML representation for a data contract, including fundamentals, schema, data quality, roles, SLA, infrastructure, and custom properties. FabricOps can export an ODCS-style YAML contract, but the governed source of truth remains the approved metadata evidence captured in FabricOps notebooks and metadata tables.

This means FabricOps should be treated as ODCS-compatible in concept, not fully ODCS-compliant in output, until an ODCS export is generated and validated against the expected field names and structure.

## Enforcement model

- `01_agreement_*` defines governance intent, accountability, and approved scope.
- `02_ex_*` discovers evidence and generates AI-assisted suggestions for steward review.
- `03_pc_*` is where executable enforcement happens through validation, DQ checks, write expectations, and pipeline logic.
- `04_gov_*` monitors whether the contract remains valid over time through drift checks, classifications, compliance reviews, and approval updates.

Policy enforcement in `03_pc_*` consumes approved metadata routed through the configured `metadata` target from `00_env_config`, so metadata reads and writes do not depend on an attached/default lakehouse.
