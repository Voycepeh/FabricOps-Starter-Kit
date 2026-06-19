# FabricOps Starter Kit

Lightweight, notebook centric, plug and play starter kit for Microsoft Fabric.

FabricOps Starter Kit helps teams quickly bootstrap governed Fabric notebook delivery using reusable templates and a lightweight helper wheel.

It gives teams a shared operating model for configuration, notebook execution, metadata collection, and pipeline guardrails without turning every project into a custom build.

<section class="fabricops-delivery-model" aria-labelledby="fabricops-delivery-model-heading" markdown="1">

<div class="fabricops-delivery-model__copy" markdown="1">

## How FabricOps connects delivery teams { #fabricops-delivery-model-heading }

FabricOps helps governance, engineering, and analytics teams work from the same notebook based delivery flow.

Governance captures agreement, enrichment, and guardrail evidence. Engineering configures the environment, runs notebooks, and writes metadata. Analysts and data scientists consume trusted outputs for BI, AI, and exploration.

The shared metadata tables act as the handoff layer. They record what was agreed, what ran, what passed, and what is ready for review. This keeps delivery repeatable without forcing every project to become a custom build.

</div>

<div class="fabricops-cta" markdown="1">

[Start the guided demo](guided-demo.md){ .md-button .md-button--primary }
[See how it works](how-fabricops-works/index.md){ .md-button }

</div>

<p class="fabricops-architecture-image">
  <img src="assets/fabricops-roles.png" alt="FabricOps roles working from a shared governed foundation">
</p>

<div class="fabricops-team-grid" markdown="1">

<div class="fabricops-team-card" markdown="1">

### Governance

Captures agreements, enrichment decisions, and pipeline guardrails.

</div>

<div class="fabricops-team-card" markdown="1">

### Engineering

Configures workspaces, runs notebooks, and records execution metadata.

</div>

<div class="fabricops-team-card" markdown="1">

### Analysts and Scientists

Use governed outputs for BI, AI, and exploration.

</div>

</div>

</section>

## What is included

<div class="grid cards" markdown="1">

-   [**5 notebook templates**](how-fabricops-works/notebook-templates.md)

    Reusable notebook workflow templates.

-   [**20 starter-kit functions**](reference/index.md)

    Shared helpers used by the templates.

-   [**23 DQ rule types**](reference/dq-rules/index.md)

    Governed checks for pipeline guardrails.

-   [**12 metadata tables**](how-fabricops-works/metadata-tables.md)

    Evidence tables for delivery and review.

</div>

## Choose where to begin

<div class="fabricops-start-grid">
  <a class="fabricops-start-card" href="guided-demo/">
    <span class="fabricops-start-card__title">Guided Demo</span>
    <span class="fabricops-start-card__body">Install, copy templates, and run the first smoke test.</span>
  </a>
  <a class="fabricops-start-card" href="how-fabricops-works/">
    <span class="fabricops-start-card__title">How FabricOps Works</span>
    <span class="fabricops-start-card__body">Understand the operating model and metadata flow.</span>
  </a>
  <a class="fabricops-start-card" href="how-fabricops-works/notebook-templates/">
    <span class="fabricops-start-card__title">Notebook Templates</span>
    <span class="fabricops-start-card__body">Know which notebook to run and what it writes.</span>
  </a>
  <a class="fabricops-start-card" href="reference/">
    <span class="fabricops-start-card__title">Function Reference</span>
    <span class="fabricops-start-card__body">Check helper behavior, parameters, and call paths.</span>
  </a>
</div>
