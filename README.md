# FabricOps Starter Kit

**Microsoft Fabric gives you the platform. FabricOps gives you the operating practice.**

<div align="center">

[![Documentation Home](https://img.shields.io/badge/Documentation-Home-blue?style=for-the-badge)](https://voycepeh.github.io/FabricOps-Starter-Kit/)

[![Notebook Templates](https://img.shields.io/badge/Notebook-Templates-blue?style=for-the-badge)](https://voycepeh.github.io/FabricOps-Starter-Kit/notebook-templates/)

[![Call Flow Diagram](https://img.shields.io/badge/Call_Flow-Dashboard-blue?style=for-the-badge)](https://voycepeh.github.io/FabricOps-Starter-Kit/function-call-graph/)

</div>

FabricOps, short for **Fabric Operations**, provides plug-and-play Data Engineering and Data Governance foundations for Microsoft Fabric.

It gives teams a repeatable operating model across **Governance ↔ Data Engineering → AI and BI analytics**, using standardized notebook templates, reusable notebook-facing functions, and a shared metadata model.

The goal is to make the desired data practice executable. Instead of treating governance, metadata, quality checks, profiling, lineage, and contract context as separate documentation work, FabricOps builds them into the engineering workflow so the resulting Production data foundation can be understood, validated, promoted, reused, and consumed consistently.

## How FabricOps works

FabricOps connects Governance and Engineering through shared metadata and Data Contracts.

Engineers configure environments, ingest and transform data, profile outputs, capture catalogue and lineage context, and validate governed expectations. Governance authors and refines Enrichment, Guardrails, Data Agreements, and Data Contracts. Those contracts are then selected and tested in the engineering flow before approved versions are activated for Production use.

The result is a standardized path from development to governed Production data rather than a collection of disconnected notebooks, checks, and metadata tables.

## Execution engines

FabricOps runs engineering workflows through **PySpark notebooks**.

Within that notebook experience, operations should execute close to the underlying data where practical. Lakehouse workloads use PySpark, while Warehouse workloads can use SQL pushdown for operations such as filtering, profiling, and validation instead of materialising unnecessarily large Warehouse datasets in Spark.

PySpark remains the shared orchestration and transformation layer when data needs to move between systems or undergo more complex engineering work. Python is used for lightweight configuration, orchestration, and supporting logic rather than as a separate equivalent execution engine.

## Start here

- [How FabricOps works](https://voycepeh.github.io/FabricOps-Starter-Kit/how-fabricops-works/) — understand the operating model, Governance ↔ Engineering loop, Data Contracts, and Production path.
- [Guided Demo](https://voycepeh.github.io/FabricOps-Starter-Kit/guided-demo/) — run the workflow step by step.
- [Notebook Templates](https://voycepeh.github.io/FabricOps-Starter-Kit/notebook-templates/) — use the standardized FabricOps notebook structure.
- [Function Reference](https://voycepeh.github.io/FabricOps-Starter-Kit/reference/) — explore the public notebook-facing APIs.
- [FabricOps Glossary](https://voycepeh.github.io/FabricOps-Starter-Kit/glossary/) — use the repository terminology source of truth.
- [Releases](https://voycepeh.github.io/FabricOps-Starter-Kit/releases/) — see what is available in each release.
