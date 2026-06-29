"""Public widget entrypoint for ``widget_author_schema_freshness_profile_rules``."""

from __future__ import annotations

from typing import Any, Mapping

from fabricops_kit.governance_review import _schema_freshness_profile_rule_authoring_widget_workflow


def widget_author_schema_freshness_profile_rules(
    state: Mapping[str, Any],
    *,
    spark_session: Any = None,
    context: dict[str, Any] | None = None,
    bypass_reason: str = "",
    source_notebook_type: str = "02_pipeline",
    created_by_role: str = "engineering",
    commit: bool = False,
) -> dict[str, Any]:
    """Render schema, freshness, and profile behavior authoring controls.

    Parameters
    ----------
    state : Mapping[str, Any]
        Guardrail target state returned by the target selector or prepared by a
        notebook workflow.
    spark_session : Any, optional
        Fabric Spark session used when committing metadata rows.
    context : dict[str, Any], optional
        Advanced override for the active Fabric context.
    bypass_reason : str, default=""
        Governance-bypass reason used when applying rules immediately.
    source_notebook_type : str, default="02_pipeline"
        Notebook role recorded on authored metadata rows.
    created_by_role : str, default="engineering"
        Actor role recorded on authored metadata rows.
    commit : bool, default=False
        When True, commit the selected rule instead of preview-only behavior.

    Returns
    -------
    dict[str, Any]
        Rendered controls and save actions for notebook automation.

    """
    return _schema_freshness_profile_rule_authoring_widget_workflow(
        state,
        spark_session=spark_session,
        context=context,
        bypass_reason=bypass_reason,
        source_notebook_type=source_notebook_type,
        created_by_role=created_by_role,
        commit=commit,
    )
