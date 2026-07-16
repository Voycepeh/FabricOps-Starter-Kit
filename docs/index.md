<div class="fabricops-landing" markdown="1">

# FabricOps Starter Kit

FabricOps (Fabric Operations) is a plug-and-play, lightweight starter kit that helps data teams quickly set up and adopt a standardized notebook workflow in Microsoft Fabric.

It is designed for teams working across governance, data engineering, and AI and BI analytics. FabricOps combines a Python package of ready-to-use helper and orchestrator functions, standardized notebook templates, shared metadata tables, a Guided Demo, and technical reference documentation.

By standardizing the workflow, FabricOps weaves essential metadata and governance processes into everyday notebook development. This gives teams a consistent foundation for data quality, lineage, handover, and AI-assisted development without having to build every supporting process from scratch.

## Why this starter kit exists

Data teams often include people with different governance, engineering, analytics, and data science backgrounds. Without a common structure, each project can configure Fabric items, organize notebooks, capture metadata, apply data quality checks, and hand over work differently.

FabricOps provides a shared starting point. The notebook templates make the workflow visible, the Python package abstracts repeated Fabric operations, and the metadata tables preserve the context and evidence needed by the next person or AI agent working on the project.

FabricOps is a lightweight starter kit, not a full engineering framework, a standalone governance platform, or a standalone data quality product.

<section class="fabricops-delivery-model" aria-labelledby="fabricops-workflow-model-heading" markdown="1">

## How FabricOps connects data teams { #fabricops-workflow-model-heading }

<p class="fabricops-architecture-image">
  <img src="assets/fabricops-roles.png" alt="Governance, data engineering, and AI and BI analytics teams working from a shared FabricOps foundation">
</p>

Governance, data engineering, and AI and BI analytics teams work through the same notebook flow while keeping clear responsibilities.

- Governance records agreement context, enriches metadata, and reviews guardrail intent and results.
- Data engineering configures Fabric targets, develops pipelines, profiles data, and writes governed outputs.
- AI and BI analytics users consume trusted outputs and metadata for analysis, reporting, modelling, and exploration.

The shared metadata tables act as the handoff layer. They record what was agreed, what data was observed, what checks were approved, what happened during execution, and what is ready for review.

</section>

## Follow the story

<div class="fabricops-card-grid">
  <a class="fabricops-landing-card" href="how-fabricops-works/">
    <span class="fabricops-landing-card__title">1. Understand how FabricOps works</span>
    <span class="fabricops-landing-card__body">See how the notebook templates, Python package, roles, Fabric items, and metadata tables work together.</span>
  </a>
  <a class="fabricops-landing-card" href="guided-demo/">
    <span class="fabricops-landing-card__title">2. Run the Guided Demo</span>
    <span class="fabricops-landing-card__body">Set up the Fabric artifacts, run the workflow in order, and inspect the evidence it creates.</span>
  </a>
  <a class="fabricops-landing-card" href="notebook-templates-implementation-guide/">
    <span class="fabricops-landing-card__title">3. Start your own project</span>
    <span class="fabricops-landing-card__body">Download the notebook templates, then use the reference pages while adapting the workflow.</span>
  </a>
</div>

## What is included

<div class="fabricops-card-grid">
  <a class="fabricops-landing-card" href="notebook-templates-implementation-guide/">
    <span class="fabricops-landing-card__title">5 main notebook templates</span>
    <span class="fabricops-landing-card__body">A visible workflow for environment setup, agreements, pipelines, governance review, and optional exploration.</span>
  </a>

  <a class="fabricops-landing-card" href="reference/">
    <span class="fabricops-landing-card__title"><!-- FABRICOPS_PUBLIC_FUNCTION_COUNT --><strong>24</strong><span> public callable functions</span><!-- /FABRICOPS_PUBLIC_FUNCTION_COUNT --></span>
    <span class="fabricops-landing-card__body"><!-- FABRICOPS_CALLABLE_RECORD_COUNT -->Ready-to-use helper and orchestrator functions support the notebook templates while implementation details stay behind the public API<!-- /FABRICOPS_CALLABLE_RECORD_COUNT -->.</span>
  </a>

  <a class="fabricops-landing-card" href="reference/dq-rules/">
    <span class="fabricops-landing-card__title">23 native DQ rule types</span>
    <span class="fabricops-landing-card__body">Metadata-driven data quality checks reviewed through governance and enforced during pipeline runs.</span>
  </a>

  <a class="fabricops-landing-card" href="reference/metadata/">
    <span class="fabricops-landing-card__title"><!-- FABRICOPS_METADATA_TABLE_COUNT --><strong>10</strong><span> metadata tables</span><!-- /FABRICOPS_METADATA_TABLE_COUNT --></span>
    <span class="fabricops-landing-card__body">Shared evidence for stewards, agreements, contracts, catalogue identities, profiles, lineage, access, enrichment, guardrails, and guardrail results.</span>
  </a>

  <a class="fabricops-landing-card" href="guided-demo/">
    <span class="fabricops-landing-card__title">Guided Demo</span>
    <span class="fabricops-landing-card__body">A maintained end-to-end path from Fabric workspace setup through governance review and metadata exploration.</span>
  </a>
</div>

## Use the reference when you need detail

<div class="fabricops-card-grid">
  <a class="fabricops-landing-card" href="reference/">
    <span class="fabricops-landing-card__title">Function Reference</span>
    <span class="fabricops-landing-card__body">Look up signatures, parameters, examples, return meaning, errors, lifecycle status, and call flows.</span>
  </a>
  <a class="fabricops-landing-card" href="reference/metadata/">
    <span class="fabricops-landing-card__title">Metadata Table Reference</span>
    <span class="fabricops-landing-card__body">Understand what each implemented metadata table stores and which functions manage its fields.</span>
  </a>
  <a class="fabricops-landing-card" href="reference/dq-rules/">
    <span class="fabricops-landing-card__title">DQ Rule Reference</span>
    <span class="fabricops-landing-card__body">Choose the smallest rule that expresses an approved data quality expectation.</span>
  </a>
  <a class="fabricops-landing-card" href="releases/">
    <span class="fabricops-landing-card__title">Releases</span>
    <span class="fabricops-landing-card__body">See which functions and metadata contracts are Live, Preview, or Discontinued in each version.</span>
  </a>
</div>

## For maintainers

Use the [FabricOps Maintainer Guide](maintainer/index.md) for release preparation and the [Product Narrative](maintainer/product-narrative.md) when updating user-facing messaging. Use [Public API & Architecture](maintainer/public-api-architecture.md) to review public API boundaries and generated call-flow contracts.

The [Public Function Call Flows Dashboard](assets/public-function-call-flows-dashboard.html) provides the detailed architecture view for maintainers working on callable structure and refactoring.

<p><small>Function and metadata metrics are generated from the current repository inventory.</small></p>

</div>
