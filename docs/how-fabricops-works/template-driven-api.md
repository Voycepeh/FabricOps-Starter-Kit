# Template-driven callable surface

FabricOps Starter Kit does not preserve unused notebook widgets or helper functions solely for backwards compatibility. The supported public callable surface is intentionally driven by the current notebook templates in `templates/notebooks/` and the helper call graph those templates require.

`widget_select_agreement` is the supported public agreement-selection/runtime-context entry point because it anchors `02_pipeline` and `99_explore` to an approved data agreement. The selector context can register the active notebook in `METADATA_NOTEBOOK_REGISTRY`, preserving `agreement_id`, `contract_version`, `notebook_registry_id`, and `notebook_id` for pipeline metadata, lineage, and run-summary evidence. This agreement-selection workflow is not a compatibility-only widget.

Current supported agreement and guardrail widgets surfaced in the pipeline and governance templates are:

- `widget_select_agreement`
- `widget_select_guardrail_target`
- `widget_author_schema_freshness_profile_rules`
- `widget_author_dq_rules`
- `widget_enrich_table_metadata`
- `widget_review_guardrail_governance`

Agreement selection and guardrail target selection are separate workflow steps: `02_pipeline` first selects/registers an agreement for notebook registry linkage, then guardrail target selection works from `METADATA_DATA_CATALOGUE` evidence after profiling. `03_governance` now surfaces enrichment plus guardrail review. The old separated business context/classification widgets are removed from the current template flow, and DQ belongs with guardrail authoring/review rather than enrichment.
