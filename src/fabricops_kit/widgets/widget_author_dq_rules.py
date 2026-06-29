"""Public widget entrypoint for ``widget_author_dq_rules``."""

from __future__ import annotations

from typing import Any, Iterable, Mapping

from fabricops_kit.governance_review import _dq_rule_authoring_widget_workflow


def widget_author_dq_rules(
    state: Mapping[str, Any],
    *,
    dq_authoring_mode: str = "manual",
    rule_type: str = "not_null",
    selected_columns: Iterable[str] | None = None,
    parameters: Mapping[str, Any] | None = None,
    severity: str = "warning",
    spark_session: Any = None,
    context: dict[str, Any] | None = None,
    bypass_reason: str = "",
    source_notebook_type: str = "02_pipeline",
    created_by_role: str = "engineering",
    commit: bool = False,
) -> dict[str, Any]:
    """Render interactive manual DQ rule authoring UI.

    Parameters
    ----------
    state : Mapping[str, Any]
        Guardrail target state returned by the target selector or prepared by a
        notebook workflow.
    dq_authoring_mode : str, default="manual"
        Authoring mode for the widget. The public widget supports manual rule
        authoring.
    rule_type : str, default="not_null"
        Initial DQ rule type selected in the widget.
    selected_columns : Iterable[str], optional
        Initial columns selected for the rule.
    parameters : Mapping[str, Any], optional
        Initial rule parameters.
    severity : str, default="warning"
        Initial rule severity.
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
    return _dq_rule_authoring_widget_workflow(
        state,
        dq_authoring_mode=dq_authoring_mode,
        rule_type=rule_type,
        selected_columns=selected_columns,
        parameters=parameters,
        severity=severity,
        spark_session=spark_session,
        context=context,
        bypass_reason=bypass_reason,
        source_notebook_type=source_notebook_type,
        created_by_role=created_by_role,
        commit=commit,
    )
