# Metadata & Contracts

FabricOps Starter Kit treats a data contract as an **operational agreement backed by evidence**.

The contract is assembled from approved metadata generated across the notebook flow, not hand-written once and forgotten.

<figure markdown>
  ![Data contract model showing metadata evidence from agreement, exploration, pipeline, and governance combined into an operational contract](../assets/data-contract.png){ .full-width }
  <figcaption>Contract assembly connects business intent, technical evidence, and governed runtime controls.</figcaption>
</figure>

## What the contract is

The contract is the governed answer to five practical questions:

1. What dataset and scope are approved?
2. What quality and governance rules are approved?
3. How is data transformed and enforced at runtime?
4. What evidence proves compliance and execution outcomes?
5. Who approved what, and when?

## What evidence feeds the contract

Approved evidence typically includes:

- agreement intent, ownership, and usage constraints
- profiling and schema evidence
- approved DQ rules and deactivation history
- lineage and transformation evidence
- governance classifications and access context
- enforcement outcomes, drift signals, and run summaries

## Notebook ownership of evidence

| Notebook | Owns | Typical metadata outputs |
| --- | --- | --- |
| `01_da` | Agreement intent and accountability | Agreement identity, scope, owners, approved usage |
| `02_ex` | Profiling evidence and DQ approval loop | Profiles, candidate rules, approved DQ rules |
| `03_pc` | Deterministic pipeline enforcement | Enforcement results, run evidence, lineage, drift evidence |
| `04_gov` | Governance review and policy metadata | Classification, sensitivity/PII, governance approvals |

For notebook implementation boundaries, use [Notebook Structure](../notebook-structure.md).

## Where enforcement happens

Deterministic contract enforcement happens in **`03_pc` notebooks**:

- load approved metadata and approved rules
- run transformations and checks
- enforce DQ and governance controls
- persist run evidence for auditability and handover

## Metadata tables and roles

| Table | Primary owner | What it captures |
| --- | --- | --- |
| `contracts` | Governance steward | Agreement scope, usage constraints, accountability context |
| `contract_columns` | Governance + analysts | Column semantics, classification context, sensitivity context |
| `contract_rules` | Analysts/stewards (approved), engineering (enforced) | Approved DQ and operational rules |
| `quality_results` | Engineering | Deterministic enforcement outcomes and quarantine evidence |
| `lineage_records` | Engineering | Source-to-target and transformation evidence per run |

## AI, human approval, deterministic enforcement

FabricOps follows one control model throughout:

- **AI suggests** rules, context, and draft metadata.
- **Humans approve** what becomes governed policy.
- **Pipelines enforce** only approved policy deterministically.

<figure markdown>
  ![Data quality workflow with AI suggestions, human review, approval, and deterministic enforcement in pipelines](../assets/DQ-with-ai.png){ .full-width }
  <figcaption>AI accelerates drafting; human approval governs policy; deterministic pipelines enforce it.</figcaption>
</figure>

## Related pages

- [Workflow Operating Model](../lifecycle-operating-model.md)
- [Data Quality Rules System](../data-quality-rules-system.md)
- [Function Reference](../reference/index.md)
