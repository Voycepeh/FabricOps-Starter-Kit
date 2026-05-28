# Workflow

This page explains: who does what, where AI helps, and where human approvals happen.
Use this when: you need the operating model behind the template execution flow.
Next read: [Start](quick-start.md), [Templates](notebook-structure.md), [Govern / Metadata](metadata-and-contracts/index.md).

<figure markdown>
  ![Orientation diagram connecting workflow operating model, notebook implementation boundaries, and metadata contract evidence](assets/docs-orientation.png){ .full-width }
  <figcaption>Lightweight operating structure: AI assisted drafting, human approved policy, deterministic notebook enforcement.</figcaption>
</figure>

## Role checkpoints

| Stage | Owner(s) | AI assisted | Human approved checkpoint | Deterministic enforcement |
| --- | --- | --- | --- | --- |
| `01_agreement_*` | Data owner + governance | Draft context support | Agreement scope and ownership | Not yet |
| `02_ex_*` | Analyst + engineer | Candidate DQ suggestions | Rule approval/rejection | Not yet |
| `03_pc_*` | Engineer + operator | Diagnostics/summaries | Run readiness and controls | Starts here |
| `04_gov_*` | Governance steward + owner | Classification suggestions | Governance sign-off | Supports next runs |

## CTA

- **Primary:** [Start Using Templates](quick-start.md)
- **Secondary:** [Govern](metadata-and-contracts/index.md) · [Deploy](deployment-and-promotion.md) · [API](reference/index.md)
