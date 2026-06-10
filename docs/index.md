# FabricOps Starter Kit

FabricOps Starter Kit is a lightweight Microsoft Fabric notebook starter kit for governed, quality checked pipelines.

Use it when you want Fabric notebooks to move data from source to target while keeping useful metadata for review, guardrails, and governance.

## FabricOps at a glance

<div class="grid cards" markdown>

-   **5 notebook templates**

    A small starter workflow covers environment setup, agreement intake, exploration, pipeline delivery, and governance review.

    [View notebook templates](how-fabricops-works/notebook-templates.md)

-   **30 reusable callables**

    Notebook-friendly helper functions keep repeated setup, IO, profiling, guardrails, lineage, and review steps consistent.

    [View function reference](reference/index.md)

-   **9 Python modules**

    The package is organized into focused implementation modules for setup, agreement, profiling, IO, lineage, drift, governance review, metadata, and pipeline support.

    [View module catalogue](api/modules/index.md)

-   **23 native DQ rules**

    Built-in data quality rule types support approved metadata-driven checks during later pipeline runs.

    [View DQ rules](reference/dq-rules/index.md)

-   **11 metadata tables**

    `00_env_config` prepares the governed evidence tables used by agreement, notebook registry, catalogue, lineage, DQ, pipeline, and review workflows.

    [View metadata tables](how-fabricops-works/metadata-tables.md)

</div>

## Start here

Choose where to begin:

<div class="home-cta" markdown="1">

[Quick Start](quick-start.md){ .md-button .md-button--primary }

[How FabricOps Works](how-fabricops-works/index.md){ .md-button }

[Notebook Templates](how-fabricops-works/notebook-templates.md){ .md-button }

</div>

## Where to go next

| Page | Use it for |
| --- | --- |
| [Quick Start](quick-start.md) | Install the helper wheel, copy the templates, and run a Fabric smoke test. |
| [How FabricOps Works](how-fabricops-works/index.md) | Understand the target delivery workflow from Agreement to Pipeline to Review. |
| [Notebook Templates](how-fabricops-works/notebook-templates.md) | See what each notebook template is for. |
| [Metadata Tables](how-fabricops-works/metadata-tables.md) | See what metadata the notebooks write and read. |
| [Pipeline Guardrails](how-fabricops-works/schema-and-data-drift.md) | Understand how `02_pipeline` checks schema, drift, and approved governance metadata. |
| [Governance Review](how-fabricops-works/governance-review.md) | Understand how `03_governance` adds reviewed governance metadata. |
