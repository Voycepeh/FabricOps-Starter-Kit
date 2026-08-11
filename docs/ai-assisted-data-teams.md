# AI-assisted Data Teams

FabricOps is not an AI model, RAG framework, or agent platform. FabricOps is a lightweight starter kit for running a standardized data workflow in Microsoft Fabric.

The same things that help a new person understand that workflow can also help an AI assistant: standardized notebook templates, FabricOps helper and orchestrator functions, FabricOps metadata tables, and approved Production data. The available context includes Data Catalogue, Data Profiled, Data Profiled Frequency, Data Lineage, Data Access, Enrichment, Guardrail, Guardrail Results, Data Agreement, and Data Contract records. `00_env_config` also identifies the configured FabricOps environment.

These components give an assistant concrete places to look and established functions to use. They do not make FabricOps the AI runtime, and they do not remove the need for human review.

## Good AI assistance starts with the existing FabricOps workflow

An AI assistant should work inside the established Governance → Data engineering → AI and BI analytics workflow rather than inventing a parallel process. It should begin with the relevant notebook, read the available FabricOps metadata tables, and use existing FabricOps helper and orchestrator functions where they fit.

This keeps the normal division of responsibilities intact. Governance decisions remain in `01_governance`, repeatable engineering work remains in `02_pipeline`, and one-off exploration remains in `99_explore`. The workflow should continue to produce the same FabricOps records and follow the same Engineering Development to Engineering Production promotion path whether a person works alone or with AI assistance.

## Governance

An AI assistant can help a Data Steward prepare for review. For example, it can:

- review Data Catalogue and Data Profiled records;
- help draft Enrichment values;
- suggest possible Guardrails for a Data Steward to review; and
- help review a Data Contract against its Data Agreement and linked Data Catalogue records.

The Data Steward or other responsible person still approves Enrichment, Guardrails, Data Agreements, Data Contracts, and promotion decisions. Suggestions from an assistant are inputs to that review, not Governance approval.

## Data engineering

An AI assistant can support an engineer while preserving the established pipeline pattern. It can:

- inspect an existing `02_pipeline`;
- help draft transformation code;
- reuse FabricOps read and write functions;
- investigate Data Profiled or Guardrail Results records;
- help explain pipeline failures; and
- follow the existing profiling, Data Catalogue, Data Lineage, Guardrail, and write pattern.

Repeatable engineering work still belongs in `02_pipeline`. It should be developed and validated in Engineering Development and promoted to Engineering Production only after the normal Governance review. An assistant should not move recurring transformations into `99_explore` or build a second path around the FabricOps workflow.

## AI and BI analytics

`99_explore` and Project-Specific Consumer workspaces can support Power BI preparation, data analysis, data science, AI-assisted exploration, and data-agent use cases. These activities should use approved Production data rather than recreating the Production pipeline.

The FabricOps metadata tables can help a person or assistant understand what the data means, how it was profiled, where it came from, which Enrichment and Guardrails apply, and whether Guardrail Results need investigation. The Data Agreement and Data Contract can provide the related ownership and delivery expectations where relevant.

## Reusable AI instructions

FabricOps can later provide small reusable instruction packs for common tasks such as pipeline development, data exploration, DQ investigation, Data Catalogue enrichment, BI exploration, and data science exploration.

These packs should point to the existing notebook workflow and FabricOps helper and orchestrator functions rather than duplicate their documentation. They should state which notebook and records to inspect, which outputs to preserve, and where human review is required. This PR does not add instruction or prompt-pack files.

## Start with a single assistant

A simple pattern is enough for most initial use cases:

1. A person gives the assistant a task.
2. The assistant reads the notebook and available FabricOps context.
3. It proposes or uses the appropriate FabricOps functions.
4. The workflow produces the normal FabricOps outputs.
5. A person reviews the result.

This pattern supports tool use, planning, and reflection without adding another operating model. Teams can start with a narrow task and maintain clear human responsibility for changes and approvals.

## Where multiple agents may fit later

A team may later choose specialized roles such as an Engineering agent, Data Quality agent, Governance agent, or Analytics agent. Those roles would still use the same FabricOps notebooks, FabricOps helper and orchestrator functions, FabricOps metadata tables, and approved Production data. FabricOps is not the multi-agent framework itself.

The goal is to reduce repeated setup and discovery so a new engineer, Data Steward, analyst, data scientist, or AI assistant can understand where approved Production data lives, what the data means, how it was produced, what Guardrails were applied, who is responsible for it, which FabricOps functions and notebooks are available, and which decisions still require human review.
