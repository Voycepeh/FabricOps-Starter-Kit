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

## Choose your route

<div class="fabricops-capability-grid">
  <a class="fabricops-card" href="architecture/"><strong>Architecture</strong><small>See the workspace topology, Governance ↔ Engineering cycle, shared metadata and consumer hand-off.</small></a>
  <a class="fabricops-card" href="reference/"><strong>Function Reference</strong><small>Inspect lifecycle status, signatures, behavior, source locations and call flows for public functions.</small></a>
</div>

## What is available today?

Core notebook setup, Fabric I/O, pipeline orchestration, profiling and metadata capture are **Live** public capabilities. Data Contract authoring, activation and AI-assisted authoring remain **Preview**. Governed execution currently fails closed until trusted deployment verification is integrated; use the reference lifecycle labels for the authoritative status of each callable.

<div class="fabricops-cta-row" markdown="1">
[Run the Guided Demo](guided-demo.md){ .md-button .md-button--primary }
</div>

</div>
