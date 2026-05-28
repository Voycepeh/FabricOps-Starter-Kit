# Templates

This page explains: which notebook templates to copy and what each template produces.
Use this when: you are setting up notebook files and ownership boundaries in your workspace.
Next read: [Start](quick-start.md), [Govern / Metadata](metadata-and-contracts/index.md), [Deploy](deployment-and-promotion.md).

<figure markdown>
  ![Notebook structure diagram showing the 00 to 04 notebook layers and governance-centered responsibilities](assets/notebook-structure.png){ .full-width }
  <figcaption>Template catalogue ownership lives here: naming, responsibilities, and output expectations.</figcaption>
</figure>

## Template catalogue

| Template | Primary owner | Main purpose | What it writes/produces |
| --- | --- | --- | --- |
| `00_env_config` | Platform/engineering | Configure environment-local runtime and metadata target routing. | Validated config context for all downstream stages. |
| `01_agreement_*` (or `01_data_sharing_agreement_*`) | Data owner + governance | Define business scope, ownership, and usage expectations. | Agreement metadata evidence. |
| `02_ex_*` | Analyst | Profile sources and draft/review DQ rules. | Profile evidence + approved DQ rule metadata. |
| `03_pc_*` | Engineer | Build deterministic transformation and enforcement flow. | Curated datasets, lineage, DQ enforcement results, run evidence. |
| `04_gov_*` (if used) | Governance steward | Maintain classification/access governance metadata and reviews. | Governance evidence and approval records. |

## Naming convention

```text
00_env_config
01_agreement_<name>
02_ex_<agreement>_<topic>
03_pc_<agreement>_<pipeline>
04_gov_<agreement>_<dataset>_<table>
```

## Copyable template pages

- [`00_env_config`](notebook-structure/00-env-config.md)
- [`01_data_sharing_agreement`](notebook-structure/01-data-sharing-agreement.md)
- [`02_exploration`](notebook-structure/02-exploration.md)
- [`03_pipeline_contract`](notebook-structure/03-pipeline-contract.md)
- [`04_governance_operations`](notebook-structure/04-governance-operations.md)
