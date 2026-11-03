<div class="fabricops-product-page" markdown="1">

# Governed engineering for Microsoft Fabric

**FabricOps Starter Kit connects reusable notebook pipelines with governance decisions that Engineering can inspect and validate.** Start with the outcome, then go as deep as the implementation requires.

<video class="fabricops-page-video" controls preload="metadata" aria-label="FabricOps Starter Kit overview video">
  <source src="assets/FabricOps_Overview_Video_web.mp4" type="video/mp4">
  Your browser does not support embedded video. <a href="assets/FabricOps_Overview_Video_web.mp4">Open the FabricOps overview video</a>.
</video>

## Two foundations, one workflow

![Governance and Engineering working in a continuous FabricOps cycle](assets/fabricops-roles.png){ .fabricops-home-loop }

FabricOps keeps project-specific PySpark visible between governed boundaries. Governance can work from Engineering observations and profiles; Engineering can trace expectations to exact contract versions and Guardrail Results.

<div class="fabricops-foundations">
  <a class="fabricops-card" href="engineering/">
    <strong>Engineering</strong>
    <small>Build portable Read → Transform → Write pipelines across Lakehouses and Warehouses, with incremental processing, recovery, profiling and lineage.</small>
  </a>
  <a class="fabricops-card" href="governance/">
    <strong>Governance</strong>
    <small>Turn steward decisions, Data Contracts, Enrichment and Guardrails into structured metadata connected to the real engineering flow.</small>
  </a>
</div>

See [Architecture](architecture.md) for the workspace topology, Governance ↔ Engineering cycle, shared metadata and consumer hand-off.

<a class="fabricops-metadata-preview" href="reference/metadata/" aria-label="Explore the interactive FabricOps metadata tables map">
  <span class="fabricops-metadata-preview__body">
    <span class="fabricops-metadata-preview__eyebrow">Interactive reference</span>
    <strong class="fabricops-metadata-preview__title">Explore the Metadata Tables map</strong>
    <span class="fabricops-metadata-preview__description">See how Governance and Engineering tables connect, then inspect their keys, relationships and schemas.</span>
    <span class="fabricops-metadata-preview__action">Open interactive map <span aria-hidden="true">→</span></span>
  </span>
  <span class="fabricops-metadata-preview__image" aria-hidden="true">
    <img src="assets/fabricops-metadata-approved.svg" alt="" loading="lazy" decoding="async">
  </span>
</a>

<a class="fabricops-metadata-preview fabricops-guided-preview" href="guided-demo/" aria-label="Start the seven-step FabricOps Guided Demo">
  <span class="fabricops-metadata-preview__body">
    <span class="fabricops-metadata-preview__eyebrow">Guided implementation</span>
    <strong class="fabricops-metadata-preview__title">Run the seven-step FabricOps lifecycle</strong>
    <span class="fabricops-metadata-preview__description">Prepare Microsoft Fabric, build the pipeline, author and preview Data Contracts, then follow the Production and consumption hand-offs.</span>
    <span class="fabricops-metadata-preview__action">Start Guided Demo <span aria-hidden="true">→</span></span>
  </span>
  <span class="fabricops-metadata-preview__image" aria-hidden="true">
    <img src="assets/fabricops-role-workflow.png" alt="" loading="eager" decoding="async">
  </span>
</a>

## Download FabricOps

Get the Python package, reusable notebook templates, and demo assets to start building. Follow the Guided Demo above to put them to work.

<nav class="fabricops-resource-list" aria-label="Download FabricOps resources">
  <a href="releases/">Releases <small>Python package</small></a>
  <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/tree/main/templates/notebooks">Notebook Templates <small>Reusable Fabric notebooks</small></a>
  <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/tree/main/templates/DemoData">Demo Assets <small>Sample data for the walkthrough</small></a>
</nav>

## Reference Documentation

Explore FabricOps functions, Data Quality rules, metadata structures, and implementation guidance.

<nav class="fabricops-resource-list" aria-label="FabricOps reference documentation">
  <a href="reference/">Function Reference</a>
  <a href="reference/dq-rules/">Data Quality Rules</a>
  <a href="reference/metadata/">Metadata Tables</a>
  <a href="reference/pyspark-transformation/">PySpark Transformation</a>
  <a href="glossary/">Glossary</a>
</nav>

## What is available today?

Core notebook setup, Fabric I/O, pipeline orchestration, profiling and metadata capture are **Live** public capabilities. Data Contract authoring, activation and AI-assisted authoring remain **Preview**. Governed execution currently fails closed until trusted deployment verification is integrated; use the reference lifecycle labels for the authoritative status of each callable.

</div>
