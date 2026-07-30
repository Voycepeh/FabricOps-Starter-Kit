# Understand FabricOps widgets and metadata outputs

FabricOps notebooks use widgets to guide users through governed selections, reviews, and configuration without requiring them to work directly with every metadata table.

This supporting walkthrough explains what the widgets display, what users select or review, which metadata outputs are involved, and how those outputs support the wider agreement, pipeline, review, contract, and consumer workflow.

## Widgets and interactions across the workflow

| Notebook | Widget or interaction | Purpose | Typical metadata or output |
| --- | --- | --- | --- |
| `01_agreement` | Steward and agreement widgets, then `widget_register_data_contract` | Create or select stewards and an agreement, then save draft membership for logical datasets discovered in the active environment. | Data steward, data agreement, and logical Data Contract membership |
| `02_pipeline` | Profiling and registration, then a current-notebook-scoped `widget_view_data_contract` | Run governed processing and inspect canonical evidence for datasets in the active environment, current workspace, and current notebook lineage. | Catalogue, profiled data, lineage, guardrail results, and pipeline evidence |
| `03_review` | Steward and agreement selection, then an agreement-scoped `widget_view_data_contract` and governance widgets | Review only logical datasets linked to the selected agreement, using canonical observations from the active environment. | Agreement-linked contract views, catalogue enrichment, guardrail rules, and governance decisions |
| `99_explore` | Read-only contract context, approved-target selections, and notebook displays | Select approved Production data for project-level exploration, AI, or BI work. | Spark dataframes, profiles, notebook displays, models, reports, or analytical outputs |

## Governance state and read-only outputs

Some widgets create or update governed metadata as part of the numbered workflow. Others only help users select, display, or inspect existing data.

| Interaction | Effect |
| --- | --- |
| Steward, agreement, enrichment, guardrail-authoring, and governance-review widgets | Create or update governed metadata in their relevant numbered workflow stages. |
| Guardrail-target and contract-context selections | Read existing governed metadata and select the context to inspect; the selection itself does not create governance state. |
| Pipeline target configuration | Selects approved Fabric targets; the governed `02_pipeline` run produces catalogue, profile, lineage, guardrail-result, and pipeline evidence. |
| `99_explore` approved-target selections, `profile_dataframe`, and notebook displays | Read approved data or produce only notebook-side and project-specific outputs; they do not update governed workflow state. |

For agreement-scoped governance review, open `03_review`, select the Data Steward, select the Data Agreement, and then select from only the logical datasets linked through `METADATA_DATA_CONTRACT`. The active environment determines which canonical metadata observations are returned. Logical membership is shared across Development and Production, but their observations remain separate; review each by running the notebook with the corresponding active environment configuration.

The pipeline and governance viewers return labelled canonical metadata tables through `get_views()`. Separate rerunnable notebook cells own their native DataFrame display; cross-environment browsing remains deferred.

Use the generated [List of Metadata Tables](../reference/metadata.md) when you need the implemented schemas and related functions behind these records.

## Expected outcome

Users can understand what each FabricOps widget is asking them to do, what metadata or data it uses, and what output they should expect before moving to the next workflow stage.

This page does not add another lifecycle step. It supports the notebook stages in which the widgets and outputs appear.

Return to the [Guided Demo overview](../guided-demo.md).

See also: [Function Reference](../reference/index.md).
