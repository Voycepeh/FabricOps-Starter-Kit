# Notebook Templates

FabricOps Starter Kit uses five notebook templates. Each notebook has a clear role in the workflow.

The notebook templates are available in the [`templates/notebooks`](https://github.com/Voycepeh/FabricOps-Starter-Kit/tree/main/templates/notebooks) folder.

!!! note "Notebook preview"
    The notebook templates are optimized for Microsoft Fabric execution. GitHub may not always render `.ipynb` previews reliably.

    If GitHub shows a notebook preview error, open the template in Microsoft Fabric or view it locally in VS Code or Jupyter.

    The `%run 00_env_config` bootstrap cell is intentionally active so the templates remain plug-and-play in Fabric. Do not manually edit the bootstrap cell unless you are intentionally customizing the template.

## Template overview

| Notebook | Main owner | Purpose |
| --- | --- | --- |
| `00_env_config` | Platform team or engineer | Defines workspace, lakehouse, warehouse, and metadata paths for each environment. |
| `01_da` | Steward or data owner | Maintains steward and data agreement records. |
| `02_ex` | Analyst or data scientist | Profiles data and proposes schema or transformation advice. |
| `03_pc` | Data engineer | Builds repeatable transformations and enforces approved metadata. |
| `04_gov` | Governance user | Reviews business context, rules, classifications, and governance decisions. |

## Role-based notebook flow

![Role-based notebook workflow from environment configuration through AI-assisted handover](../assets/fabricops-role-workflow.png){ .full-width }

| Step | Owner | Notebook or action | Result |
| --- | --- | --- | --- |
| 0 | Platform team or engineer | Configure `00_env_config`. | Environment-specific workspace, lakehouse, warehouse, and metadata paths are ready. |
| 1 | Steward or data owner | Use `01_da`. | Steward and data agreement records are stored in the Governance workspace metadata lakehouse. |
| 2 | Analyst or data scientist | Use `02_ex` in Engineering Dev. | Exploration profiles, notebook registration, and proposed schema or transformation advice are available. |
| 3 | Data engineer | Build `03_pc` in Engineering Dev. | Repeatable transformations, technical columns, drift checks, table-level lineage, profiles, and output tables are created. |
| 4 | Governance user | Use `04_gov`. | Business context, data quality rules, sensitivity classification, and governance context are reviewed and stored. |
| 5 | Data engineer | Rerun or update `03_pc` with approved metadata. | The pipeline applies approved rules using the correct environment config. |
| 6 | Engineering and support teams | Use stored production notebook evidence. | Human-readable support material can be generated from approved evidence. |

## What each template owns

### `00_env_config`

Configure this notebook first in each environment.

It stores workspace, lakehouse, warehouse, and metadata paths. Every other notebook reuses this configuration, so metadata operations use the configured metadata target rather than an attached or default lakehouse.

It also creates or checks the data agreement and steward metadata tables and reports whether active steward profiles are ready for agreement intake.

### `01_da`

Run this notebook in the Governance workspace.

Data stewards or data owners use its simplified widget UI to maintain steward and data agreement records in `metadata_lakehouse`.

Agreement intake appends immutable agreement-version rows. Creating an agreement starts a new stable ID, while updating an explicitly selected agreement appends its next version.

Governance classification and review remain in `04_gov`.

### `02_ex`

Run this notebook in Engineering Dev.

Analysts or data scientists use it for less-structured exploration of source or unified data. It profiles data, registers the notebook, links the run to a selected agreement, and may propose an output schema or desired outcome table for engineers.

AI-assisted suggestions remain advisory until a human reviews and approves the relevant metadata.

### `03_pc`

Run this notebook in Engineering Dev and Engineering Prod.

Data engineers use it for repeatable source-to-output transformations. It adds technical columns, applies schema and data drift guardrails, registers the notebook, captures table-level lineage, and profiles output tables.

After governance review, it loads approved data quality, sensitivity, and classification metadata and enforces the applicable controls.

### `04_gov`

Run this notebook in the Governance workspace after relevant `03_pc` outputs are available.

Governance users enrich profiles with approved business context, data quality rules, sensitivity and PII classification, access classification, retention or export flags, exceptions, and review notes.

These decisions stay in the governance stage and are stored through the configured metadata target for downstream enforcement.

## Next step

Continue to [Metadata Tables](metadata-tables.md) to see how the notebook flow stores reusable evidence.
