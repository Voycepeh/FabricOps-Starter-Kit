<div class="fabricops-landing" markdown="1">

# FabricOps documentation

FabricOps is a plug-and-play Data Engineering and Governance practice for Microsoft Fabric.

**Governance → Data engineering → AI and BI analytics**

<p class="fabricops-architecture-image">
  <img src="assets/fabricops-roles.png" alt="FabricOps roles working from a shared governed foundation">
</p>

FabricOps gives teams a planned operating workflow, standardized notebook templates, reusable notebook-facing functions, and a shared metadata model so Governance and Engineering activity is captured as part of the work itself.

Instead of rebuilding governance and documentation afterwards, FabricOps records Data Agreements, Catalogue metadata, profiles, lineage, source observations, resolved read strategies, governed load strategies and parameters, Enrichment, Guardrails and their results, and Data Contracts as the workflow runs.

The result is a Production data foundation that can be understood, validated, promoted, reused, and consumed with its Governance and Engineering context intact.

## What is included?

FabricOps includes:

- a Python package of notebook-facing helper and orchestrator functions
- standardized notebook templates for Governance, Engineering, and exploration workflows
- a shared metadata model connecting Governance intent with recorded profiles, lineage, source observations, resolved read strategies, governed load strategies and parameters, and Guardrail Results
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

These are the core terms most useful when first reading the workflow. The canonical definitions and supporting Microsoft Fabric, Data Engineering, security, and configuration terms are maintained in `docs/reference/_data/glossary.json`.

<details>
<summary><strong>FabricOps Starter Kit</strong></summary>
<p>A plug-and-play Data Engineering and Governance practice for Microsoft Fabric.</p>
</details>

<details>
<summary><strong>Profile</strong></summary>
<p>A summary of the data at a point in time, including structure, row counts, nulls, distinct values, ranges, and distributions.</p>
</details>

<details>
<summary><strong>Enrichment</strong></summary>
<p>Business and governance information added to the Data Catalogue after technical metadata has been captured.</p>
</details>

<details>
<summary><strong>Guardrails</strong></summary>
<p>The governed rules FabricOps applies to data and pipelines.</p>
</details>

<details>
<summary><strong>Enforcement</strong></summary>
<p>Applying active Guardrails during a pipeline run and acting on the result by continuing, warning, or stopping.</p>
</details>

<details>
<summary><strong>Guardrail Result</strong></summary>
<p>The recorded outcome after FabricOps evaluates a Guardrail during a pipeline run.</p>
</details>

<details>
<summary><strong>Data Steward</strong></summary>
<p>The person or role responsible for reviewing and maintaining the governance context for data.</p>
</details>

<details>
<summary><strong>Data Agreement</strong></summary>
<p>The governed record that establishes who is sharing what data, with whom, and why.</p>
</details>

<details>
<summary><strong>Data Contract</strong></summary>
<p>The approved definition of what is expected from governed Production data.</p>
</details>

<details>
<summary><strong>Metadata</strong></summary>
<p>Information about the data, including its structure, Profile, ownership, business meaning, sensitivity, Guardrails, lineage, Data Agreement, and Data Contract.</p>
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
