# Quick Start

This page walks through your first FabricOps Starter Kit run.
Use it when you want the shortest path from setup to contract-ready evidence.

The journey is: install the wheel, copy templates, configure `00_env_config`, run the 01/02/03/04 notebooks, then review the metadata-backed contract assembled from approved evidence.

Next read: [Fabric Wheel Install](install.md), [Notebook Structure](notebook-structure.md).

!!! tip "Dominant onboarding path"
    **Install Wheel → Copy Notebook Templates → Configure `00_env_config` → Run 01/02/03/04 notebooks → Review assembled contract evidence → Deploy later**

<div class="home-cta" markdown="1">

[Copy Notebook Template](notebook-structure.md){ .md-button .md-button--primary }
[Install Wheel](install.md){ .md-button }

</div>

<figure markdown>
  ![Quick start flow from agreement context, analysis and profiling, transform and enforcement, and governance evidence into one metadata-backed data contract](assets/notebook-flow.png){ .full-width }
  <figcaption>The contract is not another notebook. It is assembled from approved evidence written by the 01/02/03/04 notebooks into the configured metadata tables.</figcaption>
</figure>

## The first-run story

Start by installing the FabricOps wheel in your Fabric Environment so notebooks can import `fabricops_kit`, then copy the template notebooks into your workspace. Run `00_env_config` first; it owns environment settings, path configuration, and metadata target routing for the rest of the run.

From there, the work moves through four notebook responsibilities:

1. **Agreement context** — run the current agreement notebook (`01_da_<agreement>` in the template docs; sometimes described generically as `01_agreement_<agreement>`) to capture purpose, owners, stewards, access scope, and intended use.
2. **Profiling and rule drafting** — run `02_ex_<agreement>_<topic>` to explore source data, profile quality, capture observations, and draft DQ rules for review.
3. **Approved enforcement** — run `03_pc_<agreement>_<pipeline>` to transform data, apply approved rules deterministically, and store validation, lineage, and processing evidence.
4. **Governance evidence** — run `04_gov_<agreement>_<database>_<table>` to maintain table or column classification, sensitivity, access, and compliance evidence.

After those notebooks write their evidence, review the **metadata-backed data contract** as an assembled output from the framework metadata tables. Do not create or run a separate fifth contract notebook; the contract is the combined, approved evidence from the agreement, exploration, pipeline, and governance stages.

## What each notebook owns

| Notebook | Owns | Produces |
| --- | --- | --- |
| `00_env_config` | Environment bootstrap, Fabric paths, metadata lakehouse routing, shared config. | Runtime configuration that every downstream notebook reuses. |
| `01_da_<agreement>` / `01_agreement_<agreement>` | Agreement scope, purpose, owners, stewards, usage intent, access boundaries. | Agreement metadata and notebook registration evidence. |
| `02_ex_<agreement>_<topic>` | Source exploration, profiling, analyst observations, AI-assisted DQ rule suggestions. | Analysis/profiling metadata and reviewed DQ rule candidates. |
| `03_pc_<agreement>_<pipeline>` | Source-to-target processing, approved rule enforcement, run evidence. | Curated outputs, validation results, lineage, and transformation metadata. |
| `04_gov_<agreement>_<database>_<table>` | Table/column governance, classification, sensitivity, access, and policy updates. | Governance and classification metadata for the assembled contract. |

## What gets stored as metadata

The notebooks persist reusable evidence in framework metadata tables routed by `00_env_config`:

- **Agreement metadata** — agreement identity, scope, owners, stewards, usage intent, access boundaries, and initial classifications.
- **Analysis and profiling metadata** — schema observations, profiling statistics, quality observations, patterns, anomalies, and business understanding.
- **DQ rules and validation results** — proposed and approved rules, thresholds, enforcement outcomes, and test results.
- **Lineage and processing metadata** — source/target assets, transformation summaries, run context, lineage, and processing evidence.
- **Governance and classification metadata** — sensitivity, classification, access rules, policy updates, monitoring context, and compliance evidence.

## Where to go deeper

- Use [Notebook Structure](notebook-structure.md) for template boundaries, naming conventions, and per-notebook pages.
- Use [Metadata and Contracts](metadata-and-contracts/index.md) for the contract model and metadata ownership details.
- Use [Workflow](lifecycle-operating-model.md) for role checkpoints, AI assistance, approvals, and deterministic enforcement.
- Use the [Function Reference](reference/index.md) when you need callable-level guidance.
- Use [Fabric Wheel Install](install.md) when you need to install or verify the reusable helper wheel.
