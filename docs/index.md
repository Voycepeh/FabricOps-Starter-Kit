# FabricOps Starter Kit

FabricOps Starter Kit is a lightweight Microsoft Fabric notebook starter kit for governed, quality checked pipelines.

Use it when you want Fabric notebooks to move data from source to target while keeping useful metadata for review, guardrails, and governance.

## FabricOps at a glance

<div class="fabricops-kpi-grid" markdown="1">

<div class="fabricops-kpi-card" markdown="1">
  <div class="fabricops-kpi-number">5</div>
  <div class="fabricops-kpi-label">notebook templates</div>
  <p>A small starter workflow covers environment setup, agreement intake, exploration, pipeline delivery, and governance review.</p>
  <a href="how-fabricops-works/notebook-templates/">View notebook templates</a>
</div>

<div class="fabricops-kpi-card" markdown="1">
  <div class="fabricops-kpi-number">33</div>
  <div class="fabricops-kpi-label">reusable callables</div>
  <p>Notebook-friendly helper functions keep repeated setup, IO, profiling, guardrails, lineage, and review steps consistent.</p>
  <a href="reference/">View function reference</a>
</div>

<div class="fabricops-kpi-card" markdown="1">
  <div class="fabricops-kpi-number">23</div>
  <div class="fabricops-kpi-label">native DQ rules</div>
  <p>Built-in data quality rule types support approved metadata-driven checks during later pipeline runs.</p>
  <a href="reference/dq-rules/">View DQ rules</a>
</div>

<div class="fabricops-kpi-card" markdown="1">
  <div class="fabricops-kpi-number">12</div>
  <div class="fabricops-kpi-label">metadata tables</div>
  <p><code>00_env_config</code> prepares the governed evidence tables used by agreement, notebook registry, catalogue, lineage, DQ, pipeline, and review workflows.</p>
  <a href="how-fabricops-works/metadata-tables/">View metadata tables</a>
</div>

</div>

## Start here

Choose where to begin:

<div class="home-cta" markdown="1">

[Guided Demo](guided-demo.md){ .md-button .md-button--primary }

[How FabricOps Works](how-fabricops-works/index.md){ .md-button }

[Notebook Templates](how-fabricops-works/notebook-templates.md){ .md-button }

</div>

## Where to go next

| Page | Use it for |
| --- | --- |
| [Guided Demo](guided-demo.md) | Install the helper wheel, copy the templates, and run a Fabric smoke test. |
| [How FabricOps Works](how-fabricops-works/index.md) | Understand the target delivery workflow from Agreement to Pipeline to Review. |
| [Notebook Templates](how-fabricops-works/notebook-templates.md) | See what each notebook template is for. |
| [Metadata Tables](how-fabricops-works/metadata-tables.md) | See what metadata the notebooks write and read. |
| [Pipeline Guardrails](how-fabricops-works/pipeline-guardrails.md) | Understand how `02_pipeline` checks schema, freshness, profile behavior, and approved governance metadata. |
| [Governance Review](how-fabricops-works/governance-review.md) | Understand how `03_governance` adds reviewed governance metadata. |
