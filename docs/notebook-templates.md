# Notebook Templates

**FabricOps provides four editable Microsoft Fabric notebook templates that cover environment setup, Governance, repeatable Engineering pipelines, and downstream exploration.**

[Open all notebook templates on GitHub](https://github.com/Voycepeh/FabricOps-Starter-Kit/tree/main/templates/notebooks){ .md-button .md-button--primary }

<div class="template-list" markdown="1">

<div class="template-card" markdown="1">

## `00_env_config`

**Controls the shared FabricOps operating configuration.**

Use it to define:

- Governance, Engineering Development, and Engineering Production workspace settings
- Lakehouse and Warehouse names and paths
- metadata table routing
- package and runtime settings
- audit settings
- widget settings

Run it in each workspace before using the other FabricOps notebooks.

[Open `00_env_config.ipynb`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/templates/notebooks/00_env_config.ipynb){ .md-button }

</div>

<div class="template-card" markdown="1">

## `01_governance`

**Owns the Governance lifecycle around the engineering workflow.**

Use it to:

- create Data Stewards and Data Agreements
- review Data Catalogue, Data Profiled, and Data Lineage records written by `02_pipeline`
- select a governed `table_id`, author descriptive Enrichment and enforced Guardrails, review the definition, and freeze an immutable Data Contract version
- after Development validation, explicitly link the tested frozen version to a Data Agreement version and activate it for Production

The operating pattern is **Governance → Engineering → Governance**: `01_governance` → `02_pipeline` → `01_governance`.

[Open `01_governance.ipynb`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/templates/notebooks/01_governance.ipynb){ .md-button }

</div>

<div class="template-card" markdown="1">

## `02_pipeline`

**Runs repeatable ETL, profiling, metadata registration, and Guardrail evaluation.**

Use it to:

- read source data
- transform the data
- profile source and target tables
- write Data Catalogue, Data Profiled, Data Profiled Frequency where applicable, and Data Lineage records
- discover linked `table_id` values from the current notebook's `METADATA_DATA_LINEAGE`
- select one frozen Data Contract version per linked table in Development; resolve exactly one active version per linked table automatically in Production
- evaluate Guardrails and write Guardrail Results
- write the governed target output

Develop and validate this notebook in Engineering Development, then promote the validated notebook to Engineering Production.

[Open `02_pipeline.ipynb`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/templates/notebooks/02_pipeline.ipynb){ .md-button }

</div>

<div class="template-card" markdown="1">

## `99_explore`

**Supports project-specific exploration of governed Production data and FabricOps metadata.**

Use it to:

- inspect governed Production datasets
- test analysis or transformation ideas
- investigate data-quality issues
- explore Data Catalogue, Data Profiled, Data Lineage, Enrichment, Guardrail, and Guardrail Results records
- support AI, BI, and data analysis in a Project-Specific Consumer workspace

!!! note "Keep repeatable preparation in `02_pipeline`"

    `99_explore` is for analysis and experimentation. Move preparation that must become stable, recurring, or operational into the governed `02_pipeline` workflow.

[Open `99_explore.ipynb`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/templates/notebooks/99_explore.ipynb){ .md-button }

</div>

</div>

## Next step

Follow the [Guided Demo](guided-demo.md) through **Author → Freeze → Select → Validate → Link Data Agreement → Activate → Promote → Run Production**, then consume approved Production data.
