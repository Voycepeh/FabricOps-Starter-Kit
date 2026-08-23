<div class="fabricops-landing" markdown="1">

# FabricOps documentation

FabricOps is a plug-and-play Data Engineering and Governance practice for Microsoft Fabric.

**Governance → Data engineering → AI and BI analytics**

<p class="fabricops-architecture-image">
  <img src="assets/fabricops-roles.png" alt="FabricOps roles working from a shared governed foundation">
</p>

FabricOps gives teams a planned operating workflow, standardized notebook templates, reusable notebook-facing functions, and a shared metadata model so Governance and Engineering activity is captured as part of the work itself.

Instead of rebuilding governance and documentation afterwards, FabricOps is designed to write the relevant data products and supporting evidence into the configured Fabric workspaces, Lakehouses, Warehouses, and metadata tables while the workflow runs. That includes Catalogue metadata, profiling, lineage, Guardrail results, governed processing context, and Data Contracts where those capabilities are implemented.

The result is a Production data foundation that can be understood, validated, promoted, reused, and consumed with its Governance and Engineering context intact.

## What is included?

FabricOps includes:

- a Python package of notebook-facing helper and orchestrator functions
- standardized notebook templates for Governance, Engineering, and exploration workflows
- a shared metadata model connecting observed Engineering evidence with Governance intent
- a Guided Demo with practical steps and expandable technical rationale
- generated technical references for functions, metadata tables, and data-quality rules
- a planned future direction for AI-augmented Governance and Engineering workflows built on the structured context FabricOps captures

</div>

## Start here

<div class="fabricops-card-grid">
  <a class="fabricops-landing-card" href="how-fabricops-works/">
    <span class="fabricops-landing-card__title">How FabricOps works</span>
    <span class="fabricops-landing-card__body">See how the workspaces, Governance, Engineering, ETL, metadata, and Production flow fit together.</span>
  </a>

  <a class="fabricops-landing-card" href="maintainer/product-definition/">
    <span class="fabricops-landing-card__title">What we envisioned FabricOps to be</span>
    <span class="fabricops-landing-card__body">Read the Product Definition: the source of truth for terminology, decisions, boundaries, and future direction.</span>
  </a>

  <a class="fabricops-landing-card" href="guided-demo/">
    <span class="fabricops-landing-card__title">Step-by-step Guided Demo</span>
    <span class="fabricops-landing-card__body">Follow the workflow in order, with expandable notes explaining the important technical choices.</span>
  </a>

  <a class="fabricops-landing-card" href="releases/">
    <span class="fabricops-landing-card__title">Official releases</span>
    <span class="fabricops-landing-card__body">View published FabricOps releases and the assets included in each version.</span>
  </a>
</div>

## FabricOps Assets

<div class="fabricops-card-grid">
  <a class="fabricops-landing-card" href="notebook-templates/">
    <span class="fabricops-landing-card__title">4 Notebook Templates</span>
    <span class="fabricops-landing-card__body">Download the latest reusable FabricOps notebook templates.</span>
  </a>

  <a class="fabricops-landing-card" href="reference/">
    <span class="fabricops-landing-card__title"><!-- FABRICOPS_PUBLIC_FUNCTION_COUNT --><strong>29</strong><span> public callable functions</span><!-- /FABRICOPS_PUBLIC_FUNCTION_COUNT --></span>
    <span class="fabricops-landing-card__body">Search the notebook-facing FabricOps callable reference.</span>
  </a>

  <a class="fabricops-landing-card" href="reference/metadata/">
    <span class="fabricops-landing-card__title"><!-- FABRICOPS_METADATA_TABLE_COUNT --><strong>13</strong><span> metadata tables</span><!-- /FABRICOPS_METADATA_TABLE_COUNT --></span>
    <span class="fabricops-landing-card__body">Review each metadata table, its schema, purpose, and writer ownership.</span>
  </a>

  <a class="fabricops-landing-card" href="reference/dq-rules/">
    <span class="fabricops-landing-card__title">11 data quality rule types</span>
    <span class="fabricops-landing-card__body">Explore the supported Data Quality rules available for Guardrails.</span>
  </a>
</div>

## Maintain FabricOps

<div class="fabricops-card-grid">
  <a class="fabricops-landing-card" href="function-call-graph/">
    <span class="fabricops-landing-card__title">Function Call Graph</span>
    <span class="fabricops-landing-card__body">Inspect callable architecture, call flows, nested functions, and architecture violations.</span>
  </a>

  <a class="fabricops-landing-card" href="maintainer/">
    <span class="fabricops-landing-card__title">Maintainer Guide</span>
    <span class="fabricops-landing-card__body">Follow the repository maintenance and release workflow.</span>
  </a>
</div>