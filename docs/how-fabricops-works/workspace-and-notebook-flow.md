# Workspace and Notebook Flow

FabricOps Starter Kit uses a small Fabric workspace setup and five notebook templates. Governance owns the shared metadata. Engineering owns exploration, transformations, and product outputs.

## Recommended workspace setup

<figure markdown>
  ![FabricOps Starter Kit operating model with Governance, Engineering Dev, and Engineering Prod workspaces](../assets/fabricops-operating-model-overview.png){ .full-width }
  <figcaption>The recommended setup separates shared governance metadata from development and production data processing.</figcaption>
</figure>

| Workspace | Items | Purpose |
| --- | --- | --- |
| **Governance workspace** | `metadata_lakehouse` | Owns shared metadata used across the notebook flow. |
| **Engineering Dev workspace** | `source_lakehouse`, `unified_lakehouse`, `product_warehouse` | Supports exploration, profiling, transformation development, and proposed outputs. |
| **Engineering Prod workspace** | `source_lakehouse`, `unified_lakehouse`, `product_warehouse` | Runs approved repeatable pipelines and publishes production outputs. |

## Role-based flow

<figure markdown>
  ![Role-based notebook workflow from environment configuration through AI-assisted handover](../assets/fabricops-role-workflow.png){ .full-width }
  <figcaption>Each notebook gives the next role reusable evidence instead of adding a heavy process.</figcaption>
</figure>

| Step | Owner | Notebook or action | Result |
| --- | --- | --- | --- |
| **0** | Platform team or engineer | Configure `00_env_config`. | Environment-specific workspace, lakehouse, warehouse, and metadata paths are ready. |
| **1** | Steward or data owner | Use `01_da`. | Steward and data agreement records are stored in the governance `metadata_lakehouse`. |
| **2** | Analyst or data scientist | Use `02_ex` in Engineering Dev. | Exploration profiles, notebook registration, and proposed schema or transformation advice are available. |
| **3** | Data engineer | Build `03_pc` in Engineering Dev. | Repeatable transformations, technical columns, drift checks, table-level lineage, profiles, and output tables are created. |
| **4** | Governance user | Use `04_gov`. | Business context, data quality rules, sensitivity classification, and governance context are reviewed and stored. |
| **5** | Data engineer | Rerun or update `03_pc` with approved metadata. | The pipeline applies approved rules using the correct environment config. |
| **6** | Engineering and support teams | Generate AI-assisted production handover. | Human-readable support material and an AI-ready manifest are generated from approved evidence. |

## What each template owns

### `00_env_config`

Configure this notebook first in each environment. It stores workspace, lakehouse, warehouse, and metadata paths. Every other notebook reuses this configuration, so metadata operations use the configured metadata target rather than an attached or default lakehouse. It also creates or checks the data agreement and steward metadata tables and reports whether active steward profiles are ready for agreement intake.

### `01_da`

Run this notebook in the Governance workspace. Data stewards or data owners use its simplified widget UI to maintain steward and data agreement records in `metadata_lakehouse`. Agreement intake appends immutable agreement-version rows: creating an agreement starts a new stable ID, while updating an explicitly selected agreement appends its next version. Governance classification and review remain in `04_gov`.

### `02_ex`

Run this notebook in Engineering Dev. Analysts or data scientists use it for less-structured exploration of source or unified data. It profiles data, registers the notebook, links the run to a selected agreement, and may propose an output schema or desired outcome table for engineers. Its AI-assisted suggestions remain advisory until a human reviews and approves the relevant metadata.

### `03_pc`

Run this notebook in Engineering Dev and Engineering Prod. Data engineers use it for repeatable source-to-output transformations. It adds technical columns, applies schema- and data-drift guardrails, registers the notebook, captures table-level lineage, and profiles output tables. After governance review, it loads approved data quality, sensitivity, and classification metadata and enforces the applicable controls.

### `04_gov`

Run this notebook in the Governance workspace after relevant `03_pc` outputs are available. Governance users enrich profiles with approved business context, data quality rules, sensitivity and PII classification, access classification, retention or export flags, exceptions, and review notes. These decisions stay in the governance stage and are stored through the configured metadata target for downstream enforcement.

## Next step

Continue to [Metadata Tables](metadata-tables.md) to see how the notebook flow stores reusable evidence.
