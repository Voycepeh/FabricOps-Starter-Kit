"""Public widget entrypoint for ``widget_select_guardrail_target``."""

from __future__ import annotations

import importlib

from fabricops_kit.widgets import shared as _governance_review
from fabricops_kit.config.shared import resolve_fabric_context

from typing import Any



def widget_select_guardrail_target(*, spark_session: Any, context: dict[str, Any] | None = None) -> dict[str, Any]:
    """Render an interactive guardrail target selector.

    Parameters
    ----------
    spark_session : Any
        Fabric Spark session used to read metadata catalogue, enrichment, and
        guardrail rule rows.
    context : dict[str, Any], optional
        Advanced override for the active Fabric context.

    Returns
    -------
    dict[str, Any]
        Handover state for downstream enrichment, authoring, and governance
        review widgets.

    """
    return _guardrail_target_selection_widget_workflow(spark_session=spark_session, context=context)


def _guardrail_target_selection_widget_workflow(*, spark_session: Any, context: dict[str, Any] | None = None) -> dict[str, Any]:
    """Render an interactive guardrail target selector and return handover state.

    Parameters
    ----------
    spark_session : Any
        Spark session for metadata reads.
    context : dict, optional
        Advanced override context. Defaults to the active ``FABRIC_CONTEXT``
        initialized by ``00_env_config``.

    Returns
    -------
    dict[str, Any]
        Mutable handover state containing table identity, catalogue profile rows,
        existing rules, and effective table governance policy. The returned
        state updates when the user changes the selected target.

    """
    config, env, _context = resolve_fabric_context(context=context)
    widgets = importlib.import_module("ipywidgets")
    from IPython import display as ip

    catalogue = _governance_review._read_metadata_table_or_empty(config, env, _governance_review.PROFILED_TABLE, spark_session=spark_session)
    rules = _governance_review._read_metadata_table_or_empty(config, env, _governance_review.GUARDRAIL_TABLE, spark_session=spark_session)
    if not catalogue:
        raise ValueError("METADATA_DATA_PROFILED has no guardrail targets.")

    targets = {}
    for row in catalogue:
        environment_name = str(row.get("environment_name") or env)
        dataset_name = str(row.get("dataset_name") or "")
        table_name = str(row.get("table_name") or "")
        if not table_name:
            continue
        metadata_table_key = str(row.get("metadata_table_key") or _governance_review._build_metadata_table_key(
            row.get("store_type", "lakehouse"), row.get("layer", row.get("fabric_store_target", "")),
            row.get("schema_name"), table_name,
        ))
        key = (environment_name, dataset_name, table_name, metadata_table_key)
        label = f"{environment_name} / {dataset_name or '(no dataset)'} / {table_name}"
        targets.setdefault(label, key)
    if not targets:
        raise ValueError("METADATA_DATA_PROFILED has no table-level guardrail targets.")

    target_dropdown = widgets.Dropdown(options=[(label, value) for label, value in sorted(targets.items())], description="Target", layout=widgets.Layout(width="760px"))
    governance_badge = widgets.HTML()
    profile_preview = widgets.HTML()
    rules_preview = widgets.HTML()
    state: dict[str, Any] = {}

    def refresh(*_: Any) -> None:
        environment_name, dataset_name, table_name, metadata_table_key = target_dropdown.value
        table_rows = _governance_review._filter_table_rows(catalogue, environment_name=environment_name, dataset_name=dataset_name, table_name=table_name, metadata_table_key=metadata_table_key)
        table_rules = _governance_review._filter_table_rows(rules, environment_name=environment_name, dataset_name=dataset_name, table_name=table_name, metadata_table_key=metadata_table_key)
        policy = _governance_review.resolve_table_governance_policy(table_rows, environment_name=environment_name, dataset_name=dataset_name, table_name=table_name, metadata_table_key=metadata_table_key)
        latest = sorted(table_rows, key=lambda row: str(row.get("profiled_at") or row.get("run_timestamp") or row.get("profile_run_id") or ""), reverse=True)[0]
        columns = sorted({str(row.get("column_name") or "") for row in table_rows if row.get("column_name")})
        state.clear()
        state.update(
            {
                "environment_name": environment_name,
                "dataset_name": dataset_name,
                "table_name": table_name,
                "metadata_table_key": metadata_table_key,
                "profile_run_id": str(latest.get("profile_run_id") or ""),
                "profile_stage": str(latest.get("profile_stage") or ""),
                "columns": columns,
                "catalogue_profile_rows": table_rows,
                "existing_rules": table_rules,
                **policy,
            }
        )
        governance_badge.value = f"<b>Governance:</b> {state['governance_mode']} · <b>Approval policy:</b> {state['approval_policy']} · <b>Bypass allowed:</b> {state['approval_bypass_allowed']}"
        profile_preview.value = f"<b>Profile rows:</b> {len(table_rows)} · <b>Columns:</b> {', '.join(columns) if columns else '(none)'}"
        rules_preview.value = f"<b>Existing guardrail rules:</b> {len(table_rules)}"

    target_dropdown.observe(refresh, names="value")
    refresh()
    state["_controls"] = {"target": target_dropdown, "governance_badge": governance_badge, "profile_preview": profile_preview, "rules_preview": rules_preview}
    ip.display(widgets.VBox([widgets.HTML("<h3>Select guardrail target</h3>"), target_dropdown, governance_badge, profile_preview, rules_preview]))
    return state
