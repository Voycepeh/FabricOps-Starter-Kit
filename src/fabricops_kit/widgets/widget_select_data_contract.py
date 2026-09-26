"""Notebook-scoped Data Contract selection for Development and Production."""

from __future__ import annotations

from fabricops_kit.io import read_lakehouse_table

import html
from typing import Any

from fabricops_kit.config.metadata_schemas import metadata_table_physical_schema
from fabricops_kit.config.shared import (
    get_default_fabric_context,
    is_table_not_found_error,
    resolve_fabric_context,
)
from fabricops_kit.io.shared import get_spark_session
from fabricops_kit.pipeline.shared import resolve_active_data_contract
from fabricops_kit.pipeline.validate_data_contract import _validate_data_contract
from fabricops_kit.widgets.shared import (
    form_page,
    form_section,
    parse_data_contract_payload,
    pipeline_active_context,
    require_ipywidgets,
    resolve_notebook_lineage_tables,
    status_message,
    widget_common,
)

CONTRACT_TABLE = "METADATA_DATA_CONTRACT"
LINEAGE_TABLE = "METADATA_DATA_LINEAGE"


def _row_dict(row: Any) -> dict[str, Any]:
    return row.asDict(recursive=True) if hasattr(row, "asDict") else dict(row)


def _contract_options(rows: list[dict[str, Any]], table_id: str) -> list[dict[str, Any]]:
    """Return newest-first immutable contract rows for one canonical table."""
    return sorted(
        (
            dict(row) for row in rows
            if str(row.get("table_id") or "") == table_id
            and str(row.get("status") or "").lower() == "frozen"
        ),
        key=lambda row: int(row.get("contract_version") or 0), reverse=True,
    )


def _validation_contract_options(rows: list[dict[str, Any]], table_id: str) -> list[dict[str, Any]]:
    """Return newest-first frozen candidates available for validation."""
    return _contract_options(rows, table_id)


def _contract_review(row: dict[str, Any]) -> dict[str, Any]:
    """Build a compact review solely from an immutable contract payload."""
    payload = parse_data_contract_payload(row)
    table = payload["table"]
    guardrails = payload.get("guardrails") or []
    counts: dict[str, int] = {}
    expected_refresh = None
    for rule in guardrails:
        kind = str(rule.get("guardrail_type") or "unspecified")
        counts[kind] = counts.get(kind, 0) + 1
        if kind.lower() == "freshness" and rule.get("is_active", True):
            parameters = rule.get("rule_parameters") or {}
            if isinstance(parameters, dict):
                frequency = parameters.get("expected_refresh_frequency")
                unit = parameters.get("expected_refresh_unit")
                if frequency not in (None, "") and unit:
                    expected_refresh = {"frequency": frequency, "unit": str(unit)}
    return {
        "contract_version": int(row["contract_version"]),
        "status": str(row.get("status") or ""),
        "contract_date": row.get("_committed_at"),
        "table": {key: table.get(key) for key in ("table_id", "schema_name", "table_name")},
        "schema_columns": len(table.get("columns") or []),
        "guardrails": counts,
        "guardrail_details": guardrails,
        "processing": table.get("processing"),
        "expected_refresh": expected_refresh,
    }


def _set_override(context: dict[str, Any], table_id: str, contract: dict[str, Any]) -> None:
    """Set one table's immutable override without changing any other table."""
    contexts = [context]
    active = pipeline_active_context()
    if active is not None:
        if active.context is None:
            active.context = {}
        contexts.append(active.context)
    try:
        contexts.append(get_default_fabric_context())
    except RuntimeError:
        pass
    for target_context in contexts:
        overrides = dict(target_context.get("data_contract_overrides") or {})
        overrides[table_id] = {
            "contract_id": str(contract["contract_id"]),
            "contract_version": int(contract["contract_version"]),
        }
        target_context["data_contract_overrides"] = overrides


def _clear_overrides(context: dict[str, Any], table_id: str | None = None) -> None:
    """Clear one or all overrides from every active runtime context."""
    contexts = [context]
    active = pipeline_active_context()
    if active is not None:
        if active.context is None:
            active.context = {}
        contexts.append(active.context)
    try:
        contexts.append(get_default_fabric_context())
    except RuntimeError:
        pass
    seen: set[int] = set()
    for target_context in contexts:
        if id(target_context) in seen:
            continue
        seen.add(id(target_context))
        overrides = dict(target_context.get("data_contract_overrides") or {})
        if table_id is None:
            overrides.clear()
        else:
            overrides.pop(table_id, None)
        target_context["data_contract_overrides"] = overrides


def widget_select_data_contract(*, spark_session=None, context=None):
    """Select immutable Data Contracts for every table linked to this notebook.

    Parameters
    ----------
    spark_session : object, optional
        Spark session override.
    context : dict, optional
        FabricOps context normally established by ``00_env_config``. The current
        ``notebook_id``, optional ``workspace_id``, and environment scope Lineage.

    Returns
    -------
    dict
        Notebook scope, role-preserving table states, table-scoped execution
        modes and contract identities, controls, a ``set_mode`` callable, and
        a ``validate`` operation that evaluates the selected target candidate.

    Raises
    ------
    ValueError
        If notebook identity is missing, a requested frozen version is
        unavailable, or Production enforcement has no active contract for a
        Lineage-linked table.
    RuntimeError
        If Production has multiple active versions for a lineage-linked table.

    Notes
    -----
    Every Lineage-linked source remains in ``enforce`` mode. Each target can
    independently use ``enforce`` or ``validate``. Enforce resolves the
    environment's enforceable contract without showing a version picker;
    Production requires exactly one frozen version tagged active. Target validation exposes
    frozen candidates and never installs the candidate as an enforcement
    override. This widget never activates metadata.

    Examples
    --------
    >>> selection = widget_select_data_contract()
    >>> selection["set_mode"]("table-orders", "validate", "orders-contract", 3)

    See Also
    --------
    widget_data_contract

    """
    config, env, resolved = resolve_fabric_context(context=context)
    spark = get_spark_session(spark_session)
    runtime_context = {"config": config, "env": env, **(resolved or {})}
    lineage_schema = metadata_table_physical_schema(config, LINEAGE_TABLE)
    pairs, notebook_scope = resolve_notebook_lineage_tables(
        environment_name=env, store="Metadata", schema=lineage_schema,
        spark_session=spark, context=runtime_context, runtime_context=runtime_context,
        required=env == "prod",
    )
    table_ids = list(dict.fromkeys(table_id for _role, table_id in pairs))
    validation_table_ids = {
        table_id for role, table_id in pairs if str(role or "").strip().lower() == "target"
    }
    selection_context = context if isinstance(context, dict) else (resolved or runtime_context)
    state: dict[str, Any] = {
        "notebook": notebook_scope,
        "lineage_tables": [{"pipeline_role": role, "table_id": table_id} for role, table_id in pairs],
        "environment": env, "tables": {}, "resolved_contracts": {}, "message": "", "_controls": {},
    }

    catalogue_labels = {}

    # Initialization always starts Development unselected and Production ignores overrides.
    _clear_overrides(selection_context)
    if env == "prod":
        try:
            contracts = [_row_dict(row) for row in read_lakehouse_table(
                CONTRACT_TABLE, store="Metadata",
                schema=metadata_table_physical_schema(config, CONTRACT_TABLE),
                spark_session=spark, context=runtime_context,
            ).collect()]
        except Exception as exc:
            if not is_table_not_found_error(exc):
                raise
            contracts = []
        for table_id in table_ids:
            try:
                contract = resolve_active_data_contract(
                    config, env, table_id, spark_session=spark, required=True,
                )
            except ValueError as exc:
                raise ValueError(
                    f"Production environment {env!r} requires exactly one active Data Contract for "
                    f"lineage-linked table {table_id!r} (table_id={table_id!r})."
                ) from exc
            except RuntimeError as exc:
                raise RuntimeError(
                    f"Production environment {env!r} cannot resolve Data Contract for lineage-linked "
                    f"table {table_id!r} (table_id={table_id!r}): {exc}"
                ) from exc
            review = _contract_review(contract)
            state["tables"][table_id] = {
                "mode": "enforce",
                "contract_id": str(contract["contract_id"]),
                "contract_version": int(contract["contract_version"]),
                "versions": _validation_contract_options(contracts, table_id),
                "selected": contract, "review": review,
                "display_name": catalogue_labels.get(table_id) or review["table"].get("table_name") or table_id,
            }
            state["resolved_contracts"][table_id] = {
                "contract_id": str(contract["contract_id"]),
                "contract_version": int(contract["contract_version"]),
            }
        state["message"] = f"Resolved {len(table_ids)} active Production Data Contract(s)."
    else:
        try:
            catalogue_rows = [_row_dict(row) for row in read_lakehouse_table(
                "METADATA_DATA_CATALOGUE", store="Metadata",
                schema=metadata_table_physical_schema(config, "METADATA_DATA_CATALOGUE"),
                spark_session=spark, context=runtime_context,
            ).collect()]
        except Exception as exc:
            if not is_table_not_found_error(exc):
                raise
            catalogue_rows = []
        for row in catalogue_rows:
            if (
                str(row.get("environment_name") or "") == env
                and str(row.get("metadata_level") or "").lower() == "table"
                and bool(row.get("is_active"))
                and str(row.get("table_id") or "") in table_ids
            ):
                parts = (row.get("layer"), row.get("schema_name"), row.get("table_name"))
                label = " / ".join(str(part).strip() for part in parts if str(part or "").strip())
                if label:
                    catalogue_labels[str(row["table_id"])] = label
        try:
            contracts = [_row_dict(row) for row in read_lakehouse_table(
                CONTRACT_TABLE, store="Metadata",
                schema=metadata_table_physical_schema(config, CONTRACT_TABLE),
                spark_session=spark, context=runtime_context,
            ).collect()]
        except Exception as exc:
            if not is_table_not_found_error(exc):
                raise
            contracts = []
        for table_id in table_ids:
            versions = _validation_contract_options(contracts, table_id)
            enforceable = [
                row for row in _contract_options(contracts, table_id)
                if str(row.get("status") or "").lower() == "frozen" and bool(row.get("is_active"))
            ]
            if len(enforceable) > 1:
                raise RuntimeError(
                    f"Data Contract integrity error: {table_id!r} has multiple active versions."
                )
            selected = enforceable[0] if enforceable else None
            contract_table_name = None
            representative = selected or (versions[0] if versions else None)
            if representative:
                contract_table_name = parse_data_contract_payload(representative)["table"].get("table_name")
            state["tables"][table_id] = {
                "mode": "enforce",
                "contract_id": str(selected.get("contract_id") or "") if selected else None,
                "contract_version": int(selected.get("contract_version") or 0) if selected else None,
                "versions": versions,
                "selected": selected,
                "review": _contract_review(selected) if selected else None,
                "display_name": catalogue_labels.get(table_id) or contract_table_name or table_id,
            }
            if selected:
                _set_override(selection_context, table_id, selected)
                state["resolved_contracts"][table_id] = {
                    "contract_id": str(selected["contract_id"]),
                    "contract_version": int(selected["contract_version"]),
                }
        state["message"] = (
            f"Environment {env} · each table can enforce its active frozen contract or validate a frozen candidate."
        )

    def set_mode(
        table_id: str,
        mode: str,
        contract_id: str | None = None,
        contract_version: int | None = None,
    ) -> dict[str, Any]:
        """Set one table to enforce or to validate one exact frozen candidate."""
        if table_id not in state["tables"]:
            raise ValueError("The selected table_id is not linked to the current notebook in METADATA_DATA_LINEAGE.")
        normalized_mode = str(mode or "").strip().lower()
        if normalized_mode not in {"enforce", "validate"}:
            raise ValueError("Data Contract mode must be 'enforce' or 'validate'.")
        if normalized_mode == "validate" and table_id not in validation_table_ids:
            raise ValueError("Validate mode is available for pipeline target tables only.")
        table_state = state["tables"][table_id]
        if normalized_mode == "enforce":
            selected = table_state.get("enforce_contract") or (
                table_state.get("selected") if table_state.get("mode") == "enforce" else None
            )
            if env == "prod" and selected is None:
                raise ValueError("Production enforcement requires an active Data Contract.")
            if selected:
                _set_override(selection_context, table_id, selected)
                table_state.update(
                    mode="enforce",
                    contract_id=str(selected["contract_id"]),
                    contract_version=int(selected["contract_version"]),
                    selected=selected,
                    review=_contract_review(selected),
                )
                state["resolved_contracts"][table_id] = {
                    "contract_id": str(selected["contract_id"]),
                    "contract_version": int(selected["contract_version"]),
                }
            else:
                _clear_overrides(selection_context, table_id)
                table_state.update(
                    mode="enforce", contract_id=None, contract_version=None,
                    selected=None, review=None,
                )
                state["resolved_contracts"].pop(table_id, None)
            state["message"] = f"Enforce mode selected for {table_id}."
            return state
        if not str(contract_id or "").strip() or not contract_version:
            raise ValueError("Validate mode requires an exact frozen contract_id and contract_version.")
        matches = [
            row for row in table_state["versions"]
            if str(row.get("contract_id") or "") == str(contract_id or "")
            and int(row.get("contract_version") or 0) == int(contract_version or 0)
        ]
        if not matches:
            raise ValueError("Selected frozen Data Contract version is not available for this table.")
        selected = matches[0]
        review = _contract_review(selected)
        _clear_overrides(selection_context, table_id)
        table_state.update(
            mode="validate",
            contract_id=str(selected["contract_id"]),
            contract_version=int(selected["contract_version"]),
            selected=selected,
            review=review,
        )
        state["resolved_contracts"].pop(table_id, None)
        state["message"] = f"Validate mode selected with Data Contract v{selected['contract_version']} for {table_id}."
        return state

    for table_state in state["tables"].values():
        table_state["enforce_contract"] = table_state.get("selected")

    def validate(
        *, table_id: str, dataframe, spark_session=None,
        run_id: str = "", verbose: bool = True,
    ) -> dict[str, Any]:
        """Validate the exact frozen candidate selected for one target table."""
        if table_id not in state["tables"]:
            raise ValueError("The selected table_id is not linked to the current notebook in METADATA_DATA_LINEAGE.")
        table_state = state["tables"][table_id]
        if table_state.get("mode") != "validate":
            raise ValueError(f"Table {table_id!r} is not configured for validate mode.")
        return _validate_data_contract(
            table_id=table_id,
            contract_id=str(table_state["contract_id"]),
            contract_version=int(table_state["contract_version"]),
            dataframe=dataframe,
            spark_session=spark_session,
            run_id=run_id,
            verbose=verbose,
        )

    state["set_mode"] = set_mode
    state["validate"] = validate
    try:
        widgets = require_ipywidgets()
    except ModuleNotFoundError:
        return state
    status = status_message(widgets)
    sections = []
    controls: dict[str, Any] = {}
    for role, table_id in pairs:
        if table_id in controls:
            continue
        table_state = state["tables"][table_id]
        versions = table_state["versions"]
        mode_control = widgets.ToggleButtons(
            options=(
                [("Enforce", "enforce"), ("Validate", "validate")]
                if table_id in validation_table_ids else [("Enforce", "enforce")]
            ),
            value="enforce", **widget_common(widgets, role),
        )
        version_control = widgets.Dropdown(
            options=[("Select frozen candidate", ""), *[
                (f"Data Contract v{row['contract_version']} · Frozen",
                 f"{row['contract_id']}\n{row['contract_version']}") for row in versions
            ]],
            layout=widgets.Layout(display="none"),
        )
        preview = widgets.HTML(value="")

        def render(
            _change: Any,
            *,
            current_table: str = table_id,
            current_mode: Any = mode_control,
            current_version: Any = version_control,
            current_preview: Any = preview,
        ) -> None:
            try:
                if current_mode.value == "enforce":
                    current_version.layout.display = "none"
                    set_mode(current_table, "enforce")
                    selected = state["tables"][current_table].get("selected")
                    current_preview.value = (
                        f"<b>Enforce</b> · Data Contract v{selected['contract_version']} · Active"
                        if selected else "<b>Enforce</b> · No enforceable contract selected in this environment"
                    )
                else:
                    current_version.layout.display = ""
                    if not current_version.value:
                        current_preview.value = "<b>Validate</b> · Select an exact frozen candidate"
                        return
                    contract_id, version = current_version.value.split("\n", 1)
                    set_mode(current_table, "validate", contract_id, int(version))
                    current_preview.value = f"<b>Validate</b> · Data Contract v{version} · Frozen"
                current_preview.value += source_expectation_html()
                status.value = ""
            except ValueError as exc:
                status.value = html.escape(str(exc))

        mode_control.observe(render, names="value")
        version_control.observe(render, names="value")
        controls[table_id] = {"mode": mode_control, "version": version_control}
        role_label = "Read" if role.lower() == "source" else "Write"
        table_name = table_state["display_name"]

        def source_expectation_html(
            *, current_role: str = role, current_table_id: str = table_id
        ) -> str:
            if current_role.lower() != "source":
                return ""
            review = state["tables"][current_table_id].get("review") or {}
            expected = review.get("expected_refresh")
            if not expected:
                return "<br><span style='color:#667085;'>Expected refresh: Not defined</span>"
            value = expected.get("frequency")
            shown = str(int(value)) if isinstance(value, float) and value.is_integer() else str(value)
            return (
                "<br><span style='color:#667085;'>Expected refresh: "
                f"<b>{html.escape(shown)} {html.escape(str(expected.get('unit') or ''))}</b></span>"
            )
        short_table_id = f"{table_id[:8]}…{table_id[-6:]}" if len(table_id) > 18 else table_id
        sections.extend([
            widgets.HTML(value=(
                f"<b>{role_label} · {html.escape(str(table_name))}</b><br>"
                f"<span>table_id: <code title=\"{html.escape(table_id)}\">{html.escape(short_table_id)}</code></span>"
            )),
            mode_control, version_control, preview,
        ])
        render({"new": "enforce"})
    page = form_page(
        widgets, title="Pipeline Data Contracts",
        description=(f"Environment: {env} · Notebook: {notebook_scope.get('notebook_name') or notebook_scope.get('notebook_id')} · "
                     "Choose enforce or validate independently for each table."),
        children=[form_section(widgets, title="Pipeline tables", children=sections), status],
    )
    state["_controls"] = {"selections": controls, "status": status, "page": page}
    from IPython import display as ip
    ip.display(page)
    return state
