# Notebook templates

FabricOps Starter Kit uses five small notebook templates. For the complete workspace setup, role handoffs, metadata flow, and production handover, read the [FabricOps Starter Kit Operating Model](fabricops-operating-model.md).

| Template | Main user | Focus | Detailed guide |
| --- | --- | --- | --- |
| `00_env_config` | Platform team or engineer | Configure environment-specific workspace, lakehouse, warehouse, and metadata paths. | [`00_env_config`](notebook-structure/00-env-config.md) |
| `01_da` | Data steward or data owner | Maintain steward and data agreement records in the governance workspace. | [`01_da`](notebook-structure/01-data-sharing-agreement.md) |
| `02_ex` | Analyst or data scientist | Explore and profile data in Engineering Dev. | [`02_ex`](notebook-structure/02-exploration.md) |
| `03_pc` | Data engineer | Build repeatable transformations and lightweight enforcement in Engineering Dev and Prod. | [`03_pc`](notebook-structure/03-pipeline-contract.md) |
| `04_gov` | Governance user | Add approved rules, classifications, and business context in the governance workspace. | [`04_gov`](notebook-structure/04-governance-operations.md) |

Copy the templates, keep their responsibilities focused, and let every notebook reuse the paths configured by `00_env_config`.
