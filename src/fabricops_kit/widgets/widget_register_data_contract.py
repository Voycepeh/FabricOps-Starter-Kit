"""Public widget entrypoint for registering logical Data Contract membership."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime
import html
import hashlib
from typing import Any

from fabricops_kit.config.audit import build_runtime_audit_fields
from fabricops_kit.config.metadata_schemas import (
    coerce_metadata_row_types,
    metadata_table_schema_registry,
)
from fabricops_kit.config.shared import get_current_audit_timestamp, resolve_fabric_context
from fabricops_kit.io.shared import (
    get_spark_session,
    read_lakehouse_table_core,
    resolve_configured_lakehouse_table,
)
from fabricops_kit.widgets.shared import require_ipywidgets, widget_common


CONTRACT_TABLE = "METADATA_DATA_CONTRACT"
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
    """Trim and de-duplicate initial metadata identities in caller order."""
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
    """Return one deterministic, latest observation per active-environment key."""
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
        candidate = (
            _commit_sort_value(row.get("_committed_at")),
            str(row.get("schema_fingerprint") or ""),
            str(row.get("store_type") or ""),
            str(row.get("layer") or ""),
            str(row.get("schema_name") or ""),
            str(row.get("table_name") or ""),
        )
        current = latest.get(key)
        if current is None:
            latest[key] = row
            continue
        current_rank = (
            _commit_sort_value(current.get("_committed_at")),
            str(current.get("schema_fingerprint") or ""),
            str(current.get("store_type") or ""),
            str(current.get("layer") or ""),
            str(current.get("schema_name") or ""),
            str(current.get("table_name") or ""),
        )
        if candidate > current_rank:
            latest[key] = row
    return [dict(latest[key], metadata_table_key=key) for key in sorted(latest)]


def _base_dataset_label(row: dict[str, Any]) -> str:
    """Build a readable physical-coordinate label without empty segments."""
    return " / ".join(
        str(row.get(field) or "").strip()
        for field in ("layer", "schema_name", "table_name")
        if str(row.get(field) or "").strip()
    )


def _dataset_options(rows: list[dict[str, Any]]) -> list[tuple[str, str]]:
    """Return uniquely labelled options whose values remain canonical keys."""
    base_counts: dict[str, int] = {}
    for row in rows:
        base = _base_dataset_label(row)
        base_counts[base] = base_counts.get(base, 0) + 1
    provisional: list[tuple[str, str, dict[str, Any]]] = []
    for row in rows:
        base = _base_dataset_label(row)
        label = base
        if base_counts[base] > 1:
            store = str(row.get("store_type") or "").strip()
            label = f"{store} — {base}" if store else base
        provisional.append((label, str(row["metadata_table_key"]), row))
    label_counts: dict[str, int] = {}
    for label, _key, _row in provisional:
        label_counts[label] = label_counts.get(label, 0) + 1
    options = [
        (
            f"{label} — {_short_key(key)}" if label_counts[label] > 1 else label,
            key,
        )
        for label, key, _row in provisional
    ]
    return sorted(options, key=lambda option: (option[0].casefold(), option[1]))


def _short_key(key: str) -> str:
    """Return a deterministic compact identity for final label disambiguation."""
    return key if len(key) <= 12 else f"{key[:8]}…{key[-4:]}"


def _contract_id(agreement_id: str, metadata_table_key: str) -> str:
    """Return the deterministic identity for one logical agreement membership."""
    value = f"{agreement_id}\n{metadata_table_key}".encode()
    return hashlib.sha256(value).hexdigest()


def _agreement_contract_rows(contracts, agreement_id: str) -> list[dict[str, Any]]:
    """Collect only contract rows belonging to one agreement."""
    from pyspark.sql import functions as F

    return [
        row.asDict(recursive=True)
        for row in contracts.filter(F.col("agreement_id") == agreement_id).collect()
    ]


def _latest_rows_by_metadata_key(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """Return one deterministic latest row for each logical dataset key."""
    latest: dict[str, dict[str, Any]] = {}
    for row in rows:
        key = str(row.get("metadata_table_key") or "").strip()
        if not key:
            continue
        rank = (_commit_sort_value(row.get("_committed_at")), str(row.get("contract_id") or ""))
        current = latest.get(key)
        if current is None or rank > (
            _commit_sort_value(current.get("_committed_at")), str(current.get("contract_id") or "")
        ):
            latest[key] = row
    return latest


def _replace_agreement_drafts(
    *,
    draft_rows: list[dict[str, Any]],
    agreement_id: str,
    target: str,
    schema: str | None,
    spark_session: Any,
    context: dict[str, Any],
) -> None:
    """Transactionally merge only one agreement's draft contract inventory."""
    try:
        from delta.tables import DeltaTable
    except Exception as exc:  # pragma: no cover - depends on Fabric/Delta runtime
        raise RuntimeError(
            "Delta Lake support is required to save a Data Contract inventory safely."
        ) from exc
    _store, _table, _schema, path = resolve_configured_lakehouse_table(
        target, CONTRACT_TABLE, schema, context=context,
    )
    frame = spark_session.createDataFrame(
        [coerce_metadata_row_types(CONTRACT_TABLE, row) for row in draft_rows],
        schema=metadata_table_schema_registry()[CONTRACT_TABLE],
    )
    agreement_literal = agreement_id.replace("'", "''")
    (
        DeltaTable.forPath(spark_session, path)
        .alias("target")
        .merge(
            frame.alias("source"),
            "target.contract_id = source.contract_id",
        )
        .whenNotMatchedInsertAll()
        .whenNotMatchedBySourceDelete(
            condition=(
                f"target.agreement_id = '{agreement_literal}' "
                "AND lower(target.contract_status) = 'draft'"
            )
        )
        .execute()
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
    """Manage an agreement's authoritative logical dataset inventory.

    Parameters
    ----------
    agreement : dict, optional
        Data Agreement record or agreement-widget state. Its selected
        ``agreement_id`` is used when no non-empty explicit ID is supplied;
        readable agreement information is reused for display without querying
        ``METADATA_DATA_AGREEMENT``.
    agreement_id : str, optional
        Explicit canonical agreement identity. Surrounding whitespace is
        removed and a non-empty value takes precedence over ``agreement``.
    metadata_ids : sequence of str, optional
        Optional additional initial selector values. Values are trimmed and
        de-duplicated, then merged with persisted draft memberships. Unknown or
        inactive-environment identities are reported but cannot be written.
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
        Mutable inventory state containing agreement and environment details,
        existing draft and non-draft memberships, available, selected, pending,
        unknown, and saved metadata identities, saved contract IDs, draft
        status, ``get_rows``, and useful controls under ``_controls``.

    Raises
    ------
    ValueError
        If neither the explicit value nor the supplied agreement state resolves
        a valid agreement ID.
    TypeError
        If ``metadata_ids`` is not a non-string sequence.

    Notes
    -----
    On opening, the widget reads the agreement's current contract inventory and
    preselects every existing draft membership. Non-draft memberships remain
    visible but locked outside the draft editor. Catalogue discovery is
    restricted to the active environment, while the saved relationship is
    environment-independent: one agreement links to each logical
    ``metadata_table_key``. Saving narrowly replaces only this agreement's
    draft rows, preserving selected existing rows, all non-draft rows, and all
    other agreements. New memberships use minimal version ``1`` draft values,
    the latest active-environment schema fingerprint, and normal runtime audit
    fields. Review, approval, promotion, environment comparison, and pipeline
    inspection are outside this inventory editor.

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
        print(f"Data Contract registration unavailable: {message}")
        state: dict[str, Any] = {
            "agreement_id": resolved_agreement_id,
            "agreement_label": agreement_label,
            "environment_name": None,
            "available_metadata_ids": [],
            "existing_draft_metadata_ids": [],
            "existing_non_draft_metadata_ids": [],
            "selected_metadata_ids": [],
            "pending_add_metadata_ids": [],
            "pending_remove_metadata_ids": [],
            "unknown_initial_metadata_ids": initial_ids,
            "saved_contract_ids": [],
            "saved_metadata_ids": [],
            "contract_status": "draft",
            "error": message,
            "_controls": {},
        }
        state["get_rows"] = lambda: []
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
    options = _dataset_options(catalogue_rows)
    available_ids = [key for _label, key in options]
    contracts = read_lakehouse_table_core(
        CONTRACT_TABLE, target=target, schema=schema,
        spark_session=spark_session, context=runtime_context,
    )
    agreement_rows = _agreement_contract_rows(contracts, resolved_agreement_id)
    draft_rows = [
        row for row in agreement_rows
        if str(row.get("contract_status") or "").strip().lower() == "draft"
    ]
    non_draft_rows = [
        row for row in agreement_rows
        if str(row.get("contract_status") or "").strip().lower() != "draft"
    ]
    existing_drafts_by_id = _latest_rows_by_metadata_key(draft_rows)
    existing_draft_ids = sorted(existing_drafts_by_id)
    existing_non_draft_ids = sorted({
        str(row.get("metadata_table_key") or "").strip()
        for row in non_draft_rows
        if str(row.get("metadata_table_key") or "").strip()
    })
    locked_ids = set(existing_non_draft_ids)
    additional_ids = [key for key in initial_ids if key in rows_by_id and key not in locked_ids]
    selected_ids = list(dict.fromkeys([*existing_draft_ids, *additional_ids]))
    unknown_ids = [key for key in initial_ids if key not in rows_by_id]

    option_by_id = {key: label for label, key in options}
    editor_options = [option for option in options if option[1] not in locked_ids]
    for key in existing_draft_ids:
        if key not in option_by_id:
            editor_options.append((f"Unavailable catalogue dataset — {_short_key(key)}", key))
    editor_options.sort(key=lambda option: (option[0].casefold(), option[1]))

    search = widgets.Text(value="", placeholder="Search datasets...", **widget_common(widgets, "Search"))
    datasets = widgets.SelectMultiple(
        options=editor_options, value=tuple(selected_ids),
        **widget_common(widgets, "Available datasets"),
    )
    save = widgets.Button(description="Save inventory", button_style="primary")
    status = widgets.HTML(value="")
    agreement_text = widgets.HTML(value=f"<b>Agreement:</b> {html.escape(agreement_label)}")
    environment_text = widgets.HTML(value=f"<b>Environment:</b> {html.escape(env)}")
    lifecycle_text = widgets.HTML(value="<b>Status:</b> Draft")
    inventory = widgets.HTML(value="")
    pending = widgets.HTML(value="")
    if not options:
        status.value = (
            "No registered datasets are available in the active environment.<br>"
            "Run the Development pipeline registration before creating a Data Contract."
        )

    state = {
        "agreement_id": resolved_agreement_id,
        "agreement_label": agreement_label,
        "environment_name": env,
        "available_metadata_ids": available_ids,
        "existing_draft_metadata_ids": existing_draft_ids,
        "existing_non_draft_metadata_ids": existing_non_draft_ids,
        "selected_metadata_ids": list(selected_ids),
        "pending_add_metadata_ids": [],
        "pending_remove_metadata_ids": [],
        "unknown_initial_metadata_ids": unknown_ids,
        "saved_contract_ids": [],
        "saved_metadata_ids": [],
        "contract_status": "draft",
    }

    def readable_label(key: str) -> str:
        return option_by_id.get(key, f"Unavailable catalogue dataset — {_short_key(key)}")

    def escaped_list(keys: list[str]) -> str:
        return ", ".join(html.escape(readable_label(key)) for key in keys) or "None"

    def non_draft_inventory_text() -> str:
        values = [
            f"{html.escape(readable_label(str(row.get('metadata_table_key') or '').strip()))} "
            f"({html.escape(str(row.get('contract_status') or 'non-draft').strip())})"
            for row in non_draft_rows
        ]
        return ", ".join(values) or "None"

    def refresh_inventory() -> None:
        selected = list(state["selected_metadata_ids"])
        pending_add = sorted(set(selected) - set(existing_draft_ids))
        pending_remove = sorted(set(existing_draft_ids) - set(selected))
        state["pending_add_metadata_ids"] = pending_add
        state["pending_remove_metadata_ids"] = pending_remove
        inventory.value = (
            f"<b>Currently linked:</b> {len(set(existing_draft_ids) | set(existing_non_draft_ids))}<br>"
            f"<b>Draft linked datasets:</b> {len(existing_draft_ids)} — {escaped_list(existing_draft_ids)}<br>"
            f"<b>Non-draft linked datasets:</b> {len(existing_non_draft_ids)} — "
            f"{non_draft_inventory_text()}"
        )
        pending.value = (
            f"<b>Current selected draft inventory:</b> {escaped_list(selected)}<br>"
            f"<b>Pending additions:</b> {escaped_list(pending_add)}<br>"
            f"<b>Pending removals:</b> {escaped_list(pending_remove)}"
        )

    def get_rows() -> list[dict[str, Any]]:
        """Return current persisted rows for this agreement."""
        from pyspark.sql import functions as F

        frame = read_lakehouse_table_core(
            CONTRACT_TABLE, target=target, schema=schema,
            spark_session=spark_session, context=runtime_context,
        )
        return [
            row.asDict(recursive=True)
            for row in frame.filter(F.col("agreement_id") == resolved_agreement_id).collect()
        ]

    def refresh_options(change: dict[str, Any] | None = None) -> None:
        if change is not None and change.get("name") != "value":
            return
        query = str(search.value or "").strip().casefold()
        current = tuple(datasets.value or ())
        filtered = [
            option for option in editor_options
            if option[1] in current or not query or query in option[0].casefold()
        ]
        datasets.options = filtered
        visible = {value for _label, value in filtered}
        datasets.value = tuple(value for value in current if value in visible)

    def save_contract(_button: Any = None) -> None:
        selectable_ids = set(rows_by_id) | set(existing_draft_ids)
        selected = [str(value) for value in (datasets.value or ()) if str(value) in selectable_ids]
        state["selected_metadata_ids"] = selected
        new_rows = []
        audit: dict[str, Any] | None = None
        effective_from = None
        for key in selected:
            if key in existing_drafts_by_id:
                new_rows.append(existing_drafts_by_id[key])
                continue
            if audit is None:
                audit = build_runtime_audit_fields(
                    config=config, env=env, runtime_context=runtime_context,
                )
                effective_from = datetime.fromisoformat(
                    get_current_audit_timestamp(config=config, drop_microseconds=False)
                ).date()
            new_rows.append({
                "contract_id": _contract_id(resolved_agreement_id, key),
                "agreement_id": resolved_agreement_id,
                "metadata_table_key": key,
                "schema_fingerprint": str(rows_by_id[key].get("schema_fingerprint") or ""),
                "contract_version": "1",
                "contract_status": "draft",
                "effective_from": effective_from,
                "effective_to": None,
                "contract_payload_json": "{}",
                **audit,
            })
        _replace_agreement_drafts(
            draft_rows=new_rows,
            agreement_id=resolved_agreement_id,
            target=target,
            schema=schema,
            spark_session=spark_session,
            context=runtime_context,
        )
        state["saved_metadata_ids"] = selected
        state["saved_contract_ids"] = [str(row["contract_id"]) for row in new_rows]
        existing_draft_ids[:] = selected
        existing_drafts_by_id.clear()
        existing_drafts_by_id.update({str(row["metadata_table_key"]): row for row in new_rows})
        state["existing_draft_metadata_ids"] = list(selected)
        refresh_inventory()
        status.value = f"Saved an inventory of {len(selected)} logical datasets for this agreement."

    def select_datasets(change: dict[str, Any]) -> None:
        if change.get("name") != "value":
            return
        state["selected_metadata_ids"] = list(change.get("new") or ())
        refresh_inventory()

    search.observe(refresh_options, names="value")
    datasets.observe(select_datasets, names="value")
    save.on_click(save_contract)
    state["get_rows"] = get_rows
    state["_controls"] = {
        "agreement": agreement_text, "environment": environment_text,
        "search": search, "datasets": datasets, "inventory": inventory,
        "pending": pending, "save": save, "status": status,
    }
    refresh_inventory()

    from IPython import display as ip

    ip.display(widgets.VBox([
        widgets.HTML("<h2>Dataset inventory</h2>"), agreement_text,
        environment_text, inventory, search, datasets, pending,
        lifecycle_text, save, status,
    ]))
    return state
