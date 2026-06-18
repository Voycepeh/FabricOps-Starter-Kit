# FabricOps Starter Kit

FabricOps Starter Kit is a lightweight Microsoft Fabric operating model for config driven engineering, standardized notebook delivery, metadata collection, and governed pipeline execution.

Use it when analysts, data scientists, engineers, and governance users need to work from the same reusable notebook patterns while keeping setup, evidence, guardrails, lineage, and review decisions visible through shared metadata.

## FabricOps at a glance

<div class="fabricops-kpi-grid" markdown="1">

<div class="fabricops-kpi-card" markdown="1">
  <div class="fabricops-kpi-number">5</div>
  <div class="fabricops-kpi-label">notebook templates</div>
  <p>Reusable notebook patterns for setup, agreement intake, exploration, pipeline execution, and governance review.</p>
  <a href="how-fabricops-works/notebook-templates/">View notebook templates</a>
</div>

<div class="fabricops-kpi-card" markdown="1">
  <div class="fabricops-kpi-number">22</div>
  <div class="fabricops-kpi-label">starter kit functions</div>
  <p>Shared helper functions keep IO, profiling, guardrails, lineage, metadata capture, and review steps consistent across notebooks.</p>
  <a href="reference/">View function reference</a>
</div>

<div class="fabricops-kpi-card" markdown="1">
  <div class="fabricops-kpi-number">23</div>
  <div class="fabricops-kpi-label">native DQ rules</div>
  <p>Built in rule types support metadata driven data quality checks during governed pipeline runs.</p>
  <a href="reference/dq-rules/">View DQ rules</a>
</div>

<div class="fabricops-kpi-card" markdown="1">
  <div class="fabricops-kpi-number">12</div>
  <div class="fabricops-kpi-label">metadata tables</div>
  <p>Shared evidence tables capture configuration, agreements, catalogue records, lineage, DQ results, pipeline runs, and review decisions.</p>
  <a href="how-fabricops-works/metadata-tables/">View metadata tables</a>
</div>

</div>

## Start here

Choose the next page based on what you need to do:

<div class="grid cards" markdown="1">

-   **New to FabricOps?**

    Start with the [Guided Demo](guided-demo.md) to install the helper wheel, copy the templates, and run a smoke test.

-   **Want to understand the operating model?**

    Read [How FabricOps Works](how-fabricops-works/index.md) for the workspace model, role workflow, and metadata movement.

-   **Ready to open and run notebooks?**

    Use [Notebook Templates](how-fabricops-works/notebook-templates.md) to choose which notebook to open, when to run it, and what evidence it creates.

-   **Need implementation details?**

    Browse the generated [Function Reference](reference/index.md) for helper behavior, parameters, and related callable pages.

</div>

## Where to go next

| Page | Use it for |
| --- | --- |
| [Guided Demo](guided-demo.md) | First walkthrough and smoke test path for the starter workflow. |
| [How FabricOps Works](how-fabricops-works/index.md) | Operating model, role workflow, metadata movement, and what FabricOps abstracts. |
| [Notebook Templates](how-fabricops-works/notebook-templates.md) | Practical guide for choosing, opening, and running the starter notebooks. |
| [Function Reference](reference/index.md) | Callable-level implementation details generated from source code and metadata. |
| [Metadata Tables](how-fabricops-works/metadata-tables.md) | Metadata table purposes and evidence records written by the workflow. |
| [Pipeline Guardrails](how-fabricops-works/pipeline-guardrails.md) | Schema, freshness, profile behavior, and approved governance checks used by `02_pipeline`. |
