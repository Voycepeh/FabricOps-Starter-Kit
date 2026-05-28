# Quick Start: From High-Level Definition to Governed Data

FabricOps Starter Kit uses a Fabric-first notebook workflow where each notebook updates framework metadata tables. The metadata-backed data contract is assembled from approved metadata evidence across the workflow—it is not hand-written first.

<figure markdown>
  ![Overview diagram of the four-notebook FabricOps delivery flow and metadata-backed contract assembly](assets/mvp-flow.png){ .full-width }
  <figcaption>Use this as the quick mental model: each notebook stage produces approved evidence that feeds one contract story.</figcaption>
</figure>

```mermaid
flowchart LR
    A[01_agreement_*\nHigh-Level Definition] --> B[02_ex_*\nData Analysis & Profiling]
    B --> C[03_pc_*\nTransform & Enforce]
    C --> D[04_gov_*\nTable/Column Governance]
    A --> E[Metadata-Backed\nAssembled Data Contract]
    B --> E
    C --> E
    D --> E
```

## Before the four notebooks (`00_env_config`)

Start with `00_env_config` to set reusable environment settings (Lakehouse/Warehouse references, schemas, and metadata routing) once, then reuse them across all notebook layers.

## Four-notebook flow (core model)

- **`01_agreement_*` = High-Level Definition**
- **`02_ex_*` = Data Analysis & Profiling**
- **`03_pc_*` = Transform & Enforce**
- **`04_gov_*` = Table/Column Governance**
- **Assembled data contract** = built from all four layers using approved metadata evidence

## What each notebook contributes

### `01_agreement_*` contributes

- agreement/domain metadata
- purpose and scope
- owners and stewards
- usage agreements
- access restrictions
- initial classifications

### `02_ex_*` contributes

- schema and column evidence
- profiling statistics
- quality observations
- patterns and anomalies
- proposed DQ rules
- AI-assisted insights

### `03_pc_*` contributes

- source-to-target processing
- transformation summary
- lineage
- DQ validation and enforcement results
- curated output expectations
- SLA / refresh expectations

### `04_gov_*` contributes

- sensitivity/classification updates
- access and usage policy maintenance
- drift and data quality monitoring
- governance review evidence
- compliance updates

> `03_pc_*` enforces operational rules and expectations. `04_gov_*` monitors outcomes and maintains governance continuously.

## Contract assembly from approved metadata evidence

<figure markdown>
  ![Diagram showing metadata and data contract assembly from notebook evidence and approvals](assets/notebook-datacontract-flow.png){ .full-width }
  <figcaption>Approved metadata is assembled into a data contract artifact, keeping governance and engineering aligned.</figcaption>
</figure>

```mermaid
flowchart TD
    A[Agreement metadata evidence] --> Z[Assembled data contract]
    B[Analysis & profiling evidence] --> Z
    C[Pipeline enforcement evidence] --> Z
    D[Governance monitoring evidence] --> Z
```

## What the assembled data contract contains

- domain and ownership
- data assets
- schema and columns
- DQ rules and expectations
- lineage and sources
- stewards and responsibilities
- classifications and sensitivity
- access and usage
- policies and agreements
- SLA / refresh expectations
- monitoring and drift evidence


## Framework metadata tables

- **Agreement Metadata** — purpose, scope, ownership, stewards, usage agreements, access constraints.
- **Analysis Metadata** — schema evidence, profiling stats, quality observations, anomalies, proposed rules.
- **Lineage & Processing Metadata** — transformations, source-to-target lineage, validation/enforcement outcomes, refresh expectations.
- **Governance Metadata** — classifications, policy updates, monitoring signals, drift findings, governance review evidence.

## Setup and navigation

- [Create Wheel](setup/create-wheel.md)
- [Run in Fabric](setup/run-in-fabric.md)
- [Notebook Structure](notebook-structure.md)
- [Metadata and Contracts](metadata-and-contracts/)
- [Function Reference](reference/index.md)
