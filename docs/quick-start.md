# Quick start

Use this page to run the FabricOps Starter Kit in Microsoft Fabric and complete the first governed notebook flow.

FabricOps is designed to stay lightweight. The kit does not ask teams to introduce a separate platform, ticketing workflow, or governance tool before they can start. Instead, it uses Fabric workspaces, lakehouses, notebooks, and shared metadata tables to make the delivery process traceable from the first data agreement to production handover.

By the end of this quick start, you should have:

1. A Governance workspace that stores shared metadata.
2. An Engineering Dev workspace that runs the first notebook flow.
3. A configured `00_env_config` notebook.
4. A working role-based sequence from agreement to exploration, pipeline build, governance enrichment, and rule enforcement.
5. A clear path for promoting the production-ready `03_pc` notebook later.

For the full operating model, read [How FabricOps Works](how-fabricops-works.md).

## Recommended minimum setup

Start with one Governance workspace and one Engineering Dev workspace. Add Engineering Prod only when the first pipeline is ready for controlled promotion.

| Workspace                  | Required items                                               | Purpose                                                                                                                               |
| -------------------------- | ------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------- |
| Governance workspace       | `metadata_lakehouse`                                         | Stores shared metadata, notebook registration, agreements, profiles, approved rules, classifications, lineage, and handover evidence. |
| Engineering Dev workspace  | `source_lakehouse`, `unified_lakehouse`, `product_warehouse` | Used by data analysts, engineers, and pipeline contributors to build and test the governed flow.                                      |
| Engineering Prod workspace | `source_lakehouse`, `unified_lakehouse`, `product_warehouse` | Used later for production execution of approved `03_pc` notebooks.                                                                    |

Do not start by overbuilding production. The first objective is to prove that the metadata flow works in Dev.

## First run setup

| Step | Do this                                                                     | Expected result                                                                                           | Read more                                            |
| ---- | --------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------- | ---------------------------------------------------- |
| 1    | Install the FabricOps wheel in a Microsoft Fabric Environment.              | Fabric notebooks attached to that Environment can import `fabricops_kit`.                                 | [Fabric Wheel Install](fabric-wheel-install.md)      |
| 2    | Copy the notebook templates from the GitHub `templates` folder into Fabric. | You have editable copies of `00_env_config`, `01_da`, `02_ex`, `03_pc`, and `04_gov`.                     | [Notebook Templates](notebook-templates.md)          |
| 3    | Attach the same Fabric Environment to each copied notebook.                 | Each notebook uses the installed helper wheel and compatible runtime configuration.                       | [Fabric Wheel Install](fabric-wheel-install.md)      |
| 4    | Configure and run `00_env_config` for the Dev environment.                  | Workspace, lakehouse, warehouse, and governance metadata paths are available to the downstream notebooks. |[Notebook Templates](notebook-templates.md)  |
| 5    | Run the first Dev notebook sequence.                                        | The starter metadata loop is created and can be reviewed before production promotion.                     | [Notebook Templates](notebook-templates.md)          |

## Run the role-based notebook workflow

The notebooks are intentionally separated by role. Each template produces metadata or outputs that the next role can reuse.

![Role-based notebook workflow from environment configuration through AI-assisted handover](assets/fabricops-role-workflow.png){ .full-width }

Role-based notebook workflow for configuration, agreement capture, exploration, pipeline build, governance enrichment, enforcement, and handover.

Run the templates in this order:

| Order | Notebook or action                   | Main responsibility                                                                                                                      |
| ----: | ------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------- |
|     1 | `00_env_config`                      | Defines environment-specific paths, lakehouses, warehouse targets, and governance metadata routing.                                      |
|     2 | `01_da`                              | Captures steward input, data agreement records, source intent, ownership, and expected use.                                              |
|     3 | `02_ex`                              | Profiles the source data, registers exploration evidence, and proposes schema or transformation advice.                                  |
|     4 | `03_pc`                              | Builds repeatable transformations, writes output tables, records technical columns, checks drift, captures lineage, and writes profiles. |
|     5 | `04_gov`                             | Reviews and approves business context, data quality rules, sensitivity classification, and governance metadata.                          |
|     6 | Rerun `03_pc` with approved metadata | Enforces approved rules and classifications during the pipeline run.                                                                     |
|     7 | Production handover                  | Stores the production notebook export and generates handover evidence for support and review.                                            |

## What success looks like

After the first Dev run, you should be able to answer these questions from metadata instead of tribal knowledge:

| Question                                          | Where the answer should come from                                   |
| ------------------------------------------------- | ------------------------------------------------------------------- |
| Who owns the data and what is it used for?        | Agreement and steward metadata from `01_da`.                        |
| What did the source look like during exploration? | Profiling and exploration metadata from `02_ex`.                    |
| What transformations created the output?          | Pipeline registration, lineage, and output metadata from `03_pc`.   |
| Which rules and classifications were approved?    | Governance metadata from `04_gov`.                                  |
| Were approved rules enforced in the pipeline?     | The rerun of `03_pc` using approved metadata.                       |
| What should be handed over to production support? | Stored production notebook export, generated summary, and manifest. |


## Next reads

| Page                                          | Why read it                                                                                               |
| --------------------------------------------- | --------------------------------------------------------------------------------------------------------- |
| [How FabricOps Works](how-fabricops-works.md) | Understand workspace ownership, role handoffs, shared metadata, assembled views, and production handover. |
| [Notebook Templates](notebook-templates.md)   | Understand template ownership and the full role-based notebook sequence.                                  |
| [Data Quality Rules](data-quality-rules.md)   | Learn how approved rules are enforced in `03_pc` notebooks.                                               |
| [Function Reference](function-reference.md)   | Review the reusable helper APIs used by the notebook templates.                                           |
