# FabricOps Product Narrative

This page is the source of truth for the product story used across the repository README and documentation. Keep the same meaning and terminology when updating user-facing pages. Preserve early brainstorming and alternative wording in issue or pull request history rather than creating a second competing narrative page.

## Canonical description

FabricOps (Fabric Operations) is a plug-and-play, lightweight starter kit that helps data teams quickly set up and adopt a standardized notebook workflow in Microsoft Fabric.

It is designed for teams working across governance, data engineering, and AI and BI analytics. FabricOps combines a Python package of ready-to-use helper and orchestrator functions, standardized notebook templates, shared metadata tables, a Guided Demo, and technical reference documentation.

By standardizing the workflow, FabricOps weaves essential metadata and governance processes into everyday notebook development. This gives teams a consistent foundation for data quality, lineage, handover, and AI-assisted development without having to build every supporting process from scratch.

## Why it exists

Data teams often include people with different governance, engineering, analytics, and data science backgrounds. Without a common structure, each project can configure Fabric items, organize notebooks, capture metadata, apply data quality checks, and hand over work differently.

FabricOps provides a shared starting point. The notebook templates make the workflow visible, the Python package abstracts repeated Fabric operations, and the metadata tables preserve the context and evidence needed by the next person or AI agent working on the project.

FabricOps is a lightweight starter kit, not a full engineering framework, a standalone governance platform, or a standalone data quality product.

## What the starter kit contains

| Part | Role in the product story |
| --- | --- |
| Python package | Provides ready-to-use helper and orchestrator functions for common Fabric notebook operations. |
| Notebook templates | Weave the functions into a standardized workflow that teams can adopt and adapt. |
| Shared metadata tables | Connect agreement, profiling, catalogue, lineage, enrichment, guardrail intent, and guardrail results across the workflow. |
| Guided Demo | Shows users how to set up the Fabric artifacts and run the workflow in the intended order. |
| Technical documentation | Explains the operating model and provides detailed notebook, metadata, DQ rule, function, release, and maintainer references. |

## Reader journey and page ownership

Each page should answer one main question and then direct the reader to the next level of detail.

| Page | Main question | Content it owns | Next destination |
| --- | --- | --- | --- |
| Repository README | What is FabricOps, and where should I start? | Concise product description, documentation entry point, notebook links, release status. | Documentation Home |
| Documentation Home | Why does FabricOps exist, who is it for, and what is included? | Product story, supported roles, included components, and the recommended learning path. | How FabricOps Works |
| How FabricOps Works | How do the notebooks, package, roles, and metadata tables work together? | Operating model, role workflow, notebook sequence, metadata handoffs, and what FabricOps abstracts. | Guided Demo |
| Guided Demo | How do I run the complete workflow in Microsoft Fabric? | Maintainer setup, user run sequence, expected evidence, and success criteria. | Templates or the relevant reference page |
| Notebook Templates | Which notebook should I use? | Download links, notebook roles, and the maintained notebook sequence. | Matching Guided Demo step |
| Metadata Table Reference | What evidence does each metadata table store? | Implemented table purpose, schema, writer ownership, and relationships. | Related function or workflow page |
| DQ Rule Reference | Which data quality rule should I use? | Rule vocabulary, parameters, examples, and runtime behavior. | Governance and guardrail workflow |
| Function Reference | How do I call a FabricOps function? | Generated signatures, parameters, return meaning, examples, errors, lifecycle, and call flow. | Related Guided Demo or metadata page |
| Releases | What is available in a specific version? | Versioned lifecycle status, release assets, and compatibility evidence. | Relevant user or maintainer reference |
| Maintainer Guide | How is FabricOps changed and released safely? | Source ownership, deterministic generation, human decisions, validation, and release procedure. | Repository source and release workflow |

## Messaging rules

- Use **FabricOps Starter Kit** as the public product name and **FabricOps (Fabric Operations)** when expanding the name.
- Describe it as a **plug-and-play, lightweight starter kit** for Microsoft Fabric notebook workflows.
- Keep the three supported areas visible: **governance**, **data engineering**, and **AI and BI analytics**.
- Use **Guided Demo** as the user-facing name.
- Describe metadata as the shared handoff layer across roles and notebooks.
- Keep detailed architecture out of the README and detailed execution steps out of the documentation home page.
- Link to the canonical detailed page instead of copying the same explanation into several pages.
- Do not claim support for metadata tables, notebook steps, or release capabilities that are not present in the current implemented schema or release contract.
