# Quick start

Use this page to run the FabricOps Starter Kit in Microsoft Fabric and smoke test the v1.0.0 notebook flow.

FabricOps is intentionally lightweight. It uses Fabric workspaces, lakehouses, notebooks, a Fabric Environment, and shared metadata tables so teams can trace delivery from data agreement to production handover without introducing a separate platform.

By the end of this quick start, you should have:

1. a Governance workspace or shared metadata lakehouse;
2. an Engineering workspace that runs the notebook templates;
3. the FabricOps wheel installed in a Fabric Environment;
4. a configured `00_env_config` notebook;
5. a successful smoke test through `01_da`, `02_ex`, `03_pc`, `04_gov`, and a rerun of `03_pc`;
6. deliberate schema and data-change failure tests that prove `03_pc` guardrails can stop unsafe runs.

For the full operating model, read [How FabricOps Works](how-fabricops-works/index.md).

## v1.0.0 operating boundary

In v1.0.0, each `03_pc` notebook is the production control boundary. Separate data contracts are not required. The production guardrails are the schema checks, data-change checks, notebook-defined DQ checks, output writes, lineage records, profiling evidence, and run summaries implemented in the relevant `03_pc` notebook.

`04_gov` reviews and commits governance metadata for column context, DQ expectations, and classifications. It does not enforce production rules. Governance DQ rules stored in metadata are advisory expectations unless a team manually implements them as guardrails inside the relevant `03_pc` notebook. AI suggestions are optional and advisory only.

## First-run setup

Start with one Governance workspace and one Engineering workspace. For a small smoke test, you can use a single workspace if the metadata, source, unified, and product targets are still clearly configured.

| Workspace | Required items | Purpose |
| --- | --- | --- |
| Governance workspace | `metadata_lakehouse` | Stores shared metadata, notebook registrations, agreements, profiles, reviewed governance metadata, lineage, and handover evidence. |
| Engineering workspace | `source_lakehouse`, `unified_lakehouse`, `product_warehouse` | Runs exploration, production-control notebooks, and starter output targets. |

## Fabric smoke test sequence

Run the notebooks in Fabric rather than only testing locally. The smoke test should prove both the happy path and failure behavior.

| Order | Action | Expected result |
| ---: | --- | --- |
| 1 | Install the FabricOps wheel in a Fabric Environment and attach that Environment to the copied notebooks. | Each notebook can import `fabricops_kit`. |
| 2 | Copy the notebook templates from `templates/notebooks` into Fabric. | You have editable `00_env_config`, `01_da`, `02_ex`, `03_pc`, and `04_gov` notebooks. |
| 3 | Run `00_env_config`. | Metadata targets are configured and active metadata tables are created or validated. |
| 4 | Run `01_da`. | Data agreement, steward, and evidence metadata is captured. |
| 5 | Run `02_ex`. | Example source/topic setup is profiled and catalogue evidence is written. |
| 6 | Run `03_pc`. | The production-control notebook validates schema/data changes, writes outputs, records profiles, writes lineage, and produces run evidence. |
| 7 | Run `04_gov`. | A human reviews and commits column context, DQ expectations, and classification metadata. |
| 8 | Rerun `03_pc`. | The production notebook continues to use its implemented guardrails and can include any governance expectations that you manually implemented in that notebook. |
| 9 | Deliberately test schema failure behavior. | A blocking schema change stops `03_pc` when the selected preset requires it. |
| 10 | Deliberately test data-change failure behavior. | A blocking data-change result stops `03_pc` when the selected preset and baseline require it. |

![Fabric custom wheel installation example](assets/fabric-example-install-custom-whl.png)

![Fabric workspace setup example](assets/fabric-example-workspace-setup.png)

![Fabric notebook Environment assignment example](assets/fabric-example-set-notebook-environment.png)

![Fabric `00_env_config` path setup example](assets/fabric-example-00_config_paths.png)

## Notebook responsibilities

The notebooks are intentionally separated by role.

![Role-based notebook workflow from environment configuration through AI-assisted handover](assets/fabricops-role-workflow.png){ .full-width }

| Notebook | Responsibility |
| --- | --- |
| `00_env_config` | Prepares workspace/lakehouse/warehouse paths and creates or validates metadata tables. |
| `01_da` | Captures agreement, steward, and supporting evidence metadata. |
| `02_ex` | Demonstrates example source/topic setup, exploration, profiling, and catalogue evidence. |
| `03_pc` | Acts as the production guardrail notebook for schema checks, data-change checks, notebook-defined DQ checks, output writes, lineage, profiling evidence, and run summaries. |
| `04_gov` | Reviews and commits governance metadata for column context, DQ expectations, and classifications; it does not enforce production rules. |

## What to verify before handover

- The Fabric Environment uses the expected FabricOps wheel version.
- `00_env_config` routes metadata reads and writes to the configured metadata target.
- `01_da` creates or updates the expected agreement metadata.
- `02_ex` and `03_pc` write profile/catalogue evidence to metadata.
- `03_pc` writes output data only after required guardrails pass.
- `03_pc` stops on deliberately introduced blocking schema and data-change failures.
- `04_gov` commits reviewed governance metadata and keeps AI suggestions advisory.
- The rerun `03_pc` produces clear run evidence and lineage for handover.

## Next steps

- Read [Notebook Templates](how-fabricops-works/notebook-templates.md) for template ownership details.
- Read [Schema and Data-Change Guardrails](schema-and-data-drift.md) before changing `03_pc` presets.
- Read [Table-Scoped Governance](how-fabricops-works/table-scoped-governance.md) before running `04_gov` with reviewers.
