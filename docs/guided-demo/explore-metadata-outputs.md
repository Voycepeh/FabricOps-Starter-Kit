# Understand FabricOps widgets and metadata outputs

FabricOps notebooks use widgets to guide users through governed selections, reviews, and configuration without requiring them to work directly with every metadata table.

This supporting walkthrough explains what the widgets display, what users select or review, which metadata outputs are involved, and how those outputs support the wider agreement, pipeline, review, contract, and consumer workflow.

## Widgets and interactions across the workflow

| Notebook | Widget or interaction | Purpose | Typical metadata or output |
| --- | --- | --- | --- |
| `01_agreement` | `widget_render_data_steward`, `widget_render_data_agreement`, and `widget_view_data_contract` | Create or select stewards and agreements, then inspect contract context. | Data steward, data agreement, and data contract records and views |
| `02_pipeline` | Pipeline target configuration plus guardrail target, authoring, enrichment, review, and contract-view widgets | Select configured targets, run governed processing, curate metadata, and inspect evidence. | Catalogue, profiled data, lineage, guardrail results, and pipeline evidence |
| `03_review` | `widget_select_guardrail_target`, enrichment and guardrail-authoring widgets, `widget_review_guardrail_governance`, and `widget_view_data_contract` | Review tables, enrich business context, define guardrails, record governance decisions, and inspect the assembled contract. | Catalogue enrichment, guardrail rules, governance decisions, and contract views |
| `99_explore` | Read-only contract context, approved-target selections, and notebook displays | Select approved Production data for project-level exploration, AI, or BI work. | Spark dataframes, profiles, notebook displays, models, reports, or analytical outputs |

## Governance state and read-only outputs

Some widgets create or update governed metadata as part of the numbered workflow. Others only help users select, display, or inspect existing data.

| Interaction | Effect |
| --- | --- |
| Steward, agreement, enrichment, guardrail-authoring, and governance-review widgets | Create or update governed metadata in their relevant numbered workflow stages. |
| Guardrail-target and contract-context selections | Read existing governed metadata and select the context to inspect; the selection itself does not create governance state. |
| Pipeline target configuration | Selects approved Fabric targets; the governed `02_pipeline` run produces catalogue, profile, lineage, guardrail-result, and pipeline evidence. |
| `99_explore` approved-target selections, `profile_dataframe`, and notebook displays | Read approved data or produce only notebook-side and project-specific outputs; they do not update governed workflow state. |

Use the generated [List of Metadata Tables](../reference/metadata.md) when you need the implemented schemas and related functions behind these records.

## Expected outcome

Users can understand what each FabricOps widget is asking them to do, what metadata or data it uses, and what output they should expect before moving to the next workflow stage.

This page does not add another lifecycle step. It supports the notebook stages in which the widgets and outputs appear.

Return to the [Guided Demo overview](../guided-demo.md).

See also: [Function Reference](../reference/index.md).
