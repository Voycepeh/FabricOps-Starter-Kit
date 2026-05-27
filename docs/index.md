# FabricOps Starter Kit

## Standardize how teams build, govern, and operationalize Fabric notebooks.

AI-assisted metadata, data quality, governance, and pipeline workflows for Microsoft Fabric.

<div class="center-cta">
  <a class="md-button md-button--primary" href="quick-start/">Start with Quick Start</a>
  <a class="md-button" href="reference/">Browse Functions</a>
</div>

## The problem FabricOps solves

Without a shared notebook operating model:

- Exploratory notebooks drift into one-off patterns.
- Governance decisions are split across files and teams.
- Data quality logic gets duplicated and hard to maintain.
- Pipelines are harder to operationalize, schedule, and hand over.

![FabricOps workflow overview](assets/mvp-flow.png)

<div class="center-cta">
  <a class="md-button" href="workflow/">View Workflow</a>
</div>

## The notebook operating model

FabricOps uses a predictable notebook sequence so teams can move from exploration to governed operations with clear ownership.

![FabricOps governance and workspace model](assets/notebook-structure.png)

| Notebook | Practical role in the workflow |
|---|---|
| `00_env_config` | Shared environment and workspace configuration. |
| `01_da_<agreement>` | Defines approved business context, permissions, and governance scope. |
| `02_ex_<agreement>_<topic>` | Used for profiling, exploration, validation, and AI-assisted rule drafting. |
| `03_pc_<agreement>_<pipeline>` | Production-ready pipeline notebook for enforcing approved rules and outputs. |
| `04_gov_<agreement>_<dataset>_<table>` | Governance review, classification, and approval evidence workflow. |

<div class="center-cta">
  <a class="md-button" href="notebook-structure/">View Notebook Structure</a>
</div>

## Why this operating model matters

- Reusable notebook structure across projects and teams.
- AI-assisted governance workflows with human approval.
- Clear operational handover from exploration to production.
- Auditable metadata evidence for decisions and enforcement.
- Reusable pipeline contracts for repeatable execution.
- Production-ready notebook workflows that are scheduler-friendly.

## Supporting architecture views

These diagrams support the workflow above and show how contracts and quality operations are implemented.

### Metadata and contract assembly

![Data contract assembly from approved metadata evidence](assets/data-contract.png)

<div class="center-cta">
  <a class="md-button" href="metadata-and-contracts/">View Metadata and Contracts</a>
</div>

### AI-assisted data quality workflow

![AI assisted data quality workflow](assets/DQ-with-ai.png)

<div class="center-cta">
  <a class="md-button" href="ai-assisted-data-quality/">View AI Data Quality</a>
</div>

## Run it in Fabric

Install the package, run the notebooks, and promote governed outputs through the lifecycle.

<div class="center-cta">
  <a class="md-button md-button--primary" href="setup/create-wheel/">Create Wheel</a>
  <a class="md-button" href="setup/run-in-fabric/">Run in Fabric</a>
  <a class="md-button" href="deployment-and-promotion/">View Deployment</a>
</div>
