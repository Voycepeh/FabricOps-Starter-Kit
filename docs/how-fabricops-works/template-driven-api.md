# Template-driven callable surface

FabricOps Starter Kit does not preserve unused notebook widgets or helper functions solely for backwards compatibility. The supported public callable surface is intentionally driven by the current notebook templates in `templates/notebooks/` and the helper call graph those templates require.

Current supported guardrail widgets are the widgets surfaced in the pipeline and governance templates:

- `widget_select_guardrail_target`
- `widget_author_schema_freshness_profile_rules`
- `widget_author_dq_rules`
- `widget_review_guardrail_governance`

Older agreement-selection, governance-profile target, and DQ-rule review widgets were removed from the template flow. Pipeline notebooks now use explicit agreement context variables when agreement identifiers or notebook registry identifiers are needed.
