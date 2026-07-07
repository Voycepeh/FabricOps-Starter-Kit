"""Notebook registry helpers for widget-owned registration workflows."""

from __future__ import annotations

import hashlib
from typing import Any

from fabricops_kit.io.shared import (
    configured_lakehouse_schema,
    read_lakehouse_table_core,
    write_lakehouse_table_core,
)
from fabricops_kit.config.audit import _audit_timestamp_value, _context_get, _runtime_context, _safe_str, build_runtime_audit_fields
from fabricops_kit.config.metadata_schemas import AUDIT_SCHEMA_FIELDS, coerce_metadata_row_types

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

NOTEBOOK_REGISTRY_AUDIT_FIELDS = [name for name, _kind, _nullable in AUDIT_SCHEMA_FIELDS]
NOTEBOOK_REGISTRY_FIELDS = [*NOTEBOOK_REGISTRY_BASE_FIELDS, *NOTEBOOK_REGISTRY_STATE_FIELDS, *NOTEBOOK_REGISTRY_AUDIT_FIELDS]


def _coerce_row_dicts(rows):
    if rows is None:
        return []
    if hasattr(rows, "collect"):
        rows = rows.collect()
    return [row.asDict(recursive=True) if hasattr(row, "asDict") else dict(row) for row in rows]


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


def register_current_notebook(
    spark,
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
    metadata_schema: str | None = None,
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
        ``write_lakehouse_table(df, metadata_table, schema=<configured_metadata_schema>)``.
    env : str, optional
        Environment key paired with ``config`` for metadata lakehouse routing.
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
    metadata_schema : str, optional
        Explicit metadata Lakehouse schema override. When omitted, the helper
        uses the configured metadata target schema when schema routing is
        enabled.

    Returns
    -------
    dict[str, str]
        Registration row matching :data:`NOTEBOOK_REGISTRY_FIELDS`.

    Raises
    ------
    ValueError
        If the recommended ``config``/``env`` route is not provided.

    Notes
    -----
    ``00_env_config`` prepares the notebook registry as part of
    :func:`fabricops_kit.config.setup_metadata_tables`. New notebooks should
    pass ``config=CONFIG`` and ``env=ENV`` so metadata writes use the
    configured ``metadata`` target from ``00_env_config``.

    """
    if config is None or env is None:
        raise ValueError("register_current_notebook requires config and env for metadata routing.")

    ctx = _runtime_context()
    audit = build_runtime_audit_fields(config=config, env=env, runtime_context=ctx)
    workspace_id = audit["_workspace_id"]
    workspace_name = audit["_workspace_name"]
    notebook_id = audit["_notebook_id"]
    notebook_name = audit["_notebook_name"]
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
        "notebook_url": _safe_str(
            f"https://app.fabric.microsoft.com/groups/{workspace_id}/notebooks/{notebook_id}"
            if workspace_id and notebook_id
            else ""
        ),
        "user_name": _safe_str(user_name),
        "user_id": _safe_str(user_id),
        "registered_at": _audit_timestamp_value(config),
        "agreement_contract_version": _safe_str(contract_version),
        "registration_role": _safe_str(registration_role or "primary"),
        "registration_status": _safe_str(registration_status or "active"),
        "superseded_at": _safe_str(superseded_at),
        "superseded_by_registration_id": _safe_str(superseded_by_registration_id),
        **audit,
    }
    row["registration_id"] = _safe_str(registration_id or _notebook_registration_key(row))
    row = {field: row.get(field, "") for field in NOTEBOOK_REGISTRY_FIELDS}
    df = spark.createDataFrame([coerce_metadata_row_types(metadata_table, row)])
    write_lakehouse_table_core(
        df,
        metadata_table,
        target="metadata",
        schema=metadata_schema or configured_lakehouse_schema(config, env, "metadata"),
        context={"config": config, "env": env},
        mode="append",
    )
    return row


def _load_notebook_registry(
    spark,
    agreement_id=None,
    metadata_table=NOTEBOOK_REGISTRY_TABLE,
    notebook_type=None,
    environment_name=None,
    missing_ok: bool = True,
    *,
    config: Any = None,
    env: str | None = None,
    active_only: bool = False,
    notebook_id: str | None = None,
    notebook_name: str | None = None,
    registration_role: str | None = None,
    metadata_schema: str | None = None,
) -> list[dict[str, Any]]:
    if config is None or env is None:
        raise ValueError("config and env are required to read notebook registry metadata without an attached default lakehouse.")
    try:
        table = read_lakehouse_table_core(
            metadata_table,
            target="metadata",
            schema=metadata_schema or configured_lakehouse_schema(config, env, "metadata"),
            context={"config": config, "env": env},
            spark_session=spark,
        )
        rows = _coerce_row_dicts(table)
    except Exception:
        if missing_ok:
            return []
        raise
    if active_only:
        latest: dict[str, dict[str, Any]] = {}
        for row in rows:
            key = row.get("registration_id") or _notebook_registration_key(row)
            previous = latest.get(key)
            if previous is None or str(row.get("registered_at") or "") >= str(previous.get("registered_at") or ""):
                latest[key] = row
        rows = list(latest.values())
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


def current_notebook_active_registrations(
    spark,
    *,
    config: Any,
    env: str,
    metadata_table: str = NOTEBOOK_REGISTRY_TABLE,
    notebook_type: str | None = None,
    environment_name: str | None = None,
    registration_role: str | None = None,
    metadata_schema: str | None = None,
    missing_ok: bool = True,
) -> list[dict[str, Any]]:
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
    metadata_schema : str, optional
        Explicit metadata Lakehouse schema override used when reading the
        notebook registry.

    Returns
    -------
    list[dict[str, Any]]
        Active latest registration rows for the current notebook runtime.

    """
    ctx = _runtime_context()
    notebook_id = _safe_str(_context_get(ctx, "currentNotebookId", "notebookId"))
    notebook_name = _safe_str(_context_get(ctx, "currentNotebookName", "notebookName") or "unknown_notebook")
    rows = _load_notebook_registry(
        spark,
        metadata_table=metadata_table,
        notebook_type=notebook_type,
        environment_name=environment_name,
        missing_ok=missing_ok,
        config=config,
        env=env,
        active_only=True,
        notebook_id=notebook_id or None,
        notebook_name=None if notebook_id else notebook_name,
        registration_role=registration_role,
        metadata_schema=metadata_schema,
    )
    return rows
