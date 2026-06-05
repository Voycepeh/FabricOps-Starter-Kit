"""Dataset-level schema contracts for FabricOps production notebooks."""

from __future__ import annotations

import json
import warnings
from datetime import datetime, timezone
from typing import Any

from .fabric_input_output import read_lakehouse_table, write_lakehouse_table

SCHEMA_CONTRACT_TABLE = "METADATA_SCHEMA_CONTRACT"
SCHEMA_CONTRACT_COLUMN_TABLE = "METADATA_SCHEMA_CONTRACT_COLUMN"
SCHEMA_VALIDATION_EVIDENCE_TABLE = "METADATA_SCHEMA_VALIDATION_EVIDENCE"

_DATASET_ROLES = {"source", "target"}
_ENFORCEMENTS = {"observe", "warn", "fail"}
_APPROVED_STATUS = "approved"
_DRIFT_TO_RESULT_KEY = {
    "missing_required_column": "missing_required_columns",
    "unexpected_column": "unexpected_columns",
    "datatype_change": "datatype_mismatches",
    "nullability_change": "nullability_mismatches",
    "column_order_change": "column_order_mismatches",
}


class SchemaContractValidationError(RuntimeError):
    """Raised when schema-contract enforcement is configured to fail."""


def _now_utc_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _row_dict(row: Any) -> dict[str, Any]:
    return row.asDict(recursive=True) if hasattr(row, "asDict") else dict(row)


def _coerce_rows(rows_or_df: Any) -> list[dict[str, Any]]:
    if rows_or_df is None:
        return []
    if hasattr(rows_or_df, "collect"):
        rows_or_df = rows_or_df.collect()
    return [_row_dict(row) for row in rows_or_df]


def _get_any(row: dict[str, Any], *names: str, default: Any = None) -> Any:
    for name in names:
        if name in row and row.get(name) is not None:
            return row.get(name)
        upper = name.upper()
        if upper in row and row.get(upper) is not None:
            return row.get(upper)
        lower = name.lower()
        if lower in row and row.get(lower) is not None:
            return row.get(lower)
    return default


def _bool(value: Any, default: bool = False) -> bool:
    if value is None or value == "":
        return default
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "y"}


def _required_identity(value: Any, name: str) -> str:
    text = "" if value is None else str(value).strip()
    if not text:
        raise ValueError(f"{name} is required for dataset-level schema contracts.")
    return text


def _validate_dataset_role(dataset_role: str) -> str:
    role = _required_identity(dataset_role, "dataset_role").lower()
    if role not in _DATASET_ROLES:
        raise ValueError(f"dataset_role must be one of: {', '.join(sorted(_DATASET_ROLES))}.")
    return role


def _normalize_spark_data_type(data_type: Any) -> str:
    """Return a stable lowercase Spark data type representation.

    Parameters
    ----------
    data_type : Any
        Spark datatype object, simpleString string, or profile metadata value.

    Returns
    -------
    str
        Normalized type string suitable for contract comparison.
    """
    if data_type is None:
        return ""
    if hasattr(data_type, "simpleString"):
        value = data_type.simpleString()
    else:
        value = str(data_type)
    value = value.strip().lower().replace(" ", "")
    aliases = {
        "integer": "int",
        "long": "bigint",
        "boolean": "boolean",
        "bool": "boolean",
        "str": "string",
        "varchar": "string",
        "char": "string",
        "doubleprecision": "double",
    }
    return aliases.get(value, value)


def _schema_rows_from_dataframe(dataframe: Any) -> list[dict[str, Any]]:
    if hasattr(dataframe, "schema") and hasattr(dataframe.schema, "fields"):
        return [
            {
                "column_name": field.name,
                "data_type": _normalize_spark_data_type(field.dataType),
                "nullable": bool(field.nullable),
                "ordinal_position": idx + 1,
            }
            for idx, field in enumerate(dataframe.schema.fields)
        ]
    if hasattr(dataframe, "dtypes"):
        nullable_lookup: dict[str, bool] = {}
        if hasattr(dataframe, "schema"):
            for field in getattr(dataframe.schema, "fields", []):
                nullable_lookup[field.name] = bool(field.nullable)
        return [
            {
                "column_name": name,
                "data_type": _normalize_spark_data_type(dtype),
                "nullable": nullable_lookup.get(name, True),
                "ordinal_position": idx + 1,
            }
            for idx, (name, dtype) in enumerate(dataframe.dtypes)
        ]
    raise TypeError("profile_or_dataframe must be profile rows or a Spark DataFrame-like object.")


def _schema_rows_from_profile(profile_rows: Any) -> list[dict[str, Any]]:
    rows = []
    for idx, row in enumerate(_coerce_rows(profile_rows), start=1):
        column_name = _get_any(row, "column_name")
        if not column_name:
            continue
        ordinal = _get_any(row, "ordinal_position", "column_ordinal", default=idx)
        nullable_value = _get_any(row, "nullable", default=None)
        if nullable_value is None:
            null_count = _get_any(row, "null_count", default=None)
            nullable_value = True if null_count is None else int(null_count or 0) > 0
        rows.append(
            {
                "column_name": str(column_name),
                "data_type": _normalize_spark_data_type(_get_any(row, "data_type")),
                "nullable": _bool(nullable_value, default=True),
                "ordinal_position": int(ordinal),
            }
        )
    return rows


def _schema_rows(profile_or_dataframe: Any) -> list[dict[str, Any]]:
    if hasattr(profile_or_dataframe, "schema") or hasattr(profile_or_dataframe, "dtypes"):
        return _schema_rows_from_dataframe(profile_or_dataframe)
    return _schema_rows_from_profile(profile_or_dataframe)


def _suggest_schema_contract(
    profile_or_dataframe: Any, *, agreement_id: str, contract_id: str, dataset_role: str
) -> list[dict[str, Any]]:
    """Draft column-level schema-contract rows from a profile or DataFrame.

    Parameters
    ----------
    profile_or_dataframe : Any
        Spark DataFrame-like object or profile metadata rows containing column
        names, datatypes, nullability, and optional ordinal positions.
    agreement_id : str
        Data agreement identifier that will own the dataset contract.
    contract_id : str
        Dataset contract identifier for one source or target dataset.
    dataset_role : {"source", "target"}
        Dataset role within the agreement.

    Returns
    -------
    list[dict[str, Any]]
        Proposed column rows. Every discovered column is selected by default;
        no metadata is written.

    Notes
    -----
    Profiles are proposals only. Production enforcement should load an approved
    stored contract with :func:`_load_schema_contract`.
    """
    agreement = _required_identity(agreement_id, "agreement_id")
    contract = _required_identity(contract_id, "contract_id")
    role = _validate_dataset_role(dataset_role)
    rows = []
    now = _now_utc_iso()
    for row in _schema_rows(profile_or_dataframe):
        rows.append(
            {
                "agreement_id": agreement,
                "contract_id": contract,
                "dataset_role": role,
                "column_name": row["column_name"],
                "data_type": _normalize_spark_data_type(row.get("data_type")),
                "required": True,
                "nullable": bool(row.get("nullable", True)),
                "ordinal_position": int(row.get("ordinal_position") or len(rows) + 1),
                "enforcement": "",
                "selected": True,
                "created_at": now,
                "updated_at": now,
            }
        )
    return rows


def _latest_profile_for_dataset(profile_rows: Any, table_name: str | None = None) -> list[dict[str, Any]]:
    rows = _coerce_rows(profile_rows)
    if table_name:
        rows = [r for r in rows if str(_get_any(r, "table_name", "profiled_table_name", default="")) == table_name]
    if not rows:
        return []
    timestamps = [_get_any(r, "run_timestamp", default="") for r in rows]
    latest = max(str(t) for t in timestamps)
    return [r for r in rows if str(_get_any(r, "run_timestamp", default="")) == latest]


def _build_schema_contract_review_state(
    proposed_rows: list[dict[str, Any]],
    *,
    allow_extra_columns: bool = False,
    check_column_order: bool = False,
    default_enforcement: str = "fail",
) -> dict[str, Any]:
    """Build non-UI review state for schema-contract approval widgets.

    Parameters
    ----------
    proposed_rows : list[dict[str, Any]]
        Proposed rows returned by :func:`_suggest_schema_contract` or edited by
        a reviewer.
    allow_extra_columns : bool, default=False
        Whether non-contracted columns are allowed.
    check_column_order : bool, default=False
        Whether ordinal-position drift should be checked.
    default_enforcement : {"observe", "warn", "fail"}, default="fail"
        Dataset-level default enforcement mode.

    Returns
    -------
    dict[str, Any]
        Dataset-level settings and selected column rows.
    """
    enforcement = str(default_enforcement or "fail").lower()
    if enforcement not in _ENFORCEMENTS:
        raise ValueError("default_enforcement must be one of: observe, warn, fail.")
    selected = [dict(row) for row in proposed_rows or [] if _bool(row.get("selected"), default=True)]
    for idx, row in enumerate(selected, start=1):
        row["ordinal_position"] = int(row.get("ordinal_position") or idx)
        row["data_type"] = _normalize_spark_data_type(row.get("data_type"))
        row["required"] = _bool(row.get("required"), default=True)
        row["nullable"] = _bool(row.get("nullable"), default=True)
        row["enforcement"] = str(row.get("enforcement") or "")
    return {
        "settings": {
            "allow_extra_columns": bool(allow_extra_columns),
            "check_column_order": bool(check_column_order),
            "default_enforcement": enforcement,
        },
        "columns": selected,
    }


def _get_active_spark(spark_session: Any = None) -> Any:
    if spark_session is not None:
        return spark_session
    try:
        from pyspark.sql import SparkSession
    except Exception as exc:
        raise ValueError("spark_session is required when no active SparkSession is available.") from exc
    spark = SparkSession.getActiveSession()
    if spark is None:
        raise ValueError("spark_session is required when no active SparkSession is available.")
    return spark


def _contract_review_result(saved_contract: dict[str, Any], settings: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": str(saved_contract.get("contract_status") or _APPROVED_STATUS),
        "contract_id": saved_contract["contract_id"],
        "contract_version": saved_contract["contract_version"],
        "dataset_role": saved_contract["dataset_role"],
        "table_name": saved_contract["table_name"],
        "settings": settings,
        "columns": saved_contract["columns"],
    }


def review_schema_contract(
    profile_or_dataframe: Any,
    *,
    config: Any,
    env: str,
    agreement_id: str,
    contract_id: str,
    dataset_role: str,
    table_name: str,
    workspace_name: str = "",
    workspace_id: str = "",
    item_name: str = "",
    item_id: str = "",
    schema_name: str = "",
    spark_session: Any = None,
    allow_extra_columns: bool = False,
    check_column_order: bool = False,
    default_enforcement: str = "fail",
    approved: bool = False,
    approved_by: str = "",
) -> dict[str, Any]:
    """Review, approve, version, and persist a dataset schema contract.

    Parameters
    ----------
    profile_or_dataframe : Any
        Profile rows or Spark DataFrame-like object used to propose the schema.
    config : FrameworkConfig or dict
        Configuration containing the metadata lakehouse route.
    env : str
        Environment key paired with ``config``.
    agreement_id : str
        Owning data agreement identifier.
    contract_id : str
        Dataset contract identifier for this specific source or target dataset.
    dataset_role : {"source", "target"}
        Dataset role under the agreement.
    table_name : str
        Dataset table identity.
    workspace_name, workspace_id, item_name, item_id, schema_name : str, optional
        Dataset identity values persisted with the contract.
    spark_session : pyspark.sql.SparkSession, optional
        Spark session used to persist the approved contract. Required when
        ``approved=True`` unless an active Spark session exists.
    allow_extra_columns, check_column_order : bool, default=False
        Dataset-level schema settings proposed to the reviewer.
    default_enforcement : {"observe", "warn", "fail"}, default="fail"
        Dataset-level enforcement mode proposed to the reviewer.
    approved : bool, default=False
        Explicit approval flag for non-interactive workflows. In notebooks, the
        rendered approval button performs the same write after a human click.
    approved_by : str, optional
        Human approver identifier.

    Returns
    -------
    dict[str, Any]
        Concise review result. Pending reviews return ``status='pending_approval'``;
        approved reviews return the saved contract version and approved columns.

    Notes
    -----
    This is the user-facing governance workflow: proposal generation, review,
    explicit approval, versioning, and persistence happen behind one callable.
    Production validation is handled separately by :func:`apply_schema_guardrail`.
    """
    latest = _latest_profile_for_dataset(profile_or_dataframe, table_name=table_name)
    proposed = _suggest_schema_contract(
        latest or profile_or_dataframe,
        agreement_id=agreement_id,
        contract_id=contract_id,
        dataset_role=dataset_role,
    )
    state = _build_schema_contract_review_state(
        proposed,
        allow_extra_columns=allow_extra_columns,
        check_column_order=check_column_order,
        default_enforcement=default_enforcement,
    )

    def _approve(current_state: dict[str, Any]) -> dict[str, Any]:
        spark = _get_active_spark(spark_session)
        saved = _write_schema_contract(
            spark,
            config=config,
            env=env,
            agreement_id=agreement_id,
            contract_id=contract_id,
            dataset_role=dataset_role,
            workspace_name=workspace_name,
            workspace_id=workspace_id,
            item_name=item_name,
            item_id=item_id,
            schema_name=schema_name,
            table_name=table_name,
            columns=current_state["columns"],
            approved_by=approved_by,
            **current_state["settings"],
        )
        return _contract_review_result(saved, current_state["settings"])

    if approved:
        return _approve(state)

    pending_result = {
        "status": "pending_approval",
        "contract_id": contract_id,
        "contract_version": None,
        "dataset_role": _validate_dataset_role(dataset_role),
        "table_name": table_name,
        "settings": state["settings"],
        "columns": state["columns"],
        "message": "Review the proposed schema and explicitly approve before the contract is written.",
    }

    try:
        import ipywidgets as widgets
        from IPython.display import display
    except Exception:
        return pending_result

    extra = widgets.Checkbox(value=state["settings"]["allow_extra_columns"], description="Allow extra columns")
    order = widgets.Checkbox(value=state["settings"]["check_column_order"], description="Check column order")
    default = widgets.Dropdown(
        options=sorted(_ENFORCEMENTS), value=state["settings"]["default_enforcement"], description="Default"
    )
    column_widgets = []
    for row in state["columns"]:
        include = widgets.Checkbox(value=True, description=row["column_name"])
        required = widgets.Checkbox(value=row["required"], description="required")
        dtype = widgets.Text(value=row["data_type"], description="type")
        nullable = widgets.Checkbox(value=row["nullable"], description="nullable")
        enforcement = widgets.Dropdown(
            options=["", *sorted(_ENFORCEMENTS)], value=row.get("enforcement", ""), description="enforce"
        )
        column_widgets.append((row, include, required, dtype, nullable, enforcement))
    approve_button = widgets.Button(description="Approve and write contract", button_style="success")
    status = widgets.HTML(value="Review columns, then click Approve and write contract.")

    def _current_state_from_widgets() -> dict[str, Any]:
        widget_settings = {
            "allow_extra_columns": extra.value,
            "check_column_order": order.value,
            "default_enforcement": default.value,
        }
        approved_rows = []
        for row, include, required, dtype, nullable, enforcement in column_widgets:
            if not include.value:
                continue
            updated = dict(row)
            updated.update(
                {
                    "required": required.value,
                    "data_type": dtype.value,
                    "nullable": nullable.value,
                    "enforcement": enforcement.value,
                    "selected": True,
                }
            )
            approved_rows.append(updated)
        return _build_schema_contract_review_state(approved_rows, **widget_settings)

    def _on_approve(_button):
        state.update(_current_state_from_widgets())
        saved = _approve(state)
        pending_result.update(saved)
        status.value = f"Approved contract version {saved['contract_version']} with {len(saved['columns'])} column(s)."

    approve_button.on_click(_on_approve)
    controls = [widgets.HBox([extra, order, default])]
    controls.extend(widgets.HBox(items[1:]) for items in column_widgets)
    controls.extend([approve_button, status])
    display(widgets.VBox(controls))
    return pending_result


def _next_contract_version(existing_rows: list[dict[str, Any]], contract_id: str) -> int:
    versions = [
        int(_get_any(r, "contract_version", default=0) or 0)
        for r in existing_rows
        if str(_get_any(r, "contract_id", default="")) == contract_id
    ]
    return max(versions, default=0) + 1


def _write_schema_contract(
    spark: Any,
    *,
    config: Any,
    env: str,
    agreement_id: str,
    contract_id: str,
    dataset_role: str,
    columns: list[dict[str, Any]],
    workspace_name: str = "",
    workspace_id: str = "",
    item_name: str = "",
    item_id: str = "",
    schema_name: str = "",
    table_name: str = "",
    allow_extra_columns: bool = False,
    check_column_order: bool = False,
    default_enforcement: str = "fail",
    contract_status: str = _APPROVED_STATUS,
    approved_by: str = "",
    dataset_table: str = SCHEMA_CONTRACT_TABLE,
    column_table: str = SCHEMA_CONTRACT_COLUMN_TABLE,
) -> dict[str, Any]:
    """Persist a versioned approved dataset-level schema contract.

    Parameters
    ----------
    spark : pyspark.sql.SparkSession
        Spark session used to create metadata DataFrames.
    config : FrameworkConfig or dict
        Configuration containing the metadata lakehouse route.
    env : str
        Environment key paired with ``config``.
    agreement_id, contract_id : str
        Agreement and dataset-contract identifiers.
    dataset_role : {"source", "target"}
        Dataset role under the agreement.
    columns : list[dict[str, Any]]
        Approved column-level schema contract rows.
    workspace_name, workspace_id, item_name, item_id, schema_name, table_name : str, optional
        Dataset identity. At least one workspace, one item, and a table name are
        required.
    allow_extra_columns, check_column_order : bool, default=False
        Dataset-level schema settings.
    default_enforcement : {"observe", "warn", "fail"}, default="fail"
        Dataset-level enforcement mode.
    contract_status : str, default="approved"
        Version status to persist. Only approved rows are loaded for enforcement.
    approved_by : str, optional
        Human approver identifier.
    dataset_table, column_table : str
        Metadata table names.

    Returns
    -------
    dict[str, Any]
        Persisted dataset row and column rows for the new version.
    """
    agreement = _required_identity(agreement_id, "agreement_id")
    contract = _required_identity(contract_id, "contract_id")
    role = _validate_dataset_role(dataset_role)
    if not (workspace_name or workspace_id):
        raise ValueError("workspace_name or workspace_id is required.")
    if not (item_name or item_id):
        raise ValueError("item_name or item_id is required.")
    table = _required_identity(table_name, "table_name")
    if not columns:
        raise ValueError("columns are required for an approved schema contract.")
    enforcement = str(default_enforcement or "fail").lower()
    if enforcement not in _ENFORCEMENTS:
        raise ValueError("default_enforcement must be one of: observe, warn, fail.")
    try:
        existing = _coerce_rows(read_lakehouse_table(config, env, "metadata", dataset_table, spark_session=spark))
    except Exception:
        existing = []
    version = _next_contract_version(existing, contract)
    now = _now_utc_iso()
    approved_at = now if contract_status == _APPROVED_STATUS else ""
    dataset_row = {
        "contract_id": contract,
        "agreement_id": agreement,
        "dataset_role": role,
        "workspace_name": str(workspace_name or ""),
        "workspace_id": str(workspace_id or ""),
        "item_name": str(item_name or ""),
        "item_id": str(item_id or ""),
        "schema_name": str(schema_name or ""),
        "table_name": table,
        "allow_extra_columns": bool(allow_extra_columns),
        "check_column_order": bool(check_column_order),
        "default_enforcement": enforcement,
        "contract_status": contract_status,
        "contract_version": version,
        "approved_by": str(approved_by or ""),
        "approved_at": approved_at,
        "created_at": now,
        "updated_at": now,
    }
    column_rows = []
    for idx, row in enumerate(columns, start=1):
        column_rows.append(
            {
                "contract_id": contract,
                "column_name": _required_identity(row.get("column_name"), "column_name"),
                "data_type": _normalize_spark_data_type(row.get("data_type")),
                "required": _bool(row.get("required"), default=True),
                "nullable": _bool(row.get("nullable"), default=True),
                "ordinal_position": int(row.get("ordinal_position") or idx),
                "enforcement": str(row.get("enforcement") or ""),
                "contract_version": version,
                "created_at": now,
                "updated_at": now,
            }
        )
    write_lakehouse_table(spark.createDataFrame([dataset_row]), config, env, "metadata", dataset_table, mode="append")
    write_lakehouse_table(spark.createDataFrame(column_rows), config, env, "metadata", column_table, mode="append")
    return {**dataset_row, "columns": column_rows}


def _identity_matches(
    row: dict[str, Any],
    *,
    table_name: str | None,
    workspace_name: str | None,
    workspace_id: str | None,
    item_name: str | None,
    item_id: str | None,
    schema_name: str | None,
) -> bool:
    checks = [
        ("table_name", table_name),
        ("workspace_name", workspace_name),
        ("workspace_id", workspace_id),
        ("item_name", item_name),
        ("item_id", item_id),
        ("schema_name", schema_name),
    ]
    provided = False
    for key, value in checks:
        if value is None or value == "":
            continue
        provided = True
        if str(_get_any(row, key, default="")) != str(value):
            return False
    if not provided:
        raise ValueError(
            "Load schema contracts by dataset identity, not agreement_id alone; "
            "pass table_name and, when available, workspace/item identity."
        )
    return True


def _load_schema_contract(
    *,
    config: Any,
    env: str,
    agreement_id: str,
    dataset_role: str,
    table_name: str | None = None,
    workspace_name: str | None = None,
    workspace_id: str | None = None,
    item_name: str | None = None,
    item_id: str | None = None,
    schema_name: str | None = None,
    spark_session: Any = None,
    dataset_table: str = SCHEMA_CONTRACT_TABLE,
    column_table: str = SCHEMA_CONTRACT_COLUMN_TABLE,
) -> dict[str, Any]:
    """Load the latest approved schema contract for one dataset.

    Parameters
    ----------
    config : FrameworkConfig or dict
        Configuration containing the metadata lakehouse route.
    env : str
        Environment key paired with ``config``.
    agreement_id : str
        Owning data agreement identifier.
    dataset_role : {"source", "target"}
        Role of the dataset under the agreement.
    table_name, workspace_name, workspace_id, item_name, item_id, schema_name : str, optional
        Dataset identity filters. At least one dataset identity value is
        required; loading by agreement alone is intentionally unsupported.
    spark_session : pyspark.sql.SparkSession, optional
        Spark session used for metadata reads.
    dataset_table, column_table : str
        Metadata table names.

    Returns
    -------
    dict[str, Any]
        Dataset-level settings and approved column rows.

    Raises
    ------
    LookupError
        If no approved contract exists for the selected dataset.
    """
    agreement = _required_identity(agreement_id, "agreement_id")
    role = _validate_dataset_role(dataset_role)
    if not any([table_name, workspace_name, workspace_id, item_name, item_id, schema_name]):
        raise ValueError(
            "Load schema contracts by dataset identity, not agreement_id alone; "
            "pass table_name and, when available, workspace/item identity."
        )
    dataset_rows = _coerce_rows(
        read_lakehouse_table(config, env, "metadata", dataset_table, spark_session=spark_session)
    )
    candidates = [
        row
        for row in dataset_rows
        if str(_get_any(row, "agreement_id", default="")) == agreement
        and str(_get_any(row, "dataset_role", default="")).lower() == role
        and str(_get_any(row, "contract_status", default="")).lower() == _APPROVED_STATUS
        and _identity_matches(
            row,
            table_name=table_name,
            workspace_name=workspace_name,
            workspace_id=workspace_id,
            item_name=item_name,
            item_id=item_id,
            schema_name=schema_name,
        )
    ]
    if not candidates:
        raise LookupError(
            "No approved schema contract found for this dataset. Run profiling, "
            "review a proposal, and write an approved dataset contract before enforcing schema drift."
        )
    latest = max(candidates, key=lambda r: int(_get_any(r, "contract_version", default=0) or 0))
    contract = str(_get_any(latest, "contract_id"))
    version = int(_get_any(latest, "contract_version", default=0) or 0)
    column_rows = [
        row
        for row in _coerce_rows(
            read_lakehouse_table(config, env, "metadata", column_table, spark_session=spark_session)
        )
        if str(_get_any(row, "contract_id", default="")) == contract
        and int(_get_any(row, "contract_version", default=0) or 0) == version
    ]
    column_rows.sort(key=lambda r: int(_get_any(r, "ordinal_position", default=0) or 0))
    return {
        **latest,
        "contract_version": version,
        "allow_extra_columns": _bool(_get_any(latest, "allow_extra_columns")),
        "check_column_order": _bool(_get_any(latest, "check_column_order")),
        "columns": column_rows,
    }


def validate_schema(
    dataframe: Any,
    expected_schema: Any,
    *,
    allow_extra_columns: bool = False,
    check_nullability: bool = True,
    check_column_order: bool = False,
) -> dict[str, Any]:
    """Validate a DataFrame schema against approved dataset-contract columns.

    Parameters
    ----------
    dataframe : pyspark.sql.DataFrame
        Spark DataFrame or DataFrame-like object with schema metadata.
    expected_schema : Any
        Approved column rows from :func:`_load_schema_contract`.
    allow_extra_columns : bool, default=False
        Whether unexpected DataFrame columns are allowed.
    check_nullability : bool, default=True
        Whether nullable/non-nullable changes are considered drift.
    check_column_order : bool, default=False
        Whether ordinal-position changes are considered drift.

    Returns
    -------
    dict[str, Any]
        Structured schema validation result containing drift lists and
        ``is_valid``.

    Notes
    -----
    This function never writes metadata and never stops the pipeline. Use
    :func:`apply_schema_guardrail` to apply enforcement behavior.
    """
    actual = _schema_rows_from_dataframe(dataframe)
    expected = []
    for idx, row in enumerate(_coerce_rows(expected_schema), start=1):
        expected.append(
            {
                "column_name": _get_any(row, "column_name"),
                "data_type": _normalize_spark_data_type(_get_any(row, "data_type")),
                "required": _bool(_get_any(row, "required", default=True), True),
                "nullable": _bool(_get_any(row, "nullable", default=True), True),
                "ordinal_position": int(_get_any(row, "ordinal_position", default=idx) or idx),
                "enforcement": str(_get_any(row, "enforcement", default="") or ""),
            }
        )
    actual_by_name = {r["column_name"]: r for r in actual}
    expected_by_name = {r["column_name"]: r for r in expected}
    missing = [r["column_name"] for r in expected if r["required"] and r["column_name"] not in actual_by_name]
    optional_missing = [
        r["column_name"] for r in expected if not r["required"] and r["column_name"] not in actual_by_name
    ]
    unexpected = (
        [] if allow_extra_columns else [r["column_name"] for r in actual if r["column_name"] not in expected_by_name]
    )
    datatype_mismatches = []
    nullability_mismatches = []
    order_mismatches = []
    for expected_row in expected:
        name = expected_row["column_name"]
        actual_row = actual_by_name.get(name)
        if not actual_row:
            continue
        if _normalize_spark_data_type(actual_row["data_type"]) != expected_row["data_type"]:
            datatype_mismatches.append(
                {"column_name": name, "expected": expected_row["data_type"], "actual": actual_row["data_type"]}
            )
        if check_nullability and bool(actual_row["nullable"]) != bool(expected_row["nullable"]):
            nullability_mismatches.append(
                {
                    "column_name": name,
                    "expected": bool(expected_row["nullable"]),
                    "actual": bool(actual_row["nullable"]),
                }
            )
        if check_column_order and int(actual_row["ordinal_position"]) != int(expected_row["ordinal_position"]):
            order_mismatches.append(
                {
                    "column_name": name,
                    "expected": expected_row["ordinal_position"],
                    "actual": actual_row["ordinal_position"],
                }
            )
    is_valid = not any([missing, unexpected, datatype_mismatches, nullability_mismatches, order_mismatches])
    return {
        "missing_required_columns": missing,
        "optional_missing_columns": optional_missing,
        "unexpected_columns": unexpected,
        "datatype_mismatches": datatype_mismatches,
        "nullability_mismatches": nullability_mismatches,
        "column_order_mismatches": order_mismatches,
        "is_valid": is_valid,
    }


def _enforce_schema_result(
    schema_result: dict[str, Any],
    enforcement: str = "fail",
    *,
    per_drift_enforcement: dict[str, str] | None = None,
    raise_on_fail: bool = True,
) -> dict[str, Any]:
    """Apply schema-contract enforcement behavior to a validation result.

    Parameters
    ----------
    schema_result : dict[str, Any]
        Result returned by :func:`validate_schema`.
    enforcement : {"observe", "warn", "fail"}, default="fail"
        Dataset-level default behavior.
    per_drift_enforcement : dict[str, str], optional
        Drift-type overrides for ``missing_required_column``,
        ``unexpected_column``, ``datatype_change``, ``nullability_change``, and
        ``column_order_change``.

    Returns
    -------
    dict[str, Any]
        Enforcement summary with status and applied modes.

    Raises
    ------
    SchemaContractValidationError
        If any detected drift is configured with ``fail``.
    """
    default = str(enforcement or "fail").lower()
    if default not in _ENFORCEMENTS:
        raise ValueError("enforcement must be one of: observe, warn, fail.")
    overrides = {k: str(v).lower() for k, v in (per_drift_enforcement or {}).items()}
    applied = {}
    failing = []
    warning = []
    for drift_type, result_key in _DRIFT_TO_RESULT_KEY.items():
        values = schema_result.get(result_key) or []
        if not values:
            continue
        mode = overrides.get(drift_type, default)
        if mode not in _ENFORCEMENTS:
            raise ValueError(f"Invalid enforcement for {drift_type}: {mode}.")
        applied[drift_type] = mode
        if mode == "fail":
            failing.append(drift_type)
        elif mode == "warn":
            warning.append(drift_type)
    summary = {
        "status": "passed" if schema_result.get("is_valid") else "failed",
        "can_continue": not failing,
        "enforcement_applied": applied or {"no_drift": default},
        "is_valid": bool(schema_result.get("is_valid")),
    }
    if warning:
        warnings.warn(f"Schema contract drift detected: {', '.join(warning)}", UserWarning, stacklevel=2)
    if failing and raise_on_fail:
        raise SchemaContractValidationError(
            f"Schema contract validation failed for drift type(s): {', '.join(failing)}"
        )
    return summary



def apply_schema_guardrail(
    df: Any,
    *,
    config: Any,
    env: str,
    agreement_id: str,
    dataset_role: str,
    table_name: str,
    run_id: str,
    workspace_name: str | None = None,
    workspace_id: str | None = None,
    item_name: str | None = None,
    item_id: str | None = None,
    schema_name: str | None = None,
    notebook_registry_id: str | None = None,
    metadata_table: str = SCHEMA_VALIDATION_EVIDENCE_TABLE,
    spark_session: Any = None,
    require_contract: bool = False,
) -> dict[str, Any]:
    """Apply the approved dataset schema guardrail in a pipeline run.

    Parameters
    ----------
    df : pyspark.sql.DataFrame
        Current source or transformed target DataFrame to validate.
    config : FrameworkConfig or dict
        Configuration containing the metadata lakehouse route.
    env : str
        Environment key paired with ``config``.
    agreement_id : str
        Owning data agreement identifier.
    dataset_role : {"source", "target"}
        Role of the dataset under the agreement.
    table_name : str
        Dataset table identity.
    run_id : str
        Pipeline run identifier recorded in validation evidence.
    workspace_name, workspace_id, item_name, item_id, schema_name : str, optional
        Dataset identity filters used to load the approved contract and write
        evidence.
    notebook_registry_id : str, optional
        Active notebook registration identifier to include in the returned
        structured result.
    metadata_table : str, default="METADATA_SCHEMA_VALIDATION_EVIDENCE"
        Evidence metadata table.
    spark_session : pyspark.sql.SparkSession, optional
        Spark session used for metadata reads/writes.
    require_contract : bool, default=False
        When True, missing approved contracts raise ``LookupError`` instead of
        returning ``status='not_configured'``.

    Returns
    -------
    dict[str, Any]
        Structured guardrail result containing the original DataFrame, loaded
        contract, validation result, enforcement result, evidence status, and
        continuation flag.

    Raises
    ------
    LookupError
        If ``require_contract=True`` and no approved contract exists.
    SchemaContractValidationError
        If approved enforcement is ``fail`` and drift is detected. Evidence is
        written before raising when metadata writes are available.
    """
    spark = _get_active_spark(spark_session)
    identity = {
        "workspace_name": workspace_name or "",
        "workspace_id": workspace_id or "",
        "item_name": item_name or "",
        "item_id": item_id or "",
        "schema_name": schema_name or "",
    }
    try:
        contract = _load_schema_contract(
            config=config,
            env=env,
            agreement_id=agreement_id,
            dataset_role=dataset_role,
            table_name=table_name,
            spark_session=spark,
            **identity,
        )
    except LookupError as exc:
        if require_contract:
            raise
        return {
            "status": "not_configured",
            "dataframe": df,
            "contract": None,
            "validation": None,
            "enforcement": {"status": "not_configured", "can_continue": True},
            "evidence_status": "not_written",
            "can_continue": True,
            "message": str(exc),
            "notebook_registry_id": notebook_registry_id,
        }

    validation = validate_schema(
        df,
        contract["columns"],
        allow_extra_columns=contract["allow_extra_columns"],
        check_column_order=contract["check_column_order"],
    )
    enforcement = _enforce_schema_result(
        validation,
        enforcement=contract["default_enforcement"],
        raise_on_fail=False,
    )
    evidence = _build_schema_validation_evidence(
        validation,
        run_id=run_id,
        agreement_id=agreement_id,
        contract_id=contract["contract_id"],
        contract_version=contract["contract_version"],
        dataset_role=dataset_role,
        table_name=table_name,
        enforcement_applied=enforcement,
        workspace_name=identity["workspace_name"],
        workspace_id=identity["workspace_id"],
        item_name=identity["item_name"],
        item_id=identity["item_id"],
    )
    evidence_df = _write_schema_validation_evidence(
        spark, evidence, config=config, env=env, metadata_table=metadata_table
    )
    result = {
        "status": enforcement["status"],
        "dataframe": df,
        "contract": contract,
        "validation": validation,
        "enforcement": enforcement,
        "evidence": evidence,
        "evidence_dataframe": evidence_df,
        "evidence_status": "written",
        "can_continue": enforcement["can_continue"],
        "notebook_registry_id": notebook_registry_id,
    }
    if not enforcement["can_continue"]:
        raise SchemaContractValidationError(
            "Schema contract validation failed before write. Evidence was written to metadata."
        )
    return result

def _build_schema_validation_evidence(
    result: dict[str, Any],
    *,
    run_id: str,
    agreement_id: str,
    contract_id: str,
    contract_version: int | str,
    dataset_role: str,
    table_name: str,
    workspace_name: str = "",
    workspace_id: str = "",
    item_name: str = "",
    item_id: str = "",
    enforcement_applied: Any = None,
) -> dict[str, Any]:
    """Build one schema-validation evidence row.

    Parameters
    ----------
    result : dict[str, Any]
        Result from :func:`validate_schema`.
    run_id, agreement_id, contract_id, contract_version, dataset_role, table_name : str
        Run, contract, and dataset identifiers.
    workspace_name, workspace_id, item_name, item_id : str, optional
        Additional dataset identity fields.
    enforcement_applied : Any, optional
        Enforcement summary returned by :func:`apply_schema_guardrail`.

    Returns
    -------
    dict[str, Any]
        Metadata row suitable for ``METADATA_SCHEMA_VALIDATION_EVIDENCE``.
    """
    return {
        "run_id": _required_identity(run_id, "run_id"),
        "agreement_id": _required_identity(agreement_id, "agreement_id"),
        "contract_id": _required_identity(contract_id, "contract_id"),
        "contract_version": str(contract_version),
        "dataset_role": _validate_dataset_role(dataset_role),
        "workspace_name": str(workspace_name or ""),
        "workspace_id": str(workspace_id or ""),
        "item_name": str(item_name or ""),
        "item_id": str(item_id or ""),
        "table_name": _required_identity(table_name, "table_name"),
        "validation_status": "passed" if result.get("is_valid") else "failed",
        "enforcement_applied": json.dumps(enforcement_applied or {}, sort_keys=True, default=str),
        "missing_columns": json.dumps(result.get("missing_required_columns") or [], sort_keys=True, default=str),
        "unexpected_columns": json.dumps(result.get("unexpected_columns") or [], sort_keys=True, default=str),
        "datatype_mismatches": json.dumps(result.get("datatype_mismatches") or [], sort_keys=True, default=str),
        "nullability_mismatches": json.dumps(result.get("nullability_mismatches") or [], sort_keys=True, default=str),
        "column_order_mismatches": json.dumps(result.get("column_order_mismatches") or [], sort_keys=True, default=str),
        "validated_at": _now_utc_iso(),
    }


def _write_schema_validation_evidence(
    spark: Any,
    evidence_rows: list[dict[str, Any]] | dict[str, Any],
    *,
    config: Any,
    env: str,
    metadata_table: str = SCHEMA_VALIDATION_EVIDENCE_TABLE,
) -> Any:
    """Write schema-validation evidence through the metadata lakehouse route.

    Parameters
    ----------
    spark : pyspark.sql.SparkSession
        Spark session used to create the evidence DataFrame.
    evidence_rows : list[dict[str, Any]] or dict[str, Any]
        Evidence rows from :func:`_build_schema_validation_evidence`.
    config : FrameworkConfig or dict
        Configuration containing the metadata lakehouse route.
    env : str
        Environment key paired with ``config``.
    metadata_table : str, default="METADATA_SCHEMA_VALIDATION_EVIDENCE"
        Metadata table name.

    Returns
    -------
    pyspark.sql.DataFrame
        Evidence DataFrame that was appended.
    """
    rows = [evidence_rows] if isinstance(evidence_rows, dict) else list(evidence_rows or [])
    if not rows:
        raise ValueError("evidence_rows are required.")
    df = spark.createDataFrame(rows)
    write_lakehouse_table(df, config, env, "metadata", metadata_table, mode="append")
    return df
