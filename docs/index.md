<div class="fabricops-landing" markdown="1">

# FabricOps Starter Kit

Lightweight, notebook centric, plug and play starter kit for Microsoft Fabric.

FabricOps Starter Kit helps teams quickly bootstrap config driven Fabric notebook using reusable templates and a lightweight helper wheel.

It gives teams a standardized operating model for configuration, notebook execution, metadata collection, and pipeline guardrails.

<section class="fabricops-delivery-model" aria-labelledby="fabricops-delivery-model-heading" markdown="1">

## How FabricOps connects delivery teams { #fabricops-delivery-model-heading }

<p class="fabricops-architecture-image">
  <img src="assets/fabricops-roles.png" alt="FabricOps roles working from a shared governed foundation">
</p>

FabricOps helps governance, engineering, and analytics teams work from the same notebook flow.

Governance captures agreement, enrichment, and pipeline guardrail evidence. 
Engineering configures the environment, runs notebooks, and writes metadata. 
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
</div>

## What is included

<div class="fabricops-card-grid">
  <a class="fabricops-landing-card" href="notebook-templates-implementation-guide/">
    <span class="fabricops-landing-card__title">5 main notebook templates</span>
    <span class="fabricops-landing-card__body">With step by step guide in guide in implementation guide.</span>
  </a>

  <a class="fabricops-landing-card" href="reference/">
    <span class="fabricops-landing-card__title"><!-- FABRICOPS_PUBLIC_FUNCTION_COUNT --><strong>26</strong><span> public callable functions</span><!-- /FABRICOPS_PUBLIC_FUNCTION_COUNT --></span>
    <span class="fabricops-landing-card__body"><!-- FABRICOPS_CALLABLE_RECORD_COUNT -->Each public callable is documented as a standalone function, with supporting private functions, classes, and internal methods kept behind the scenes<!-- /FABRICOPS_CALLABLE_RECORD_COUNT -->.</span>
  </a>

  <a class="fabricops-landing-card" href="reference/dq-rules/">
    <span class="fabricops-landing-card__title">23 Data quality rule types</span>
    <span class="fabricops-landing-card__body">Suggested by AI and enforced in pipeline guardrails.</span>
  </a>

  <a class="fabricops-landing-card" href="reference/metadata/">
    <span class="fabricops-landing-card__title"><!-- FABRICOPS_METADATA_TABLE_COUNT --><strong>11</strong><span>metadata tables</span><!-- /FABRICOPS_METADATA_TABLE_COUNT --></span>
    <span class="fabricops-landing-card__body">Written by functions and widgets during runtime for enforcement and review.</span>
  </a>
</div>

## For maintainers

FabricOps Starter Kit includes maintainer tooling to keep the framework clean, explainable, and safe to refactor as it grows. Use the Function Call Graph Dashboard and Function Inventory to review public API architecture and export raw function-level packets.

<div class="fabricops-card-grid">
  <a class="fabricops-landing-card" href="assets/function-call-graph-dashboard.html">
    <span class="fabricops-landing-card__title">Function Call Graph Dashboard</span>
    <span class="fabricops-landing-card__body">Review the public API shape, callable relationships, chain depth, fan out, source Python files, and architecture signals.</span>
    <span class="fabricops-landing-card__meta">Open Function Call Graph Dashboard</span>
  </a>

  <a class="fabricops-landing-card" href="reference/function-call-graph/">
    <span class="fabricops-landing-card__title">Function Call Graph Reference</span>
    <span class="fabricops-landing-card__body">Read about the architecture and the motivation behind the function call graph dashboard.</span>
    <span class="fabricops-landing-card__meta">Open Function Call Graph Reference</span>
  </a>
</div>

<p><small>Function metrics are generated from the function inventory data.</small></p>
