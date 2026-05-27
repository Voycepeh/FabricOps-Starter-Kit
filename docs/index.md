# FabricOps Starter Kit

Governed, quality-checked, AI-ready notebooks in Microsoft Fabric.

[Quick Start](quick-start.md){ .md-button .md-button--primary }
[Workflow](lifecycle-operating-model.md){ .md-button }
[Functions](reference/index.md){ .md-button }

## How FabricOps fits into Fabric

FabricOps Starter Kit is a lightweight framework for running notebook-led delivery inside Microsoft Fabric while keeping governance and handover explicit.

![FabricOps in Microsoft Fabric architecture](assets/data-platform-architecture.png){ .full-width }

## How FabricOps works

The delivery workflow moves from agreement to exploration, then into approved metadata, pipeline contract assembly, and handover.

`agreement → exploration → approved metadata → pipeline contract → handover`

![FabricOps lifecycle workflow](assets/mvp-flow.png){ .full-width }

## Data contracts are assembled from evidence

Data contracts are generated from approved metadata and quality evidence so implementation and governance stay aligned.

![Data contract assembly from metadata evidence](assets/data-contract.png){ .full-width }

## Notebook operating model

Use the canonical notebook structure to keep package loading, analysis, implementation, and governance checkpoints consistent.

`00_env_config → 01_da → 02_ex → 03_pc → 04_gov`

![Notebook and workspace structure](assets/notebook-structure.png){ .full-width }

## Choose where to go next

| Need | Go to |
| --- | --- |
| Start the framework in a new workspace | [Quick Start](quick-start.md) |
| Understand the end-to-end delivery lifecycle | [Workflow](lifecycle-operating-model.md) |
| Build and publish the package | [Create Wheel](setup/create-wheel.md) |
| Run the kit in Fabric | [Run in Fabric](setup/run-in-fabric.md) |
| Reuse notebook templates and structure | [Notebook Structure](notebook-structure.md) |
| Explore callable APIs | [Function Reference](reference/index.md) |

!!! note "Compatibility"
    The package import remains `fabricops_kit`.
