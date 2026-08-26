<div class="fabricops-landing" markdown="1">

# FabricOps documentation

FabricOps is a plug-and-play Data Engineering and Governance practice for Microsoft Fabric.

**Governance → Data engineering → AI and BI analytics**

<p class="fabricops-architecture-image">
  <img src="assets/fabricops-roles.png" alt="FabricOps roles working from a shared governed foundation">
</p>

FabricOps gives teams a planned operating workflow, standardized notebook templates, reusable notebook-facing functions, and a shared metadata model so Governance and Engineering activity is captured as part of the work itself.

Instead of rebuilding governance and documentation afterwards, FabricOps records Data Agreements, Catalogue metadata, profiles, lineage, Enrichment, Guardrails and their results, processing context, and Data Contracts as the workflow runs.

The result is a Production data foundation that can be understood, validated, promoted, reused, and consumed with its Governance and Engineering context intact.

## What is included?

FabricOps includes:

- a Python package of notebook-facing helper and orchestrator functions
- standardized notebook templates for Governance, Engineering, and exploration workflows
- a shared metadata model connecting Governance intent with recorded profiles, lineage, Guardrail Results, and processing context
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
    <span class="fabricops-landing-card__title"><!-- FABRICOPS_PUBLIC_FUNCTION_COUNT --><strong>28</strong><span> public callable functions</span><!-- /FABRICOPS_PUBLIC_FUNCTION_COUNT --></span>
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

## Key FabricOps terms

These are the terms most useful when first reading the workflow. The repository's canonical terminology remains maintained in `docs/reference/_data/glossary.json`.

<details>
<summary><strong>Data Agreement</strong></summary>
<p>A FabricOps agreement record that captures ownership, steward context, usage, and expectations.</p>
</details>

<details>
<summary><strong>Data Catalogue</strong></summary>
<p>The recorded structural metadata for governed tables and columns that Engineering creates and Governance can enrich.</p>
</details>

<details>
<summary><strong>Profile</strong></summary>
<p>Reusable measurements about source data or pipeline outputs, such as schema, row count, nulls, distinct values, and distributions.</p>
</details>

<details>
<summary><strong>Enrichment</strong></summary>
<p>Reviewed descriptive metadata that adds business meaning, ownership, sensitivity, classification, and usage context.</p>
</details>

<details>
<summary><strong>Guardrails</strong></summary>
<p>Approved checks that evaluate schema, freshness, profile behavior, or Data Quality expectations during a pipeline run.</p>
</details>

<details>
<summary><strong>Guardrail Result</strong></summary>
<p>The runtime outcome from evaluating a Guardrail, including pass, fail, or warning details.</p>
</details>

<details>
<summary><strong>Data Contract</strong></summary>
<p>The versioned governed expectations for a table that Production checks resolve and execute against.</p>
</details>

<details>
<summary><strong>Production data</strong></summary>
<p>Approved persisted outputs in Engineering Production that downstream AI, BI, analytics, and data science consumers can use.</p>
</details>

For table-level schemas and writer ownership, see the [metadata reference](reference/metadata/).

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
