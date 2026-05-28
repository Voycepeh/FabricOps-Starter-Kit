# FabricOps Starter Kit Operating Model

FabricOps Starter Kit gives teams a lightweight way to coordinate governance, analysis, and engineering around approved metadata and contract-ready evidence. AI can accelerate suggestion, drafting, review, and summarization, but people remain accountable for decisions, approvals, and implementation readiness.

<figure markdown>
  ![FabricOps Starter Kit workflow showing how governance, analysts, data scientists, engineers, AI assistance, metadata, contracts, and handover work together](assets/mvp-flow.png){ .full-width }
  <figcaption>Governed, quality-checked, AI-ready collaboration from business need to approved metadata, engineering delivery, and handover.</figcaption>
</figure>

## How to read this workflow

The workflow is a collaboration model, not a notebook execution guide:

- **Governance stewards** define the business scope, required approvals, metadata expectations, and usage boundaries.
- **Analysts and data scientists** explore source data, validate business meaning, and review candidate quality controls before they become approved metadata.
- **Data engineers** implement pipeline behavior from approved metadata and rules, then publish handover evidence for operational use.
- **AI assists at selected points**, such as drafting metadata or summarizing evidence, but human approval remains central where governance, control, and usage decisions matter.

For implementation detail, use the [Quick Start](quick-start.md), [Notebook Structure / Templates](notebook-structure.md), [Metadata and Contracts](metadata-and-contracts/index.md), and [API Reference](reference/index.md) pages.

## Roles in the workflow

### Governance steward

Governance stewards set the business-facing boundaries for the work. They define or approve scope, permissions, restrictions, sensitivity, stewardship decisions, and intended use. They are accountable for the controls and usage boundaries that determine whether metadata and contracts are safe to use.

### Analyst / data scientist

Analysts and data scientists turn raw data into validated business understanding. They profile and explore data, validate meaning with stakeholders, review candidate data quality logic, and help convert data understanding into approved metadata and usable controls.

### Data engineer

Data engineers build the technical implementation from approved inputs. They operationalize quality checks, manage pipeline behavior, publish lineage and quality evidence, and produce handover output that downstream teams can understand and reuse.

## Where AI helps

AI is in the loop to speed up repeatable drafting and review work. It can help draft metadata, suggest data quality rules, summarize profiling outputs, and assemble handover evidence.

AI does **not** replace accountability. Use these interaction patterns to keep ownership clear:

- **AI suggests, human approves** when governance, sensitivity, restrictions, or quality rules affect policy or control decisions.
- **AI assists, human validates** when analysts and data scientists use suggestions to accelerate exploration, profiling, or rule review.
- **AI generates from approved evidence** when the output is a summary, handover artifact, or contract-ready view based on already approved metadata and results.

## How the roles work together

FabricOps Starter Kit works best when each role contributes at the right point:

- Governance sets boundaries and approves intended use before engineering treats metadata as implementation-ready.
- Analysis converts source data into reviewed business meaning and candidate controls.
- Engineering implements only from approved metadata, reviewed rules, and agreed operating expectations.
- The metadata and contract store acts as the shared source of truth between roles.
- Handover is the result of coordinated governance, analysis, and engineering work rather than a separate afterthought.

## What this operating model produces

The operating model keeps the work concise, reviewable, and ready for delivery. Typical outputs include:

- Approved metadata and stewardship decisions.
- Reviewed data quality controls.
- Reusable inputs for pipeline implementation.
- Lineage and quality evidence.
- Contract-ready handover output.
