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

<div class="cta-center">
  <a class="md-button md-button--primary" href="notebook-templates.md">
    Open the Template Notebooks user guide
  </a>
</div>

## How metadata moves between notebooks

FabricOps notebooks do not pass state through notebook memory or informal handover notes. They share state through metadata tables, so each notebook can continue from the configuration, agreement context, pipeline evidence, and review decisions written by earlier steps.

<div class="metadata-flow-grid">

<div class="metadata-flow-card">
<strong><code>00_env_config</code></strong>
<p>Creates the metadata foundation.</p>
<p>Writes or validates the 12 metadata tables used by the workflow.</p>
</div>

<div class="metadata-flow-card">
<strong><code>01_agreement</code></strong>
<p>Captures agreement and steward context.</p>
<p>Writes to agreement metadata tables, including agreement records, steward context, approved usage, and supporting agreement evidence.</p>
</div>

<div class="metadata-flow-card">
<strong><code>02_pipeline</code></strong>
<p>Runs governed source to target delivery.</p>
<p>Reads agreement and configuration metadata.</p>
<p>Writes pipeline evidence, schema evidence, DQ results, drift results, lineage, output table records, and run status.</p>
</div>

<div class="metadata-flow-card">
<strong><code>03_governance</code></strong>
<p>Reviews and approves governed outputs.</p>
<p>Reads agreement, pipeline evidence, schema evidence, DQ results, drift results, lineage, and run status.</p>
<p>Writes review decisions, approval state, rule outcomes, enrichment decisions, lifecycle decisions, and production handover state.</p>
</div>

</div>

Dashboard and reference pages consume metadata to show current state, history, and implementation details; they are not writers in the notebook workflow.
