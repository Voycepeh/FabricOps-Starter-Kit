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
    <span class="fabricops-landing-card__title"><!-- FABRICOPS_PUBLIC_FUNCTION_COUNT --><strong>26</strong><span> public callables</span><!-- /FABRICOPS_PUBLIC_FUNCTION_COUNT --></span>
    <span class="fabricops-landing-card__body"><!-- FABRICOPS_CALLABLE_RECORD_COUNT -->Supported by <strong>50</strong><span> functions and </span><strong>22</strong><span> non-function records</span><!-- /FABRICOPS_CALLABLE_RECORD_COUNT -->.</span>
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

FabricOps Starter Kit includes maintainer tooling to keep the framework clean, explainable, and safe to refactor as it grows. Use the callable dashboards to review public API architecture and export raw callable inventory packets.

<div class="fabricops-card-grid">
  <a class="fabricops-landing-card" href="/FabricOps-Starter-Kit/dev/reference/callable-flow/">
    <span class="fabricops-landing-card__title">Callable Flow Guide</span>
    <span class="fabricops-landing-card__body">Understand the Public, Internal, and Utility callable hierarchy, why the dashboard exists, and how to read its architecture signals.</span>
    <span class="fabricops-landing-card__meta">Read the guide</span>
  </a>

  <a class="fabricops-landing-card" href="assets/callable-functions-dashboard.html">
    <span class="fabricops-landing-card__title">Architecture</span>
    <span class="fabricops-landing-card__body">Review public API shape, chain depth, fan-out, modules touched, cross-layer warnings, and flattening recommendations.</span>
    <span class="fabricops-landing-card__meta">Open Architecture</span>
  </a>

  <a class="fabricops-landing-card" href="assets/callable-functions-inventory.html">
    <span class="fabricops-landing-card__title">Inventory</span>
    <span class="fabricops-landing-card__body">Search/filter all callables, select rows, and export AI refactor packets.</span>
    <span class="fabricops-landing-card__meta">Open Inventory</span>
  </a>
</div>

<p><small>Callable metrics are generated from the callable inventory data.</small></p>
