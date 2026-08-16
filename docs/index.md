<div class="fabricops-landing" markdown="1">

# FabricOps documentation

FabricOps is a lightweight starter kit that connects:

**Governance → Data engineering → AI and BI analytics**

Governance defines ownership and approval. Data engineering develops pipelines and records how data was prepared and checked. Approved pipelines are promoted from Engineering Development to Engineering Production, where AI and BI analytics can use approved Production data.

<section class="fabricops-delivery-model" aria-labelledby="what-is-fabricops" markdown="1">

## What is FabricOps?

<p class="fabricops-architecture-image">
  <img src="assets/fabricops-roles.png" alt="FabricOps roles working from a shared governed foundation">
</p>

FabricOps, short for Fabric Operations, is a plug-and-play, lightweight starter kit that helps data teams quickly set up and adopt an out-of-the-box workflow within the Microsoft Fabric platform.

- Governance
- Data engineering
- AI and BI analytics

</section>

By standardizing these workflows, FabricOps ensures that essential metadata and governance processes are built directly into engineering pipelines.

The workflow connects:

- **Governance:** Data Stewards, Data Agreements, Enrichment, Guardrails, and Data Contracts.
- **Data engineering:** ETL, Data Catalogue, Data Profiled, Data Profiled Frequency, Data Lineage, Guardrail Results, and Development-to-Production promotion.
- **AI and BI analytics:** approved Production data for Power BI, fabric data agents, data analysis, and data science.

## What is included?

FabricOps consists of:

- A Python package containing out-of-the-box helper and orchestrator functions
- Standardized Python notebook templates that weave these functions into reusable workflows
- A set of shared metadata tables that connects governance and engineering activities
- A guided demo to help teams understand and adopt the workflow quickly
- Technical documentation for the notebook templates, metadata tables, and individual functions

</div>

## Quick Links

<div class="fabricops-card-grid">
  <a class="fabricops-landing-card" href="how-fabricops-works/">
    <span class="fabricops-landing-card__title">How FabricOps Works</span>
    <span class="fabricops-landing-card__body">Understand the workspace, notebook and metadata architecture, engineering + governance workflow and development production promotion.</span>
  </a>

  <a class="fabricops-landing-card" href="guided-demo/">
    <span class="fabricops-landing-card__title">Guided Demo</span>
    <span class="fabricops-landing-card__body">Follow the step-by-step guide to set up, configure, and perform the engineering + governance workflow.</span>
  </a>

  <a class="fabricops-landing-card" href="solutions/">
    <span class="fabricops-landing-card__title">Solution Bank</span>
    <span class="fabricops-landing-card__body">See practical problems already solved by FabricOps and the notebook workflows and functions that implement them.</span>
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
    <span class="fabricops-landing-card__body">Download the latest notebooks here.</span>
  </a>

  <a class="fabricops-landing-card" href="reference/">
    <span class="fabricops-landing-card__title"><!-- FABRICOPS_PUBLIC_FUNCTION_COUNT --><strong>26</strong><span> public callable functions</span><!-- /FABRICOPS_PUBLIC_FUNCTION_COUNT --></span>
    <span class="fabricops-landing-card__body">Search and read the function documentations.</span>
  </a>

  <a class="fabricops-landing-card" href="reference/metadata/">
    <span class="fabricops-landing-card__title"><!-- FABRICOPS_METADATA_TABLE_COUNT --><strong>13</strong><span> metadata tables</span><!-- /FABRICOPS_METADATA_TABLE_COUNT --></span>
    <span class="fabricops-landing-card__body">Read every metadata table's purpose, schema, and know which functions write to them.</span>
  </a>

  <a class="fabricops-landing-card" href="reference/dq-rules/">
    <span class="fabricops-landing-card__title">23 data quality rule types</span>
    <span class="fabricops-landing-card__body">Explore supported data quality rules that can be used as guardrails.</span>
  </a>
</div>

## Maintain FabricOps

<div class="fabricops-card-grid">
  <a class="fabricops-landing-card" href="function-call-graph/">
    <span class="fabricops-landing-card__title">Function Call Graph</span>
    <span class="fabricops-landing-card__body">Monitor public function architecture violations, their underlying call flows and nested functions for optimization and code cleanliness.</span>
  </a>

  <a class="fabricops-landing-card" href="maintainer/">
    <span class="fabricops-landing-card__title">Maintainer Guide</span>
    <span class="fabricops-landing-card__body">Based on the skills, a human-readable version of the repository maintenance and release workflow.</span>
  </a>

  <a class="fabricops-landing-card" href="maintainer/product-definition/">
    <span class="fabricops-landing-card__title">Product Definition</span>
    <span class="fabricops-landing-card__body">The original foundational product terminology, responsibilities, and workflow used as truth.</span>
  </a>
</div>