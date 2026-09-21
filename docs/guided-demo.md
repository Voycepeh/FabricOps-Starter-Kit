# FabricOps Guided Demo

**Use the Guided Demo to run the FabricOps operating flow in Microsoft Fabric from setup through governed Production consumption.**

`00A`, `00B`, and `00C` prepare the Fabric environment, configure the notebooks, exercise the FabricOps I/O helpers, and seed the managed demo tables. The seven numbered steps then walk through the same lifecycle described in [How FabricOps Works](how-fabricops-works.md).

!!! tip "New to Microsoft Fabric?"

    Start with [Microsoft Learn: Fabric fundamentals](https://learn.microsoft.com/en-us/fabric/fundamentals/) for the platform concepts used throughout the demo. When you reach the engineering parts, continue with [Microsoft Learn: Fabric Data Engineering](https://learn.microsoft.com/en-us/fabric/data-engineering/) for Lakehouse, notebooks, Spark, and Data Engineering workflows.

    **Useful visual reference:** [Microsoft Fabric Visual Notes](https://www.slideshare.net/slideshow/microsoft-fabric-complete-handwritten-notes-pdf/289496813) — a visual community reference covering Fabric architecture, PySpark, pipelines, incremental loading, data quality, CI/CD, monitoring, and related concepts.

    FabricOps documentation remains the source of truth for how this starter kit is designed and used.

## Foundation setup

| Setup | What you do | Why it matters |
| --- | --- | --- |
| [0A. Prepare Fabric artifacts](guided-demo/00A-setup-fabric-artifacts.md) | Create the workspaces, stores, and Fabric Environments, then install the FabricOps wheel. | The physical Fabric foundation exists. |
| [0B. Load and configure the Guided Demo assets](guided-demo/00B-run-environment-setup.md) | Import the core notebooks, attach their Fabric Environments, configure `00_env_config`, create the metadata tables, and upload the packaged demo files to Bronze `Files/Demo`. | Every notebook can resolve the configured Fabric stores and the raw demo assets are in place. |
| [0C. Prepare the demo data with FabricOps I/O](guided-demo/00C-prepare-demo-data.md) | Run `00C_demo_setup` in Engineering Development to demonstrate file, Lakehouse, and Warehouse I/O and seed the managed source tables. | `02_pipeline` starts from real managed tables prepared through the public FabricOps I/O helpers. |

## The seven-step FabricOps workflow

![FabricOps role workflow](assets/fabricops-role-workflow.png)

| Step | Notebook | What you do |
| --- | --- | --- |
| [1. Establish Governance context](guided-demo/01-create-agreement.md) | `01_governance` | Create Data Stewards and a Data Agreement. |
| [2. Build and run the ETL](guided-demo/02-run-pipeline.md) | `02_pipeline` | Run the full-read Read → Transform → Write pipeline and profile the real governed tables. |\n| [2A. Run an incremental pipeline](guided-demo/02A-run-incremental-pipeline.md) | `03_incremental_pipeline` | Reuse the same pipeline pattern with target-aware incremental reads, safe publication, and explicit batch-versus-complete profiling. |
| [3. Author and freeze the Data Contract](guided-demo/03-enrich-guardrails.md) | `01_governance` | Select the real `table_id`, author Enrichment, Guardrails, and Processing, then freeze the contract version. |
| [4. Select and validate the Data Contract](guided-demo/04-run-pipeline-with-guardrails.md) | `02_pipeline` | Select the frozen contract and rerun the pipeline with its checks enforced. |
| [5. Link the Data Agreement and activate](guided-demo/05-create-data-contract.md) | `01_governance` | Link the tested contract version to the Data Agreement version and activate it for Production. |
| [6. Promote and run Production](guided-demo/06-promote-to-production.md) | `02_pipeline` | Promote the validated pipeline and run it with Production configuration and the active contract. |
| [7. Consume approved Production data](guided-demo/99-explore.md) | `99_explore` | Read approved Production outputs from the consumer workspace. |
