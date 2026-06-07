# Metadata tables

FabricOps metadata tables are the shared memory for the notebook workflow. They help notebooks agree on what was requested, what ran, what evidence was recorded, and what reviewers approved.

This page is a lightweight map. It is not a manual schema guide. `00_env_config` creates and validates the active schemas, so most users should not maintain metadata columns by hand.

## Product-truth metadata model

| Table | Written by | Main purpose |
| --- | --- | --- |
| `METADATA_DATA_STEWARD` | `01_agreement` | Stores data steward contact and ownership context. |
| `METADATA_DATA_AGREEMENT` | `01_agreement` | Stores the agreed purpose, owner, status, and versioned agreement details. |
| `METADATA_DATA_AGREEMENT_EVIDENCE` | `01_agreement` | Stores file or link references that support an agreement. |
| `METADATA_NOTEBOOK_REGISTRY` | `00_env_config`, workflow notebooks | Records notebook participation and active notebook registrations. |
| `METADATA_DATA_LINEAGE_TABLE` | `02_pipeline` | Stores table-level source-to-target lineage evidence. |
| `METADATA_DATA_CATALOGUE` | `02_pipeline` | Stores profile and catalogue evidence for source and target tables. |
| `METADATA_DATA_ACCESS` | Optional workflow capture | Stores access or sharing context when teams choose to capture it. |
| `METADATA_COLUMN_CONTEXT` | `03_review` | Stores reviewed business context for columns. |
| `METADATA_DQ_RULES` | `03_review` | Stores reviewed DQ expectations. These do not enforce anything by themselves. |
| `METADATA_COLUMN_CLASSIFICATION` | `03_review` | Stores reviewed sensitivity and classification context. |

## Architecture

![Shared FabricOps metadata model connecting governance and engineering notebooks](../assets/fabricops-metadata-model.png){ .full-width }

## How the tables support the workflow

| Workflow moment | Metadata used | Why it matters |
| --- | --- | --- |
| Configure the environment | `METADATA_NOTEBOOK_REGISTRY` and schema setup | Confirms notebooks are using the expected environment and metadata target. |
| Capture agreement | Steward, agreement, and evidence tables | Makes the request and ownership clear before build work is treated as production-ready. |
| Build the pipeline | Agreement records, catalogue records, lineage records | Lets `02_pipeline` connect work to an agreement and record what it produced. |
| Review the evidence | Catalogue and lineage records | Gives reviewers enough metadata evidence to understand tables and columns. |
| Save approved context | Column context, DQ rules, and classification tables | Stores reviewed metadata for handover and possible future pipeline use. |

## Table purpose summaries

### Agreement and owner tables

| Table | What consumers need to know |
| --- | --- |
| `METADATA_DATA_STEWARD` | Identifies who can answer questions about a data area or agreement. |
| `METADATA_DATA_AGREEMENT` | Captures the agreed purpose, owner, status, and version. Updates append new versions instead of replacing the past. |
| `METADATA_DATA_AGREEMENT_EVIDENCE` | Points to supporting files or references. Keep these public-safe and useful for review. |

Useful relationship: an agreement points to a steward and can have multiple evidence records.

### Notebook and pipeline evidence tables

| Table | What consumers need to know |
| --- | --- |
| `METADATA_NOTEBOOK_REGISTRY` | Shows which notebooks are registered for the workflow and environment. |
| `METADATA_DATA_LINEAGE_TABLE` | Records table-level source and target relationships from `02_pipeline`. |
| `METADATA_DATA_CATALOGUE` | Holds profile and catalogue evidence that `03_review` can use to select and review tables. |
| `METADATA_DATA_ACCESS` | Captures access context when a team chooses to record it. |

Useful relationship: `02_pipeline` writes catalogue rows for profiled source and target columns, then writes lineage so readers can understand how tables connect.

### Reviewed metadata tables

| Table | What consumers need to know |
| --- | --- |
| `METADATA_COLUMN_CONTEXT` | Stores human-reviewed descriptions and business meaning for columns. |
| `METADATA_DQ_RULES` | Stores reviewed DQ expectations. These are approved expectations, not automatic enforcement. |
| `METADATA_COLUMN_CLASSIFICATION` | Stores reviewed sensitivity, PII, and classification context for columns. |

Useful relationship: `03_review` reads catalogue evidence from `02_pipeline`, then writes reviewed metadata for the selected table or columns.

## Minimum useful fields to recognize

You usually only need to recognize a few kinds of fields when reading metadata:

| Field type | Why it exists |
| --- | --- |
| Stable identifiers | Link agreements, tables, columns, notebooks, and review records across runs. |
| Version and status fields | Show which agreement or reviewed metadata record is current. |
| Environment and runtime fields | Show where and when a notebook created metadata evidence. |
| Source and target fields | Explain what data a pipeline read and wrote. |
| Review fields | Capture what a person approved and when. |

For exact column-level details, use the generated function reference or inspect the notebook and package source. The main consumer need is to understand how the metadata tables coordinate agreement, pipeline evidence, review, handover, and visibility.

## Important boundaries

- `metadata_lakehouse` is the shared metadata location configured by `00_env_config`.
- `02_pipeline` records metadata evidence and owns guardrails.
- `03_review` stores reviewed metadata after human approval.
- Reviewed metadata does not enforce production behavior unless `02_pipeline` is built to use it.
- Separate data contracts are not part of the current v1.0.0 operating model.

## Next step

Continue to [Metadata Dashboard](metadata-dashboard.md) to see the planned visibility layer over this metadata evidence.
