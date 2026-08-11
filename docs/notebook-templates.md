# Notebook Templates

FabricOps provides four editable Microsoft Fabric notebook templates for configuring the workspaces, registering governance metadata, running data pipelines, defining guardrails, preparing Data Contracts for promotion, and exploring data.

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

Owns the complete Governance lifecycle in one persistent notebook. Use it before Engineering to establish Data Stewards and the Data Agreement, then return after `02_pipeline` has produced evidence to read that catalogue and profile evidence, enrich the Data Catalogue, define guardrails, and later create the Data Contract that prepares the validated ETL workflow for promotion.

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

Follow the [Guided Demo](guided-demo.md) to create the agreement, run the Development pipeline, define guardrails, re-validate the pipeline, prepare the Data Contract, and promote the pipeline to Production.

## Using the templates with AI assistants

The notebook responsibilities do not change when an AI assistant is involved. `00_env_config` remains the source of FabricOps configuration, and `01_governance` remains the Governance workflow. `02_pipeline` remains the place for repeatable ETL, profiling, Data Catalogue, Data Lineage, Guardrail evaluation, and Production promotion. `99_explore` remains the place for one-off exploration and project-specific analytics, AI, BI, and data science work.

Prefer existing FabricOps helper and orchestrator functions rather than recreating the same logic inline. AI-generated changes still require review. See [AI-assisted Data Teams](ai-assisted-data-teams.md) for examples and scope boundaries.
