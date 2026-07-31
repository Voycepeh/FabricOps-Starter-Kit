"""Public widget entrypoints for FabricOps notebook workflows."""

__all__ = [
    "widget_view_agreement_catalogue",
    "widget_view_pipeline_catalogue",
    "widget_view_data_catalogue",
    "widget_register_data_contract",
    "widget_author_dq_rules",
    "widget_author_schema_freshness_profile_rules",
    "widget_enrich_table_metadata",
    "widget_render_data_agreement",
    "widget_render_data_steward",
    "widget_review_guardrail_governance",
    "widget_select_guardrail_target",
]

_WIDGET_MODULES = {name: f"fabricops_kit.widgets.{name}" for name in __all__}


def __getattr__(name: str):
    """Lazily load public widget callables."""
    if name not in _WIDGET_MODULES:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    from importlib import import_module

    value = getattr(import_module(_WIDGET_MODULES[name]), name)
    globals()[name] = value
    return value
