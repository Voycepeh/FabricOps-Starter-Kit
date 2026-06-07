# Quick start

Use this page to run the FabricOps Starter Kit in Microsoft Fabric and complete the first governed notebook flow.

FabricOps is designed to stay lightweight. The kit does not ask teams to introduce a separate platform, ticketing workflow, or governance tool before they can start. Instead, it uses Fabric workspaces, lakehouses, notebooks, and shared metadata tables to make the delivery process traceable from the first data agreement through production review.

By the end of this quick start, you should have:

1. A Governance workspace that stores shared metadata.
2. An Engineering workspace that runs the first notebook flow.
3. A configured `00_env_config` notebook.
4. A working role-based sequence for the required delivery path: Agreement → Pipeline → Review. Optional Explore support remains available for discovery, profiling, troubleshooting, investigation, and ad hoc analysis.

For the full operating model, read [How FabricOps Works](how-fabricops-works/index.md).

## First run setup

Start with one Governance workspace and one Engineering workspace. **Alternatively,** you can even simply put them a singular workspace for simplicity sake

| Workspace                  | Required items                                               | Purpose                                                                                                                               |
| -------------------------- | ------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------- |
| Governance workspace       | `metadata_lakehouse`                                         | Stores shared metadata, notebook registration, agreements, profiles, reviewed DQ expectations, classifications, and lineage evidence. |
| Engineering workspace  | `source_lakehouse`, `unified_lakehouse`, `product_warehouse` | Used by data analysts, engineers, and pipeline contributors to build and test the governed flow.                                      |

## Once you have the workspace and lakehouses & warehouses set up follow these 5 steps


| Step | Do this | Expected result | Read more |
| ---- | ------- | --------------- |---------- |
| 1    | Install the FabricOps wheel in a Microsoft Fabric Environment.              | Fabric notebooks attached to that Environment can import `fabricops_kit`.                                 | [Fabric Wheel Install](install.md)      |

![IMG](assets/fabric-example-install-custom-whl.png)

| Step | Do this | Expected result | Read more |
| ---- | ------- | --------------- |---------- |
| 2    | Copy the notebook templates from the GitHub `templates` folder and upload into Fabric. | You have editable copies of `00_env_config`, `01_agreement`, `02_pipeline`, `03_review`, and optional `99_explore`.                     | [Notebook Templates](how-fabricops-works/notebook-templates.md)          |

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
| 5    | Run the required notebooks in sequence. | The Agreement → Pipeline → Review delivery flow is created and can be reviewed before production promotion. | [Notebook Templates](how-fabricops-works/notebook-templates.md)    |

On first and later pipeline runs, approved DQ warning rules do not block publication and write the full dataset; approved DQ error rules block before the target write.

The notebooks are intentionally separated by role. Each template produces metadata or outputs that the next role can reuse.

![Role-based notebook workflow from environment configuration through governed review](assets/fabricops-role-workflow.png){ .full-width }

Role-based notebook workflow for configuration, agreement capture, pipeline build, review, optional exploration support, and guardrails.

Run the required delivery templates in this order:

| Order | Notebook or action | Main responsibility |
| ----: | ------------------ | ------------------- |
| 1 | `00_env_config` | Defines environment-specific paths, lakehouses, warehouse targets, and governance metadata routing. |
| 2 | `01_agreement` | Defines what should be built, who owns it, what rules apply, and what readiness means. |
| 3 | `02_pipeline` | Builds repeatable transformations, validates source and target data, enforces active approved DQ rules, publishes outputs, records runtime audit columns, captures lineage, and writes profiles. |
| 4 | `03_review` | Checks evidence, metadata, ownership, rules, and readiness; approved DQ expectations are stored for the next pipeline run. |
| 5 | Rerun `02_pipeline` when needed | Loads active approved DQ rules from `METADATA_DQ_RULES` and enforces them before the target write. |
| 6 | Operational support | Use the production notebook export plus FabricOps metadata evidence for support and review. |

Optional support:

| Notebook | Use it for |
| -------- | ---------- |
| `99_explore` | Discovery, profiling, troubleshooting, investigation, and ad hoc analysis. It is not required before Agreement, Pipeline, or Review. |

## What success looks like

After the first full run, the flow should replace tribal knowledge with metadata-backed answers.

| Question                                          | Where the answer should come from                                                           |
| ------------------------------------------------- | ------------------------------------------------------------------------------------------- |
| Who owns the data and what is it used for?        | Agreement and steward metadata captured in `01_agreement`.                                         |
| What did the source look like during optional exploration? | Optional profiling, schema, and exploration notes captured in `99_explore`, when used.                            |
| What transformations created the output?          | Pipeline registration, lineage, and output metadata captured in `02_pipeline`.                    |
| Which expectations and classifications were reviewed? | Governance metadata from `03_review`.                                                     |
| Which production guardrails ran?                  | Evidence from `02_pipeline` schema checks, data-change monitoring, notebook-defined checks, output writes, lineage, and run summaries. |
| What should support use after production? | Stored production notebook export, metadata evidence, run summaries, and support notes. |

The goal is that support and review should no longer depend on memory or side conversations. The metadata should explain who owns the data, how it was transformed, which controls were approved, what evidence exists from the production run, and which optional exploration notes support troubleshooting when `99_explore` was used.


## Next reads

| Page                                          | Why read it                                                                                               |
| --------------------------------------------- | --------------------------------------------------------------------------------------------------------- |
| [How FabricOps Works](how-fabricops-works/index.md) | Start with the v1.0.0 metadata-backed notebook workflow, production guardrails, governance review, and support story. |
| [Production Guardrails Workflow](how-fabricops-works/schema-and-data-drift.md) | Learn how `02_pipeline` owns production guardrails and run evidence. |
| [Governance Review Workflow](how-fabricops-works/governance-review.md) | Learn how `03_review` reviews profile evidence and commits governance metadata. |
| [Function Reference](reference/index.md)   | Review the reusable helper APIs used by the notebook templates.                                           |
