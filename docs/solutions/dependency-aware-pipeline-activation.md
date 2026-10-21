# Governed Pipelines from Development to Production

<span class="fabricops-release-status fabricops-release-status--preview">Preview</span>

![Development validation of affected pipelines followed by coordinated Production activation](../assets/governed-pipelines-development-to-production.png){ .fabricops-solution-hero }

*Develop pipelines with versioned Data Contracts, validate shared dependencies, and promote them safely to Production.*

## What is a Data Contract?

A **Data Contract** is a shared agreement between the teams producing and consuming a dataset. It defines what data a pipeline is expected to deliver, how its quality is assessed, and how sensitive information must be handled.

A schema describes the columns and their data types. A Data Contract goes further by defining the rules and responsibilities associated with that data:

- **Structure:** Which columns exist, their data types, and which fields are required.
- **Data quality:** Expectations such as completeness, uniqueness, valid values, and acceptable failure thresholds.
- **Sensitive data:** Which fields need protection and what treatment should be applied.
- **Ownership and accountability:** Who is responsible for the dataset and its agreed expectations.

For example, an employee dataset might require a non-null `employee_id`, unique employee records, valid department values, and protection of personal identifiers. These are explicit, testable expectations rather than assumptions that downstream users must discover themselves.

In FabricOps, Data Contracts provide the governance rules used to validate pipeline reads and writes. **Versioning lets teams develop against proposed changes without immediately changing the contract used in Production.**

## The problem

Pipelines depend on one another. A change that works in Development can still break downstream pipelines in Production.

## The solution

<div class="fabricops-mascot-callout">
  <img src="/FabricOps-Starter-Kit/assets/mascots/robot-validate.png" alt="FabricOps validation mascot" loading="eager">
  <div><p><strong>Develop confidently. Promote safely.</strong> Validate affected pipelines together before changing Production.</p></div>
</div>

FabricOps aims to identify dependencies, validate compatible Data Contracts, and coordinate promotion of affected pipelines.

## From Development to Production

**Development:** Build and validate pipelines against versioned Data Contracts without affecting Production.

**Production:** Governance reviews validation evidence and activates compatible changes together.

*Coordinated dependency-aware promotion is planned and marked Preview.*

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
