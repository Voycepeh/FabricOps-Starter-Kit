from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any
from .fabric_input_output import read_lakehouse_table, write_lakehouse_table

EVIDENCE_SOURCE_PROFILE = "source_profile"
EVIDENCE_OUTPUT_PROFILE = "output_profile"
EVIDENCE_DRIFT_RESULT = "drift_result"
EVIDENCE_LINEAGE = "lineage"
EVIDENCE_BUSINESS_CONTEXT = "business_context"
EVIDENCE_GOVERNANCE_CONTEXT = "governance_context"

NOTEBOOK_REGISTRY_TABLE = "METADATA_NOTEBOOK_REGISTRY"
NOTEBOOK_REGISTRY_BASE_FIELDS = [
    "agreement_id",
    "environment_name",
    "dataset_name",
    "table_name",
    "topic",
    "pipeline_name",
    "notebook_type",
    "workspace_id",
    "workspace_name",
    "notebook_id",
    "notebook_name",
    "notebook_url",
    "user_name",
    "user_id",
    "registered_at",
]

NOTEBOOK_REGISTRY_STATE_FIELDS = [
    "registration_id",
    "agreement_contract_version",
    "registration_role",
    "registration_status",
    "superseded_at",
    "superseded_by_registration_id",
]

NOTEBOOK_REGISTRY_FIELDS = [*NOTEBOOK_REGISTRY_BASE_FIELDS, *NOTEBOOK_REGISTRY_STATE_FIELDS]


def _get_notebook_registry_schema() -> list[str]:
    """Return the required notebook registry metadata schema.

    Returns
    -------
    list[str]
        Column names written by :func:`_register_current_notebook` and required
        by :func:`_setup_notebook_registry_table`.

    Notes
    -----
    The notebook registry schema intentionally does not include a generated
    ``notebook_registry_key`` column. Notebook registrations are append-only
    evidence rows keyed by agreement and runtime notebook context.
    """
    return list(NOTEBOOK_REGISTRY_FIELDS)


def _notebook_registry_base_schema() -> list[str]:
    """Return columns required by legacy notebook registry tables."""
    return list(NOTEBOOK_REGISTRY_BASE_FIELDS)


def _notebook_registration_key(row: dict[str, Any]) -> str:
    parts = [
        str(row.get("workspace_id") or ""),
        str(row.get("notebook_id") or ""),
        str(row.get("notebook_name") or ""),
        str(row.get("agreement_id") or ""),
        str(row.get("agreement_contract_version") or ""),
        str(row.get("registration_role") or ""),
    ]
    return hashlib.sha256("||".join(parts).encode("utf-8")).hexdigest()[:24]


def _coerce_row_dicts(rows: Any) -> list[dict[str, Any]]:
    if rows is None:
        return []
    if hasattr(rows, "collect"):
        rows = rows.collect()
    return [row.asDict(recursive=True) if hasattr(row, "asDict") else dict(row) for row in rows]


def _column_names(rows_or_df: Any) -> list[str]:
    if hasattr(rows_or_df, "columns"):
        return list(rows_or_df.columns)
    rows = _coerce_row_dicts(rows_or_df)
    return list(rows[0]) if rows else []


def _setup_notebook_registry_table(*, spark: Any, config: Any, env: str, metadata_table: str = NOTEBOOK_REGISTRY_TABLE) -> dict[str, Any]:
    """Create or validate the notebook registry metadata table.

    Parameters
    ----------
    spark : pyspark.sql.SparkSession
        Fabric Spark session used to create an empty table when the registry is
        missing.
    config : FrameworkConfig or dict
        Configuration containing the metadata lakehouse route from
        ``00_env_config``.
    env : str
        Environment key configured by ``00_env_config``.
    metadata_table : str, default=NOTEBOOK_REGISTRY_TABLE
        Physical metadata table name to prepare.

    Returns
    -------
    dict[str, Any]
        Setup status, checked table, schema, and whether the table was created.

    Raises
    ------
    ValueError
        If an existing table is missing required registry columns.

    Notes
    -----
    This helper is separate from ``_setup_data_agreement_tables`` because the
    registry is workflow-notebook bootstrap metadata, not ``01_agreement`` agreement
    intake metadata. Reads and writes use the configured ``metadata`` target
    from ``00_env_config``.
    """
    fields = _get_notebook_registry_schema()
    created = False
    try:
        table = read_lakehouse_table(config, env, "metadata", metadata_table, spark_session=spark)
    except Exception:
        empty_df = spark.createDataFrame([{field: "" for field in fields}]).limit(0)
        write_lakehouse_table(empty_df, config, env, "metadata", metadata_table, mode="ignore", overwrite_schema=True)
        table = read_lakehouse_table(config, env, "metadata", metadata_table, spark_session=spark)
        created = True

    columns = _column_names(table)
    missing_base = [field for field in NOTEBOOK_REGISTRY_BASE_FIELDS if field not in columns]
    if missing_base:
        raise ValueError(f"{metadata_table} is missing required column(s): {', '.join(missing_base)}. Migrate or recreate the notebook registry table before workflow notebooks register themselves.")

    migrated = False
    missing_state = [field for field in NOTEBOOK_REGISTRY_STATE_FIELDS if field not in columns]
    if missing_state:
        existing_rows = _coerce_row_dicts(table)
        migrated_rows = []
        for row in existing_rows:
            migrated_row = {field: _safe_str(row.get(field)) for field in NOTEBOOK_REGISTRY_BASE_FIELDS}
            migrated_row["agreement_contract_version"] = _safe_str(row.get("agreement_contract_version"))
            migrated_row["registration_role"] = _safe_str(row.get("registration_role") or "primary")
            migrated_row["registration_status"] = _safe_str(row.get("registration_status") or "active")
            migrated_row["superseded_at"] = _safe_str(row.get("superseded_at"))
            migrated_row["superseded_by_registration_id"] = _safe_str(row.get("superseded_by_registration_id"))
            migrated_row["registration_id"] = _safe_str(row.get("registration_id") or _notebook_registration_key(migrated_row))
            migrated_rows.append({field: migrated_row.get(field, "") for field in fields})
        df = spark.createDataFrame(_column_context_rows_for_spark(migrated_rows or [{field: "" for field in fields}])).limit(0 if not migrated_rows else len(migrated_rows))
        write_lakehouse_table(df, config, env, "metadata", metadata_table, mode="overwrite", overwrite_schema=True)
        migrated = True
    return {"status": "ready", "table": metadata_table, "schema": fields, "created": created, "migrated": migrated, "created_tables": [metadata_table] if created else []}


def _default_evidence_types() -> dict[str, str]:
    """Return canonical evidence type names used across metadata records."""
    return {
        "source_profile": EVIDENCE_SOURCE_PROFILE,
        "output_profile": EVIDENCE_OUTPUT_PROFILE,
        "drift_result": EVIDENCE_DRIFT_RESULT,
        "lineage": EVIDENCE_LINEAGE,
        "business_context": EVIDENCE_BUSINESS_CONTEXT,
        "governance_context": EVIDENCE_GOVERNANCE_CONTEXT,
    }


def _build_evidence_row(*, dataset_name: str, table_name: str, run_id: str | None, evidence_type: str, payload_json: str, workspace_id: str | None = None, workspace_name: str | None = None, notebook_id: str | None = None, notebook_name: str | None = None, created_at: str | None = None) -> dict:
    """Build a lightweight metadata-ready evidence row."""
    return {
        "dataset_name": dataset_name,
        "table_name": table_name,
        "run_id": run_id,
        "workspace_id": workspace_id,
        "workspace_name": workspace_name,
        "notebook_id": notebook_id,
        "notebook_name": notebook_name,
        "evidence_type": evidence_type,
        "payload_json": payload_json,
        "created_at": created_at or _now_utc_iso(),
    }


def _now_utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _resolve_action_by(action_by: str | None = None) -> str:
    if action_by:
        return str(action_by)
    context = _runtime_context()
    return str(_context_get(context, "userName", "userId") or "unknown")


def _key_part(value) -> str:
    return str(value or "").strip().lower()


def _sha256_key(*parts) -> str:
    normalized = "|".join(_key_part(p) for p in parts)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def _build_metadata_table_key(environment_name, dataset_name, table_name) -> str:
    return _sha256_key(environment_name, dataset_name, table_name)


def _build_metadata_column_key(environment_name, dataset_name, table_name, column_name) -> str:
    return _sha256_key(environment_name, dataset_name, table_name, column_name)


def _build_dq_rule_key(environment_name, dataset_name, table_name, rule_id) -> str:
    return _sha256_key(environment_name, dataset_name, table_name, rule_id)


def _extract_columns_from_profile(profile_rows) -> list[str]:
    cols = []
    for row in profile_rows or []:
        c = row.get("column_name") or row.get("COLUMN_NAME")
        if c:
            cols.append(str(c))
    return sorted(set(cols))


def _normalise_records_by_column(records) -> dict[str, dict]:
    out = {}
    for row in records or []:
        key = str(row.get("column_name") or row.get("COLUMN_NAME") or "")
        if key:
            out[key] = dict(row)
    return out


def _column_context_rows_for_spark(rows: list[dict]) -> list[dict]:
    out = []
    for row in rows or []:
        item = dict(row)
        if isinstance(item.get("approved_at"), datetime):
            item["approved_at"] = item["approved_at"].isoformat()
        if isinstance(item.get("ai_suggestion_json"), (dict, list)):
            item["ai_suggestion_json"] = json.dumps(item["ai_suggestion_json"], sort_keys=True)
        out.append(item)
    return out


def _write_metadata_rows(spark, rows: list[dict], metadata_path, table_name: str, mode: str = "append"):
    """Write metadata rows to a legacy lakehouse metadata path."""
    df = spark.createDataFrame(_column_context_rows_for_spark(rows))
    _write_metadata_rows_legacy(df, metadata_path=metadata_path, table_name=table_name, mode=mode)
    return df


def _write_metadata_rows_legacy(df: Any, metadata_path: Any, table_name: str, mode: str = "append") -> None:
    """Write metadata rows using the pre-route lakehouse path convention."""
    root = getattr(metadata_path, "root", None) or str(metadata_path or "").strip()
    if not root:
        raise ValueError("metadata_path must be a FabricStore-like object or lakehouse root path.")
    path = f"{root.rstrip('/')}/Tables/{table_name}"
    writer = df.write.format("delta").mode(mode).option("overwriteSchema", "true")
    writer.save(path)


def _write_column_business_context(spark, rows: list[dict], metadata_path, table_name: str = "METADATA_COLUMN_CONTEXT", mode: str = "append"):
    return _write_metadata_rows(spark, rows, metadata_path, table_name, mode=mode)


def _write_column_governance_context(spark, rows: list[dict], metadata_path, table_name: str = "METADATA_COLUMN_CLASSIFICATION", mode: str = "append"):
    return _write_metadata_rows(spark, rows, metadata_path, table_name, mode=mode)


def _context_get(context: Any, *keys: str) -> Any:
    for key in keys:
        try:
            if isinstance(context, dict):
                value = context.get(key)
            else:
                getter = getattr(context, "get", None)
                value = getter(key) if callable(getter) else None
        except Exception:
            value = None
        if value is not None:
            return value
    return None


def _safe_str(value: Any) -> str:
    return "" if value is None else str(value)


def _runtime_context() -> dict[str, Any]:
    try:
        import notebookutils  # type: ignore
    except Exception:
        return {}

    runtime = getattr(notebookutils, "runtime", None)
    context = getattr(runtime, "context", None)
    if context is None:
        return {}

    keys = [
        "currentWorkspaceId",
        "currentWorkspaceName",
        "currentNotebookId",
        "currentNotebookName",
        "workspaceId",
        "workspaceName",
        "notebookId",
        "notebookName",
        "userId",
        "userName",
        "activityId",
    ]
    return {key: _context_get(context, key) for key in keys}


def _build_runtime_audit_fields(
    *,
    config: Any = None,
    env: str | None = None,
    timestamp_field: str = "_committed_at",
    user_field: str = "_committed_by",
    workspace_field: str = "_workspace_name",
    notebook_field: str = "_notebook_name",
    metadata_lakehouse_field: str = "_metadata_lakehouse_name",
    activity_field: str = "_activity_id",
    committed_by: str | None = None,
    committed_at: str | None = None,
    runtime_context: dict[str, Any] | None = None,
) -> dict[str, str]:
    """Build reusable framework-managed audit fields for metadata-table rows.

    Parameters
    ----------
    config : FrameworkConfig | dict, optional
        Framework config containing ``path_config.paths[env]["metadata"]``.
    env : str, optional
        Environment key paired with ``config``.
    timestamp_field, user_field, workspace_field, notebook_field : str
        Output keys for timestamp, user, workspace, and notebook audit values.
    metadata_lakehouse_field, activity_field : str
        Output keys for metadata lakehouse and Fabric activity audit values.
    committed_by, committed_at : str, optional
        Deterministic audit overrides. When omitted, values resolve from Fabric
        runtime context and the current UTC timestamp.
    runtime_context : dict[str, Any], optional
        Values merged over :func:`_runtime_context`, primarily for tests or
        controlled notebook overrides.

    Returns
    -------
    dict[str, str]
        Framework-managed metadata audit values keyed by the supplied field
        names.

    Notes
    -----
    DataFrame runtime audit columns and metadata-table audit fields both use
    underscore-prefixed names. This helper centralizes the metadata-table
    convention so notebooks can reuse runtime context when adding dataframe
    audit columns inline.
    """
    context = {**_runtime_context(), **(runtime_context or {})}

    def _first_non_blank(*keys: str) -> Any:
        for key in keys:
            value = _context_get(context, key)
            if value is not None and str(value).strip():
                return value
        return None

    metadata_lakehouse_name = ""
    if config is not None and env is not None:
        paths = config.path_config.paths if hasattr(config, "path_config") else config.paths
        metadata_lakehouse_name = _safe_str(paths[env]["metadata"].name)
    return {
        user_field: _safe_str(committed_by).strip() if committed_by and _safe_str(committed_by).strip() else _safe_str(_first_non_blank("userName", "userId") or "unknown"),
        timestamp_field: _safe_str(committed_at) if committed_at else datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        workspace_field: _safe_str(_first_non_blank("currentWorkspaceName", "workspaceName") or ""),
        notebook_field: _safe_str(_first_non_blank("currentNotebookName", "notebookName") or ""),
        metadata_lakehouse_field: metadata_lakehouse_name,
        activity_field: _safe_str(_first_non_blank("activityId") or ""),
    }


def _register_current_notebook(
    spark,
    metadata_path=None,
    agreement_id=None,
    notebook_type=None,
    environment_name=None,
    dataset_name=None,
    table_name=None,
    topic=None,
    pipeline_name=None,
    contract_version=None,
    registration_role="primary",
    registration_status="active",
    registration_id=None,
    superseded_at=None,
    superseded_by_registration_id=None,
    metadata_table=NOTEBOOK_REGISTRY_TABLE,
    *,
    config: Any = None,
    env: str | None = None,
):
    """Append a runtime notebook registration row.

    Parameters
    ----------
    spark : pyspark.sql.SparkSession
        Fabric Spark session used to append the registration row.
    config : FrameworkConfig or dict, optional
        Recommended metadata route configuration from ``00_env_config``. When
        paired with ``env``, the row is written through
        ``write_lakehouse_table(df, config, env, "metadata", metadata_table)``.
    env : str, optional
        Environment key paired with ``config`` for metadata lakehouse routing.
    metadata_path : Any, optional
        Backward-compatible lakehouse store or root path. Prefer ``config`` and
        ``env`` for new notebooks.
    agreement_id : str
        Agreement identifier this notebook supports.
    notebook_type : str
        Notebook family or workflow phase. When blank, the value is inferred
        from the current notebook name prefix.
    environment_name, dataset_name, table_name, topic, pipeline_name : str, optional
        Optional workflow context recorded with the notebook registration.
    contract_version : str, optional
        Agreement contract version selected when the notebook was registered.
    registration_role : {"primary", "additional"}, default="primary"
        Whether the row represents the notebook's user-facing active agreement
        or an additional audit link.
    registration_status : {"active", "superseded"}, default="active"
        Current registration event state. Superseded rows are retained for audit
        and ignored by active-registration helpers.
    registration_id : str, optional
        Stable registration identifier. When omitted, a deterministic identifier
        is generated from the notebook and agreement identity.
    superseded_at, superseded_by_registration_id : str, optional
        Audit values populated when a prior registration is superseded.
    metadata_table : str, default=NOTEBOOK_REGISTRY_TABLE
        Physical notebook registry table name.

    Returns
    -------
    dict[str, str]
        Registration row matching :func:`_get_notebook_registry_schema`.

    Raises
    ------
    ValueError
        If neither the recommended ``config``/``env`` route nor a legacy
        ``metadata_path`` is provided.

    Notes
    -----
    Prepare the registry with :func:`_setup_notebook_registry_table` before
    workflow notebooks register themselves. New notebooks should pass
    ``config=CONFIG`` and ``env=ENV`` so metadata writes use the configured
    ``metadata`` target from ``00_env_config``.
    """
    if (config is None or env is None) and metadata_path is None:
        raise ValueError("_register_current_notebook requires config and env for metadata routing. Pass metadata_path only for legacy notebooks.")

    ctx = _runtime_context()
    workspace_id = _context_get(ctx, "currentWorkspaceId", "workspaceId")
    workspace_name = _context_get(ctx, "currentWorkspaceName", "workspaceName")
    notebook_id = _context_get(ctx, "currentNotebookId", "notebookId")
    notebook_name = _context_get(ctx, "currentNotebookName", "notebookName") or "unknown_notebook"
    user_id = _context_get(ctx, "userId")
    user_name = _context_get(ctx, "userName")
    inferred_type = notebook_type or str(notebook_name).split("_", 1)[0]
    row = {
        "agreement_id": _safe_str(agreement_id),
        "environment_name": _safe_str(environment_name),
        "dataset_name": _safe_str(dataset_name),
        "table_name": _safe_str(table_name),
        "topic": _safe_str(topic),
        "pipeline_name": _safe_str(pipeline_name),
        "notebook_type": _safe_str(inferred_type),
        "workspace_id": _safe_str(workspace_id),
        "workspace_name": _safe_str(workspace_name),
        "notebook_id": _safe_str(notebook_id),
        "notebook_name": _safe_str(notebook_name),
        "notebook_url": _safe_str(f"https://app.fabric.microsoft.com/groups/{workspace_id}/notebooks/{notebook_id}" if workspace_id and notebook_id else ""),
        "user_name": _safe_str(user_name),
        "user_id": _safe_str(user_id),
        "registered_at": datetime.now(timezone.utc).isoformat(),
        "agreement_contract_version": _safe_str(contract_version),
        "registration_role": _safe_str(registration_role or "primary"),
        "registration_status": _safe_str(registration_status or "active"),
        "superseded_at": _safe_str(superseded_at),
        "superseded_by_registration_id": _safe_str(superseded_by_registration_id),
    }
    row["registration_id"] = _safe_str(registration_id or _notebook_registration_key(row))
    row = {field: row.get(field, "") for field in NOTEBOOK_REGISTRY_FIELDS}
    df = spark.createDataFrame(_column_context_rows_for_spark([row]))
    if config is not None and env is not None:
        write_lakehouse_table(df, config, env, "metadata", metadata_table, mode="append")
    elif metadata_path is not None:
        _write_metadata_rows_legacy(df, metadata_path=metadata_path, table_name=metadata_table, mode="append")
    return row


def _registry_rows_with_defaults(rows: Any) -> list[dict[str, Any]]:
    out = []
    for source in _coerce_row_dicts(rows):
        row = {field: _safe_str(source.get(field)) for field in NOTEBOOK_REGISTRY_BASE_FIELDS}
        row["agreement_contract_version"] = _safe_str(source.get("agreement_contract_version"))
        row["registration_role"] = _safe_str(source.get("registration_role") or "primary")
        row["registration_status"] = _safe_str(source.get("registration_status") or "active")
        row["superseded_at"] = _safe_str(source.get("superseded_at"))
        row["superseded_by_registration_id"] = _safe_str(source.get("superseded_by_registration_id"))
        row["registration_id"] = _safe_str(source.get("registration_id") or _notebook_registration_key(row))
        out.append({field: row.get(field, "") for field in NOTEBOOK_REGISTRY_FIELDS})
    return out


def _latest_registration_events(rows: Any) -> list[dict[str, Any]]:
    latest: dict[str, dict[str, Any]] = {}
    for row in _registry_rows_with_defaults(rows):
        key = row.get("registration_id") or _notebook_registration_key(row)
        previous = latest.get(key)
        if previous is None or str(row.get("registered_at") or "") >= str(previous.get("registered_at") or ""):
            latest[key] = row
    return list(latest.values())


def _load_notebook_registry(spark, agreement_id=None, metadata_table=NOTEBOOK_REGISTRY_TABLE, notebook_type=None, environment_name=None, missing_ok: bool = True, *, config: Any = None, env: str | None = None, active_only: bool = False, notebook_id: str | None = None, notebook_name: str | None = None, registration_role: str | None = None) -> list[dict[str, Any]]:
    try:
        table = read_lakehouse_table(config, env, "metadata", metadata_table, spark_session=spark) if config is not None and env is not None else spark.table(metadata_table)
        rows = _registry_rows_with_defaults(table)
    except Exception:
        if missing_ok:
            return []
        raise
    rows = _latest_registration_events(rows) if active_only else rows
    out = []
    for row in rows:
        if agreement_id is not None and str(row.get("agreement_id") or "") != str(agreement_id):
            continue
        if notebook_type and str(row.get("notebook_type") or "") != str(notebook_type):
            continue
        if environment_name and str(row.get("environment_name") or "") != str(environment_name):
            continue
        if notebook_id and str(row.get("notebook_id") or "") != str(notebook_id):
            continue
        if notebook_name and str(row.get("notebook_name") or "") != str(notebook_name):
            continue
        if registration_role and str(row.get("registration_role") or "") != str(registration_role):
            continue
        if active_only and str(row.get("registration_status") or "active") != "active":
            continue
        out.append(row)
    return out


def _current_notebook_active_registrations(spark, *, config: Any, env: str, metadata_table: str = NOTEBOOK_REGISTRY_TABLE, notebook_type: str | None = None, environment_name: str | None = None, registration_role: str | None = None, missing_ok: bool = True) -> list[dict[str, Any]]:
    """Return active agreement registrations for the running notebook.

    Parameters
    ----------
    spark : pyspark.sql.SparkSession
        Fabric Spark session used to read the metadata table.
    config : FrameworkConfig or dict
        Metadata route configuration from ``00_env_config``.
    env : str
        Environment key paired with ``config``.
    metadata_table : str, default=NOTEBOOK_REGISTRY_TABLE
        Physical notebook registry table name.
    notebook_type, environment_name, registration_role : str, optional
        Optional filters for notebook phase, environment, and primary versus
        additional registration role.
    missing_ok : bool, default=True
        Return an empty list when the registry cannot be read.

    Returns
    -------
    list[dict[str, Any]]
        Active latest registration rows for the current notebook runtime.
    """
    ctx = _runtime_context()
    notebook_id = _safe_str(_context_get(ctx, "currentNotebookId", "notebookId"))
    notebook_name = _safe_str(_context_get(ctx, "currentNotebookName", "notebookName") or "unknown_notebook")
    rows = _load_notebook_registry(spark, metadata_table=metadata_table, notebook_type=notebook_type, environment_name=environment_name, missing_ok=missing_ok, config=config, env=env, active_only=True, notebook_id=notebook_id or None, notebook_name=None if notebook_id else notebook_name, registration_role=registration_role)
    return rows
