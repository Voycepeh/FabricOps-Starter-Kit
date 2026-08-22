<div class="fabricops-landing" markdown="1">

# FabricOps documentation

FabricOps is a plug-and-play, lightweight starter kit for governed, quality-checked Microsoft Fabric notebook workflows across:

**Governance → Data engineering → AI and BI analytics**

<p class="fabricops-architecture-image">
  <img src="assets/fabricops-roles.png" alt="FabricOps roles working from a shared governed foundation">
</p>

FabricOps builds governance and metadata collection into the engineering workflow instead of treating them as after-the-fact documentation. Engineering develops and validates reusable pipelines, Engineering Production runs against governed definitions, and AI and BI consumers use the resulting Production data foundation.

## What is included?

FabricOps includes:

- a Python package of notebook-facing helper and orchestrator functions
- standardized notebook templates for Governance, Engineering, and exploration workflows
- a shared metadata model connecting observed Engineering evidence with Governance intent
- a Guided Demo with practical steps and expandable technical rationale
- generated technical references for functions, metadata tables, and data-quality rules

</div>

## Quick Links

<div class="fabricops-card-grid">
  <a class="fabricops-landing-card" href="how-fabricops-works/">
    <span class="fabricops-landing-card__title">How FabricOps Works</span>
    <span class="fabricops-landing-card__body">Understand the workspace model, Governance and Engineering workflow, ETL operating model, metadata flow, and Production consumption pattern.</span>
  </a>

  <a class="fabricops-landing-card" href="guided-demo/">
    <span class="fabricops-landing-card__title">Guided Demo</span>
    <span class="fabricops-landing-card__body">Follow the step-by-step workflow and expand the technical notes to understand why FabricOps uses each pattern.</span>
  </a>

  <a class="fabricops-landing-card" href="maintainer/product-definition/">
    <span class="fabricops-landing-card__title">Product Definition</span>
    <span class="fabricops-landing-card__body">Read the source of truth for FabricOps terminology, operating decisions, responsibilities, and product boundaries.</span>
  </a>

  <a class="fabricops-landing-card" href="releases/">
    <span class="fabricops-landing-card__title">Releases</span>
    <span class="fabricops-landing-card__body">View published releases and their included assets.</span>
  </a>
</div>

## Technical lookup

<div class="fabricops-card-grid">
  <a class="fabricops-landing-card" href="notebook-templates/">
    <span class="fabricops-landing-card__title">4 Notebook Templates</span>
    <span class="fabricops-landing-card__body">Download the latest notebook templates.</span>
  </a>

  <a class="fabricops-landing-card" href="reference/">
    <span class="fabricops-landing-card__title"><!-- FABRICOPS_PUBLIC_FUNCTION_COUNT --><strong>29</strong><span> public callable functions</span><!-- /FABRICOPS_PUBLIC_FUNCTION_COUNT --></span>
    <span class="fabricops-landing-card__body">Search the notebook-facing callable reference.</span>
  </a>

  <a class="fabricops-landing-card" href="reference/metadata/">
    <span class="fabricops-landing-card__title"><!-- FABRICOPS_METADATA_TABLE_COUNT --><strong>13</strong><span> metadata tables</span><!-- /FABRICOPS_METADATA_TABLE_COUNT --></span>
    <span class="fabricops-landing-card__body">Review each metadata table's purpose, schema, and writer ownership.</span>
  </a>

  <a class="fabricops-landing-card" href="reference/dq-rules/">
    <span class="fabricops-landing-card__title">11 data quality rule types</span>
    <span class="fabricops-landing-card__body">Explore the supported DQ rules available for Guardrails.</span>
  </a>
</div>

## Maintain FabricOps

<div class="fabricops-card-grid">
  <a class="fabricops-landing-card" href="function-call-graph/">
    <span class="fabricops-landing-card__title">Function Call Graph</span>
    <span class="fabricops-landing-card__body">Inspect public callable architecture, call flows, nested functions, and architecture violations.</span>
  </a>

  <a class="fabricops-landing-card" href="maintainer/">
    <span class="fabricops-landing-card__title">Maintainer Guide</span>
    <span class="fabricops-landing-card__body">Follow the repository maintenance and release workflow.</span>
  </a>
</div>