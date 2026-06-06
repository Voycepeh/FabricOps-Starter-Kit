# How FabricOps Works

FabricOps Starter Kit is a lightweight Microsoft Fabric notebook starter kit for governed, quality-checked, AI-ready notebooks.

Start here before reading the workflow detail pages. The v1.0.0 story is intentionally simple: metadata tables and notebook templates create a traceable operating trail from agreement, to production, to governance review, to handover.

FabricOps is not a full governance platform or a standalone data quality product. Data quality checks are one part of a broader Fabric notebook workflow.

## v1.0.0 workflow

| Workflow | What it means in v1.0.0 |
| --- | --- |
| Metadata enabled workflow | `01_da` captures agreement and steward context, the notebook registry records notebook participation, `03_pc` writes profiling, lineage, and run evidence, and `04_gov` enriches that evidence with reviewed governance metadata. |
| Production guardrails workflow | `03_pc` is the production control boundary. It validates schema, monitors data changes, applies notebook-defined checks, writes outputs, records lineage, and creates run evidence. |
| Governance review workflow | `04_gov` reviews profile evidence and commits approved column context, DQ expectations, and classifications. It does not enforce production rules. |

Separate data contracts are not part of the v1.0.0 operating model.

## Notebook responsibilities

| Notebook | v1.0.0 responsibility |
| --- | --- |
| `00_env_config` | Prepares configuration and metadata tables. |
| `01_da` | Captures data agreement, steward, and evidence metadata. |
| `02_ex` | Supports exploration or example topic setup. |
| `03_pc` | Runs production with notebook-scoped guardrails. |
| `04_gov` | Reviews and commits governance metadata. |

## Operating trail

The metadata lakehouse is the shared evidence layer:

1. `01_da` records agreement, steward, and evidence context.
2. The notebook registry records which notebooks participate in an agreement or workflow.
3. `03_pc` writes profile evidence, lineage, output evidence, and run summaries as part of production execution.
4. `04_gov` commits reviewed column context, DQ expectations, and classifications.
5. Handover is supported by collected evidence instead of memory or manually reconstructed notes.

## What to read next

| Page | Use it for |
| --- | --- |
| [Workspace Operating Model](workspace-operating-model.md) | Understand workspace separation and production promotion. |
| [Notebook Templates](notebook-templates.md) | Understand what each notebook template owns. |
| [Metadata Tables](metadata-tables.md) | Understand what evidence is stored and where. |
| [Production Guardrails Workflow](../schema-and-data-drift.md) | Understand `03_pc` schema and data-change guardrails. |
| [Governance Review Workflow](../data-quality-rules-system.md) | Understand `04_gov` review metadata and optional AI assistance. |
| [Metadata Dashboard](metadata-dashboard.md) | Understand the planned post-v1.0.0 visibility layer over collected metadata. |

## Planned after v1.0.0

| Planned enhancement | Notes |
| --- | --- |
| Metadata dashboard visibility layer | A complete dashboard experience is planned after v1.0.0. |
| Richer governance dashboard views | Additional views over agreements, profiles, lineage, classifications, and DQ expectations. |
| Optional metadata-driven DQ rule execution | Future opt-in execution of reviewed DQ metadata. |
| Rule promotion workflow | Future path from reviewed expectations to implemented guardrails. |
| Richer AI-assisted review | More complete AI support while keeping humans accountable for approval. |
| More complete operational monitoring | Broader run health and support visibility. |
