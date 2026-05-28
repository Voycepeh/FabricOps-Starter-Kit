# Quick Start

Use this page to get from zero to a first FabricOps Starter Kit run in Microsoft Fabric.

## Get running quickly

1. **Install the wheel** in a Fabric Environment.
   - **Expected result:** notebooks can import `fabricops_kit`.
   - **Docs:** [Fabric Wheel Install](install.md)
2. **Copy the notebook templates** into your Fabric workspace.
   - **Expected result:** you have a working `00_env_config`, agreement, exploration, pipeline, and governance notebook set.
   - **Docs:** [Notebook Structure](notebook-structure.md)
3. **Open Microsoft Fabric and attach the Environment** to the copied notebooks.
   - **Expected result:** each notebook runs with the same installed helper wheel and runtime configuration.
   - **Docs:** [Fabric Wheel Install](install.md)
4. **Configure and run `00_env_config`**.
   - **Expected result:** paths, environment settings, and metadata routing are ready for downstream notebooks.
   - **Docs:** [Template: `00_env_config`](notebook-structure/00-env-config.md)
5. **Run the 01/02/03/04 notebooks in order**.
   - **Expected result:** agreement context, profiling evidence, approved enforcement results, and governance evidence are written to metadata.
   - **Docs:** [Notebook Structure](notebook-structure.md)
6. **Review the generated metadata-backed contract evidence**.
   - **Expected result:** the data contract is assembled from approved metadata evidence; it is not a separate fifth notebook.
   - **Docs:** [Metadata and Contracts](metadata-and-contracts/index.md)

## Quick flow

<figure markdown>
  ![Quick start flow from agreement context, analysis and profiling, transform and enforcement, and governance evidence into one metadata-backed data contract](assets/notebook-flow.png){ .full-width }
  <figcaption>The contract is not another notebook. It is assembled from approved evidence written by the 01/02/03/04 notebooks into the configured metadata tables.</figcaption>
</figure>

## Optional: what each notebook owns

| Notebook | Owns | Produces |
| --- | --- | --- |
| `00_env_config` | Environment bootstrap, Fabric paths, metadata lakehouse routing, shared config. | Runtime configuration that every downstream notebook reuses. |
| `01_da_<agreement>` / `01_agreement_<agreement>` | Agreement scope, purpose, owners, stewards, usage intent, access boundaries. | Agreement metadata and notebook registration evidence. |
| `02_ex_<agreement>_<topic>` | Source exploration, profiling, analyst observations, AI-assisted DQ rule suggestions. | Analysis/profiling metadata and reviewed DQ rule candidates. |
| `03_pc_<agreement>_<pipeline>` | Source-to-target processing, approved rule enforcement, run evidence. | Curated outputs, validation results, lineage, and transformation metadata. |
| `04_gov_<agreement>_<database>_<table>` | Table/column governance, classification, sensitivity, access, and policy updates. | Governance and classification metadata for the assembled contract. |

## Optional: what gets stored as metadata

The notebooks persist reusable evidence in framework metadata tables routed by `00_env_config`:

- **Agreement metadata** — agreement identity, scope, owners, stewards, usage intent, access boundaries, and initial classifications.
- **Analysis and profiling metadata** — schema observations, profiling statistics, quality observations, patterns, anomalies, and business understanding.
- **DQ rules and validation results** — proposed and approved rules, thresholds, enforcement outcomes, and test results.
- **Lineage and processing metadata** — source/target assets, transformation summaries, run context, lineage, and processing evidence.
- **Governance and classification metadata** — sensitivity, classification, access rules, policy updates, monitoring context, and compliance evidence.

## Optional: go deeper

- [Fabric Wheel Install](install.md): install or verify the reusable helper wheel.
- [Notebook Structure](notebook-structure.md): template boundaries, naming conventions, and per-notebook pages.
- [Metadata and Contracts](metadata-and-contracts/index.md): contract model and metadata ownership details.
- [Workflow](lifecycle-operating-model.md): role checkpoints, AI assistance, approvals, and deterministic enforcement.
- [Function Reference](reference/index.md): callable-level guidance.
