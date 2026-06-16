# Template-driven callable surface

FabricOps Starter Kit does not preserve unused notebook widgets or helper functions solely for backwards compatibility. The supported public callable surface is intentionally driven by the current notebook templates in `templates/notebooks/` and the helper call graph those templates require.

`widget_select_agreement` and `get_selected_agreement` remain supported public callables because they anchor `02_pipeline` to an approved data agreement. The selector can register the active notebook in `METADATA_NOTEBOOK_REGISTRY`, preserving `agreement_id`, `contract_version`, `notebook_registry_id`, and `notebook_id` for pipeline metadata, lineage, and run-summary evidence. This agreement-selection workflow is not a compatibility-only widget.

Current supported guardrail widgets are the widgets surfaced in the pipeline and governance templates:

- `widget_select_guardrail_target`
- `widget_author_schema_freshness_profile_rules`
- `widget_author_dq_rules`
- `widget_review_guardrail_governance`

Agreement selection and guardrail target selection are separate workflow steps: `02_pipeline` first selects/registers an agreement, then guardrail target selection works from `METADATA_DATA_CATALOGUE` evidence after profiling. Older governance-profile target, column context/classification, and DQ-rule review widgets remain removed from the template flow.
