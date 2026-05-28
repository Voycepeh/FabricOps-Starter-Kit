# Notebook Structure

Use this page for the **practical implementation conventions**: which notebooks exist, how they are named, and what each notebook owns. For people/process sequencing and AI/human approval flow, start with the [Workflow Operating Model](lifecycle-operating-model.md).

<figure markdown>
  ![Notebook structure diagram showing the 00 to 04 notebook layers and governance-centered responsibilities](assets/notebook-structure.png){ .full-width }
  <figcaption>This structure anchors ownership: agreement, exploration, pipeline contract, and governance each have clear boundaries.</figcaption>
</figure>

## Canonical notebook sequence

<figure markdown>
  ![Notebook flow diagram showing execution sequence from environment configuration to governance operations](assets/notebook-flow.png){ .full-width }
  <figcaption>The sequence keeps teams aligned on execution order and handoff points between notebook stages.</figcaption>
</figure>

```text
00_env_config
01_da_<agreement>
02_ex_<agreement>_<topic>
03_pc_<agreement>_<pipeline>
04_gov_<agreement>_<dataset>_<table>
```

## Notebook overview (01–04 truth model)

| Stage | Notebook | Primary role owner | Purpose | Metadata contract contribution |
|---|---|---|---|---|
| 01 | `01_da_<agreement>` | Steward / data owner | Define the high-level data-sharing agreement: purpose, scope, approved use, and control-plane context. | Writes approved agreement metadata evidence for downstream notebooks. |
| 02 | `02_ex_<agreement>_<topic>` | Analyst | Profile and analyze data, then propose and approve DQ rules for operational enforcement. | Writes approved DQ metadata used by 03. |
| 03 | `03_pc_<agreement>_<pipeline>` | Engineer | Execute source-to-target transformation contract, enforce approved rules, and publish run evidence. | Consumes approved metadata from 01/02/04 and writes lineage, run, and enforcement evidence. |
| 04 | `04_gov_<agreement>_<dataset>_<table>` | Governance | Review governed outputs from 03 and set sensitivity, PII, classification, and access metadata. | Writes approved governance metadata used by 03 and downstream consumers. |

## Shared metadata contract layer

The metadata tables are the shared contract layer across notebooks:

- **01 defines** approved agreement metadata.
- **02 analyzes** and writes approved DQ metadata.
- **03 engineers/enforces** by consuming approved metadata from 01/02/04.
- **04 governs** by writing approved governance metadata for enforcement and downstream use.

Always route metadata reads/writes through configured metadata targets (`read_lakehouse_table`/`write_lakehouse_table` with `CONFIG`, `env_name`, and `"metadata"`). Do not rely on default-lakehouse metadata access.

## Workspace placement

- **Governance workspace:** agreement and governance operations responsibilities.
- **Execution workspace (dev/test/prod):** configuration, exploration, and pipeline contract responsibilities.

## Environment versioning (dev/prod)

- Keep notebook logic aligned across environments; promote through controlled dev/test/prod transitions.
- Keep environment-specific values in configuration inputs rather than hard-coded notebook logic.
- Use consistent notebook naming across environments so approvals and evidence remain traceable.

## Notebook details

Each notebook detail page summarizes purpose, what it reads, what it writes, when it runs, template link, and related function groups.


- [`00_env_config`](notebook-structure/00-env-config.md)
- [`01_da_<agreement>`](notebook-structure/01-data-sharing-agreement.md)
- [`02_ex_<agreement>_<topic>`](notebook-structure/02-exploration.md)
- [`03_pc_<agreement>_<pipeline>`](notebook-structure/03-pipeline-contract.md)
- [`04_gov_<agreement>_<dataset>_<table>`](notebook-structure/04-governance-operations.md)

## Related pages

- [Workflow Operating Model](lifecycle-operating-model.md)
- [Metadata and Data Contract Assembly](metadata-and-contracts/)
- [Data Quality Rules System](data-quality-rules-system.md)
