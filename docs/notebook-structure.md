# Notebook Operating Model

This page defines how FabricOps Starter Kit notebooks operate across governance and execution workspaces, how stages connect, and where each notebook boundary applies.

![Governance-Centered Workspace Model](assets/notebook-structure.png){ .full-width }

## Workspace model

FabricOps uses two workspace zones connected by a shared governance metadata plane:

- **Governance Workspace**
  - `01_da_<agreement>`
  - Governance metadata lakehouse
  - `04_gov_<agreement>_<dataset>_<table>` (planned stage)
- **Execution Workspace (Dev / Test / Prod)**
  - `00_env_config`
  - `02_ex_<agreement>_<topic>`
  - Lakehouse / Warehouse data store
  - `03_pc_<agreement>_<pipeline>`

## Stage sequence

```text
00_env_config
01_da_<agreement>
02_ex_<agreement>_<topic>
03_pc_<agreement>_<pipeline>
04_gov_<agreement>_<dataset>_<table>
```

## Notebook roles and boundaries

| Notebook | Workspace | Primary role | Boundary |
|---|---|---|---|
| `00_env_config` | Execution | Runtime bootstrap and routing config | Does not define agreements or governance outcomes. |
| `01_da_<agreement>` | Governance | Agreement-level approval evidence | Writes agreement evidence only; no column-level enrichment. |
| `02_ex_<agreement>_<topic>` | Execution | Exploration and profiling evidence | Uses existing `agreement_id`; does not approve governance policy. |
| `03_pc_<agreement>_<pipeline>` | Execution | Pipeline contract execution | Enforces approved metadata; does not create agreements. |
| `04_gov_<agreement>_<dataset>_<table>` | Governance | Column governance enrichment (planned stage) | Reviews business context and classification/PII/confidentiality; not part of execution workspace. |

## Governance flow across stages

- `01_da` defines and approves agreement-level metadata once.
- `02_ex` and `03_pc` run under that approved `agreement_id` and produce execution evidence.
- `04_gov` is the documented governance-stage follow-on for table/column enrichment after evidence exists (planned where template support is not yet available).

## Required metadata routing rule

Never rely on default-lakehouse metadata access such as `spark.table("METADATA_*")`.
Always route metadata through configured targets using `read_lakehouse_table(...)` and `write_lakehouse_table(...)` with `CONFIG`, `env_name`, and `"metadata"`.

## Notebook-specific pages

- [`00_env_config`](notebook-structure/00-env-config.md)
- [`01_da_<agreement>`](notebook-structure/01-data-sharing-agreement.md)
- [`02_ex_<agreement>_<topic>`](notebook-structure/02-exploration.md)
- [`03_pc_<agreement>_<pipeline>`](notebook-structure/03-pipeline-contract.md)
- [`04_gov_<agreement>_<dataset>_<table>`](notebook-structure/04-governance-enrichment.md)

## Related pages

- [Workflow](workflow.md)
- [Metadata and Data Contract Assembly](metadata-and-contracts.md)
- [Data Quality Rules System](data-quality-rules-system.md)
