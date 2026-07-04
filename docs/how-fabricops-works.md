# How FabricOps Works

FabricOps Starter Kit gives data teams a guided starting point for Microsoft Fabric notebook projects. The workflow starts with environment setup, captures agreement context, runs pipelines with guardrails, writes metadata for catalogue, lineage, checks, notebook registry, and pipeline runs, then supports governance review and troubleshooting.

This overview explains how the starter kit works: the workspace setup, the role workflow, how metadata moves between notebooks, and what FabricOps abstracts. For practical instructions about which notebook to open and run, use the [Notebook Templates Implementation Guide](../notebook-templates-implementation-guide/).

## Workspace Operating Model

![FabricOps operating model overview](assets/fabricops-operating-model-overview.png)

*Figure: FabricOps operates as a governed notebook workflow across workspace configuration, Lakehouse/Warehouse targets, shared metadata, runtime guardrails, and review.*

FabricOps Starter Kit assumes Microsoft Fabric is the execution runtime and GitHub is the source of truth for reusable project assets. The operating model keeps the moving parts visible:

| Component | Responsibility | FabricOps handoff |
| --- | --- | --- |
| Workspace | Hosts notebooks, Lakehouses/Warehouses, runtime identity, and interactive execution. | `00_env_config` captures workspace/runtime context and validates configured targets. |
| Source target | Lakehouse, Warehouse, files, or other configured input location. | `02_pipeline` reads through configured IO helpers rather than hardcoded paths. |
| Metadata target | Dedicated metadata Lakehouse/schema for `METADATA_*` tables. | Every notebook reads or writes workflow context through the configured `metadata` route. |
| Target output | Curated Lakehouse/Warehouse table or file output. | `02_pipeline` writes only after guardrails allow continuation. |
| Governance review | Human review of rules, enrichment, and lifecycle state. | `03_governance` appends review decisions instead of mutating away history. |
| Dashboard/reporting | Visibility over current state and run history. | Dashboard pages consume metadata tables; they do not become the source of truth. |

The model is intentionally notebook-first for handover. Junior engineers can open the active notebook, see what it owns, then inspect the metadata table it writes. Governance users can review metadata tables without reverse-engineering cell order from a previous run.

## Role workflow

![FabricOps role workflow](assets/fabricops-role-workflow.png)

The role workflow keeps implementation and review responsibilities clear without requiring every user to understand every notebook line by line:

1. Project owners, engineers, or workspace administrators run `00_env_config` to establish runtime configuration and metadata routing.
2. Governance users, data stewards, project owners, or supporting engineers run `01_agreement` to record approved steward and agreement context.
3. Engineers, analyst engineers, or data scientists run `02_pipeline` to execute governed source-to-target pipeline work under the selected agreement context.
4. Governance users, stewards, reviewers, or supporting engineers run `03_governance` to review rules, enrichment, approvals, rejections, replacements, deactivations, and lifecycle decisions.
5. Dashboard and reference pages read shared metadata and source-generated docs so current state, history, and implementation details remain visible.

<div class="cta-center">
  <a class="md-button md-button--primary" href="../notebook-templates-implementation-guide/">
    Open the Notebook Templates Implementation Guide
  </a>
</div>

## How metadata moves between notebooks

FabricOps notebooks do not pass state through notebook memory or informal handover notes. They share state through metadata tables, so each notebook can continue from the configuration, agreement context, pipeline run details, and review decisions written by earlier steps.

<div class="metadata-flow-grid">

<div class="metadata-flow-card">
<strong><a href="../notebook-templates-implementation-guide/environment-config/"><code>00_env_config</code></a></strong>
<p>Creates the <a href="../reference/metadata/">metadata foundation</a>.</p>
<p>Writes or validates the 12 <a href="../reference/metadata/">metadata tables</a> used by the workflow.</p>
</div>

<div class="metadata-flow-card">
<strong><a href="../notebook-templates-implementation-guide/agreement-setup/"><code>01_agreement</code></a></strong>
<p>Captures <a href="../reference/metadata/metadata_data_agreement/">agreement</a> and <a href="../reference/metadata/metadata_data_steward/">steward context</a>.</p>
<p>Writes to <a href="../reference/metadata/">agreement metadata tables</a>, including <a href="../reference/metadata/metadata_data_agreement/">agreement records</a>, <a href="../reference/metadata/metadata_data_steward/">steward context</a>, <a href="../reference/metadata/metadata_data_agreement/">approved usage</a>, and supporting <a href="../reference/metadata/metadata_data_agreement_evidence/">agreement files</a>.</p>
</div>

<div class="metadata-flow-card">
<strong><a href="../notebook-templates-implementation-guide/pipeline-execution/"><code>02_pipeline</code></a></strong>
<p>Runs governed source-to-target pipeline execution.</p>
<p>Reads <a href="../reference/metadata/metadata_data_agreement/">agreement</a> and configuration metadata.</p>
<p>Writes <a href="../reference/metadata/metadata_pipeline_runs/">pipeline run details</a>, <a href="../reference/metadata/metadata_data_catalogue/">catalogue profiles</a>, <a href="../reference/metadata/metadata_guardrail_results/">DQ results</a>, <a href="../reference/metadata/metadata_guardrail_results/">drift results</a>, <a href="../reference/metadata/metadata_data_lineage_table/">lineage</a>, <a href="../reference/metadata/metadata_data_catalogue/">output table records</a>, and <a href="../reference/metadata/metadata_pipeline_runs/">run status</a>.</p>
</div>

<div class="metadata-flow-card">
<strong><a href="../notebook-templates-implementation-guide/governance-review/"><code>03_governance</code></a></strong>
<p>Reviews and approves governed outputs.</p>
<p>Reads <a href="../reference/metadata/metadata_data_agreement/">agreement</a>, <a href="../reference/metadata/metadata_pipeline_runs/">pipeline run details</a>, <a href="../reference/metadata/metadata_data_catalogue/">catalogue profiles</a>, <a href="../reference/metadata/metadata_guardrail_results/">DQ results</a>, <a href="../reference/metadata/metadata_guardrail_results/">drift results</a>, <a href="../reference/metadata/metadata_data_lineage_table/">lineage</a>, and <a href="../reference/metadata/metadata_pipeline_runs/">run status</a>.</p>
<p>Writes <a href="../reference/metadata/metadata_guardrail_rules/">review decisions</a>, <a href="../reference/metadata/metadata_guardrail_rules/">approval state</a>, <a href="../reference/metadata/metadata_guardrail_rules/">rule outcomes</a>, <a href="../reference/metadata/metadata_enrichment_rules/">enrichment decisions</a>, <a href="../reference/metadata/metadata_enrichment_rules/">lifecycle decisions</a>, and production handover state.</p>
</div>

</div>

Dashboard and reference pages consume metadata to show current state, history, and implementation details; they are not writers in the notebook workflow.
