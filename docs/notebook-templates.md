# Notebook Templates

FabricOps provides four editable Microsoft Fabric notebook templates for configuring the workspaces, registering governance metadata, running data pipelines, defining guardrails, approving data contracts, and exploring data.

[Open all notebook templates on GitHub](https://github.com/Voycepeh/FabricOps-Starter-Kit/tree/main/templates/notebooks){ .md-button .md-button--primary }

<div class="template-list" markdown="1">

<div class="template-card" markdown="1">

## `00_env_config`

Creates and stores the FabricOps configuration used by the other notebooks.

It contains the Governance, Engineering Development, and Engineering Production workspace settings; lakehouse and warehouse names; metadata table routing; package settings; runtime validation; audit settings; and widget settings.

Run it in each workspace before running the other FabricOps notebooks.

[Open `00_env_config.ipynb`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/templates/notebooks/00_env_config.ipynb){ .md-button }

</div>

<div class="template-card" markdown="1">

## `01_governance`

Owns the complete Governance lifecycle in one persistent notebook. Use it before Engineering to establish Data Stewards and the Data Agreement, then return after `02_pipeline` has produced evidence to register Data Contracts, review catalogue and profile evidence, enrich metadata, author guardrails, and complete formal Governance review.

The operating model is **Governance → Engineering → Governance**: `01_governance` → `02_pipeline` → `01_governance`.

[Open `01_governance.ipynb`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/templates/notebooks/01_governance.ipynb){ .md-button }

</div>

<div class="template-card" markdown="1">

## `02_pipeline`

Reads source data, transforms it, and writes the output to a Fabric lakehouse or warehouse.

It profiles the source and target tables, writes Data Catalogue, Data Profiled, and Data Lineage metadata, reads approved enrichment and guardrail rules, evaluates those rules, and writes the guardrail results.

Develop and validate this notebook in Engineering Development, then promote the completed notebook to Engineering Production.

[Open `02_pipeline.ipynb`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/templates/notebooks/02_pipeline.ipynb){ .md-button }

</div>

<div class="template-card" markdown="1">

## `99_explore`

Reads data and FabricOps metadata for one-off analysis in Engineering Development.

Use it to inspect datasets, test transformation logic, investigate data-quality issues, and explore Data Catalogue, Data Profiled, Data Lineage, Enrichment, Guardrail, and Guardrail Results records.

It does not create data agreements, data contracts, enrichment records, or guardrail rules. Move repeatable ingestion and transformation work into `02_pipeline`.

[Open `99_explore.ipynb`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/templates/notebooks/99_explore.ipynb){ .md-button }

</div>

</div>

Follow the [Guided Demo](guided-demo.md) to create the agreement, run the Development pipeline, define guardrails, validate the pipeline, approve the data contract, and promote the pipeline to Production.
