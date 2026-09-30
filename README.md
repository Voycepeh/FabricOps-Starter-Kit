# FabricOps Starter Kit

**Microsoft Fabric gives you the platform. FabricOps gives you the operating practice.**

<div align="center">

[![Documentation Home](https://img.shields.io/badge/Documentation-Home-blue?style=for-the-badge)](https://voycepeh.github.io/FabricOps-Starter-Kit/)

</div>

FabricOps, short for **Fabric Operations**, provides plug-and-play Data Engineering and Data Governance foundations for Microsoft Fabric.

It gives teams a repeatable operating model across **Governance ↔ Data Engineering → AI and BI analytics**, using standardized notebook templates, reusable notebook-facing functions, Data Contracts, and a shared metadata model.

The goal is to make the desired data practice executable. Instead of treating governance, metadata, quality checks, profiling, lineage, and contract context as separate documentation work, FabricOps builds them into the engineering workflow so Production data can be understood, validated, promoted, reused, and consumed consistently.

## The Big Picture

FabricOps connects Governance and Engineering through a shared Metadata Lakehouse and versioned Data Contracts.

- **Governance** defines Data Stewards, Data Agreements, Enrichment, Guardrails, Data Contracts, and access metadata.
- **Engineering Development** builds and profiles the real pipeline, captures catalogue and lineage metadata, and validates frozen Data Contract versions.
- **Engineering Production** runs the same validated pipeline using Production configuration and the active Data Contract.
- **Consumer workspaces** read approved Production data without recreating the governed engineering pipeline.

Development and Production keep the same logical Bronze, Silver, and Gold architecture while FabricOps environment configuration resolves the physical Fabric objects for each environment.

[Read How FabricOps works →](https://voycepeh.github.io/FabricOps-Starter-Kit/how-fabricops-works/)

## Data Contracts

A FabricOps Data Contract is the **versioned, executable governance definition for one governed `table_id`**.

Engineering supplies what physically exists through catalogue, profiling, lineage, and source observations. Governance adds what the data means and what must be enforced through Enrichment, Processing, and Guardrails. FabricOps persists that governed definition as a versioned JSON manifest in `METADATA_DATA_CONTRACT`.

Drafts can be reviewed and changed. Freezing makes a contract version immutable. Engineering validates the exact frozen version against the real pipeline. Once approved, Governance activates that tested version for Production.

[Explore Data Contracts in How FabricOps works →](https://voycepeh.github.io/FabricOps-Starter-Kit/how-fabricops-works/#data-contracts)

## The 7-step FabricOps lifecycle

| Step | What happens |
| --- | --- |
| **1. Establish Governance context** | Create Data Stewards and a Data Agreement. |
| **2. Build and run the ETL** | Run the real Engineering Development pipeline and capture its technical metadata. |
| **3. Author and freeze the Data Contract** | Select the real `table_id`, author Enrichment, Guardrails, and Processing, then freeze the contract version. |
| **4. Validate the frozen Data Contract** | Evaluate the exact frozen candidate against the real pipeline. |
| **5. Activate the Data Contract and promote** | Activate the tested version for Production and promote the validated engineering artifact. |
| **6. Run the pipeline in Production** | Run the same workflow using Production configuration and the active Data Contract. |
| **7. Consume approved Production data** | Read approved Production outputs from a consumer workspace. |

**Steps 3 ↔ 4 are intentionally iterative.** Governance can refine the next contract version and Engineering validates it again until the governed definition and implementation agree.

[Run the full Guided Demo →](https://voycepeh.github.io/FabricOps-Starter-Kit/guided-demo/)

## What FabricOps provides

FabricOps packages the operating model into a small set of reusable assets:

- **Notebook templates** for environment configuration, Governance, Engineering pipelines, and Production consumption.
- **Public Python functions** for Fabric-aware I/O, profiling, metadata registration, Guardrail enforcement, contract workflows, and related notebook operations.
- **Data Contracts** that combine observed Engineering metadata with reviewed Governance decisions.
- **Metadata tables** that connect catalogue, profiling, lineage, source observations, Steward and Agreement context, contracts, Guardrail results, and access information.

PySpark notebooks remain the shared orchestration and transformation layer. Lakehouse workloads use PySpark, while Warehouse workloads can use SQL pushdown where practical.

## Featured Solutions

- [Sensitive Data Classification & Treatment](https://voycepeh.github.io/FabricOps-Starter-Kit/solutions/ai-assisted-data-contract-authoring/) — classify sensitive data and enforce governed treatments before publication, with optional AI assistance during authoring.
- [Generate Enforceable Data Quality Rules from Business Rules](https://voycepeh.github.io/FabricOps-Starter-Kit/solutions/business-rules-to-data-quality/) — turn plain-language business rules into reviewable, deterministic Data Quality rules.
- [Plug-and-Play Data Pipelines with Data Contract Enforcement](https://voycepeh.github.io/FabricOps-Starter-Kit/solutions/plug-and-play-data-pipelines/) — promote the same pipeline while configuration resolves environment-specific Fabric resources.
- [Scan Effective Data Access](https://voycepeh.github.io/FabricOps-Starter-Kit/solutions/effective-data-access/) — resolve effective access across overlapping Fabric permission paths.
- [Public Function Call Flow Dashboard](https://voycepeh.github.io/FabricOps-Starter-Kit/assets/public-function-call-flows-dashboard.html) — explore generated public callable relationships and architecture signals.

## Download FabricOps

Use the [Guided Demo](https://voycepeh.github.io/FabricOps-Starter-Kit/guided-demo/) for the end-to-end setup and workflow.

- [Releases / Python package](https://voycepeh.github.io/FabricOps-Starter-Kit/releases/)
- [Notebook Templates](https://github.com/Voycepeh/FabricOps-Starter-Kit/tree/main/templates/notebooks)
- [Demo Assets](https://github.com/Voycepeh/FabricOps-Starter-Kit/tree/main/templates/DemoData)

## Reference Documentation

For implementation details, use the dedicated references rather than the README:

- [Function Reference](https://voycepeh.github.io/FabricOps-Starter-Kit/reference/)
- [Data Quality Rules](https://voycepeh.github.io/FabricOps-Starter-Kit/reference/dq-rules/)
- [Metadata Tables](https://voycepeh.github.io/FabricOps-Starter-Kit/reference/metadata/)
- [Glossary](https://voycepeh.github.io/FabricOps-Starter-Kit/glossary/)

For issues or feature requests, use [GitHub Issues](https://github.com/Voycepeh/FabricOps-Starter-Kit/issues).
