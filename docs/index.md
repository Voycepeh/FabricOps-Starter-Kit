# FabricOps Starter Kit

FabricOps Starter Kit is a lightweight Microsoft Fabric notebook starter kit for governed, quality checked pipelines.

Use it when you want Fabric notebooks to move data from source to target while keeping useful metadata for review, guardrails, and governance.

## Start fast

New to the kit? Start with [Quick Start](quick-start.md).

Want to understand the workflow? Read [How FabricOps Works](how-fabricops-works/index.md).

Need the notebook files? Open [Notebook Templates](how-fabricops-works/notebook-templates.md).

<div class="home-cta" markdown="1">

[Quick Start](quick-start.md){ .md-button .md-button--primary }

[How FabricOps Works](how-fabricops-works/index.md){ .md-button }

</div>

## Main flow

`01_da` captures the agreement, steward, and context.

`03_pc` pipes data from source to target and captures key metadata such as data profile, lineage, schema, and data drift details.

`04_gov` uses that metadata to add business context, data quality rules, data sensitivity, and classification.

When the pipeline runs again, `03_pc` uses the approved rules and classifications alongside schema and data drift guardrails.

## Where to go next

| Page | Use it for |
| --- | --- |
| [Quick Start](quick-start.md) | Install the helper wheel, copy the templates, and run a Fabric smoke test. |
| [How FabricOps Works](how-fabricops-works/index.md) | Understand the target workflow from agreement to pipeline enforcement. |
| [Notebook Templates](how-fabricops-works/notebook-templates.md) | See what each notebook template is for. |
| [Metadata Tables](how-fabricops-works/metadata-tables.md) | See what metadata the notebooks write and read. |
| [Pipeline Guardrails](schema-and-data-drift.md) | Understand how `03_pc` checks schema, drift, and approved governance metadata. |
| [Governance Review](data-quality-rules-system.md) | Understand how `04_gov` adds reviewed governance metadata. |
