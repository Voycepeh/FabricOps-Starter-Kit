# FabricOps Starter Kit

FabricOps, short for **Fabric Operations**, is a plug-and-play Data Engineering and Governance practice for Microsoft Fabric.

It gives teams a ready-to-adopt workflow across **Governance → Data engineering → AI and BI analytics**, using standardized notebook templates, reusable notebook-facing functions, and a shared metadata model.

The goal is to make the desired data practice executable. Instead of treating governance, metadata, quality checks, profiling, lineage, and contract context as separate documentation work, FabricOps builds them into the planned workflow. As the work is performed, FabricOps records Data Agreements, Catalogue metadata, profiles, lineage, source observations, resolved read strategies, governed load strategies and parameters, Enrichment, Guardrails and their results, and Data Contracts in the configured Fabric workspaces and metadata tables where those capabilities are implemented.

This creates a governed Production data foundation that can be understood, validated, promoted, reused, and consumed without rebuilding its context afterwards.

<div align="center">

[![Documentation Home](https://img.shields.io/badge/Documentation-Home-blue?style=for-the-badge)](https://voycepeh.github.io/FabricOps-Starter-Kit/)

[![Notebook Templates](https://img.shields.io/badge/Notebook-Templates-blue?style=for-the-badge)](https://voycepeh.github.io/FabricOps-Starter-Kit/notebook-templates/)

[![View Releases](https://img.shields.io/badge/View-Releases-blue?style=for-the-badge)](https://voycepeh.github.io/FabricOps-Starter-Kit/releases/)

</div>

## Built for AI-assisted engineering

AI can now help teams write PySpark, SQL, Python, tests, and documentation very quickly. Much of FabricOps itself was built with AI assistance and then reviewed against the intended workflow and product rules.

**Humans decide what the data should do and what “good” looks like. FabricOps provides the structure, workflow, and guardrails. AI helps accelerate the coding, testing, documentation, and repetitive engineering work.**

FabricOps gives teams a ready-made skeleton for a Data Engineering and Governance practice, so they can spend less time rebuilding the same foundations and more time on the engineering and analytics work that is specific to their project. Teams can use Microsoft Fabric capabilities such as Copilot, AI Functions, or other AI assistance available in their environment without making the core FabricOps runtime depend on external tooling.

FabricOps was also born from a practical constraint: the Production environment it originated from runs inside Microsoft Fabric, while users may have no general internet access from their local machine to external tools or services beyond Fabric. The framework was therefore designed to be self-contained within Microsoft Fabric, including its reusable functions, metadata structures, validation patterns, and notebook workflow, while still allowing teams to benefit from Fabric-native AI capabilities where available.

**Use AI where it helps you move faster. Keep the Production foundation deterministic, reviewable, and self-contained within Fabric.**

FabricOps is also designed to support future **AI-augmented Governance and Engineering workflows** using the structured context it already captures—for example Enrichment suggestions, Data Quality and Guardrail authoring, contract review, pipeline review, failure explanation, impact analysis, governed discovery, and consumer context preparation. These remain future direction unless separately implemented and documented.

