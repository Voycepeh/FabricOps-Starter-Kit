# How FabricOps Works

Lightweight, notebook centric, plug and play starter kit for Microsoft Fabric.

FabricOps Starter Kit helps teams quickly bootstrap governed Fabric notebook delivery using reusable templates and a lightweight helper wheel.

## Workspace model

FabricOps works best when shared metadata (data about the actual data) is kept separate from the actual data itself .

![FabricOps Starter Kit operating model with Governance, Engineering Dev, and Engineering Prod workspaces](../assets/fabricops-operating-model-overview.png)

| Workspace | Typical items | Purpose |
| --- | --- | --- |
| Governance workspace | `metadata_lakehouse` | Stores agreements, metadata evidence, and reviewed metadata for support. |
| Engineering Dev workspace | `source_lakehouse`, `unified_lakehouse`, `product_warehouse` | Develops and tests `02_pipeline` notebooks before production. |
| Engineering Prod workspace | `source_lakehouse`, `unified_lakehouse`, `product_warehouse` | Runs approved production `02_pipeline` notebooks and publishes production outputs. |

Run the notebooks in this order for the standard path: `01_agreement` , `02_pipeline` , `03_review` read more [Notebook Templates](notebook-templates.md)

## Where metadata lives

`00_env_config` defines where metadata tables live. The shared metadata target is the Governance workspace `metadata_lakehouse`.

The notebooks use that metadata target to coordinate the workflow:
 `00_env_config` creates and validates the active metadata tables so the other notebooks can read and write them consistently.
- `01_agreement` writes agreement, steward, and agreement evidence records.
- `02_pipeline` is a thin orchestration notebook that writes data profiles, catalogue evidence, lineage, guardrail results, and runtime summaries in `METADATA_PIPELINE_RUNS`.
- `03_review` writes goverance reivewed rules like data quality, sensitivity, classification on the data profiled earlier.


## Promotion and production use

Keep production promotion lightweight:

1. Build and test the production-ready `02_pipeline` in Engineering Dev.
2. Promote the notebook to Engineering Prod.
3. Run it with the production `00_env_config`.
4. Store the .py or .ipynb files inside the metadata lakehouse or a git repository for version history

Do not copy development outputs into production. Production pipelines should read production configuration and approved production metadata.

## Which page should I read next?

| Page | Use it when you want to... |
| --- | --- |
| [Notebook Templates](notebook-templates.md) | Choose the right notebook and understand the handoff between notebooks. |
| [Metadata Tables](metadata-tables.md) | See the lightweight map of metadata tables and what each table is for. |
| [Pipeline Guardrails](schema-and-data-drift.md) | Understand the checks that `02_pipeline` can run before writing outputs. |
| [Governance Review](governance-review.md) | Understand what `03_review` adds and who approves reviewed metadata. |
| [Metadata Dashboard](metadata-dashboard.md) | Understand the planned post-v1.0.0 visibility layer. |
