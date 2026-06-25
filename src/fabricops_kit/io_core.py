"""Metadata Lakehouse IO core used by internal governance workflows.

Notebook-facing Fabric IO public callables own their flows under
``fabricops_kit.io`` and use ``fabricops_kit.io.shared`` for reusable IO
implementation helpers. This module remains only for metadata/governance/
pipeline internals and supported store compatibility objects.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
import re

from .config import get_store, resolve_fabric_context

DEFAULT_ENV = "Sandbox"
DEFAULT_TARGET = "Source"


@dataclass(frozen=True)
class FabricStore:
    """Fabric lakehouse or warehouse connection details."""

    env: str
    workspace_id: str
    item_id: str
    name: str
    kind: str
    schema_enabled: bool = False
    schema: str | None = None

    def __post_init__(self) -> None:
        """Validate and normalize initialized values."""
        for field_name in ("env", "workspace_id", "item_id", "name", "kind"):
            value = getattr(self, field_name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{field_name} must be a non-empty string.")
        normalized_kind = self.kind.strip().lower()
        if normalized_kind not in {"lakehouse", "warehouse"}:
            raise ValueError("kind must be one of: lakehouse, warehouse.")
        object.__setattr__(self, "kind", normalized_kind)
        object.__setattr__(self, "schema_enabled", bool(self.schema_enabled))
        schema_value = None if self.schema is None else str(self.schema).strip()
        if self.schema_enabled and normalized_kind == "lakehouse":
            if not schema_value:
                raise ValueError("schema is required when schema_enabled is True for a lakehouse store.")
            if any(separator in schema_value for separator in ("/", "\\", ".")):
                raise ValueError("schema must be a simple schema name; do not use paths or dots.")
            if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", schema_value):
                raise ValueError("schema must contain only letters, numbers, and underscores, and must not start with a number.")
        object.__setattr__(self, "schema", schema_value or None)

    @property
    def root(self) -> str:
        """Return the OneLake ABFSS root for lakehouse stores."""
        if self.kind != "lakehouse":
            raise ValueError("root is only available for lakehouse stores.")
        return f"abfss://{self.workspace_id}@onelake.dfs.fabric.microsoft.com/{self.item_id}"


# ---------------------------------------------------------------------------
# Utility layer: small pure helpers only.
# ---------------------------------------------------------------------------


def _join_lakehouse_area_path(store: FabricStore, area: str, relative_path: str) -> str:
    """Return an ABFSS path under a lakehouse area."""
    return f"{store.root.rstrip('/')}/{area.strip('/')}/{relative_path.strip('/')}"


def _resolve_lakehouse_table_identifier(store: FabricStore, table_name: str, schema_name: str | None = None) -> str:
    """Return the Spark table identifier for an already-normalized lakehouse table."""
    return f"{schema_name}.{table_name}" if schema_name else table_name


# ---------------------------------------------------------------------------
# Validator layer: input shape and runtime-target validation.
# ---------------------------------------------------------------------------


def _normalize_table_name(table: str) -> str:
    """Return a safe table identifier."""
    value = str(table or "").strip()
    if not value:
        raise ValueError("table is required.")
    if any(separator in value for separator in ("/", "\\", ".")):
        raise ValueError("table must be a simple table name; pass schema separately and do not use paths or dots.")
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", value):
        raise ValueError("table must contain only letters, numbers, and underscores, and must not start with a number.")
    return value


def _normalize_schema_name(schema: str | None) -> str | None:
    """Return a safe schema identifier, or None when omitted."""
    if schema is None:
        return None
    value = str(schema).strip()
    if not value:
        raise ValueError("schema must be a non-empty identifier when provided.")
    if any(separator in value for separator in ("/", "\\", ".")):
        raise ValueError("schema must be a simple schema name; do not use paths or dots.")
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", value):
        raise ValueError("schema must contain only letters, numbers, and underscores, and must not start with a number.")
    return value


def _normalize_write_mode(mode: str) -> str:
    """Return a supported Spark write mode."""
    value = str(mode or "").lower().strip()
    if value not in {"append", "overwrite", "errorifexists", "ignore"}:
        raise ValueError("mode must be one of append, overwrite, errorifexists, ignore.")
    return value


def _validate_lakehouse_store(store: FabricStore, env: str, target: str) -> None:
    """Validate that a resolved store is a lakehouse."""
    if store.kind != "lakehouse":
        raise ValueError(f"Target '{env}/{target}' is not a lakehouse store.")


def _validate_warehouse_store(store: FabricStore, env: str, target: str) -> None:
    """Validate that a resolved store is a warehouse."""
    if store.kind != "warehouse":
        raise ValueError(f"Target '{env}/{target}' is not a warehouse store.")


def _validate_dataframe_writer(df) -> None:
    """Validate that the object exposes the Spark DataFrame write contract."""
    if not hasattr(df, "write"):
        raise ValueError("df must be a Spark DataFrame-like object with a write attribute.")


# ---------------------------------------------------------------------------
# Resolver layer: context, stores, physical paths, and connector targets.
# ---------------------------------------------------------------------------


def get_spark(spark_session=None):
    """Return an explicit Spark session or the active notebook global spark."""
    if spark_session is not None:
        return spark_session
    try:
        return globals()["spark"]
    except KeyError as exc:
        raise RuntimeError("Spark session was not provided and global 'spark' was not found. Run this inside Fabric/Spark or pass spark_session explicitly.") from exc


def resolve_target_store(target: str, expected_kind: str, *, context: dict[str, Any] | None = None) -> tuple[FabricStore, str]:
    """Resolve a configured Fabric target and validate its store kind."""
    config, env, _context = resolve_fabric_context(context=context)
    store = get_store(config, env, target)
    if expected_kind == "lakehouse":
        _validate_lakehouse_store(store, env, target)
    elif expected_kind == "warehouse":
        _validate_warehouse_store(store, env, target)
    else:
        raise ValueError("expected_kind must be one of: lakehouse, warehouse.")
    return store, env


def _resolve_lakehouse_schema(store: FabricStore, schema: str | None) -> str | None:
    """Resolve explicit or configured lakehouse schema names."""
    return _normalize_schema_name(schema if schema is not None else (store.schema if store.schema_enabled else None))


def _resolve_lakehouse_table_path(store: FabricStore, table_name: str, schema_name: str | None = None) -> str:
    """Return the physical OneLake Delta table path."""
    table_relative_path = f"{schema_name}/{table_name}" if schema_name else table_name
    return _join_lakehouse_area_path(store, "Tables", table_relative_path)


def _resolve_lakehouse_table_location(store: FabricStore, table_name: str, schema: str | None) -> tuple[str, str | None, str]:
    """Resolve a lakehouse table to normalized table, schema, and path."""
    table_value = _normalize_table_name(table_name)
    schema_value = _resolve_lakehouse_schema(store, schema)
    return table_value, schema_value, _resolve_lakehouse_table_path(store, table_value, schema_value)


def configured_lakehouse_schema(config: Any, env: str, target: str) -> str | None:
    """Return the configured schema for a schema-enabled lakehouse target."""
    try:
        store = get_store(config, env, target)
    except ValueError:
        return None
    if store.kind != "lakehouse" or not getattr(store, "schema_enabled", False):
        return None
    return _normalize_schema_name(getattr(store, "schema", None))


# ---------------------------------------------------------------------------
# Adapter layer: runtime connector and Spark/pandas calls.
# ---------------------------------------------------------------------------


def _read_delta_path(spark_obj, path: str):
    """Read a Delta path through Spark."""
    return spark_obj.read.format("delta").load(path)


def _write_delta_path(df, path: str, *, mode: str, partition_by=None, options: dict[str, Any] | None = None) -> None:
    """Write a DataFrame to a Delta path through Spark."""
    writer = df.write.mode(mode).format("delta")
    if partition_by is not None:
        writer = writer.partitionBy(*partition_by) if isinstance(partition_by, (list, tuple)) else writer.partitionBy(partition_by)
    for key, value in (options or {}).items():
        writer = writer.option(key, value)
    writer.save(path)


# ---------------------------------------------------------------------------
# Shared metadata IO workflows used by non-public orchestration modules.
# ---------------------------------------------------------------------------


def read_lakehouse_table_core(table_name: str, *, target: str, schema: str | None = None, spark_session=None, context: dict[str, Any] | None = None):
    """Read a Lakehouse Delta table for metadata and orchestration internals.

    This remains in ``io_core`` because governance, metadata, pipeline, config,
    guardrail, and data-agreement internals share configured metadata table
    reads. Notebook-facing IO public functions own their implementation in
    ``fabricops_kit.io`` and do not call this compatibility workflow.
    """
    store, _env = resolve_target_store(target, "lakehouse", context=context)
    _table_value, _schema_value, path = _resolve_lakehouse_table_location(store, table_name, schema)
    return _read_delta_path(get_spark(spark_session), path)


def write_lakehouse_table_core(df, table_name: str, *, target: str, schema: str | None = None, mode: str = "append", partition_by=None, repartition_by=None, options=None, verbose: bool = True, context=None):
    """Write a Lakehouse Delta table for metadata and orchestration internals.

    This remains in ``io_core`` because governance, metadata, pipeline, config,
    guardrail, and data-agreement internals share configured metadata table
    writes. Notebook-facing IO public functions own their implementation in
    ``fabricops_kit.io`` and do not call this compatibility workflow.
    """
    _validate_dataframe_writer(df)
    store, _env = resolve_target_store(target, "lakehouse", context=context)
    _table_value, _schema_value, path = _resolve_lakehouse_table_location(store, table_name, schema)
    normalized_mode = _normalize_write_mode(mode)
    if repartition_by is not None:
        if isinstance(repartition_by, (list, tuple)):
            df = df.repartition(*repartition_by) if not (repartition_by and isinstance(repartition_by[0], int)) else df.repartition(repartition_by[0], *repartition_by[1:])
        else:
            df = df.repartition(repartition_by)
    if verbose:
        print(f"Writing Lakehouse table to {path}")
    _write_delta_path(df, path, mode=normalized_mode, partition_by=partition_by, options=options)
