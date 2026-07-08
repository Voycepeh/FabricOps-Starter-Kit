<div class="fabricops-landing" markdown="1">

# FabricOps Starter Kit

FabricOps Starter Kit is a lightweight starter kit for data teams working in Microsoft Fabric.

It brings together reusable notebook templates, helper functions, metadata tables, guardrails, and guided demos so Fabric notebook projects can start with a clearer structure.

Teams can configure workspaces, run pipelines, track lineage, review data quality checks, and maintain pipeline run history without building every support piece from scratch.

<section class="fabricops-delivery-model" aria-labelledby="fabricops-workflow-model-heading" markdown="1">

## How FabricOps connects data teams { #fabricops-workflow-model-heading }

<p class="fabricops-architecture-image">
  <img src="assets/fabricops-roles.png" alt="FabricOps roles working from a shared governed foundation">
</p>

FabricOps helps governance, engineering, and analytics teams work from the same notebook flow.

Governance reviews agreement context, enrichment, and pipeline guardrail results.
Engineering configures the environment, runs notebooks, and writes metadata tables.
Analysts and data scientists consume trusted outputs for BI, AI, and exploration.

The shared metadata tables act as the handoff layer.
They record what was agreed, what ran, what passed, and what is ready for review.
They abstract the important but tedious work into a simplified plug and play workflow that makes handover easy, even for new team members.

</section>

## Choose where to begin

<div class="fabricops-card-grid">
  <a class="fabricops-landing-card" href="guided-demo/">
    <span class="fabricops-landing-card__title">Guided Demo</span>
    <span class="fabricops-landing-card__body">Build the wheel, set up Fabric artifacts, and run the first smoke test.</span>
  </a>
  <a class="fabricops-landing-card" href="how-fabricops-works/">
    <span class="fabricops-landing-card__title">How FabricOps Works</span>
    <span class="fabricops-landing-card__body">Understand the operating model and metadata flow.</span>
  </a>
  <a class="fabricops-landing-card" href="releases/">
    <span class="fabricops-landing-card__title">Releases</span>
    <span class="fabricops-landing-card__body">See current and past releases and download plug-and-play assets.</span>
  </a>
</div>

## What is included

<div class="fabricops-card-grid">
  <a class="fabricops-landing-card" href="notebook-templates-implementation-guide/">
    <span class="fabricops-landing-card__title">5 main notebook templates</span>
    <span class="fabricops-landing-card__body">With step by step guide in guide in implementation guide.</span>
  </a>

  <a class="fabricops-landing-card" href="reference/">
    <span class="fabricops-landing-card__title"><!-- FABRICOPS_PUBLIC_FUNCTION_COUNT --><strong>25</strong><span> public callable functions</span><!-- /FABRICOPS_PUBLIC_FUNCTION_COUNT --></span>
    <span class="fabricops-landing-card__body"><!-- FABRICOPS_CALLABLE_RECORD_COUNT -->Helper functions support the notebook templates and demo workflows, with supporting private functions, classes, and internal methods kept behind the scenes<!-- /FABRICOPS_CALLABLE_RECORD_COUNT -->.</span>
  </a>

  <a class="fabricops-landing-card" href="reference/dq-rules/">
    <span class="fabricops-landing-card__title">23 Data quality rule types</span>
    <span class="fabricops-landing-card__body">Suggested by AI and enforced in pipeline guardrails.</span>
  </a>

  <a class="fabricops-landing-card" href="reference/metadata/">
    <span class="fabricops-landing-card__title"><!-- FABRICOPS_METADATA_TABLE_COUNT --><strong>11</strong><span>metadata tables</span><!-- /FABRICOPS_METADATA_TABLE_COUNT --></span>
    <span class="fabricops-landing-card__body">Stores data about agreements, catalogue entries, lineage, guardrail results, notebook registry entries, and pipeline runs.</span>
  </a>
</div>

## For maintainers

FabricOps Starter Kit includes maintainer tooling to keep the project clean, explainable, and safe to refactor as it grows. Use the Public Function Call Flows Dashboard to review public API architecture, inspect the selected callable inventory, and export focused cleanup packets.

<div class="fabricops-card-grid">
  <a class="fabricops-landing-card" href="assets/public-function-call-flows-dashboard.html">
    <span class="fabricops-landing-card__title">Public Function Call Flows Dashboard</span>
    <span class="fabricops-landing-card__body">Review the public API shape, callable relationships, chain depth, fan out, source Python files, and architecture signals.</span>
    <span class="fabricops-landing-card__meta">Open Public Function Call Flows Dashboard</span>
  </a>

  <a class="fabricops-landing-card" href="function-call-graph/">
    <span class="fabricops-landing-card__title">Function Call Graph Guide</span>
    <span class="fabricops-landing-card__body">Read about the architecture and the motivation behind the function call graph dashboard.</span>
    <span class="fabricops-landing-card__meta">Open Function Call Graph Guide</span>
  </a>
</div>

<p><small>Function metrics are generated from the selected callable inventory data.</small></p>
