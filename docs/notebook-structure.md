# Notebook Structure

Use this page for the **practical implementation conventions**: which notebooks exist, how they are named, and what each notebook owns. For people/process sequencing and AI/human approval flow, start with the [Workflow Operating Model](lifecycle-operating-model.md).

![Governance-Centered Workspace Model](assets/notebook-structure.png){ .full-width }

## Canonical notebook sequence

```text
00_env_config
01_da_<agreement>
02_ex_<agreement>_<topic>
03_pc_<agreement>_<pipeline>
04_gov_<agreement>_<dataset>_<table>
```

## Naming and ownership conventions

| Notebook | Naming convention | Primary ownership | What it owns |
|---|---|---|---|
| Environment config | `00_env_config` | Platform / delivery engineering | Runtime bootstrap, environment configuration, metadata target routing. |
| Data-sharing agreement | `01_da_<agreement>` | Governance + business data owners | Agreement context and approval-ready agreement evidence. |
| Exploration | `02_ex_<agreement>_<topic>` | Delivery / analytics | Profiling, evidence capture, and exploratory quality outputs for a scoped topic. |
| Pipeline contract | `03_pc_<agreement>_<pipeline>` | Data engineering | Operational pipeline checks and contract enforcement for a pipeline scope. |
| Governance enrichment | `04_gov_<agreement>_<dataset>_<table>` | Governance stewardship | Governance-side enrichment and handover artifacts for dataset/table scope. |

## Workspace placement

- **Governance workspace:** agreement and governance enrichment responsibilities.
- **Execution workspace (dev/test/prod):** configuration, exploration, and pipeline contract responsibilities.

## Environment versioning (dev/prod)

- Keep notebook logic aligned across environments; promote through controlled dev/test/prod transitions.
- Keep environment-specific values in configuration inputs rather than hard-coded notebook logic.
- Use consistent notebook naming across environments so approvals and evidence remain traceable.

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

- [Workflow Operating Model](lifecycle-operating-model.md)
- [Metadata and Data Contract Assembly](metadata-and-contracts.md)
- [Data Quality Rules System](data-quality-rules-system.md)
