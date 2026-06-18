# How FabricOps Works

FabricOps Starter Kit is a practical notebook handshake for governed, quality-checked Microsoft Fabric workflows. The notebooks pass context, evidence, and review state through shared metadata tables instead of relying on notebook memory or informal handover notes.

## The notebook handshake

| Step | What it does | What the next step receives |
| --- | --- | --- |
| [00 Environment Configuration](environment-config.md) | Defines where the workflow runs and validates workspace, Lakehouse, Warehouse, schema, and metadata routing. | A configured `CONFIG`, environment name, and metadata tables that later notebooks can use. |
| [01 Agreement Setup](agreement-setup.md) | Defines what is allowed, who owns it, and which agreement evidence applies. | Agreement and steward metadata that pipeline notebooks can select. |
| [02 Pipeline Execution](pipeline-execution.md) | Reads source data, prepares table configs, executes guardrails, writes outputs, and records run evidence. | Runtime evidence in catalogue, guardrail results, lineage, and pipeline run metadata. |
| [03 Governance Review](governance-review.md) | Reviews governed rules and enrichment records, and manages formal rule lifecycle. | Approved, rejected, superseded, active, or pending rule and enrichment state. |
| [Metadata Tables](metadata-tables.md) | Act as the shared memory for agreements, catalogue evidence, rules, results, lineage, runs, and review state. | A durable view of what was configured, checked, written, and reviewed. |
| [Metadata Dashboard](metadata-dashboard.md) | Exposes the current governed state for users who need visibility without reading every metadata row. | Operational insight into agreements, rules, results, runs, lineage, and review status. |

## What FabricOps is trying to do

FabricOps keeps notebook delivery explainable for teams that need junior-friendly handover and governance evidence:

- **Make setup explicit.** `00_env_config` owns the runtime and metadata target instead of assuming an attached/default Lakehouse.
- **Make intent selectable.** `01_agreement` records the steward and agreement context that `02_pipeline` can select later.
- **Make checks executable.** `02_pipeline` applies active guardrail rules and writes guardrail result evidence.
- **Make review append-only.** `03_governance` manages rule and enrichment lifecycle without overwriting history.
- **Make evidence reusable.** Metadata tables connect notebook actions to the dashboard and reference docs.

Use the pages in this section as the user guide for running and adapting the starter notebooks. Use the generated [Function Reference](../reference/) only when you need callable-level details.
