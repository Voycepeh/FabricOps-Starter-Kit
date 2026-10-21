# Governed Pipelines from Development to Production

<span class="fabricops-release-status fabricops-release-status--preview">Preview</span>

![Development validation of affected pipelines followed by coordinated Production activation](../assets/governed-pipelines-development-to-production.png){ .fabricops-solution-hero }

*Develop pipelines with versioned Data Contracts, validate shared dependencies, and promote them safely to Production.*

## What is a Data Contract?

A **Data Contract** defines the expectations for a dataset: its structure, quality rules, and how sensitive information should be handled. It gives Data Engineers and Governance teams a shared definition of what a pipeline must deliver.

For example, an employee dataset may require an `employee_id` column, prohibit missing employee identifiers, and specify how personal information is protected. A pipeline can then be validated against these expectations before its output is used downstream.

**A Data Contract defines what good data looks like. FabricOps helps keep that agreement consistent as pipelines evolve.**

## The problem

Data pipelines rarely operate in isolation. One pipeline writes a table, while several others may read it and depend on its structure and quality.

A pipeline change can pass its own checks in Development yet still break a downstream workload in Production. Teams must otherwise work out which pipelines are affected, confirm that they remain compatible, and coordinate when to promote the changes.

## The solution

<div class="fabricops-mascot-callout">
  <img src="/FabricOps-Starter-Kit/assets/mascots/robot-validate.png" alt="FabricOps validation mascot" loading="eager">
  <div><p><strong>Develop confidently. Understand the impact. Promote safely.</strong> Keep connected pipelines aligned with their Data Contracts as they move from Development to Production.</p></div>
</div>

The proposed FabricOps promotion workflow brings together versioned Data Contracts, pipeline dependencies, and validation evidence so teams can:

- **Develop independently** without disrupting Production.
- **See what's affected** when a shared table or pipeline changes.
- **Validate connected pipelines** rather than checking each in isolation.
- **Promote compatible changes together** under Governance approval.

This is a **Preview** of the planned dependency-aware, coordinated-promotion capability, not a claim that every dependency check is implemented today.

## From Development to Production

In **Development**, engineers select frozen Data Contract versions, build their pipelines, and validate affected dependencies without changing Production. In **Production**, Governance reviews successful validation evidence and coordinates activation of compatible configurations. Contract definitions are centrally managed, while the active version remains specific to each environment.

## How it works

| Responsibility | What happens |
| --- | --- |
| **Governance authors** | Freezes a new Data Contract version for a table. |
| **Engineering develops and validates** | Runs affected pipelines against the proposed frozen version. |
| **FabricOps checks** | Identifies active readers, writer ownership, version conflicts and affected downstream dependencies. |
| **Governance promotes and activates** | Reviews complete Testing evidence and approves a coordinated switch. |

## Under the hood

<div class="fabricops-mascot-callout">
  <img src="/FabricOps-Starter-Kit/assets/mascots/robot-prod.png" alt="FabricOps production mascot" loading="lazy">
  <div><p>Explore how shared-table dependencies affect the decision to activate a new contract.</p></div>
</div>

??? info "Shared-table governance invariants"

    - One global `table_id` and centrally managed Data Contract version history.
    - One active contract version per environment and table.
    - One active writer per environment and table; multiple readers are allowed.
    - One active configuration per environment and pipeline.
    - Testing may select any frozen version associated with the table.
    - An activatable Testing run requires frozen contracts for every participating table; contract-free exploratory Testing is not eligible.

??? info "Cascading dependency checks"

    When a proposed activation changes a shared table's contract, FabricOps should identify active pipelines referencing that table, including the writer and readers. Affected downstream pipelines are included when their effective inputs or contract expectations change.

    Every affected pipeline must have complete successful Testing evidence for compatible contract mappings. Missing tests, conflicting contract versions and competing writers block activation.

    Coordinated activation must publish consistent governance metadata. It does not imply that notebook deployments, already-running executions and business-table writes are transactionally atomic.

## Example

??? info "Upgrade the hr.employees Data Contract from v3 to v4"

    **Current PROD:** Pipeline A writes the table on v3, Pipeline B reads it on v3, and Pipeline C is an affected downstream consumer.

    1. Governance freezes v4 without changing the active PROD version.
    2. Engineers test A and B on v4, and C where its expectations change.
    3. FabricOps collects complete successful runs and identifies missing evidence.
    4. Governance reviews and approves the affected pipeline configurations together.
    5. PROD activates the consistent v4 mappings. DEV may independently use a different active version.

    **Blocked case:** A passes v4 Testing but B remains Live on v3 without compatible Testing evidence. A cannot activate alone.

## Go deeper

See [Plug-and-Play Data Pipelines](plug-and-play-data-pipelines.md) for the engineering workflow and [Step 5: Activate Data Contract and Promote](../guided-demo/05-activate-data-contract-and-promote.md) for the current activation walkthrough.
