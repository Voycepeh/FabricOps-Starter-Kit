# Metadata

This page explains: how approved metadata evidence becomes a contract-ready artifact.
Use this when: you need to understand contract contents, metadata tables, and notebook evidence ownership.
Next read: [Quality](../data-quality-rules-system.md), [Notebooks](../notebook-structure.md), [Deploy](../deployment-and-promotion.md).

<figure markdown>
  ![Data contract model showing metadata evidence from agreement, exploration, pipeline, and governance combined into an operational contract](../assets/data-contract.png){ .full-width }
  <figcaption>Data contract evidence ownership belongs here: approved evidence feeding contract-ready handover.</figcaption>
</figure>

## What the contract is

A governed operational artifact assembled from approved metadata and run evidence across notebook stages.

## Evidence sources by notebook ownership

| Notebook | Evidence it owns |
| --- | --- |
| `01_agreement_*` | Scope, ownership, usage intent, access boundaries |
| `02_ex_*` | Profiling evidence and approved DQ rule metadata |
| `03_pc_*` | Lineage, deterministic enforcement results, run evidence |
| `04_gov_*` | Classification, sensitivity, and governance approval metadata |

## Metadata tables and roles

| Metadata table (logical) | Role owner | Purpose |
| --- | --- | --- |
| Agreement metadata | Governance + data owner | Agreement-level intent and accountability |
| Quality/rules metadata | Analyst + steward (approve), engineering (enforce) | Approved DQ rule policy history |
| Lineage/run metadata | Engineering | Traceable enforcement and processing evidence |
| Governance metadata | Governance steward | Classification and access-governance outcomes |

## Enforcement note

Policy enforcement is deterministic in `03_pc_*` and consumes approved metadata routed through the configured `metadata` target from `00_env_config`.
