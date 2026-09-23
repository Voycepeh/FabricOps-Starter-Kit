# Notebook Templates

FabricOps provides five editable Microsoft Fabric notebook templates. Open a template to see its workflow, configuration, and usage directly in the notebook.

[Open all notebook templates on GitHub](https://github.com/Voycepeh/FabricOps-Starter-Kit/tree/main/templates/notebooks){ .md-button .md-button--primary }

<div class="template-list" markdown="1">

<div class="template-card" markdown="1">

## `00_env_config`

Configure the Fabric environments and shared runtime settings used by the other templates.

[Open `00_env_config.ipynb`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/templates/notebooks/00_env_config.ipynb){ .md-button }

</div>

<div class="template-card" markdown="1">

## `01_governance`

Author and manage FabricOps Governance metadata and Data Contracts.

[Open `01_governance.ipynb`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/templates/notebooks/01_governance.ipynb){ .md-button }

</div>

<div class="template-card" markdown="1">

## `02_pipeline`

**Full Refresh Pipeline Template.** Read complete governed sources, transform them, and fully overwrite one or more governed targets. Use it when rereading each complete source and replacing each complete target is acceptable.

[Open `02_pipeline.ipynb`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/templates/notebooks/02_pipeline.ipynb){ .md-button }

</div>

<div class="template-card" markdown="1">

## `02B_incremental_append_pipeline`

**Incremental Append Pipeline Variant.** Start from the canonical `02_pipeline` shape, switch the driving source to `read_mode="incremental"`, keep supporting sources explicit, and append the processed scope to the target.

Committed progress is source → target specific and advances only after the append target publishes successfully. The starter flow deliberately uses one incremental driving source with one full supporting source. An initial append bootstrap requires a new or empty target; a populated target without committed source → target state fails safely instead of appending a duplicate complete source. Future `02C` and `02D` variants can own the SCD patterns separately.

[Open `02B_incremental_append_pipeline.ipynb`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/templates/notebooks/02B_incremental_append_pipeline.ipynb){ .md-button }\n\n[Follow the incremental append Guided Demo](guided-demo/02B-run-incremental-append-pipeline.md)

</div>

<div class="template-card" markdown="1">

## `99_explore`

Explore approved Production data and its FabricOps metadata without modifying the governed pipeline.

[Open `99_explore.ipynb`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/templates/notebooks/99_explore.ipynb){ .md-button }

</div>

</div>

## Where to go next

Read [How FabricOps Works](how-fabricops-works.md) for the operating model, or follow the [Guided Demo](guided-demo.md) to run the workflow yourself.
