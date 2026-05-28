# Templates

This page explains: which notebook templates to copy and what each template produces.
Use this when: you are setting up a plug and play notebook flow in your workspace.
Next read: [Start](quick-start.md), [Install](install.md), [Govern / Metadata](metadata-and-contracts/index.md).

<div class="home-cta" markdown="1">

[Copy Notebook Template](notebook-structure/00-env-config.md){ .md-button .md-button--primary }
[Start Using Templates](quick-start.md){ .md-button }

</div>

<figure markdown>
  ![Notebook structure diagram showing the 00 to 04 notebook layers and governance-centered responsibilities](assets/notebook-structure.png){ .full-width }
  <figcaption>Template-first model: copy stage notebooks, run sequence, and capture contract ready evidence.</figcaption>
</figure>

## Template cards

| Template | Copy this template when... | Primary owner | Writes/produces |
| --- | --- | --- | --- |
| [`00_env_config`](notebook-structure/00-env-config.md) | You need environment setup and metadata routing before any execution. | Platform/engineering | Validated runtime config and metadata target context. |
| [`01_agreement_*`](notebook-structure/01-data-sharing-agreement.md) | You are defining agreement scope and ownership. | Data owner + governance | Agreement metadata evidence. |
| [`02_ex_*`](notebook-structure/02-exploration.md) | You need profiling and AI assisted DQ drafting. | Analyst | Profile evidence and approved DQ rule metadata. |
| [`03_pc_*`](notebook-structure/03-pipeline-contract.md) | You are implementing deterministic pipeline enforcement. | Engineer | Curated outputs, enforcement evidence, lineage/run records. |
| [`04_gov_*`](notebook-structure/04-governance-operations.md) | You need human approved governance metadata updates. | Governance steward | Classification/access governance evidence. |

## Naming convention

```text
00_env_config
01_agreement_<name>
02_ex_<agreement>_<topic>
03_pc_<agreement>_<pipeline>
04_gov_<agreement>_<dataset>_<table>
```
