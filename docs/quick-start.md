# Quick start

Use this page to get FabricOps Starter Kit running in Microsoft Fabric. For the complete role flow and workspace model, read the [How FabricOps Works](how-fabricops-works/index.md).

!!! note "Notebook preview"
    The notebook templates are optimized for Microsoft Fabric execution. GitHub may not always render `.ipynb` previews reliably. If GitHub shows a notebook preview error, open the template in Microsoft Fabric or view it locally in VS Code / Jupyter. The `%run 00_env_config` bootstrap cell is intentionally active so the templates remain plug-and-play in Fabric. Do not manually edit the bootstrap cell unless you are intentionally customizing the template.

## Recommended minimum workspaces

Prepare these Fabric workspaces and items before copying the notebooks:

| Workspace | Items |
| --- | --- |
| Governance workspace | `metadata_lakehouse` |
| Engineering Dev workspace | `source_lakehouse`, `unified_lakehouse`, `product_warehouse` |
| Engineering Prod workspace | `source_lakehouse`, `unified_lakehouse`, `product_warehouse` |

Start in the governance and Engineering Dev workspaces. Add production configuration when the first pipeline is ready to promote.

## First run setup

| Step | Do this | Expected result | Read more |
| --- | --- | --- | --- |
| 1 | Install the FabricOps wheel in a Microsoft Fabric Environment. | Fabric notebooks attached to that Environment can import `fabricops_kit`. | [Fabric Wheel Install](install.md) |
| 2 | Copy the notebook templates from the GitHub templates folder into Fabric. | You have editable copies of `00_env_config`, `01_da`, `02_ex`, `03_pc`, and `04_gov`. | [Notebook templates](https://github.com/Voycepeh/FabricOps-Starter-Kit/tree/main/templates/notebooks), [Workspace and Notebook Flow](how-fabricops-works/workspace-and-notebook-flow.md) |
| 3 | Attach the same Fabric Environment to each copied notebook. | Each notebook uses the installed helper wheel and compatible runtime configuration. | [Fabric Wheel Install](install.md) |
| 4 | Configure and run `00_env_config` for the current environment. | Workspace, lakehouse, warehouse, and governance metadata paths are ready for the downstream notebooks. | [Template: `00_env_config`](how-fabricops-works/workspace-and-notebook-flow.md) |

## Run the role-based notebook workflow

The role-based notebook workflow shows how each template hands work to the next role without adding a heavy process.

<figure markdown>
  ![Role-based notebook workflow from environment configuration through AI-assisted handover](assets/fabricops-role-workflow.png){ .full-width }
  <figcaption>Role-based notebook workflow for configuration, agreements, exploration, pipeline build, governance enrichment, enforcement, and handover.</figcaption>
</figure>

After setup, use the templates in this order:

```text
00_env_config
01_da
02_ex
03_pc
04_gov
03_pc rerun with approved metadata
production handover
```

Each template has one main responsibility:

| Template | Main outcome |
| --- | --- |
| `00_env_config` | Environment-specific paths and metadata routing. |
| `01_da` | Steward and data agreement records. |
| `02_ex` | Exploration profiles, notebook registration, and proposed schema or transformation advice. |
| `03_pc` | Repeatable transformations, technical columns, drift checks, lineage, profiles, and output tables. |
| `04_gov` | Approved business context, data quality rules, and sensitivity classification. |
| Production handover | A stored production notebook export that supports an AI-assisted handover summary and manifest. |

## Next reads

- [How FabricOps Works](how-fabricops-works/index.md): workspace ownership, role handoffs, shared metadata, assembled views, and production handover.
- [Workspace and Notebook Flow](how-fabricops-works/workspace-and-notebook-flow.md): workspace setup and the role-based notebook sequence.
- [Data Quality Rules](data-quality-rules-system.md): approved-rule enforcement in `03_pc` notebooks.
- [Function Reference](reference/index.md): reusable helper APIs.
