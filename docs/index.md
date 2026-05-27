# FabricOps Starter Kit

## Standardize how teams build, govern, and operationalize Fabric notebooks.

AI-assisted metadata, data quality, governance, and pipeline workflows for Microsoft Fabric.

<div class="center-cta">
  <a class="md-button md-button--primary" href="quick-start/">Quick Start</a>
  <a class="md-button" href="workflow/">View Notebook Workflow</a>
</div>

## The problem

Without a shared notebook operating model:

- Exploratory notebooks drift into one-off patterns.
- Governance decisions become fragmented across teams.
- Data quality logic gets duplicated and harder to maintain.
- Operational handover becomes inconsistent.

## Notebook operating workflow

How exploratory notebooks become governed operational data products:

### 1. [`00_env_config`](notebook-structure/00-env-config.md)
Shared environment and workspace configuration.

---

### 2. [`01_da_<agreement>`](notebook-structure/01-data-sharing-agreement.md)
Approved business context, permissions, and governance scope.

---

### 3. [`02_ex_<agreement>_<topic>`](notebook-structure/02-exploration.md)
Profiling, exploration, validation, and AI-assisted rule drafting.

---

### 4. [`03_pc_<agreement>_<pipeline>`](notebook-structure/03-pipeline-contract.md)
Production-ready pipeline notebook enforcing approved rules and outputs.

---

### 5. [`04_gov_<agreement>_<dataset>_<table>`](notebook-structure/04-governance-enrichment.md)
Governance review, classification, and approval evidence workflow.

## Why the workflow matters

- Reusable notebook structure.
- AI-assisted governance workflows.
- Operational handover.
- Auditable metadata evidence.
- Reusable pipeline contracts.
- Production-ready notebook workflows.

## AI-assisted data quality

![AI assisted data quality workflow](assets/DQ-with-ai.png)

<div class="center-cta">
  <a class="md-button" href="ai-assisted-data-quality/">Explore AI Data Quality</a>
</div>

## Metadata & contracts

![Data contract assembly from approved metadata evidence](assets/data-contract.png)

<div class="center-cta">
  <a class="md-button" href="metadata-and-contracts/">View Metadata and Contracts</a>
</div>

## Run in Fabric

Install the package, run the notebooks, and promote governed outputs through the lifecycle.

<div class="center-cta">
  <a class="md-button md-button--primary" href="setup/create-wheel/">Create Wheel</a>
  <a class="md-button" href="setup/run-in-fabric/">Run in Fabric</a>
</div>
