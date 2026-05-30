# Notebook Structure

Notebook Structure explains how FabricOps organizes Fabric notebooks across governance and execution workspaces.
Governance stays separate. Execution notebooks consume approved metadata and write evidence.

This structure keeps three concerns from being mixed in the same notebook: agreement approval and business context, exploration and profiling, and production pipeline enforcement.

![FabricOps workspace model](assets/workspace_model.png)

The workspace model shows how governance-owned agreement metadata is kept separate from execution notebooks. The Governance Workspace owns the Governance Metadata Lakehouse, while Execution Workspaces for sandbox, development, test, and production use `00_env_config` to route metadata access and run `02_ex` and `03_pc` notebooks against the Lakehouse / Warehouse Data Store without redefining governance rules locally.

!!! note
    The diagram shortens `01_data_sharing_agreement_<agreement>` to `01_agreement_<agreement>` for readability.

## What this model means

The Governance Workspace is where agreement scope, ownership, classifications, policy decisions, and reviewed governance evidence are approved. Its Governance Metadata Lakehouse is the shared source for approved metadata and rules.

Execution Workspaces are where teams configure runtime paths, explore data, and run deterministic pipelines. Sandbox, development, test, and production notebooks reuse approved metadata from governance instead of copying control logic into each workspace.

## Notebook roles

| Notebook | Primary owner | Purpose | What belongs here |
| --- | --- | --- | --- |
| [`00_env_config`](notebook-structure/00-env-config.md) | Platform or engineering | Configure the execution workspace. | Environment names, metadata targets, storage paths, runtime defaults, and validation that notebooks read and write the intended Fabric locations. |
| [`01_data_sharing_agreement_<agreement>`](notebook-structure/01-data-sharing-agreement.md) | Data owner and governance | Define approved agreement context. | Agreement scope, owners, consumers, permitted usage, approval status, and business context that governs downstream work. |
| [`02_ex_<agreement>_<topic>`](notebook-structure/02-exploration.md) | Analyst or data engineer | Explore and profile source data. | Profiling evidence, metadata proposals, data quality suggestions, classification suggestions, and notes that require review before enforcement. |
| [`03_pc_<agreement>_<pipeline>`](notebook-structure/03-pipeline-contract.md) | Data engineer | Run deterministic pipeline enforcement. | Approved metadata consumption, pipeline checks, data quality enforcement, curated writes, lineage, run results, and evidence summaries. |
| [`04_gov_<agreement>_<dataset>_<table>`](notebook-structure/04-governance-operations.md) | Governance steward | Review business context and classifications. | Reviewed classifications, policy updates, governance decisions, and evidence that can update the Governance Metadata Lakehouse after human approval. |

## How the notebooks work together

1. `01_data_sharing_agreement_<agreement>` defines the approved agreement context for a governed data use case.
2. `00_env_config` configures the execution workspace so notebooks use the correct metadata, lakehouse, warehouse, and runtime paths.
3. `02_ex_<agreement>_<topic>` explores source data and proposes profiling evidence, metadata, data quality rules, and classification suggestions.
4. `04_gov_<agreement>_<dataset>_<table>` reviews business context, classifications, policy updates, and governance evidence before metadata changes are promoted.
5. `03_pc_<agreement>_<pipeline>` consumes approved metadata and enforces deterministic production pipeline rules.
6. `03_pc_<agreement>_<pipeline>` writes runtime evidence, quality results, lineage, and run summaries. Evidence can feed back into governance metadata after review.

## AI boundary and human approval

AI can suggest classifications, data quality rules, summaries, metadata, and draft contract changes. Humans approve governance controls and contract expectations before they become enforceable rules. Production pipeline contracts enforce approved rules only. See [Metadata and Data Contract Assembly](metadata-and-contracts/index.md) for the shared-promise model and recommended early contract gates.

## Start from the templates

Use the starter notebook templates from GitHub instead of creating notebooks from scratch. The templates give you the standard FabricOps structure and can be adapted to your agreement, source tables, and pipeline.

[Download notebook templates from GitHub](https://github.com/Voycepeh/FabricOps-Starter-Kit/tree/main/templates/notebooks){ .md-button .md-button--primary }

[Read the Quick Start](quick-start.md){ .md-button }

## Related pages

- [Quick Start](quick-start.md)
- [Workflow](lifecycle-operating-model.md)
- [Metadata and Data Contract Assembly](metadata-and-contracts/index.md)
- [Data Quality Rules System](data-quality-rules-system.md)
