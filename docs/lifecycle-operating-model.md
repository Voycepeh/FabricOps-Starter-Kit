# Workflow

This page explains: the operating model for roles, approvals, and AI-vs-human responsibilities.
Use this when: you need checkpoint ownership and accountability before implementation details.
Next read: [Start](quick-start.md), [Govern / Metadata](metadata-and-contracts/index.md), [Deploy](deployment-and-promotion.md).

<figure markdown>
  ![Orientation diagram connecting workflow operating model, notebook implementation boundaries, and metadata contract evidence](assets/docs-orientation.png){ .full-width }
  <figcaption>Role lifecycle ownership belongs here: people, process, and approval checkpoints.</figcaption>
</figure>

## Role-based workflow

| Stage | Primary roles | AI responsibility | Human responsibility | Approval checkpoint |
| --- | --- | --- | --- | --- |
| Agreement setup | Data owner, governance steward | Draft context suggestions where needed. | Confirm scope, ownership, usage boundaries. | Agreement intent approved. |
| Exploration and DQ drafting | Analyst, delivery engineer | Suggest candidate DQ rules from profiling evidence. | Review and approve/reject candidate rules. | DQ policy approved for enforcement. |
| Pipeline enforcement | Delivery engineer, platform operator | Assist with draft diagnostics and summaries. | Execute deterministic controls and validate outcomes. | Operational readiness accepted. |
| Governance operations | Governance steward, data owner | Suggest governance annotations/classification candidates. | Approve policy metadata and release posture. | Governance sign-off recorded. |

## Stage checkpoints

- **No policy without approval:** AI suggestions never become active controls until humans approve.
- **No production promotion without evidence:** enforcement and governance evidence must be present.
- **No ownership gaps:** every stage has named human accountable roles.
