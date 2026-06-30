"""Public widget entrypoints for FabricOps notebook workflows."""

__all__ = [
    "widget_author_dq_rules",
    "widget_author_schema_freshness_profile_rules",
    "widget_enrich_table_metadata",
    "widget_render_agreement_evidence",
    "widget_render_data_agreement",
    "widget_render_data_steward",
    "widget_review_guardrail_governance",
    "widget_select_agreement",
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


from .widget_select_agreement import widget_select_agreement
