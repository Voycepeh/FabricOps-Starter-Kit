from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Any

from .metadata import _resolve_action_by, _runtime_context

_SELECTED_AGREEMENT: dict[str, Any] | None = None

DEFAULT_SENSITIVITY_LABELS = ["Public", "Confidential", "Restricted"]
YES_NO_OPTIONS = ["Yes", "No"]
DEFAULT_REFRESH_FREQUENCIES = [
    "One Time",
    "Daily",
    "Weekly",
    "Monthly",
    "Quarterly",
    "Ad Hoc",
    "Not Applicable",
]

_HEADER_REQUIRED_FIELDS = [
    "agreement_id",
    "agreement_name",
    "data_steward_name",
    "data_steward_email",
    "department",
    "scope_of_use",
    "purpose",
    "expiry_date",
    "renewal_required",
    "sensitivity_label",
]

_HEADER_FIELDS = [
    "agreement_id",
    "agreement_name",
    "data_steward_name",
    "data_steward_email",
    "department",
    "business_owner",
    "scope_of_use",
    "purpose",
    "start_date",
    "expiry_date",
    "agreement_status",
    "status_as_of_date",
    "renewal_required",
    "sensitivity_label",
    "commit_note",
    "committed_by",
    "committed_at",
    "notebook_name",
    "workspace_name",
    "lakehouse_name",
    "run_id",
]

_CATALOGUE_FIELDS = [
    "agreement_id",
    "catalogue_id",
    "source_system",
    "source_database",
    "source_schema",
    "source_table",
    "business_name",
    "business_description",
    "data_owner",
    "data_steward_name",
    "contains_sensitive_data",
    "sensitivity_label",
    "intended_use",
    "commit_note",
    "committed_by",
    "committed_at",
    "notebook_name",
    "workspace_name",
    "lakehouse_name",
    "run_id",
]

_SCOPE_FIELDS = [
    "agreement_id",
    "scope_id",
    "allowed_consumer",
    "allowed_consumer_type",
    "allowed_output_type",
    "dashboard_allowed",
    "data_dump_allowed",
    "self_service_extract_allowed",
    "refresh_frequency",
    "retention_expectation",
    "special_conditions",
    "commit_note",
    "committed_by",
    "committed_at",
    "notebook_name",
    "workspace_name",
    "lakehouse_name",
    "run_id",
]

_AGREEMENT_WIDGET_FIELDS = [
    "agreement_id",
    "agreement_name",
    "data_steward_name",
    "data_steward_email",
    "department",
    "scope_of_use",
    "purpose",
    "start_date",
    "expiry_date",
    "renewal_required",
    "sensitivity_label",
    "source_system",
    "source_table",
    "contains_sensitive_data",
    "allowed_output_type",
    "dashboard_allowed",
    "data_dump_allowed",
    "self_service_extract_allowed",
    "refresh_frequency",
    "commit_note",
    "business_owner",
    "source_database",
    "source_schema",
    "business_name",
    "business_description",
    "data_owner",
    "intended_use",
    "allowed_consumer",
    "allowed_consumer_type",
    "retention_expectation",
    "special_conditions",
]

_DROPDOWN_DESCRIPTIONS = {
    "renewal_required": YES_NO_OPTIONS,
    "contains_sensitive_data": YES_NO_OPTIONS,
    "dashboard_allowed": YES_NO_OPTIONS,
    "data_dump_allowed": YES_NO_OPTIONS,
    "self_service_extract_allowed": YES_NO_OPTIONS,
}


def _coerce_row_dicts(rows: Any) -> list[dict[str, Any]]:
    if rows is None:
        return []
    if hasattr(rows, "collect"):
        rows = rows.collect()
    out = []
    for row in rows:
        if hasattr(row, "asDict"):
            out.append(row.asDict(recursive=True))
        else:
            out.append(dict(row))
    return out


def _latest_distinct_agreements(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    latest: dict[str, dict[str, Any]] = {}
    for row in rows:
        agreement_id = str(row.get("agreement_id") or "").strip()
        if not agreement_id:
            continue
        cur = latest.get(agreement_id)
        row_ts = str(row.get("updated_at") or row.get("approved_at") or row.get("committed_at") or "")
        cur_ts = str(
            (cur or {}).get("updated_at")
            or (cur or {}).get("approved_at")
            or (cur or {}).get("committed_at")
            or ""
        )
        if cur is None or row_ts >= cur_ts:
            latest[agreement_id] = row
    return list(latest.values())


def load_agreements(
    spark, metadata_table: str = "METADATA_DATA_AGREEMENT", missing_ok: bool = False
) -> list[dict[str, Any]]:
    """Load latest distinct agreement metadata rows for widget selection."""
    try:
        rows = _coerce_row_dicts(spark.table(metadata_table))
    except Exception:
        if missing_ok:
            return []
        raise RuntimeError("No agreements found. Run 01_da first.")
    picked = []
    for row in _latest_distinct_agreements(rows):
        picked.append(
            {
                "agreement_id": row.get("agreement_id"),
                "agreement_name": row.get("agreement_name") or row.get("agreement_id"),
                "approved_usage": row.get("approved_usage") or row.get("scope_of_use") or "",
                "business_context": row.get("business_context") or row.get("purpose") or "",
                "ownership": row.get("ownership") or row.get("data_steward_name") or "",
                "updated_at": row.get("updated_at"),
                "approved_at": row.get("approved_at"),
                "committed_at": row.get("committed_at"),
            }
        )
    return picked


def _agreement_option_label(row: dict[str, Any]) -> str:
    name = row.get("agreement_name") or row.get("agreement_id") or "unknown"
    agreement_id = row.get("agreement_id") or "unknown"
    approved_usage = row.get("approved_usage") or ""
    return f"{name} | {agreement_id} | {approved_usage}"


def select_agreement(agreement_rows_or_df) -> None:
    """Render a widget dropdown and store selected agreement metadata row in module state."""
    import ipywidgets as widgets
    from IPython.display import display

    global _SELECTED_AGREEMENT
    rows = _coerce_row_dicts(agreement_rows_or_df)
    if not rows:
        raise ValueError("No agreements found. Save a data agreement in notebook 01 first.")
    options = [(_agreement_option_label(r), r) for r in rows]
    dropdown = widgets.Dropdown(options=options, description="Agreement", layout=widgets.Layout(width="1000px"))

    def _on_change(change):
        if change.get("name") == "value" and change.get("new") is not None:
            _SELECTED_AGREEMENT = dict(change["new"])
            globals()["_SELECTED_AGREEMENT"] = _SELECTED_AGREEMENT

    dropdown.observe(_on_change)
    _SELECTED_AGREEMENT = dict(options[0][1])
    display(dropdown)


def get_selected_agreement() -> dict[str, Any]:
    """Return selected agreement from widget flow."""
    if not _SELECTED_AGREEMENT:
        raise RuntimeError("No agreement selected. Run select_agreement(...) and pick an agreement first.")
    return dict(_SELECTED_AGREEMENT)


def _non_empty_options(
    options: list[str] | None, *, default: list[str] | None = None, field_name: str = "options"
) -> list[str]:
    selected = default if options is None else options
    values = [str(value).strip() for value in selected or [] if str(value).strip()]
    if not values:
        raise ValueError(f"{field_name} must include at least one non-empty value.")
    return values


def _agreement_widget_specs(
    *,
    sensitivity_labels: list[str] | None = None,
    departments: list[str] | None = None,
    source_systems: list[str] | None = None,
    refresh_frequencies: list[str] | None = None,
    default_values: dict[str, str] | None = None,
) -> list[dict[str, Any]]:
    defaults = {key: str(value) for key, value in (default_values or {}).items()}
    specs: list[dict[str, Any]] = []
    dropdowns = {
        **_DROPDOWN_DESCRIPTIONS,
        "sensitivity_label": _non_empty_options(
            sensitivity_labels, default=DEFAULT_SENSITIVITY_LABELS, field_name="sensitivity_labels"
        ),
        "refresh_frequency": _non_empty_options(
            refresh_frequencies, default=DEFAULT_REFRESH_FREQUENCIES, field_name="refresh_frequencies"
        ),
    }
    if departments is not None:
        dropdowns["department"] = _non_empty_options(departments, field_name="departments")
    if source_systems is not None:
        dropdowns["source_system"] = _non_empty_options(source_systems, field_name="source_systems")

    for field_name in _AGREEMENT_WIDGET_FIELDS:
        default_value = defaults.get(field_name, "")
        if field_name in dropdowns:
            options = list(dropdowns[field_name])
            if not default_value or default_value not in options:
                default_value = options[0]
            specs.append({"name": field_name, "kind": "dropdown", "default": default_value, "options": options})
        else:
            specs.append({"name": field_name, "kind": "text", "default": default_value})
    return specs


def _get_fabric_widgets() -> Any:
    for module_name in ("notebookutils", "mssparkutils"):
        try:
            module = __import__(module_name)
        except Exception:
            continue
        widgets = getattr(module, "widgets", None)
        if widgets is not None:
            return widgets
    raise RuntimeError(
        "Fabric notebook widgets are unavailable. Run this inside Fabric or provide widget values directly."
    )


def _widget_dropdown(widgets: Any, name: str, default_value: str, options: list[str]) -> None:
    for args in ((name, default_value, options), (name, default_value, options, name)):
        try:
            widgets.dropdown(*args)
            return
        except TypeError:
            continue
    widgets.dropdown(name, default_value, options)


def _widget_text(widgets: Any, name: str, default_value: str) -> None:
    for args in ((name, default_value), (name, default_value, name)):
        try:
            widgets.text(*args)
            return
        except TypeError:
            continue
    widgets.text(name, default_value)


def create_agreement_widgets(
    *,
    sensitivity_labels: list[str] | None = None,
    departments: list[str] | None = None,
    source_systems: list[str] | None = None,
    refresh_frequencies: list[str] | None = None,
    default_values: dict[str, str] | None = None,
) -> None:
    """Create Fabric widgets for data sharing agreement metadata capture.

    Parameters
    ----------
    sensitivity_labels : list[str] | None, optional
        Dropdown options for ``sensitivity_label``. Defaults to
        ``["Public", "Confidential", "Restricted"]`` when omitted.
    departments : list[str] | None, optional
        Department dropdown options. When omitted, ``department`` is a free-text
        widget.
    source_systems : list[str] | None, optional
        Source-system dropdown options. When omitted, ``source_system`` is a
        free-text widget.
    refresh_frequencies : list[str] | None, optional
        Dropdown options for ``refresh_frequency``. Defaults to the canonical
        FabricOps refresh-frequency list when omitted.
    default_values : dict[str, str] | None, optional
        Optional initial widget values keyed by widget field name.

    Raises
    ------
    RuntimeError
        If Fabric notebook widgets are unavailable.
    ValueError
        If a supplied option list is empty after trimming blank values.

    Notes
    -----
    This function creates widgets for human-entered agreement metadata only.
    Derived fields such as ``agreement_status`` and ``status_as_of_date`` are
    intentionally not exposed as widgets.
    """
    widgets = _get_fabric_widgets()
    for spec in _agreement_widget_specs(
        sensitivity_labels=sensitivity_labels,
        departments=departments,
        source_systems=source_systems,
        refresh_frequencies=refresh_frequencies,
        default_values=default_values,
    ):
        if spec["kind"] == "dropdown":
            _widget_dropdown(widgets, spec["name"], spec["default"], spec["options"])
        else:
            _widget_text(widgets, spec["name"], spec["default"])


def read_agreement_widget_values() -> dict[str, str]:
    """Read agreement metadata values from Fabric notebook widgets.

    Returns
    -------
    dict[str, str]
        Widget values keyed by agreement metadata field name.

    Raises
    ------
    RuntimeError
        If Fabric notebook widgets are unavailable.
    """
    widgets = _get_fabric_widgets()
    return {field_name: str(widgets.get(field_name) or "").strip() for field_name in _AGREEMENT_WIDGET_FIELDS}


def _parse_date(value: date | datetime | str, *, field_name: str) -> date:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    text = str(value or "").strip()
    if not text:
        raise ValueError(f"{field_name} is required and must use YYYY-MM-DD format.")
    try:
        return date.fromisoformat(text[:10])
    except ValueError as exc:
        raise ValueError(f"{field_name} must be a valid date in YYYY-MM-DD format.") from exc


def _normalize_optional_date(value: Any, *, field_name: str) -> str:
    if value is None or str(value).strip() == "":
        return ""
    return _parse_date(value, field_name=field_name).isoformat()


def derive_agreement_status(
    expiry_date: str,
    *,
    as_of_date: date | str | None = None,
) -> dict[str, str]:
    """Derive agreement status from an expiry date.

    Parameters
    ----------
    expiry_date : str
        Agreement expiry date in ``YYYY-MM-DD`` format.
    as_of_date : date | str | None, optional
        Date used to evaluate the agreement. Defaults to the current UTC date.

    Returns
    -------
    dict[str, str]
        Mapping with ``agreement_status`` set to ``"Active"`` or
        ``"Inactive"`` and ``status_as_of_date`` in ISO date format.

    Raises
    ------
    ValueError
        If ``expiry_date`` or ``as_of_date`` cannot be parsed as dates.
    """
    expiry = _parse_date(expiry_date, field_name="expiry_date")
    as_of = (
        _parse_date(as_of_date, field_name="as_of_date")
        if as_of_date is not None
        else datetime.now(timezone.utc).date()
    )
    return {
        "agreement_status": "Active" if as_of <= expiry else "Inactive",
        "status_as_of_date": as_of.isoformat(),
    }


def _require_fields(values: dict[str, Any], required_fields: list[str]) -> None:
    missing = [field for field in required_fields if not str(values.get(field) or "").strip()]
    if missing:
        raise ValueError(f"Missing required agreement field(s): {', '.join(missing)}.")


def _validate_yes_no(values: dict[str, Any], fields: list[str]) -> None:
    invalid = [
        field
        for field in fields
        if str(values.get(field) or "").strip()
        and str(values.get(field)).strip() not in YES_NO_OPTIONS
    ]
    if invalid:
        raise ValueError(f"Agreement field(s) must be Yes or No: {', '.join(invalid)}.")


def _resolve_committed_at(committed_at: datetime | str | None = None) -> str:
    if committed_at is None:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    if isinstance(committed_at, datetime):
        if committed_at.tzinfo is None:
            committed_at = committed_at.replace(tzinfo=timezone.utc)
        return committed_at.isoformat()
    return str(committed_at)


def _context_value(runtime_context: dict[str, str], *keys: str) -> str:
    for key in keys:
        value = runtime_context.get(key)
        if value is not None and str(value).strip():
            return str(value).strip()
    return ""


def _record_base(
    widget_values: dict[str, str],
    *,
    committed_by: str | None,
    committed_at: datetime | str | None,
    runtime_context: dict[str, str] | None,
) -> dict[str, Any]:
    ctx = {str(k): v for k, v in (_runtime_context() | (runtime_context or {})).items()}
    return {
        "agreement_id": str(widget_values.get("agreement_id") or "").strip(),
        "commit_note": str(widget_values.get("commit_note") or "").strip(),
        "committed_by": _resolve_action_by(committed_by),
        "committed_at": _resolve_committed_at(committed_at),
        "notebook_name": _context_value(ctx, "notebook_name", "currentNotebookName", "notebookName"),
        "workspace_name": _context_value(ctx, "workspace_name", "currentWorkspaceName", "workspaceName"),
        "lakehouse_name": _context_value(ctx, "lakehouse_name", "lakehouseName"),
        "run_id": _context_value(ctx, "run_id", "activityId", "runId"),
    }


def _normalise_widget_values(widget_values: dict[str, str]) -> dict[str, str]:
    values = {key: str(value or "").strip() for key, value in widget_values.items()}
    _require_fields(values, _HEADER_REQUIRED_FIELDS)
    _validate_yes_no(
        values,
        [
            "renewal_required",
            "contains_sensitive_data",
            "dashboard_allowed",
            "data_dump_allowed",
            "self_service_extract_allowed",
        ],
    )
    values["expiry_date"] = _parse_date(values["expiry_date"], field_name="expiry_date").isoformat()
    values["start_date"] = _normalize_optional_date(values.get("start_date"), field_name="start_date")
    values.update(derive_agreement_status(values["expiry_date"]))
    return values


def _select_record_fields(record: dict[str, Any], fields: list[str]) -> dict[str, Any]:
    return {field: record.get(field, "") for field in fields}


def build_agreement_header_record(
    widget_values: dict[str, str],
    *,
    committed_by: str | None = None,
    committed_at: datetime | str | None = None,
    runtime_context: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Build an audited agreement header metadata record.

    Parameters
    ----------
    widget_values : dict[str, str]
        Values read from agreement metadata widgets or supplied by tests/scripts.
    committed_by : str | None, optional
        Actor identity. When omitted, the Fabric runtime user is used when
        available, then ``"unknown"``.
    committed_at : datetime | str | None, optional
        Commit timestamp. Defaults to the current UTC timestamp.
    runtime_context : dict[str, str] | None, optional
        Optional notebook/workspace/lakehouse/run identifiers to copy into the
        record.

    Returns
    -------
    dict[str, Any]
        Append-friendly agreement header record containing computed status and
        audit fields.

    Raises
    ------
    ValueError
        If required fields are missing, dates are invalid, or Yes/No fields use
        another value.
    """
    values = _normalise_widget_values(widget_values)
    record = {
        **values,
        **_record_base(
            values,
            committed_by=committed_by,
            committed_at=committed_at,
            runtime_context=runtime_context,
        ),
    }
    return _select_record_fields(record, _HEADER_FIELDS)


def build_agreement_catalogue_record(
    widget_values: dict[str, str],
    *,
    committed_by: str | None = None,
    committed_at: datetime | str | None = None,
    runtime_context: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Build an audited agreement catalogue metadata record.

    Parameters
    ----------
    widget_values : dict[str, str]
        Values read from agreement metadata widgets or supplied by tests/scripts.
    committed_by : str | None, optional
        Actor identity. When omitted, the Fabric runtime user is used when
        available, then ``"unknown"``.
    committed_at : datetime | str | None, optional
        Commit timestamp. Defaults to the current UTC timestamp.
    runtime_context : dict[str, str] | None, optional
        Optional notebook/workspace/lakehouse/run identifiers to copy into the
        record.

    Returns
    -------
    dict[str, Any]
        Append-friendly catalogue record for the source table covered by the
        agreement.

    Raises
    ------
    ValueError
        If required header fields are missing, dates are invalid, or Yes/No
        fields use another value.
    """
    values = _normalise_widget_values(widget_values)
    base = _record_base(values, committed_by=committed_by, committed_at=committed_at, runtime_context=runtime_context)
    catalogue_id = (
        values.get("catalogue_id")
        or f"{values['agreement_id']}|{values.get('source_system', '')}|{values.get('source_table', '')}"
    )
    record = {**values, **base, "catalogue_id": catalogue_id}
    return _select_record_fields(record, _CATALOGUE_FIELDS)


def build_agreement_scope_record(
    widget_values: dict[str, str],
    *,
    committed_by: str | None = None,
    committed_at: datetime | str | None = None,
    runtime_context: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Build an audited agreement scope metadata record.

    Parameters
    ----------
    widget_values : dict[str, str]
        Values read from agreement metadata widgets or supplied by tests/scripts.
    committed_by : str | None, optional
        Actor identity. When omitted, the Fabric runtime user is used when
        available, then ``"unknown"``.
    committed_at : datetime | str | None, optional
        Commit timestamp. Defaults to the current UTC timestamp.
    runtime_context : dict[str, str] | None, optional
        Optional notebook/workspace/lakehouse/run identifiers to copy into the
        record.

    Returns
    -------
    dict[str, Any]
        Append-friendly scope record covering approved consumers and outputs.

    Raises
    ------
    ValueError
        If required header fields are missing, dates are invalid, or Yes/No
        fields use another value.
    """
    values = _normalise_widget_values(widget_values)
    base = _record_base(values, committed_by=committed_by, committed_at=committed_at, runtime_context=runtime_context)
    scope_id = (
        values.get("scope_id")
        or f"{values['agreement_id']}|{values.get('allowed_consumer', '')}|{values.get('allowed_output_type', '')}"
    )
    record = {**values, **base, "scope_id": scope_id}
    return _select_record_fields(record, _SCOPE_FIELDS)


def _metadata_root(metadata_lakehouse: Any) -> str | None:
    if metadata_lakehouse is None:
        return None
    root = getattr(metadata_lakehouse, "root", None)
    if root is not None:
        return str(root).rstrip("/")
    return str(metadata_lakehouse).rstrip("/")


def _write_record(spark: Any, record: dict[str, Any], table_name: str, *, metadata_lakehouse: Any, mode: str) -> None:
    df = spark.createDataFrame([record])
    root = _metadata_root(metadata_lakehouse)
    if root:
        df.write.format("delta").mode(mode).save(f"{root}/Tables/{table_name}")
    else:
        df.write.format("delta").mode(mode).saveAsTable(table_name)


def commit_agreement_metadata(
    *,
    spark,
    header_record: dict[str, Any],
    catalogue_record: dict[str, Any] | None = None,
    scope_record: dict[str, Any] | None = None,
    metadata_lakehouse: str | None = None,
    table_prefix: str = "metadata",
    mode: str = "append",
) -> dict[str, Any]:
    """Commit agreement metadata records to append-friendly Delta tables.

    Parameters
    ----------
    spark : object
        Active Spark session used to create and write metadata DataFrames.
    header_record : dict[str, Any]
        Agreement header record to write.
    catalogue_record : dict[str, Any] | None, optional
        Optional catalogue record to write.
    scope_record : dict[str, Any] | None, optional
        Optional scope record to write.
    metadata_lakehouse : str | None, optional
        Metadata lakehouse root path or ``FabricStore``. Pass
        ``CONFIG.path_config.paths[env_name]["metadata"]`` in Fabric notebooks
        to avoid default-lakehouse assumptions.
    table_prefix : str, default="metadata"
        Logical table prefix used to create table names such as
        ``metadata.agreement_header``.
    mode : str, default="append"
        Spark write mode.

    Returns
    -------
    dict[str, Any]
        Commit summary including agreement identity, status, audit values, and
        the table names updated.

    Notes
    -----
    When ``metadata_lakehouse`` is supplied, records are written to the
    configured lakehouse ``Tables/`` path. If omitted, Spark ``saveAsTable`` is
    used for compatibility with attached-lakehouse development scenarios.
    """
    if not header_record:
        raise ValueError("header_record is required.")
    prefix = str(table_prefix or "").strip().strip(".")
    table_names = {
        "header": f"{prefix}.agreement_header" if prefix else "agreement_header",
        "catalogue": f"{prefix}.agreement_catalogue" if prefix else "agreement_catalogue",
        "scope": f"{prefix}.agreement_scope" if prefix else "agreement_scope",
    }
    _write_record(spark, header_record, table_names["header"], metadata_lakehouse=metadata_lakehouse, mode=mode)
    updated = [table_names["header"]]
    if catalogue_record is not None:
        _write_record(
            spark,
            catalogue_record,
            table_names["catalogue"],
            metadata_lakehouse=metadata_lakehouse,
            mode=mode,
        )
        updated.append(table_names["catalogue"])
    if scope_record is not None:
        _write_record(spark, scope_record, table_names["scope"], metadata_lakehouse=metadata_lakehouse, mode=mode)
        updated.append(table_names["scope"])
    return {
        "agreement_id": header_record.get("agreement_id", ""),
        "agreement_status": header_record.get("agreement_status", ""),
        "expiry_date": header_record.get("expiry_date", ""),
        "status_as_of_date": header_record.get("status_as_of_date", ""),
        "committed_by": header_record.get("committed_by", ""),
        "committed_at": header_record.get("committed_at", ""),
        "tables_updated": updated,
    }
