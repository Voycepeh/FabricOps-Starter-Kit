# FabricOps Guided Demo

Use this walkthrough to set up the FabricOps Starter Kit in Microsoft Fabric, run the standardized notebook workflow, and inspect the metadata evidence produced at each stage.

The Guided Demo is the canonical execution guide: it explains what to open, what to configure, what to run, and what you should see afterward. Use the [Notebook Templates guide](notebook-templates-implementation-guide/index.md) for notebook downloads and role summaries. Use the [Function Reference](reference/index.md), [Metadata Table Reference](reference/metadata.md), and [DQ Rule Reference](reference/dq-rules/index.md) when you need implementation detail.

## Before you begin

Read [How FabricOps Works](how-fabricops-works.md) first if you have not yet seen how the package, notebook templates, roles, and metadata tables work together.

For the first run, keep the public-safe demo values supplied by the templates and walkthrough. This makes the expected inputs, outputs, and metadata evidence easier to compare.

## Part 1: workspace maintainer setup

These steps prepare the shared Fabric workspace and runtime foundation. A workspace maintainer or project owner normally completes them before workflow users begin.

| Order | Step | What you do | What you should have afterward |
| --- | --- | --- | --- |
| 1 | [Setup Fabric Artifacts](guided-demo/setup-fabric-artifacts.md) | Create or select the workspace, data items, Fabric Environment, installed FabricOps release, and copied notebooks. | A workspace where the notebooks can import `fabricops_kit` and reach the intended Fabric items. |
| 2 | [Run Environment Setup](guided-demo/run-environment-setup.md) | Configure and run `00_env_config`. | Shared `CONFIG` and `ENV` values, validated Fabric routes, and the implemented metadata tables in the configured metadata Lakehouse. |

## Part 2: run the FabricOps workflow

These steps show how engineering, governance, and analytics users work through the same metadata-backed flow.

| Order | Step | What you do | What you should have afterward |
| --- | --- | --- | --- |
| 3 | [Run IO and Profiling Demo](guided-demo/run-io-and-profiling-demo.md) | Use `99_explore` to confirm configured Lakehouse and Warehouse IO and basic profiling behavior. | A successful smoke test showing that the same helper pattern works across configured Fabric targets. |
| 4 | [Register Agreement](guided-demo/create-agreement.md) | Run `01_agreement` to capture steward, purpose, recipient, and approved usage context. | Agreement metadata that later profiling, lineage, and guardrail evidence can be tied to. |
| 5 | [Run a Data Pipeline](guided-demo/run-pipeline.md) | Run `02_pipeline` in the standard read, profile, transform, profile, and write flow. | Governed outputs plus catalogue, profile, and lineage evidence for the source and target. |
| 6 | [Review Governance](guided-demo/review-guardrails.md) | Run `03_governance` to enrich observed metadata and review executable guardrail intent. | Approved enrichment and active guardrail records ready for later enforcement. |
| 7 | [Run a Data Pipeline with Guardrails](guided-demo/run-pipeline-with-guardrails.md) | Rerun the relevant `02_pipeline` flow with active approved rules. | Fresh guardrail results and a continuation decision before critical publication steps. |
| 8 | [Explore Metadata](guided-demo/explore-metadata-outputs.md) | Use `99_explore` and the reference pages to trace the evidence created across the workflow. | Reviewable answers about ownership, observed data, lineage, enrichment, approved rules, and runtime outcomes. |

## What the sequence is teaching

The first pipeline run records what the data and pipeline look like. Governance then reviews that observed evidence and records approved enrichment and guardrail intent. The later guarded run evaluates those active rules against fresh data.

This order keeps three responsibilities separate:

| Responsibility | Canonical metadata |
| --- | --- |
| Observed table, column, profile, and lineage evidence | `METADATA_DATA_CATALOGUE`, `METADATA_DATA_PROFILED`, and `METADATA_DATA_LINEAGE` |
| Human-reviewed business context and executable rule intent | `METADATA_ENRICHMENT` and `METADATA_GUARDRAIL` |
| Runtime outcomes from evaluated rules | `METADATA_GUARDRAIL_RESULTS` |

## Success criteria

After the walkthrough, you should be able to answer these questions from shared metadata rather than notebook memory.

| Question | Metadata-backed answer |
| --- | --- |
| Who owns the data, who receives it, and what is it used for? | Steward and agreement context from `01_agreement`. |
| Which tables and columns were observed? | Physical identities and schema fingerprints in `METADATA_DATA_CATALOGUE`. |
| What did the values in each profiled column look like? | Statistical and frequency evidence in `METADATA_DATA_PROFILED`. |
| Which source and target tables participated in the notebook activity? | Runtime participation evidence in `METADATA_DATA_LINEAGE`. |
| What business context did governance add? | Append-only enrichment records in `METADATA_ENRICHMENT`. |
| Which expectations were reviewed and activated? | Executable rule intent in `METADATA_GUARDRAIL`. |
| Which checks ran and whether execution could continue? | Runtime outcomes in `METADATA_GUARDRAIL_RESULTS`. |

## Where to go next

- Use [Notebook Templates](notebook-templates-implementation-guide/index.md) to download the notebooks and adapt the standard sequence.
- Use [Metadata Table Reference](reference/metadata.md) to inspect the implemented evidence model and table schemas.
- Use [DQ Rule Reference](reference/dq-rules/index.md) to select and configure supported data quality rules.
- Use [Function Reference](reference/index.md) when you need a callable signature, example, return meaning, error guidance, lifecycle status, or call flow.
