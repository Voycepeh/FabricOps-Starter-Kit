# How FabricOps Works

FabricOps combines standardized notebook templates, a Python package of helper and orchestrator functions, and shared metadata tables into one Microsoft Fabric workflow.

The notebooks make the workflow visible, the package abstracts repeated Fabric operations, and the metadata tables carry context and evidence between governance, data engineering, and AI and BI analytics users. This page explains how those pieces interact. When you are ready to run them, continue to the [Guided Demo](guided-demo.md).

## Workspace operating model

![FabricOps operating model overview](assets/fabricops-operating-model-overview.png)

*Figure: FabricOps operates as a governed notebook workflow across workspace configuration, Lakehouse and Warehouse targets, shared metadata, runtime guardrails, and governance review.*

Microsoft Fabric is the execution runtime, while GitHub remains the source of truth for the reusable package, templates, documentation, and release assets.

| Component | Responsibility | FabricOps handoff |
| --- | --- | --- |
| Fabric workspace and Environment | Host notebooks and provide the installed FabricOps package and runtime identity. | `00_env_config` validates the runtime and makes shared configuration available to later notebooks. |
| Source targets | Hold Lakehouse tables, Warehouse tables, and files used as pipeline inputs. | FabricOps IO helpers resolve configured targets instead of relying on hardcoded paths or the attached default item. |
| Metadata target | Holds the shared `METADATA_*` tables in the configured metadata Lakehouse. | Agreement, profiling, catalogue, lineage, enrichment, guardrail intent, and guardrail results use the same configured route. |
| Output targets | Hold governed Lakehouse or Warehouse outputs. | `02_pipeline` writes outputs only after the relevant processing and guardrail decisions allow continuation. |
| Governance review | Reviews observed evidence and records approved business context and guardrail intent. | `03_governance` appends review decisions while preserving historical evidence. |
| Reference and reporting | Make the workflow, current state, and implementation details easier to inspect. | Documentation and dashboards read source-generated reference data and metadata; they do not replace the source of truth. |

This model is notebook-first so the workflow remains easy to inspect and hand over. A new team member can open the active notebook, understand what it owns, and follow its metadata links without reconstructing hidden state from previous notebook sessions.

## Standard notebook workflow

![FabricOps role workflow](assets/fabricops-role-workflow.png)

The main notebooks form a repeatable cycle rather than separate utilities:

1. A workspace maintainer or project owner runs `00_env_config` to configure Fabric items, runtime behavior, shared settings, and metadata routing.
2. A data steward, governance user, project owner, or supporting engineer runs `01_agreement` to capture steward and approved agreement context.
3. An engineer, analytics engineer, or data scientist runs `02_pipeline` to read, transform, profile, validate, and write data under the selected agreement.
4. A governance user, steward, reviewer, or supporting engineer runs `03_governance` to enrich observed metadata and review guardrail intent.
5. The pipeline is run again when approved guardrails should be enforced against fresh data.
6. Any role can use `99_explore` for optional read-only discovery and troubleshooting.

The [Notebook Templates guide](notebook-templates-implementation-guide/index.md) provides the download links and a compact description of each notebook. The Guided Demo owns the detailed run instructions.

## Metadata is the handoff layer

FabricOps notebooks do not depend on notebook memory or informal handover notes to continue the workflow. They use shared metadata tables so later steps can read the context and evidence produced earlier.

<div class="metadata-flow-grid">

<div class="metadata-flow-card">
<strong><a href="../guided-demo/run-environment-setup/"><code>00_env_config</code></a></strong>
<p>Creates or validates the <a href="../reference/metadata/">metadata foundation</a> and configures the metadata Lakehouse route used by every later notebook.</p>
</div>

<div class="metadata-flow-card">
<strong><a href="../guided-demo/create-agreement/"><code>01_agreement</code></a></strong>
<p>Writes <a href="../reference/metadata/metadata_data_steward/"><code>METADATA_DATA_STEWARD</code></a> and <a href="../reference/metadata/metadata_data_agreement/"><code>METADATA_DATA_AGREEMENT</code></a> so later evidence has an accountable owner, purpose, recipient, and lifecycle context.</p>
</div>

<div class="metadata-flow-card">
<strong><a href="../guided-demo/run-pipeline/"><code>02_pipeline</code></a></strong>
<p>Reads agreement context and, when approved rules are active, guardrail intent. It writes observed <a href="../reference/metadata/metadata_data_catalogue/">catalogue</a>, <a href="../reference/metadata/metadata_data_profiled/">profile</a>, and <a href="../reference/metadata/metadata_data_lineage/">lineage</a> evidence, plus <a href="../reference/metadata/metadata_guardrail_results/">guardrail results</a> when rules are evaluated.</p>
</div>

<div class="metadata-flow-card">
<strong><a href="../guided-demo/review-guardrails/"><code>03_governance</code></a></strong>
<p>Reads observed evidence and appends approved business context to <a href="../reference/metadata/metadata_enrichment/"><code>METADATA_ENRICHMENT</code></a> and executable rule intent to <a href="../reference/metadata/metadata_guardrail/"><code>METADATA_GUARDRAIL</code></a>.</p>
</div>

<div class="metadata-flow-card">
<strong><a href="../guided-demo/explore-metadata-outputs/"><code>99_explore</code> and reference pages</a></strong>
<p>Read the shared evidence for discovery, support, and handover. They do not create required production workflow state.</p>
</div>

</div>

The [Metadata Table Reference](reference/metadata.md) documents all ten implemented tables, including contract and access tables reserved for their implemented lifecycle evidence. It remains the source of truth for table purpose and schema details.

## What FabricOps abstracts

FabricOps keeps project-specific transformation logic visible while standardizing the repeated support work around it:

- environment and Fabric item configuration;
- Lakehouse and Warehouse reads and writes;
- data profiling and catalogue registration;
- lineage participation evidence;
- metadata-driven guardrail review and enforcement;
- audit context and shared metadata routing; and
- reference documentation for functions, metadata tables, and DQ rules.

This lets teams adopt one workflow without requiring every user to rebuild the same configuration, metadata, governance, and handover processes for every notebook project.

## Next: run the workflow

The architecture is easiest to understand after seeing the same handoffs in Microsoft Fabric. Continue to the [FabricOps Guided Demo](guided-demo.md).

<div class="cta-center">
  <a class="md-button md-button--primary" href="../guided-demo/">
    Open the Guided Demo
  </a>
</div>
