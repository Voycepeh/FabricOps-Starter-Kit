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

The Guided Demo follows this operating flow. Use the navigation on the left to move through each numbered step.

![FabricOps role workflow](assets/fabricops-role-workflow.png)

For the rationale behind the workflow, Data Contracts, Guardrails, metadata, and the Engineering design, see [How FabricOps Works](how-fabricops-works.md).

## Start

[Begin with 0A: Prepare Fabric artifacts](guided-demo/00A-setup-fabric-artifacts.md)
