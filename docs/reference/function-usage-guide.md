# Function Usage Guide

Use this guide to start from the notebook templates first, then use the [Function Reference](../) only when you need implementation details such as exact callable signatures and return values.

## Start from the templates

| Template notebook | Purpose | Guided page | Notebook template |
| --- | --- | --- | --- |
| `00_env_config` | Shared environment bootstrap. Validates imports, paths, metadata locations, runtime variables, AI prompt scaffolding, and sample settings required by downstream notebooks. | [00_env_config guide](../../notebook-structure/00-env-config/) | [00_env_config.ipynb](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/templates/notebooks/00_env_config.ipynb) |
| `01_da_agreement_template` | Agreement level source of truth for approved usage, business context, stewardship notes, governance approvals, DQ approvals, restrictions, and reusable agreement metadata. | [01 data sharing agreement guide](../../notebook-structure/01-data-sharing-agreement/) | [01_da_agreement_template.ipynb](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/templates/notebooks/01_da_agreement_template.ipynb) |
| `02_ex_agreement_topic` | Exploration flow for source profiling, data understanding, AI assisted proposals, evidence capture, and governance or pipeline handoff. | [02 exploration guide](../../notebook-structure/02-exploration/) | [02_ex_agreement_topic.ipynb](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/templates/notebooks/02_ex_agreement_topic.ipynb) |
| `04_gov_agreement_dataset_table` *(optional)* | Optional governance enrichment flow after profile evidence exists. Reviews column context and governance classification, then writes approved metadata rows. | [04 governance enrichment guide](../../notebook-structure/04-governance-enrichment/) | [04_gov_agreement_dataset_table.ipynb](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/templates/notebooks/04_gov_agreement_dataset_table.ipynb) |
| `03_pc_agreement_pipeline_template` | Pipeline contract flow for loading approved metadata, applying deterministic validation, adding technical columns, splitting valid and quarantine rows, and writing controlled outputs. | [03 pipeline contract guide](../../notebook-structure/03-pipeline-contract/) | [03_pc_agreement_pipeline_template.ipynb](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/templates/notebooks/03_pc_agreement_pipeline_template.ipynb) |

## Recommended run order

1. `00_env_config`
2. `01_da_agreement_template`
3. `02_ex_agreement_topic`
4. Optional `04_gov_agreement_dataset_table`
5. `03_pc_agreement_pipeline_template`

- `00_env_config` sets the shared runtime.
- `01_da_agreement_template` defines approved agreement metadata.
- `02_ex_agreement_topic` creates profile evidence and draft proposals.
- `04_gov_agreement_dataset_table` enriches approved governance metadata when used.
- `03_pc_agreement_pipeline_template` enforces approved metadata in a controlled pipeline.

## What runs where

- `00_env_config` is shared setup.
- `01_da_agreement_template` is agreement governance and business context.
- `02_ex_agreement_topic` is exploration and advisory evidence.
- `04_gov_agreement_dataset_table` is optional governance review and approval enrichment.
- `03_pc_agreement_pipeline_template` is deterministic enforcement and publishing.

AI assisted functions propose and document. Human approved metadata and pipeline notebooks are the enforcement point.

## When to use Function Reference

Use the generated [Function Reference](../) when you need exact callable names, signatures, parameters, and return values.
