# Workspace Operating Model

FabricOps Starter Kit is designed to stay self-contained within Microsoft Fabric while keeping governance metadata separate from development and production processing.

The recommended setup uses three workspaces:

| Workspace | Items | Purpose |
| --- | --- | --- |
| Governance workspace | `metadata_lakehouse` | Owns shared metadata, approved agreements, steward records, governance review outputs, and production notebook evidence. |
| Engineering Dev workspace | `source_lakehouse`, `unified_lakehouse`, `product_warehouse` | Supports exploration, profiling, transformation development, and proposed outputs. |
| Engineering Prod workspace | `source_lakehouse`, `unified_lakehouse`, `product_warehouse` | Runs approved repeatable pipelines and publishes production outputs. |

![FabricOps Starter Kit operating model with Governance, Engineering Dev, and Engineering Prod workspaces](../assets/fabricops-operating-model-overview.png){ .full-width }

## Promotion principle

Production promotion should remain lightweight.

Promote the production-ready `03_pc` notebook from Engineering Dev to Engineering Prod, run it with the production `00_env_config`, and let the production notebook create production outputs in the production workspace.

Do not copy development outputs into production.

## What moves to production

| Item | Promotion approach |
| --- | --- |
| `00_env_config` | Recreate or maintain separately in each environment. Do not blindly promote it. |
| `03_pc` | Promote the production-ready transformation notebook from Engineering Dev to Engineering Prod. |
| Approved metadata | Promote or recreate through a controlled process. |
| Production outputs | Create by running the production notebook in Engineering Prod. |
| Draft metadata, dev paths, unreviewed rules | Do not promote. |

Production pipelines must read only production configuration and approved production metadata.

## Store production notebook evidence

Once a production `03_pc` pipeline is stable, store a copy of the final production notebook as a `.py` or `.ipynb` file in the Governance workspace metadata lakehouse file area.

This keeps handover and support material grounded in the actual production implementation, not a separate manually written explanation.

The stored notebook evidence can later support:

| Output | Purpose |
| --- | --- |
| Handover summary | Explains what the production notebook does and how it should be supported. |
| Production support notes | Helps support teams understand inputs, outputs, dependencies, and checks. |
| Data product explanation | Describes the production data product in business-friendly language. |
| AI-assisted documentation | Uses the notebook implementation as source evidence for draft documentation. |

Review generated material before publishing it. AI can speed up documentation and support preparation, but people remain accountable for the approved metadata and production notebook.

## Workspace responsibilities

| Responsibility | Governance workspace | Engineering Dev workspace | Engineering Prod workspace |
| --- | --- | --- | --- |
| Steward and agreement metadata | Owns | Reads when needed | Reads approved metadata |
| Exploration and profiling | Reviews outputs | Creates proposed evidence | Not used for exploration |
| Transformation development | Reviews metadata | Builds and tests `03_pc` | Runs approved `03_pc` |
| Governance review | Owns `04_gov` outputs | Provides profiled outputs | Uses approved rules |
| Production outputs | Stores evidence summary | Does not publish production outputs | Creates production outputs |
| Handover evidence | Stores final production notebook copy | Provides candidate implementation | Provides final implementation |

## Next step

Continue to [Notebook Templates](notebook-templates.md) to understand what each notebook owns in the workflow.
