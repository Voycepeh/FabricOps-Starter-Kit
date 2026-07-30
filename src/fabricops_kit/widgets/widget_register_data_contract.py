"""Public widget entrypoint for registering logical Data Contract membership."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime
import hashlib
from typing import Any

from fabricops_kit.config.audit import build_runtime_audit_fields
from fabricops_kit.config.metadata_schemas import (
    coerce_metadata_row_types,
    metadata_table_schema_registry,
)
from fabricops_kit.config.shared import get_current_audit_timestamp, resolve_fabric_context
from fabricops_kit.io.shared import get_spark_session, read_lakehouse_table_core, write_lakehouse_table_core
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
    """Return an environment-independent deterministic membership identity."""
    value = f"{agreement_id}\n{metadata_table_key}".encode()
    return hashlib.sha256(value).hexdigest()


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
    """Register an agreement's authoritative logical dataset membership.

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
        Initial selector values only. Values are trimmed and de-duplicated;
        unknown or inactive-environment identities are reported but cannot be
        selected or written.
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
        Mutable state containing agreement and environment details, available,
        selected, unknown, and saved metadata identities, saved contract IDs,
        draft status, ``get_rows``, and the ``datasets``, ``save``, and
        ``status`` controls under ``_controls``.

    Raises
    ------
    ValueError
        If neither the explicit value nor the supplied agreement state resolves
        a valid agreement ID.
    TypeError
        If ``metadata_ids`` is not a non-string sequence.

    Notes
    -----
    Catalogue discovery is restricted to the active environment, while the
    saved relationship is environment-independent: one agreement links once to
    each logical ``metadata_table_key``. Saving writes minimal version ``1``
    draft rows with the latest active-environment schema fingerprint and normal
    runtime audit fields. The selection is authoritative for this agreement:
    new memberships are inserted, selected draft memberships are preserved,
    and deselected draft memberships are removed. Rows for other agreements and
    non-draft rows are preserved. Review, approval, promotion, environment
    comparison, and pipeline inspection are outside this draft-only writer.

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
            "selected_metadata_ids": [],
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
    selected_ids = [key for key in initial_ids if key in rows_by_id]
    unknown_ids = [key for key in initial_ids if key not in rows_by_id]

    search = widgets.Text(value="", placeholder="Search datasets...", **widget_common(widgets, "Search"))
    datasets = widgets.SelectMultiple(
        options=options, value=tuple(selected_ids),
        **widget_common(widgets, "Datasets"),
    )
    save = widgets.Button(description="Save contract", button_style="primary")
    status = widgets.HTML(value="")
    agreement_text = widgets.HTML(value=f"<b>Agreement:</b> {agreement_label}")
    environment_text = widgets.HTML(value=f"<b>Environment:</b> {env}")
    lifecycle_text = widgets.HTML(value="<b>Status:</b> Draft")
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
        "selected_metadata_ids": list(selected_ids),
        "unknown_initial_metadata_ids": unknown_ids,
        "saved_contract_ids": [],
        "saved_metadata_ids": [],
        "contract_status": "draft",
    }

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
            option for option in options
            if option[1] in current or not query or query in option[0].casefold()
        ]
        datasets.options = filtered
        visible = {value for _label, value in filtered}
        datasets.value = tuple(value for value in current if value in visible)

    def save_contract(_button: Any = None) -> None:
        selected = [str(value) for value in (datasets.value or ()) if str(value) in rows_by_id]
        state["selected_metadata_ids"] = selected
        existing_frame = read_lakehouse_table_core(
            CONTRACT_TABLE, target=target, schema=schema,
            spark_session=spark_session, context=runtime_context,
        )
        existing = [row.asDict(recursive=True) for row in existing_frame.collect()]
        selected_set = set(selected)
        preserved = [
            row for row in existing
            if str(row.get("agreement_id") or "").strip() != resolved_agreement_id
            or str(row.get("contract_status") or "").strip().lower() != "draft"
        ]
        audit = build_runtime_audit_fields(
            config=config, env=env, runtime_context=runtime_context,
        )
        effective_from = datetime.fromisoformat(
            get_current_audit_timestamp(config=config, drop_microseconds=False)
        ).date()
        new_rows = []
        for key in selected:
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
        output_rows = [coerce_metadata_row_types(CONTRACT_TABLE, row) for row in [*preserved, *new_rows]]
        frame = spark_session.createDataFrame(
            output_rows,
            schema=metadata_table_schema_registry()[CONTRACT_TABLE],
        )
        write_lakehouse_table_core(
            frame, CONTRACT_TABLE, target=target, schema=schema, mode="overwrite",
            context=runtime_context,
        )
        saved_rows = [
            row for row in output_rows
            if str(row.get("agreement_id") or "").strip() == resolved_agreement_id
            and str(row.get("contract_status") or "").strip().lower() == "draft"
            and str(row.get("metadata_table_key") or "").strip() in selected_set
        ]
        state["saved_metadata_ids"] = selected
        state["saved_contract_ids"] = [str(row["contract_id"]) for row in saved_rows]
        status.value = f"Saved {len(selected)} logical datasets to this agreement."

    search.observe(refresh_options, names="value")
    datasets.observe(
        lambda change: state.update(selected_metadata_ids=list(change.get("new") or ()))
        if change.get("name") == "value" else None,
        names="value",
    )
    save.on_click(save_contract)
    state["get_rows"] = get_rows
    state["_controls"] = {
        "search": search, "datasets": datasets, "save": save, "status": status,
    }

    from IPython import display as ip

    ip.display(widgets.VBox([
        widgets.HTML("<h2>Register Data Contract</h2>"), agreement_text,
        environment_text, search, datasets, lifecycle_text, save, status,
    ]))
    return state
