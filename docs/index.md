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

Use this lifecycle as a workflow navigator. Start at `00_env_config`, then move stage-by-stage into governed operations.

### Step 1 — [`00_env_config`](notebook-structure/00-env-config.md)
Environment and workspace setup for shared runtime configuration.

[View notebook stage →](notebook-structure/00-env-config.md)

⬇️

### Step 2 — [`01_da_<agreement>`](notebook-structure/01-data-sharing-agreement.md)
Business context, permissions, and agreement approvals.

[View notebook stage →](notebook-structure/01-data-sharing-agreement.md)

⬇️

### Step 3 — [`02_ex_<agreement>_<topic>`](notebook-structure/02-exploration.md)
Profiling, exploration, validation, and AI-assisted rule drafting.

[View notebook stage →](notebook-structure/02-exploration.md)

⬇️

### Step 4 — [`03_pc_<agreement>_<pipeline>`](notebook-structure/03-pipeline-contract.md)
Production-ready pipeline notebook that enforces approved rules and outputs.

[View notebook stage →](notebook-structure/03-pipeline-contract.md)

⬇️

### Step 5 — [`04_gov_<agreement>_<dataset>_<table>`](notebook-structure/04-governance-enrichment.md)
Governance review, classification, and approval evidence workflow.

[View notebook stage →](notebook-structure/04-governance-enrichment.md)

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
