<div class="fabricops-landing" markdown="1">

# FabricOps documentation

**Microsoft Fabric gives you the platform. FabricOps gives you the operating practice.**

FabricOps is a plug-and-play Data Engineering and Data Governance practice for Microsoft Fabric. It packages the repeatable foundations teams otherwise need to define project by project so they can focus on project-specific engineering, analytics, and AI-assisted development.

<!-- VIDEO SLOT: Main FabricOps landing-page explainer (target 2.5-4 minutes) -->

<div class="fabricops-card-grid">
  <a class="fabricops-landing-card" href="how-fabricops-works/">
    <span class="fabricops-landing-card__title">How FabricOps works</span>
    <span class="fabricops-landing-card__body">Understand the Governance ↔ Engineering loop, Data Contract lifecycle, Production path, and shared metadata model.</span>
  </a>

  <a class="fabricops-landing-card" href="guided-demo/">
    <span class="fabricops-landing-card__title">Step-by-step Guided Demo</span>
    <span class="fabricops-landing-card__body">Run the complete FabricOps workflow with practical actions, screenshots, expected results, and links to deeper concepts.</span>
  </a>
</div>

<p class="fabricops-architecture-image">
  <img src="assets/fabricops-roles.png" alt="FabricOps roles working from a shared governed foundation">
</p>

## Why FabricOps

Microsoft Fabric already provides the platform capabilities for Data Engineering, Governance, analytics, AI, workspaces, notebooks, Lakehouses, Warehouses, and related services.

What teams still need to define is **how those capabilities should work together as a repeatable operating practice**.

Without a shared practice, each project can end up rebuilding the same foundations: environment configuration, reusable I/O, metadata capture, profiling, lineage, governance hand-offs, Data Quality controls, Data Contracts, Development-to-Production conventions, and downstream consumption patterns.

FabricOps packages those repeatable foundations into a ready-to-adopt starter kit.

## What FabricOps gives you

FabricOps is organised around four reusable notebooks that work together as one workflow:

| Notebook | What it provides |
| --- | --- |
| `00_env_config` | Environment-aware configuration and Fabric item routing. |
| `01_governance` | Data Stewards, Data Agreements, Enrichment, Guardrails, and Data Contracts. |
| `02_pipeline` | Project-specific ETL with Catalogue, profiling, lineage, Guardrail validation, and governed Production execution. |
| `99_explore` | Controlled consumption of approved Production data for BI, AI, data science, and exploration. |

Around those notebooks, FabricOps provides standardized notebook-facing functions and a shared metadata model so Governance and Engineering work from the same structured context.

As the workflow runs, FabricOps records the implemented Governance and Engineering context, including Data Agreements, Catalogue metadata, profiles, lineage, source observations, resolved read strategies, governed load strategies and parameters, Enrichment, Guardrails and their results, and Data Contracts.

The result is a governed Production data foundation that can be understood, validated, promoted, reused, and consumed without rebuilding its context afterwards.

## The core idea

FabricOps does not try to replace project-specific engineering logic. Instead, it standardizes the repeatable operating foundation around that work.

Engineering Development builds and observes the data. Governance uses the shared metadata to add meaning and governed expectations. Engineering validates those expectations. Governance freezes and activates the approved Data Contract. Engineering Production runs the validated pipeline against the active contract. Project-specific consumer workspaces then use approved Production data through `99_explore`.

[See the workflow in detail →](how-fabricops-works.md)

## Built for AI-assisted engineering

FabricOps provides the structure, workflow, and Guardrails while engineers and analysts remain responsible for project-specific logic and decisions about what the data should do and what “good” looks like.

Teams can use Copilot, AI Functions, or other approved AI assistance to accelerate coding, testing, documentation, and analysis without making the core Production foundation depend on external tooling or nondeterministic decisions.

## Reference and resources

<div class="fabricops-card-grid">
  <a class="fabricops-landing-card" href="reference/engineering-cheat-sheet/">
    <span class="fabricops-landing-card__title">FabricOps Engineering Guide</span>
    <span class="fabricops-landing-card__body">Go deeper into configuration-driven engineering, Lakehouse/Warehouse choices, PySpark, processing strategies, optimisation, and Warehouse SQL.</span>
  </a>

  <a class="fabricops-landing-card" href="reference/metadata/">
    <span class="fabricops-landing-card__title">Metadata Tables</span>
    <span class="fabricops-landing-card__body">Review the shared metadata tables, schemas, purpose, and writer ownership.</span>
  </a>

  <a class="fabricops-landing-card" href="reference/">
    <span class="fabricops-landing-card__title">FabricOps Functions</span>
    <span class="fabricops-landing-card__body">Browse notebook-facing public functions, signatures, relationships, and exact contracts.</span>
  </a>

  <a class="fabricops-landing-card" href="notebook-templates/">
    <span class="fabricops-landing-card__title">Notebook Templates</span>
    <span class="fabricops-landing-card__body">Download the reusable Governance, Engineering, and exploration notebook templates.</span>
  </a>

  <a class="fabricops-landing-card" href="glossary/">
    <span class="fabricops-landing-card__title">FabricOps Glossary</span>
    <span class="fabricops-landing-card__body">Look up FabricOps, Governance, and Engineering terms as you encounter them.</span>
  </a>

  <a class="fabricops-landing-card" href="releases/">
    <span class="fabricops-landing-card__title">Official Releases</span>
    <span class="fabricops-landing-card__body">View published FabricOps releases and the assets included in each version.</span>
  </a>
</div>

</div>
