# Quick start

Use this page to run the FabricOps Starter Kit in Microsoft Fabric and complete the first governed notebook flow.

FabricOps is designed to stay lightweight. The kit does not ask teams to introduce a separate platform, ticketing workflow, or governance tool before they can start. Instead, it uses Fabric workspaces, lakehouses, notebooks, and shared metadata tables to make the delivery process traceable from the first data agreement to production handover.

By the end of this quick start, you should have:

1. A Governance workspace that stores shared metadata.
2. An Engineering workspace that runs the first notebook flow.
3. A configured `00_env_config` notebook.
4. A working role-based sequence from agreement to exploration, pipeline build, governance enrichment, and rule enforcement.

For the full operating model, read [How FabricOps Works](how-fabricops-works/index.md).

## First run setup

Start with one Governance workspace and one Engineering workspace. **Alternatively,** you can even simply put them a singular workspace for simplicity sake

| Workspace                  | Required items                                               | Purpose                                                                                                                               |
| -------------------------- | ------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------- |
| Governance workspace       | `metadata_lakehouse`                                         | Stores shared metadata, notebook registration, agreements, profiles, reviewed DQ expectations, classifications, lineage, and handover evidence. |
| Engineering workspace  | `source_lakehouse`, `unified_lakehouse`, `product_warehouse` | Used by data analysts, engineers, and pipeline contributors to build and test the governed flow.                                      |

## Once you have the workspace and lakehouses & warehouses set up follow these 5 steps


| Step | Do this | Expected result | Read more |
| ---- | ------- | --------------- |---------- |
| 1    | Install the FabricOps wheel in a Microsoft Fabric Environment.              | Fabric notebooks attached to that Environment can import `fabricops_kit`.                                 | [Fabric Wheel Install](install.md)      |

![IMG](assets/fabric-example-install-custom-whl.png)

| Step | Do this | Expected result | Read more |
| ---- | ------- | --------------- |---------- |
| 2    | Copy the notebook templates from the GitHub `templates` folder and upload into Fabric. | You have editable copies of `00_env_config`, `01_da`, `02_ex`, `03_pc`, and `04_gov`.                     | [Notebook Templates](how-fabricops-works/notebook-templates.md)          |

![IMG](assets/fabric-example-workspace-setup.png)

| Step | Do this | Expected result | Read more |
| ---- | ------- | --------------- |---------- |
| 3    | Attach the same Fabric Environment to each copied notebook.                 | Each notebook uses the installed helper wheel and compatible runtime configuration.                       | [Fabric Wheel Install](install.md)      |

![IMG](assets/fabric-example-set-notebook-environment.png)

| Step | Do this | Expected result | Read more |
| ---- | ------- | --------------- |---------- |
| 4    | Configure `00_env_config` and update the path via the lakehouse/warehouse urls   | Workspace, lakehouse, warehouse, and governance metadata paths are available to the downstream notebooks. |[Notebook Templates](how-fabricops-works/notebook-templates.md)  |

![IMG](assets/fabric-example-00_config_paths.png)

| Step | Do this | Expected result | Read more |
| ---- | ------- | --------------- |---------- |
| 5    | Run the notebook in sequence. | The starter metadata loop is created and can be reviewed before production promotion. | [Notebook Templates](how-fabricops-works/notebook-templates.md)    |

The notebooks are intentionally separated by role. Each template produces metadata or outputs that the next role can reuse.

![Role-based notebook workflow from environment configuration through AI-assisted handover](assets/fabricops-role-workflow.png){ .full-width }

Role-based notebook workflow for configuration, agreement capture, exploration, pipeline build, governance enrichment, enforcement, and handover.

Run the templates in this order:

| Order | Notebook or action                   | Main responsibility                                                                                                                      |
| ----: | ------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------- |
|     1 | `00_env_config`                      | Defines environment-specific paths, lakehouses, warehouse targets, and governance metadata routing.                                      |
|     2 | `01_da`                              | Captures steward input, data agreement records, source intent, ownership, and expected use.                                              |
|     3 | `02_ex`                              | Profiles the source data, registers exploration evidence, and proposes schema or transformation advice.                                  |
|     4 | `03_pc`                              | Builds repeatable transformations, writes output tables, records runtime audit columns, captures lineage, and writes profiles. |
|     5 | `04_gov`                             | Reviews and commits business context, DQ expectations, sensitivity classification, and governance metadata.                              |
|     6 | Rerun `03_pc`                         | Runs the production notebook guardrails again and records updated evidence.                                                              |
|     7 | Production handover                  | Stores the production notebook export and generates handover evidence for support and review.                                            |

## What success looks like

After the first full run, the flow should replace tribal knowledge with metadata-backed answers.

| Question                                          | Where the answer should come from                                                           |
| ------------------------------------------------- | ------------------------------------------------------------------------------------------- |
| Who owns the data and what is it used for?        | Agreement and steward metadata captured in `01_da`.                                         |
| What did the source look like during exploration? | Profiling, schema, and exploration metadata captured in `02_ex`.                            |
| What transformations created the output?          | Pipeline registration, lineage, and output metadata captured in `03_pc`.                    |
| Which expectations and classifications were reviewed? | Governance metadata from `04_gov`.                                                     |
| Which production guardrails ran?                  | Evidence from `03_pc` schema checks, data-change monitoring, notebook-defined checks, output writes, lineage, and run summaries. |
| What should be handed over to production support? | Stored production notebook export, generated handover summary, manifest, and support notes. |

The goal is that support, review, and handover should no longer depend on memory or side conversations. The metadata should explain who owns the data, how it was explored, how it was transformed, which controls were approved, and what evidence exists from the production run.


## Next reads

| Page                                          | Why read it                                                                                               |
| --------------------------------------------- | --------------------------------------------------------------------------------------------------------- |
| [How FabricOps Works](how-fabricops-works/index.md) | Start with the v1.0.0 metadata-backed notebook workflow, production guardrails, governance review, and handover story. |
| [Production Guardrails Workflow](schema-and-data-drift.md) | Learn how `03_pc` owns production guardrails and run evidence. |
| [Governance Review Workflow](data-quality-rules-system.md) | Learn how `04_gov` reviews profile evidence and commits governance metadata. |
| [Function Reference](reference/index.md)   | Review the reusable helper APIs used by the notebook templates.                                           |
