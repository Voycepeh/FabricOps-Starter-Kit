# Workflow lifecycle operating model

FabricOps Starter Kit runs as a governed notebook lifecycle in Microsoft Fabric:

`agreement → exploration → approved metadata → pipeline contract → handover`

## Lifecycle sequence

```mermaid
flowchart TD
    A[01_da Agreement] --> B[02_ex Exploration and profiling]
    B --> C[Approved metadata and DQ evidence]
    C --> D[03_pc Pipeline contract execution]
    D --> E[04_gov Governance handover evidence]
```

## Notebook mapping

- `00_env_config`: shared environment and metadata target routing.
- `01_da_<agreement>`: agreement scope, ownership, and approval context.
- `02_ex_<agreement>_<topic>`: exploration, profiling, and evidence preparation.
- `03_pc_<agreement>_<pipeline>`: approved rules and operational pipeline contract.
- `04_gov_<agreement>_<dataset>_<table>`: governance outputs and handover package.

## Go next

- [Quick Start](quick-start.md)
- [Notebook Structure](notebook-structure.md)
- [Function Reference](reference/index.md)
