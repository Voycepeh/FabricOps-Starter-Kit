# Notebook Templates

FabricOps provides five editable Microsoft Fabric notebook templates for creating the workspaces, registering governance metadata, running data pipelines, defining guardrails, approving data contracts, and exploring data.

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

## `01_agreement`

Creates data stewards and records a data agreement between them before pipeline development begins.

After the pipeline has been reviewed and validated, the same notebook creates the data contract, links the registered data tables to the agreement, and records the data steward sign-off required before promotion to Engineering Production.

[Open `01_agreement.ipynb`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/templates/notebooks/01_agreement.ipynb){ .md-button }

</div>

<div class="template-card" markdown="1">

## `02_pipeline`

Reads source data, transforms it, and writes the output to a Fabric lakehouse or warehouse.

It profiles the source and target tables, writes Data Catalogue, Data Profiled, and Data Lineage metadata, reads approved enrichment and guardrail rules, evaluates those rules, and writes the guardrail results.

Develop and validate this notebook in Engineering Development, then promote the completed notebook to Engineering Production.

[Open `02_pipeline.ipynb`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/templates/notebooks/02_pipeline.ipynb){ .md-button }

</div>

<div class="template-card" markdown="1">

## `03_review`

Reads the Data Catalogue and Data Profiled metadata created by `02_pipeline`.

It allows governance users to add table and column descriptions, assign classifications, define schema rules, define data-quality rules, and review the recorded pipeline metadata before data contract approval.

[Open `03_review.ipynb`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/templates/notebooks/03_review.ipynb){ .md-button }

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
