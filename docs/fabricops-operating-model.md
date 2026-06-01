# FabricOps Starter Kit Operating Model

FabricOps Starter Kit is a plug-and-play Microsoft Fabric notebook starter kit. It helps governance, analysts, scientists, and engineers work together with a small set of Fabric workspaces, notebook templates, and shared metadata tables.

The kit is intentionally lightweight. It does not add a large platform around Fabric. Teams continue to use familiar Fabric workspaces, lakehouses, warehouses, and notebooks. FabricOps Starter Kit adds reusable templates and simple enforcement so that exploration, engineering, governance, and handover stay connected.

## Recommended minimum workspace setup

Start with three Fabric workspaces:

| Workspace | Items | Purpose |
| --- | --- | --- |
| **Governance workspace** | `metadata_lakehouse` | Owns shared governance metadata used across the notebook flow. |
| **Engineering Dev workspace** | `source_lakehouse`, `unified_lakehouse`, `product_warehouse` | Supports exploration, transformation development, profiling, and proposed product outputs. |
| **Engineering Prod workspace** | `source_lakehouse`, `unified_lakehouse`, `product_warehouse` | Runs approved repeatable pipelines and publishes production outputs. |

The governance workspace owns the shared metadata. Engineering workspaces own the actual exploration, transformation, and product outputs. This separation is simple enough for a starter kit while still making responsibilities clear.

## Notebook template model

The templates are designed to be copied and adapted in Fabric. Each one has a focused job.

### `00_env_config`

`00_env_config` stores workspace, lakehouse, warehouse, and metadata paths. It is the first notebook users configure, and the other notebooks reuse its configuration. Each environment should have its own config so development and production notebooks point to the correct Fabric items and metadata target.

### `01_da`

`01_da` runs in the governance workspace. Data stewards or data owners use its simplified widget UI to maintain data steward and data agreement records. The notebook stores those records in the governance `metadata_lakehouse`.

### `02_ex`

`02_ex` runs in the Engineering Dev workspace. Analysts or data scientists use it to explore source or unified data in a less structured way. It profiles data, stores profile metadata in the governance `metadata_lakehouse`, links the notebook run to a selected data agreement, and registers the notebook in the notebook registry. It may also produce a proposed output schema or desired outcome table for engineers.

### `03_pc`

`03_pc` runs in Engineering Dev and Engineering Prod workspaces. Data engineers use it to read source data, apply repeatable transformations, and write output tables. It adds technical columns, applies schema-drift and data-drift guardrails, links the notebook to a data agreement, and registers the notebook in the notebook registry.

The notebook also creates output-table profiles in the same metadata profile table used by `02_ex`. It captures table-level lineage showing the source and output tables for the registered notebook. After governance review is available, `03_pc` fetches approved metadata produced through `04_gov` and enforces approved data quality rules, sensitivity rules, and classification rules.

### `04_gov`

`04_gov` runs in the governance workspace. Governance users work through a simplified widget UI to enhance profiles created by `02_ex` and `03_pc` with business context, data quality rules, sensitivity classification, and other governance metadata. It stores those records in governance metadata tables so engineering pipelines can reuse approved decisions.

### Production handover

Once a `03_pc` pipeline is running in production, store a copy of the production notebook as a `.py` or `.ipynb` file in the governance workspace lakehouse file area. The stored notebook file plus a reusable AI prompt can generate:

- a human-readable handover summary;
- an AI manifest;
- production support notes; and
- a data product explanation.

The notebook export keeps the handover grounded in the production implementation while leaving room for a human review before publishing the generated material.

## Role-based flow

| Step | Owner | Action | Result |
| --- | --- | --- | --- |
| **0** | Platform team or engineer | Configure `00_env_config`. | Environment-specific workspace, lakehouse, warehouse, and metadata paths are ready for the other notebooks. |
| **1** | Steward or data owner | Create data steward and data agreement records with `01_da`. | The shared metadata lakehouse contains ownership and agreement records. |
| **2** | Analyst or data scientist | Explore data with `02_ex`. | Profiling metadata, notebook registration, and proposed transformation or schema advice are available for engineering. |
| **3** | Data engineer | Build the repeatable pipeline with `03_pc`. | The pipeline produces governed source-to-output transformations, technical columns, drift checks, lineage, profile metadata, and output tables. |
| **4** | Governance user | Enrich metadata with `04_gov`. | Approved business context, data quality rules, sensitivity classification, and governance context are stored as shared metadata. |
| **5** | Data engineer | Rerun or update `03_pc` to consume approved metadata from `04_gov`. | The pipeline enforces approved rules using the correct environment configuration. |
| **6** | Engineering and support teams | Generate production handover from the stored notebook export and reusable AI prompt. | Human-readable support material and an AI-ready manifest are available for handover. |

The flow is deliberately small: configure, document, explore, build, govern, enforce, and hand over.

## Lightweight metadata model

The governance `metadata_lakehouse` only needs a small conceptual model to connect the notebook flow:

| Metadata table | What it keeps |
| --- | --- |
| `data_stewards` | Steward and owner records. |
| `data_agreements` | Shared purpose, scope, and agreement context. |
| `notebook_registry` | Registered notebook runs and links back to their agreement. |
| `data_profiles` | Profiles produced by exploration and pipeline notebooks. |
| `data_lineage` | Table-level source-to-output lineage for registered notebooks. |
| `data_quality_rules` | Reviewed and approved quality rules. |
| `sensitivity_classification` | Approved sensitivity and classification records. |
| `business_context` | Business descriptions and other useful context. |
| `handover_manifest` | Generated handover and AI-ready manifest records. |

These names describe the minimum conceptual model. Teams can map them to the starter kit metadata helpers and extend them only when needed. Metadata reads and writes should always use the metadata target configured by `00_env_config`; notebooks should not assume an attached or default lakehouse.

## Development and production

Keep promotion straightforward:

- configure `00_env_config` separately for each environment;
- develop and test `03_pc` notebooks in Engineering Dev;
- promote production-ready `03_pc` notebooks to Engineering Prod;
- promote or recreate approved metadata through a controlled process; and
- make production pipelines read production config and approved production metadata only.

See [Deployment and promotion](deployment-and-promotion.md) for the short deployment appendix.

## Where to go next

- Follow the [Quick Start](quick-start.md) to install and configure the kit.
- Open [Notebook Templates](notebook-structure.md) for template-specific guides.
- Read [Data Quality Rules](data-quality-rules-system.md) for the approved-rule enforcement pattern.
- Use the [Function Reference](reference/index.md) when adapting notebooks.
