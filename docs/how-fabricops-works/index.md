# How FabricOps Works

FabricOps helps teams <span class="glossary-term" title="Measure schema, counts, nulls, distinct values, and other reusable facts about data.">profile</span> <span class="glossary-term" title="Data read from configured upstream Lakehouse or Warehouse targets before transformation.">source data</span> and <span class="glossary-term" title="DataFrames or tables produced by the pipeline after transformation.">pipeline outputs</span>, enrich metadata, define guardrails, and enforce those guardrails during pipeline runs.

FabricOps Starter Kit is a lightweight, notebook-centric starter kit for governed, quality-checked Microsoft Fabric notebook workflows.

## Standard flow

1. Select source data and pipeline outputs.
2. Profile data.
3. Enrich metadata.
4. Review guardrails.
5. Enforce guardrails.
6. Write results to the metadata lakehouse.

## Workspace model

FabricOps works best when shared metadata is kept separate from the data being processed.

![FabricOps Starter Kit operating model with Governance, Engineering Dev, and Engineering Prod workspaces](../assets/fabricops-operating-model-overview.png)

| Workspace | Typical items | Purpose |
| --- | --- | --- |
| Governance workspace | `metadata_lakehouse` | Stores agreements, metadata, guardrails, and review records. |
| Engineering Dev workspace | `source_lakehouse`, `unified_lakehouse`, `product_warehouse` | Develops and tests `02_pipeline` notebooks before production. |
| Engineering Prod workspace | `source_lakehouse`, `unified_lakehouse`, `product_warehouse` | Runs approved production `02_pipeline` notebooks and publishes pipeline outputs. |

Run the notebooks in this order for the standard path: `01_agreement`, `02_pipeline`, then `03_governance`. See [Notebook Templates](notebook-templates.md) for the handoff between notebooks.

## Where metadata lives

`00_env_config` defines the <span class="glossary-term" title="Configured metadata target where FabricOps stores agreements, profiles, guardrail rules, guardrail results, lineage, and run summaries.">metadata lakehouse</span>. The notebooks use that metadata target to coordinate the workflow:

- `00_env_config` creates and validates the active metadata tables.
- `01_agreement` writes agreement, steward, and agreement evidence records.
- `02_pipeline` profiles data, writes lineage, enforces guardrails, and records run summaries.
- `03_governance` lets reviewers enrich metadata and approve, reject, replace, or deactivate guardrail records for profiled data.

## Promotion and production use

Keep production promotion lightweight:

1. Build and test the production-ready `02_pipeline` in Engineering Dev.
2. Promote the notebook to Engineering Prod.
3. Run it with the production `00_env_config`.
4. Store the `.py` or `.ipynb` files in Git or a configured metadata location for version history.

Do not copy development outputs into production. Production pipelines should read production configuration and approved production metadata.

## Which page should I read next?

| Page | Use it when you want to... |
| --- | --- |
| [Notebook Templates](notebook-templates.md) | Choose the right notebook and understand the handoff between notebooks. |
| [Metadata Tables](metadata-tables.md) | See the metadata tables and what each table is for. |
| [Pipeline Guardrails](pipeline-guardrails.md) | Understand the checks that `02_pipeline` can run before writing pipeline outputs. |
| [Governance Review](governance-review.md) | Understand what `03_governance` adds and who approves reviewed metadata. |
| [Metadata Dashboard](metadata-dashboard.md) | Understand the planned visibility layer. |
