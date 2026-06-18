# How FabricOps Works

FabricOps Starter Kit is a lightweight Microsoft Fabric operating model for reusable notebook delivery, shared metadata evidence, and governed pipeline execution.

This overview explains how the system works: the workspace operating model, the role workflow, how metadata moves between notebooks, and what FabricOps abstracts. For practical instructions about which notebook to open and run, use the [Template Notebooks user guide](notebook-templates.md).

## Workspace Operating Model

![FabricOps operating model overview](../assets/fabricops-operating-model-overview.png)

*Figure: FabricOps operates as a governed notebook workflow across workspace configuration, Lakehouse/Warehouse targets, shared metadata, runtime guardrails, and review.*

FabricOps Starter Kit assumes Microsoft Fabric is the execution runtime and GitHub is the source of truth for reusable project assets. The operating model keeps the moving parts visible:

| Component | Responsibility | FabricOps handoff |
| --- | --- | --- |
| Workspace | Hosts notebooks, Lakehouses/Warehouses, runtime identity, and interactive execution. | `00_env_config` captures workspace/runtime context and validates configured targets. |
| Source target | Lakehouse, Warehouse, files, or other configured input location. | `02_pipeline` reads through configured IO helpers rather than hardcoded paths. |
| Metadata target | Dedicated metadata Lakehouse/schema for `METADATA_*` tables. | Every notebook reads/writes shared evidence through the configured `metadata` route. |
| Target output | Curated Lakehouse/Warehouse table or file output. | `02_pipeline` writes only after guardrails allow continuation. |
| Governance review | Human review of rules, enrichment, and lifecycle state. | `03_governance` appends review decisions instead of mutating away history. |
| Dashboard/reporting | Visibility over current state and historical evidence. | Dashboard pages consume metadata tables; they do not become the source of truth. |

The model is intentionally notebook-first for handover. Junior engineers can open the active notebook, see what it owns, then inspect the metadata table it writes. Governance users can review durable evidence without reverse-engineering cell order from a previous run.

## Role workflow

![FabricOps role workflow](../assets/fabricops-role-workflow.png)

The role workflow keeps implementation and review responsibilities clear without requiring every user to understand every notebook line by line:

1. Project owners, engineers, or workspace administrators run `00_env_config` to establish runtime configuration and metadata routing.
2. Governance users, data stewards, project owners, or supporting engineers run `01_agreement` to record approved steward and agreement context.
3. Engineers, analyst engineers, or data scientists run `02_pipeline` to execute governed source-to-target delivery under the selected agreement context.
4. Governance users, stewards, reviewers, or supporting engineers run `03_governance` to review evidence, rules, enrichment, approvals, rejections, replacements, deactivations, and lifecycle decisions.
5. Dashboard and reference pages read shared metadata and source-generated docs so current state, history, and implementation details remain visible.

[Open the Template Notebooks user guide](notebook-templates.md){ .md-button .md-button--primary }

## How metadata moves between notebooks

FabricOps notebooks do not depend on notebook memory or informal handover notes. Each notebook reads and writes shared metadata so configuration, agreement context, catalogue evidence, guardrail results, lineage, run status, and review decisions remain visible across the workflow.

<div class="grid cards" markdown="1">

-   **`00_env_config`**

    Creates workspace, runtime, and metadata configuration.

-   **`01_agreement`**

    Records steward, agreement, and approved usage context.

-   **`02_pipeline`**

    Uses agreement context, executes data movement, writes catalogue evidence, guardrail results, lineage, and run status.

-   **`03_governance`**

    Reviews rules, enrichment, lifecycle decisions, and approval state.

-   **Dashboard and reference pages**

    Read metadata tables to show current state, history, and implementation details.

</div>

The Overview page explains how the system works. The [Template Notebooks page](notebook-templates.md) explains what to open and run.

## What FabricOps abstracts

FabricOps abstracts the repeated setup and governance work that often slows down Microsoft Fabric delivery. Instead of asking every analyst, data scientist, or engineer to design their own workspace conventions, notebook structure, metadata capture, and review process, the starter kit provides a lightweight operating model that teams can reuse.

It does this through config driven engineering, standardized notebook templates, shared metadata collection, and pipeline guardrails. Engineers can focus on data movement and transformation. Analysts and data scientists can work from clearer inputs and reusable patterns. Governance users can review evidence, rules, enrichment, and lifecycle decisions without reading every notebook line by line.

Use the pages in this section as the user guide for running and adapting the starter notebooks. Use the generated [Function Reference](../reference/) only when you need callable-level details.
