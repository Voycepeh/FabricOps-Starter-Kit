"""Public widget entrypoint for immutable Data Contract inventories."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime
import html
from typing import Any
import uuid

from fabricops_kit.config.audit import build_runtime_audit_fields
from fabricops_kit.config.metadata_schemas import coerce_metadata_row_types, metadata_table_schema_registry
from fabricops_kit.config.shared import resolve_fabric_context
from fabricops_kit.io.shared import get_spark_session, read_lakehouse_table_core, write_lakehouse_table_core
from fabricops_kit.widgets.shared import require_ipywidgets, widget_common


CONTRACT_TABLE = "METADATA_DATA_CONTRACT"
SNAPSHOT_TABLE = "METADATA_DATA_CONTRACT_SNAPSHOT"
CATALOGUE_TABLE = "METADATA_DATA_CATALOGUE"


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


def _latest_snapshot_header(headers, agreement_id: str) -> dict[str, Any] | None:
    """Return the latest immutable snapshot header for one agreement."""
    from pyspark.sql import functions as F

    rows = [
        row.asDict(recursive=True)
        for row in headers.filter(F.col("agreement_id") == agreement_id).collect()
    ]
    if not rows:
        return None
    return max(rows, key=lambda row: (
        _commit_sort_value(row.get("snapshot_saved_at")),
        str(row.get("contract_snapshot_id") or ""),
    ))


def _snapshot_membership_rows(memberships, snapshot_id: str | None) -> list[dict[str, Any]]:
    """Return de-duplicated membership rows for exactly one snapshot."""
    if not snapshot_id:
        return []
    from pyspark.sql import functions as F

    rows = [
        row.asDict(recursive=True)
        for row in memberships.filter(F.col("contract_snapshot_id") == snapshot_id).collect()
    ]
    by_key: dict[str, dict[str, Any]] = {}
    for row in rows:
        key = str(row.get("metadata_table_key") or "").strip()
        if key and key not in by_key:
            by_key[key] = row
    return [by_key[key] for key in sorted(by_key)]


def _append_snapshot(
    *,
    snapshot_row: dict[str, Any],
    membership_rows: list[dict[str, Any]],
    target: str,
    schema: str | None,
    spark_session: Any,
    context: dict[str, Any],
) -> None:
    """Append immutable membership rows and then their snapshot header."""
    registry = metadata_table_schema_registry()
    if membership_rows:
        membership_frame = spark_session.createDataFrame(
            [coerce_metadata_row_types(CONTRACT_TABLE, row) for row in membership_rows],
            schema=registry[CONTRACT_TABLE],
        )
        write_lakehouse_table_core(
            membership_frame, CONTRACT_TABLE, target=target, schema=schema,
            mode="append", context=context,
        )
    header_frame = spark_session.createDataFrame(
        [coerce_metadata_row_types(SNAPSHOT_TABLE, snapshot_row)],
        schema=registry[SNAPSHOT_TABLE],
    )
    write_lakehouse_table_core(
        header_frame, SNAPSHOT_TABLE, target=target, schema=schema,
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
        canonical agreement ID and a readable label locally.
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
        Mutable snapshot-oriented state containing the latest snapshot,
        editable inventory, save result, ``get_rows``, ``get_snapshot``, and
        notebook controls under ``_controls``.

    Raises
    ------
    ValueError
        If no valid agreement ID can be resolved.
    TypeError
        If ``metadata_ids`` is not a non-string sequence.

    Notes
    -----
    This is an immutable snapshot-based inventory of logical datasets linked
    to a Data Agreement. Each explicit save appends one snapshot header and the
    complete current membership list, while the widget displays only the
    latest saved snapshot. Historical snapshots are never updated or deleted.
    Catalogue discovery is restricted to the active environment, but logical
    ``metadata_table_key`` membership remains environment-independent.

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
    widget_view_data_contract

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
            "environment_name": None, "latest_snapshot_id": None,
            "latest_snapshot_saved_at": None, "available_metadata_ids": [],
            "inventory_metadata_ids": [], "inventory_count": 0,
            "unknown_initial_metadata_ids": initial_ids, "has_unsaved_changes": False,
            "saved_snapshot_id": None, "saved_metadata_ids": [], "error": message,
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
    headers = read_lakehouse_table_core(
        SNAPSHOT_TABLE, target=target, schema=schema,
        spark_session=spark_session, context=runtime_context,
    )
    memberships = read_lakehouse_table_core(
        CONTRACT_TABLE, target=target, schema=schema,
        spark_session=spark_session, context=runtime_context,
    )
    latest_header = _latest_snapshot_header(headers, resolved_agreement_id)
    latest_snapshot_id = str((latest_header or {}).get("contract_snapshot_id") or "") or None
    latest_rows = _snapshot_membership_rows(memberships, latest_snapshot_id)
    saved_ids = [str(row["metadata_table_key"]) for row in latest_rows]
    valid_initial_ids = [key for key in initial_ids if key in rows_by_id]
    inventory_ids = list(dict.fromkeys([*saved_ids, *valid_initial_ids]))
    unknown_ids = [key for key in initial_ids if key not in rows_by_id]

    search = widgets.Text(value="", placeholder="Search catalogue...", **widget_common(widgets, "Search catalogue"))
    available = widgets.Select(options=[], **widget_common(widgets, "Add datasets"))
    add = widgets.Button(description="Add selected dataset")
    inventory = widgets.Select(options=[], **widget_common(widgets, "Existing inventory"))
    remove = widgets.Button(description="Remove selected dataset")
    save = widgets.Button(description="Save inventory", button_style="primary")
    summary = widgets.HTML(value="")
    status = widgets.HTML(value="")
    agreement_text = widgets.HTML(value=f"<b>Agreement:</b> {html.escape(agreement_label)}")
    environment_text = widgets.HTML(value=f"<b>Environment:</b> {html.escape(env)}")

    state: dict[str, Any] = {
        "agreement_id": resolved_agreement_id, "agreement_label": agreement_label,
        "environment_name": env, "latest_snapshot_id": latest_snapshot_id,
        "latest_snapshot_saved_at": (latest_header or {}).get("snapshot_saved_at"),
        "available_metadata_ids": [key for _label, key in all_options],
        "inventory_metadata_ids": inventory_ids, "inventory_count": len(inventory_ids),
        "unknown_initial_metadata_ids": unknown_ids,
        "has_unsaved_changes": inventory_ids != saved_ids,
        "saved_snapshot_id": None, "saved_metadata_ids": [],
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
        state["inventory_count"] = len(current)
        state["has_unsaved_changes"] = current != saved_ids
        summary.value = (
            f"<b>Current inventory count:</b> {len(current)}<br>"
            f"<b>Unsaved changes:</b> {'Yes' if state['has_unsaved_changes'] else 'No'}"
        )

    def add_selected(_button: Any = None) -> None:
        key = str(available.value or "")
        if key and key in rows_by_id and key not in state["inventory_metadata_ids"]:
            state["inventory_metadata_ids"].append(key)
        refresh_controls()

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
        return _snapshot_membership_rows(frame, state["latest_snapshot_id"])

    def get_snapshot() -> dict[str, Any]:
        if not state["latest_snapshot_id"]:
            return {"header": None, "memberships": []}
        header_frame = read_lakehouse_table_core(
            SNAPSHOT_TABLE, target=target, schema=schema,
            spark_session=spark_session, context=runtime_context,
        )
        header = _latest_snapshot_header(header_frame, resolved_agreement_id)
        return {"header": header, "memberships": get_rows()}

    def save_inventory(_button: Any = None) -> None:
        nonlocal latest_header
        current = list(dict.fromkeys(state["inventory_metadata_ids"]))
        current = [key for key in current if key in rows_by_id or key in saved_ids]
        snapshot_id = str(uuid.uuid4())
        audit = build_runtime_audit_fields(config=config, env=env, runtime_context=runtime_context)
        saved_at = audit["_committed_at"]
        header_row = {
            "contract_snapshot_id": snapshot_id, "agreement_id": resolved_agreement_id,
            "snapshot_saved_at": saved_at, "linked_dataset_count": len(current), **audit,
        }
        rows = [{
            "contract_snapshot_id": snapshot_id, "agreement_id": resolved_agreement_id,
            "metadata_table_key": key,
            "schema_fingerprint": str(rows_by_id.get(key, {}).get("schema_fingerprint") or next(
                (row.get("schema_fingerprint") for row in latest_rows if row.get("metadata_table_key") == key), ""
            )),
            **audit,
        } for key in current]
        _append_snapshot(
            snapshot_row=header_row, membership_rows=rows, target=target, schema=schema,
            spark_session=spark_session, context=runtime_context,
        )
        latest_header = header_row
        latest_rows[:] = rows
        saved_ids[:] = current
        state.update(
            latest_snapshot_id=snapshot_id, latest_snapshot_saved_at=saved_at,
            inventory_metadata_ids=list(current), inventory_count=len(current),
            has_unsaved_changes=False, saved_snapshot_id=snapshot_id,
            saved_metadata_ids=list(current),
        )
        refresh_controls()
        status.value = f"Saved inventory snapshot with {len(current)} logical datasets."

    search.observe(refresh_controls, names="value")
    add.on_click(add_selected)
    remove.on_click(remove_selected)
    save.on_click(save_inventory)
    state["get_rows"] = get_rows
    state["get_snapshot"] = get_snapshot
    state["_controls"] = {
        "agreement": agreement_text, "environment": environment_text,
        "summary": summary, "inventory": inventory, "remove": remove,
        "search": search, "available": available, "add": add, "save": save,
        "status": status,
    }
    refresh_controls()
    if not all_options:
        status.value = (
            "No registered datasets are available in the active environment.<br>"
            "Historical inventory memberships remain available for removal or preservation."
        )

    from IPython import display as ip

    ip.display(widgets.VBox([
        widgets.HTML("<h2>Dataset inventory</h2>"), agreement_text, environment_text,
        summary, inventory, remove, search, available, add, save, status,
    ]))
    return state
