<div class="fabricops-landing" markdown="1">

# FabricOps documentation

**Microsoft Fabric gives you the platform. FabricOps gives you the operating practice.**

A plug-and-play Data Engineering and Data Governance practice for Microsoft Fabric, with the repeatable foundations already in place so teams can focus on project-specific engineering and analytics.

<!--
VIDEO SLOT: Main FabricOps homepage explainer.
Wrap the final responsive iframe/video embed in:
<div class="fabricops-video-shell">...</div>
-->

<div class="fabricops-card-grid fabricops-primary-actions">
  <a class="fabricops-landing-card" href="how-fabricops-works/">
    <span class="fabricops-landing-card__title">How FabricOps works</span>
    <span class="fabricops-landing-card__body">Operating model, Governance ↔ Engineering loop, Data Contract lifecycle, Production, and consumption.</span>
  </a>

  <a class="fabricops-landing-card" href="guided-demo/">
    <span class="fabricops-landing-card__title">Step-by-step Guided Demo</span>
    <span class="fabricops-landing-card__body">Build and run the complete FabricOps workflow with practical actions, screenshots, and expected results.</span>
  </a>
</div>

<p class="fabricops-architecture-image">
  <img src="assets/fabricops-roles.png" alt="FabricOps Governance, Data Engineering, and AI and BI analytics working from one shared foundation">
</p>

<p class="fabricops-image-caption"><strong>One shared operating foundation</strong> connecting Governance, Data Engineering, and downstream analytics and AI.</p>

## The four notebooks

<div class="fabricops-notebook-grid">
  <a class="fabricops-mini-card" href="notebook-templates/">
    <span class="fabricops-mini-card__code">00_env_config</span>
    <span class="fabricops-mini-card__title">Configure</span>
    <span class="fabricops-mini-card__body">Environment-aware Fabric item routing.</span>
  </a>
  <a class="fabricops-mini-card" href="notebook-templates/">
    <span class="fabricops-mini-card__code">01_governance</span>
    <span class="fabricops-mini-card__title">Govern</span>
    <span class="fabricops-mini-card__body">Agreements, Enrichment, Guardrails, and Data Contracts.</span>
  </a>
  <a class="fabricops-mini-card" href="notebook-templates/">
    <span class="fabricops-mini-card__code">02_pipeline</span>
    <span class="fabricops-mini-card__title">Engineer</span>
    <span class="fabricops-mini-card__body">ETL, profiling, lineage, validation, and Production execution.</span>
  </a>
  <a class="fabricops-mini-card" href="notebook-templates/">
    <span class="fabricops-mini-card__code">99_explore</span>
    <span class="fabricops-mini-card__title">Consume</span>
    <span class="fabricops-mini-card__body">Approved Production data for BI, AI, data science, and exploration.</span>
  </a>
</div>

## Opinionated engineering choices

<div class="fabricops-principles-grid">
  <a href="reference/engineering-cheat-sheet/#config-driven-engineering">Configuration-driven</a>
  <a href="reference/engineering-cheat-sheet/#notebook-first">Code-first</a>
  <a href="reference/engineering-cheat-sheet/#pyspark-first">PySpark-first</a>
  <a href="reference/engineering-cheat-sheet/#lakehouse-first">Lakehouse-first</a>
  <a href="reference/engineering-cheat-sheet/#governance-as-code">Governance as Code</a>
  <a href="reference/engineering-cheat-sheet/#medallion-architecture">Medallion architecture</a>
  <a href="reference/engineering-cheat-sheet/#full-vs-incremental">Incremental loading</a>
  <a href="reference/engineering-cheat-sheet/#failure-safe-processing">Failure-safe processing</a>
</div>

## Quick links

<div class="fabricops-quick-grid">
  <a class="fabricops-mini-card" href="reference/engineering-cheat-sheet/">
    <span class="fabricops-mini-card__title">Engineering Guide</span>
    <span class="fabricops-mini-card__body">The engineering decisions behind FabricOps.</span>
  </a>
  <a class="fabricops-mini-card" href="reference/metadata/">
    <span class="fabricops-mini-card__title">Metadata Tables</span>
    <span class="fabricops-mini-card__body">Shared schemas, context, and ownership.</span>
  </a>
  <a class="fabricops-mini-card" href="reference/">
    <span class="fabricops-mini-card__title">Functions</span>
    <span class="fabricops-mini-card__body">Notebook-facing functions and exact contracts.</span>
  </a>
  <a class="fabricops-mini-card" href="notebook-templates/">
    <span class="fabricops-mini-card__title">Notebook Templates</span>
    <span class="fabricops-mini-card__body">Reusable Governance, Engineering, and exploration notebooks.</span>
  </a>
  <a class="fabricops-mini-card" href="glossary/">
    <span class="fabricops-mini-card__title">Glossary</span>
    <span class="fabricops-mini-card__body">FabricOps, Governance, and Engineering terms.</span>
  </a>
  <a class="fabricops-mini-card" href="releases/">
    <span class="fabricops-mini-card__title">Releases</span>
    <span class="fabricops-mini-card__body">Published versions and release assets.</span>
  </a>
</div>

</div>
