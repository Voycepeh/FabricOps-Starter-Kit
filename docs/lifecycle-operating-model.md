# Workflow Operating Model

This page explains **who does what, in what sequence, and where AI/human approval fits** in FabricOps Starter Kit. Use it as the people-and-process view, then use [Notebook Structure](notebook-structure.md) for implementation conventions.

```mermaid
flowchart LR
    A[Workflow Operating Model\npeople + approvals] --> B[Notebook Structure\nimplementation conventions]
    B --> C[Metadata Evidence\napproved records + DQ outputs]
    C --> D[Data Contract / Pipeline Enforcement\noperational controls]
```

## Operating flow

FabricOps Starter Kit follows a governed flow in Microsoft Fabric:

`agreement → exploration → approved metadata evidence → pipeline enforcement → handover`

### 1) Agreement and ownership setup

- Governance and data owners define scope, ownership, and approval expectations.
- Humans approve agreement intent before downstream execution proceeds.
- AI can assist drafting and consistency checks, but approval remains a human decision.

### 2) Exploration and evidence generation

- Delivery teams run exploratory profiling and evidence-building work.
- AI can accelerate profiling, rule suggestions, and draft summaries.
- Human reviewers validate evidence quality and business fit before approvals are promoted.

### 3) Metadata approval and contract assembly

- Approved metadata and quality evidence become the basis for contract-ready outputs.
- AI supports synthesis and change impact analysis.
- Human governance reviews confirm policy alignment before enforcement.

### 4) Pipeline enforcement and handover

- Execution pipelines enforce approved controls.
- Delivery and governance teams publish handover evidence for traceability.
- Human accountability remains explicit for sign-off and operational acceptance.

## Stage checkpoints (high level)

- **Configuration stage:** establish environment and metadata routing baselines.
- **Agreement stage:** capture and approve business/data-sharing intent.
- **Exploration stage:** generate profiling and quality evidence.
- **Pipeline stage:** enforce approved controls operationally.
- **Governance handover stage:** finalize review artifacts and transfer ownership evidence.

For notebook naming, boundaries, and ownership by notebook, go to [Notebook Structure](notebook-structure.md).

## Related pages

- [Notebook Structure](notebook-structure.md)
- [Metadata and Data Contract Assembly](metadata-and-contracts.md)
- [Quick Start](quick-start.md)
