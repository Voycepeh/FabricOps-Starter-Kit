"""Public widget entrypoint for immutable Data Contract inventories."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime
import html
from typing import Any

from fabricops_kit.config.audit import build_runtime_audit_fields
from fabricops_kit.config.metadata_schemas import coerce_metadata_row_types, metadata_table_schema_registry
from fabricops_kit.config.shared import resolve_fabric_context
from fabricops_kit.io.shared import get_spark_session, read_lakehouse_table_core, write_lakehouse_table_core
from fabricops_kit.widgets.shared import require_ipywidgets, widget_common


CONTRACT_TABLE = "METADATA_DATA_CONTRACT"
CATALOGUE_TABLE = "METADATA_DATA_CATALOGUE"


def _display_widget(value: Any) -> None:
    """Display a widget when the optional IPython runtime is available."""
    try:
        from IPython import display as ip
    except ModuleNotFoundError:
        return
    ip.display(value)


def _agreement_details(agreement: dict[str, Any] | None, agreement_id: str | None) -> tuple[str, str]:
    """Resolve the canonical ID and a readable label from supplied state only."""
    explicit = str(agreement_id or "").strip()
    supplied = agreement or {}
    row: dict[str, Any] = supplied
    resolved = explicit or str(supplied.get("agreement_id") or "").strip()
    if not resolved:
        selected = supplied.get("existing_record")
        selected_id = str(getattr(selected, "value", "") or "").strip()
        row = (supplied.get("existing_records_by_id") or {}).get(selected_id, {})
        resolved = str(row.get("agreement_id") or selected_id).strip()
    if not resolved:
        if "existing_record" in supplied:
            return "", ""
        raise ValueError("A valid agreement_id is required. Supply agreement_id or an agreement state with a selected agreement.")
    label = str(row.get("agreement_name") or supplied.get("agreement_name") or resolved).strip() or resolved
    return resolved, label


def _normalize_initial_ids(metadata_ids: Sequence[str] | None) -> list[str]:
    """Trim and de-duplicate optional initial identities in caller order."""
    if metadata_ids is None:
        return []
    if isinstance(metadata_ids, (str, bytes)):
        raise TypeError("metadata_ids must be a non-string sequence or None")
    result: list[str] = []
    for value in metadata_ids:
        key = str(value or "").strip()
        if key and key not in result:
            result.append(key)
    return result


def _commit_sort_value(value: Any) -> tuple[int, str]:
    """Return a comparable timestamp value that also handles test doubles."""
    if value is None:
        return (0, "")
    if isinstance(value, datetime):
        return (1, value.isoformat())
    return (1, str(value))


def _latest_catalogue_rows(catalogue, environment_name: str) -> list[dict[str, Any]]:
    """Return one deterministic latest observation per active-environment key."""
    from pyspark.sql import functions as F

    fields = [
        "metadata_table_key", "schema_fingerprint", "store_type", "layer",
        "schema_name", "table_name", "_committed_at",
    ]
    observed = [
        row.asDict(recursive=True)
        for row in catalogue.filter(F.col("environment_name") == environment_name).select(*fields).collect()
        if str(row["metadata_table_key"] or "").strip()
    ]
    latest: dict[str, dict[str, Any]] = {}
    for row in observed:
        key = str(row.get("metadata_table_key") or "").strip()
        rank = (
            _commit_sort_value(row.get("_committed_at")),
            str(row.get("schema_fingerprint") or ""),
            str(row.get("store_type") or ""),
            str(row.get("layer") or ""),
            str(row.get("schema_name") or ""),
            str(row.get("table_name") or ""),
        )
        current = latest.get(key)
        current_rank = (
            _commit_sort_value(current.get("_committed_at")),
            str(current.get("schema_fingerprint") or ""),
            str(current.get("store_type") or ""),
            str(current.get("layer") or ""),
            str(current.get("schema_name") or ""),
            str(current.get("table_name") or ""),
        ) if current else None
        if current_rank is None or rank > current_rank:
            latest[key] = row
    return [dict(latest[key], metadata_table_key=key) for key in sorted(latest)]


def _base_dataset_label(row: dict[str, Any]) -> str:
    """Build a readable physical-coordinate label without empty segments."""
    return " / ".join(
        str(row.get(field) or "").strip()
        for field in ("layer", "schema_name", "table_name")
        if str(row.get(field) or "").strip()
    )


def _short_key(key: str) -> str:
    """Return a deterministic compact identity for fallback labels."""
    return key if len(key) <= 12 else f"{key[:8]}…{key[-4:]}"


def _dataset_options(rows: list[dict[str, Any]]) -> list[tuple[str, str]]:
    """Return uniquely labelled options whose values remain canonical keys."""
    base_counts: dict[str, int] = {}
    for row in rows:
        label = _base_dataset_label(row)
        base_counts[label] = base_counts.get(label, 0) + 1
    provisional: list[tuple[str, str]] = []
    for row in rows:
        label = _base_dataset_label(row)
        if base_counts[label] > 1:
            store = str(row.get("store_type") or "").strip()
            label = f"{store} — {label}" if store else label
        provisional.append((label, str(row["metadata_table_key"])))
    label_counts: dict[str, int] = {}
    for label, _key in provisional:
        label_counts[label] = label_counts.get(label, 0) + 1
    return sorted([
        (f"{label} — {_short_key(key)}" if label_counts[label] > 1 else label, key)
        for label, key in provisional
    ], key=lambda option: (option[0].casefold(), option[1]))


def _latest_inventory(memberships, agreement_id: str) -> tuple[dict[str, Any] | None, list[dict[str, Any]]]:
    """Return the latest audit activity summary and its membership rows."""
    from pyspark.sql import functions as F

    rows = [
        row.asDict(recursive=True)
        for row in memberships.filter(F.col("agreement_id") == agreement_id).collect()
    ]
    if not rows:
        return None, []
    latest_row = max(rows, key=lambda row: (
        _commit_sort_value(row.get("_committed_at")),
        str(row.get("_activity_id") or ""),
    ))
    activity_id = str(latest_row.get("_activity_id") or "")
    activity_rows = [row for row in rows if str(row.get("_activity_id") or "") == activity_id]
    summary = {
        "activity_id": activity_id,
        "agreement_id": agreement_id,
        "committed_at": latest_row.get("_committed_at"),
        "linked_dataset_count": len({str(row.get("metadata_table_key") or "") for row in activity_rows}),
    }
    return summary, _deduplicate_memberships(activity_rows)


def _deduplicate_memberships(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return one membership row per logical dataset identity."""
    by_key: dict[str, dict[str, Any]] = {}
    for row in rows:
        key = str(row.get("metadata_table_key") or "").strip()
        if key and key not in by_key:
            by_key[key] = row
    return [by_key[key] for key in sorted(by_key)]


def _append_inventory(
    *,
    membership_rows: list[dict[str, Any]],
    target: str,
    schema: str | None,
    spark_session: Any,
    context: dict[str, Any],
) -> None:
    """Append one complete immutable inventory under shared audit fields."""
    registry = metadata_table_schema_registry()
    membership_frame = spark_session.createDataFrame(
        [coerce_metadata_row_types(CONTRACT_TABLE, row) for row in membership_rows],
        schema=registry[CONTRACT_TABLE],
    )
    write_lakehouse_table_core(
        membership_frame, CONTRACT_TABLE, target=target, schema=schema,
        mode="append", context=context,
    )


def widget_register_data_contract(
    *,
    agreement: dict[str, Any] | None = None,
    agreement_id: str | None = None,
    metadata_ids: Sequence[str] | None = None,
    target: str = "metadata",
    schema: str | None = None,
    spark_session=None,
    context=None,
):
    """Manage an immutable snapshot inventory for one Data Agreement.

    Parameters
    ----------
    agreement : dict, optional
        Agreement record or agreement-widget state used to resolve the
        canonical agreement ID and a readable label locally. When the supplied
        state exposes ``existing_record``, changing that selector reloads the
        latest inventory without rerunning the cell. The editor remains
        disabled while no saved agreement is selected.
    agreement_id : str, optional
        Explicit canonical agreement identity. A non-empty trimmed value takes
        precedence over ``agreement``.
    metadata_ids : sequence of str, optional
        Additional unsaved initial inventory identities. Valid active-
        environment identities extend the latest snapshot only in memory;
        unknown identities are reported and never written.
    target : str, default="metadata"
        Configured FabricStore target containing FabricOps metadata tables.
    schema : str, optional
        Metadata Lakehouse schema override.
    spark_session : object, optional
        Spark session override.
    context : object, optional
        Active FabricOps context override, normally created by
        ``00_env_config``.

    Returns
    -------
    dict
        Mutable inventory state containing ``latest_activity_id``,
        ``latest_committed_at``, editable membership identities,
        ``saved_activity_id``, ``get_rows``, ``get_snapshot``, and notebook
        controls under ``_controls``. Activity and commit values come directly
        from the standard FabricOps audit fields rather than dedicated schema
        columns.

    Raises
    ------
    ValueError
        If no valid agreement ID can be resolved.
    TypeError
        If ``metadata_ids`` is not a non-string sequence.

    Notes
    -----
    This is an immutable snapshot-based inventory of logical datasets linked
    to a Data Agreement. Each explicit save builds the FabricOps audit fields
    once and appends the complete current membership list. ``_activity_id``
    groups the save and ``_committed_at`` orders saves, while the widget displays
    only the latest inventory. Historical rows are never updated or deleted.
    Catalogue discovery is restricted to the active environment, but logical
    ``metadata_table_key`` membership remains environment-independent.
    An unsaved agreement draft cannot create an inventory snapshot; select an
    existing agreement or save the new agreement first.

    Examples
    --------
    >>> contract_state = widget_register_data_contract(
    ...     agreement=agreement_state,
    ...     target="metadata",
    ...     schema=METADATA_SCHEMA,
    ...     spark_session=spark,
    ... )
    >>> contract_state = widget_register_data_contract(
    ...     agreement_id="agreement-123",
    ...     metadata_ids=["table-key-1", "table-key-2"],
    ...     target="metadata",
    ...     schema=METADATA_SCHEMA,
    ...     spark_session=spark,
    ... )

    See Also
    --------
    widget_render_data_agreement
    widget_view_agreement_catalogue

    """
    resolved_agreement_id, agreement_label = _agreement_details(agreement, agreement_id)
    initial_ids = _normalize_initial_ids(metadata_ids)
    try:
        widgets = require_ipywidgets()
    except ModuleNotFoundError as exc:
        message = str(exc)
        print(f"Data Contract inventory unavailable: {message}")
        state: dict[str, Any] = {
            "agreement_id": resolved_agreement_id, "agreement_label": agreement_label,
            "environment_name": None, "latest_activity_id": None,
            "latest_committed_at": None, "available_metadata_ids": [],
            "inventory_metadata_ids": [], "inventory_count": 0,
            "unknown_initial_metadata_ids": initial_ids, "has_unsaved_changes": False,
            "saved_activity_id": None, "saved_metadata_ids": [], "error": message,
            "_controls": {},
        }
        state["get_rows"] = lambda: []
        state["get_snapshot"] = lambda: {"header": None, "memberships": []}
        return state

    config, env, resolved = resolve_fabric_context(context=context)
    spark_session = get_spark_session(spark_session)
    runtime_context = {"config": config, "env": env, **(resolved or {})}
    catalogue = read_lakehouse_table_core(
        CATALOGUE_TABLE, target=target, schema=schema,
        spark_session=spark_session, context=runtime_context,
    )
    catalogue_rows = _latest_catalogue_rows(catalogue, env)
    rows_by_id = {row["metadata_table_key"]: row for row in catalogue_rows}
    all_options = _dataset_options(catalogue_rows)
    option_by_id = {key: label for label, key in all_options}
    memberships = read_lakehouse_table_core(
        CONTRACT_TABLE, target=target, schema=schema,
        spark_session=spark_session, context=runtime_context,
    )
    latest_summary, latest_rows = (
        _latest_inventory(memberships, resolved_agreement_id)
        if resolved_agreement_id else (None, [])
    )
    latest_activity_id = str((latest_summary or {}).get("activity_id") or "") or None
    saved_ids = [str(row["metadata_table_key"]) for row in latest_rows]
    valid_initial_ids = [key for key in initial_ids if key in rows_by_id]
    inventory_ids = (
        list(dict.fromkeys([*saved_ids, *valid_initial_ids]))
        if resolved_agreement_id else []
    )
    unknown_ids = [key for key in initial_ids if key not in rows_by_id]

    search = widgets.Text(value="", placeholder="Search catalogue...", **widget_common(widgets, "Search catalogue"))
    available = widgets.Select(options=[], **widget_common(widgets, "Add datasets"))
    add = widgets.Button(description="Add selected dataset")
    inventory = widgets.Select(options=[], **widget_common(widgets, "Existing inventory"))
    remove = widgets.Button(description="Remove selected dataset")
    save = widgets.Button(description="Save inventory", button_style="primary")
    summary = widgets.HTML(value="")
    status = widgets.HTML(value="")
    agreement_text = widgets.HTML(value=f"<b>Agreement:</b> {html.escape(agreement_label or 'Select an agreement')}")
    environment_text = widgets.HTML(value=f"<b>Environment:</b> {html.escape(env)}")

    state: dict[str, Any] = {
        "agreement_id": resolved_agreement_id or None, "agreement_label": agreement_label,
        "environment_name": env, "latest_activity_id": latest_activity_id,
        "latest_committed_at": (latest_summary or {}).get("committed_at"),
        "available_metadata_ids": [key for _label, key in all_options],
        "inventory_metadata_ids": inventory_ids, "inventory_count": len(inventory_ids),
        "unknown_initial_metadata_ids": unknown_ids,
        "has_unsaved_changes": inventory_ids != saved_ids,
        "saved_activity_id": None, "saved_metadata_ids": [],
    }

    def readable_label(key: str) -> str:
        return option_by_id.get(key, f"Unavailable catalogue dataset — {_short_key(key)}")

    def refresh_controls(*_args: Any) -> None:
        current = list(state["inventory_metadata_ids"])
        current_set = set(current)
        inventory.options = [(readable_label(key), key) for key in current]
        query = str(search.value or "").strip().casefold()
        choices = [
            option for option in all_options
            if option[1] not in current_set and (not query or query in option[0].casefold())
        ]
        available.options = choices
        available.value = None
        add.disabled = True
        state["inventory_count"] = len(current)
        state["has_unsaved_changes"] = current != saved_ids
        summary.value = (
            f"<b>Current inventory count:</b> {len(current)}<br>"
            f"<b>Unsaved changes:</b> {'Yes' if state['has_unsaved_changes'] else 'No'}"
        )

    def set_editor_enabled(enabled: bool) -> None:
        for control in (search, available, inventory, remove, save):
            control.disabled = not enabled
        add.disabled = not enabled or available.value is None

    def load_agreement(selected_id: str) -> None:
        nonlocal latest_summary
        selected_id = str(selected_id or "").strip()
        if not selected_id:
            latest_summary = None
            latest_rows.clear()
            saved_ids.clear()
            state.update(
                agreement_id=None, agreement_label="", latest_activity_id=None,
                latest_committed_at=None, inventory_metadata_ids=[],
                inventory_count=0, has_unsaved_changes=False,
                saved_activity_id=None, saved_metadata_ids=[],
            )
            agreement_text.value = "<b>Agreement:</b> Select or save an agreement first"
            status.value = "Select an existing agreement or save a new agreement before maintaining its dataset inventory."
            set_editor_enabled(False)
            refresh_controls()
            return
        selected_row = (agreement or {}).get("existing_records_by_id", {}).get(selected_id, {})
        selected_label = str(selected_row.get("agreement_name") or selected_id).strip() or selected_id
        latest_summary, loaded_rows = _latest_inventory(memberships, selected_id)
        activity_id = str((latest_summary or {}).get("activity_id") or "") or None
        latest_rows[:] = loaded_rows
        saved_ids[:] = [str(row["metadata_table_key"]) for row in loaded_rows]
        valid_initial = [key for key in initial_ids if key in rows_by_id]
        current = list(dict.fromkeys([*saved_ids, *valid_initial]))
        state.update(
            agreement_id=selected_id, agreement_label=selected_label,
            latest_activity_id=activity_id,
            latest_committed_at=(latest_summary or {}).get("committed_at"),
            inventory_metadata_ids=current, inventory_count=len(current),
            has_unsaved_changes=current != saved_ids,
            saved_activity_id=None, saved_metadata_ids=[],
        )
        agreement_text.value = f"<b>Agreement:</b> {html.escape(selected_label)}"
        status.value = ""
        set_editor_enabled(True)
        refresh_controls()

    def add_selected(_button: Any = None) -> None:
        key = str(available.value or "")
        if key and key in rows_by_id and key not in state["inventory_metadata_ids"]:
            state["inventory_metadata_ids"].append(key)
        refresh_controls()

    def select_available(change: dict[str, Any]) -> None:
        if change.get("name") == "value":
            add.disabled = not bool(state.get("agreement_id") and change.get("new"))

    def remove_selected(_button: Any = None) -> None:
        key = str(inventory.value or "")
        state["inventory_metadata_ids"] = [
            value for value in state["inventory_metadata_ids"] if value != key
        ]
        refresh_controls()

    def get_rows() -> list[dict[str, Any]]:
        frame = read_lakehouse_table_core(
            CONTRACT_TABLE, target=target, schema=schema,
            spark_session=spark_session, context=runtime_context,
        )
        _summary, rows = _latest_inventory(frame, str(state.get("agreement_id") or ""))
        return rows

    def get_snapshot() -> dict[str, Any]:
        if not state["latest_activity_id"]:
            return {"header": None, "memberships": []}
        frame = read_lakehouse_table_core(
            CONTRACT_TABLE, target=target, schema=schema,
            spark_session=spark_session, context=runtime_context,
        )
        summary, rows = _latest_inventory(frame, str(state["agreement_id"]))
        return {"header": summary, "memberships": rows}

    def save_inventory(_button: Any = None) -> None:
        nonlocal latest_summary
        if not state.get("agreement_id"):
            status.value = "Select or save an agreement before saving an inventory."
            return
        current = list(dict.fromkeys(state["inventory_metadata_ids"]))
        current = [key for key in current if key in rows_by_id or key in saved_ids]
        if not current:
            status.value = "An inventory save must contain at least one logical dataset."
            return
        audit = build_runtime_audit_fields(config=config, env=env, runtime_context=runtime_context)
        activity_id = str(audit["_activity_id"])
        saved_at = audit["_committed_at"]
        rows = [{
            "agreement_id": state["agreement_id"],
            "metadata_table_key": key,
            "schema_fingerprint": str(rows_by_id.get(key, {}).get("schema_fingerprint") or next(
                (row.get("schema_fingerprint") for row in latest_rows if row.get("metadata_table_key") == key), ""
            )),
            **audit,
        } for key in current]
        _append_inventory(
            membership_rows=rows, target=target, schema=schema,
            spark_session=spark_session, context=runtime_context,
        )
        latest_summary = {
            "activity_id": activity_id, "agreement_id": state["agreement_id"],
            "committed_at": saved_at, "linked_dataset_count": len(current),
        }
        latest_rows[:] = rows
        saved_ids[:] = current
        state.update(
            latest_activity_id=activity_id, latest_committed_at=saved_at,
            inventory_metadata_ids=list(current), inventory_count=len(current),
            has_unsaved_changes=False, saved_activity_id=activity_id,
            saved_metadata_ids=list(current),
        )
        refresh_controls()
        status.value = f"Saved inventory with {len(current)} logical datasets."

    search.observe(refresh_controls, names="value")
    available.observe(select_available, names="value")
    add.on_click(add_selected)
    remove.on_click(remove_selected)
    save.on_click(save_inventory)
    agreement_selector = (agreement or {}).get("existing_record")
    if agreement_selector is not None and hasattr(agreement_selector, "observe"):
        agreement_selector.observe(
            lambda change: load_agreement(str(change.get("new") or ""))
            if change.get("name") == "value" else None,
            names="value",
        )
    state["get_rows"] = get_rows
    state["get_snapshot"] = get_snapshot
    state["_controls"] = {
        "agreement": agreement_text, "environment": environment_text,
        "summary": summary, "inventory": inventory, "remove": remove,
        "search": search, "available": available, "add": add, "save": save,
        "status": status,
    }
    refresh_controls()
    set_editor_enabled(bool(state["agreement_id"]))
    if not state["agreement_id"]:
        status.value = "Select an existing agreement or save a new agreement before maintaining its dataset inventory."
    elif not all_options:
        status.value = (
            "No registered datasets are available in the active environment.<br>"
            "Historical inventory memberships remain available for removal or preservation."
        )

    _display_widget(widgets.VBox([
        widgets.HTML("<h2>Dataset inventory</h2>"), agreement_text, environment_text,
        summary, inventory, remove, search, available, add, save, status,
    ]))
    return state
