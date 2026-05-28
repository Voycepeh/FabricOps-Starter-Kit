# Metadata & Contracts

A data contract in FabricOps Starter Kit is an **operational agreement** across people, notebooks, and controls—not just a YAML file or a schema snapshot.

FabricOps assembles the contract from **approved metadata evidence** captured through the notebook lifecycle.

<figure markdown>
  ![Data contract model showing metadata evidence from agreement, exploration, pipeline, and governance combined into an operational contract](../assets/data-contract.png){ .full-width }
  <figcaption>The contract is assembled from approved evidence, so policy, quality, and implementation stay synchronized.</figcaption>
</figure>

## What contract evidence includes

The assembled contract can include:

- agreement metadata and business intent
- profiling evidence and discovery findings
- approved data quality (DQ) rules
- schema snapshots
- lineage and transformation evidence
- governance approvals and classifications
- run summaries and enforcement outcomes
- drift guardrails and monitoring signals
- steward decisions and review history

## Ownership across the notebook lifecycle

- **`01_da` owns agreement/business intent** (purpose, scope, ownership, allowed use).
- **`02_ex` owns profiling/discovery and DQ rule proposal + approval flow**.
- **`03_pc` owns deterministic pipeline enforcement and run evidence**.
- **`04_gov` owns ongoing governance/classification/access review**.

This separation keeps roles clear while preserving a single governed contract story.

## Where enforcement happens

Contract enforcement is primarily executed in **`03_pc` notebooks**:

- load approved metadata and approved DQ rules
- run deterministic transformations
- enforce rules and record results
- write run evidence for downstream governance and incident response

## AI, human approval, and pipeline enforcement

FabricOps follows a practical control model:

- **AI suggests** candidate rules and insights
- **Humans approve** what becomes governed policy
- **Pipelines enforce** approved policy deterministically

<figure markdown>
  ![Data quality workflow with AI suggestions, human review, approval, and deterministic enforcement in pipelines](../assets/DQ-with-ai.png){ .full-width }
  <figcaption>AI speeds drafting and triage, but only human-approved rules become enforceable runtime controls.</figcaption>
</figure>

## Contracts as change-management artifacts

Data contracts are also change-management artifacts for:

- schema change planning and drift handling
- ownership and steward accountability
- consumer impact assessment
- incident handling and auditability

Use this page for the evidence and enforcement narrative. For notebook-level implementation boundaries, see [Notebook Structure](../notebook-structure.md). For callable details, see the generated [Function Reference](../reference/index.md).
