"""Owner file for lightweight table observation and incremental read planning."""

from __future__ import annotations

from datetime import UTC, datetime
import hashlib
import json
import re
from typing import Any

from fabricops_kit.config.audit import build_runtime_audit_fields
from fabricops_kit.config.metadata_schemas import coerce_metadata_row_types, metadata_table_schema_registry
from fabricops_kit.config.shared import get_store, is_table_not_found_error, resolve_fabric_context
from fabricops_kit.io.shared import (
    configured_lakehouse_schema,
    get_spark_session,
    read_lakehouse_table_core,
    read_warehouse_query_core,
    write_lakehouse_table_core,
)

OBSERVATION_TABLE = "METADATA_SOURCE_OBSERVATION"
_IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def _identifier(value: str | None, label: str) -> str:
    text = str(value or "").strip()
    if not _IDENTIFIER.fullmatch(text):
        raise ValueError(f"{label} must be a simple identifier containing letters, numbers, and underscores.")
    return text


def _warehouse_observation_query(schema: str, table_name: str, partition_column: str, change_column: str) -> str:
    return (
        "SELECT\n"
        f"  [{partition_column}] AS partition_value,\n"
        "  COUNT_BIG(*) AS row_count,\n"
        f"  MAX([{change_column}]) AS max_change_value\n"
        f"FROM [{schema}].[{table_name}]\n"
        f"GROUP BY [{partition_column}]"
    )


def _compact_rows(frame: Any) -> list[dict[str, Any]]:
    compact = []
    for row in frame.collect():
        value = row.asDict(recursive=True) if hasattr(row, "asDict") else dict(row)
        maximum = value.get("max_change_value")
        compact.append({
            "partition_value": str(value.get("partition_value", "")),
            "is_present": True,
            "row_count": int(value.get("row_count") or 0),
            "max_change_value": None if maximum is None else str(maximum),
        })
    return compact


def _observe_lakehouse(
    table_name: str,
    target: str,
    schema: str | None,
    partition_column: str,
    change_column: str,
    *,
    spark_session: Any,
    context: dict[str, Any],
) -> list[dict[str, Any]]:
    from pyspark.sql import functions as F

    frame = read_lakehouse_table_core(
        table_name, target=target, schema=schema, spark_session=spark_session, context=context,
    ).select(partition_column, change_column)
    observed = frame.groupBy(partition_column).agg(
        F.count(F.lit(1)).alias("row_count"),
        F.max(F.col(change_column)).alias("max_change_value"),
    ).select(
        F.col(partition_column).alias("partition_value"), "row_count", "max_change_value"
    )
    return _compact_rows(observed)


def _load_previous(
    source_id: str, observation_definition_id: str, *, spark_session: Any,
    context: dict[str, Any], metadata_schema: str | None,
) -> list[dict[str, Any]]:
    try:
        frame = read_lakehouse_table_core(
            OBSERVATION_TABLE, target="metadata", schema=metadata_schema,
            spark_session=spark_session, context=context,
        )
    except Exception as exc:
        if is_table_not_found_error(exc):
            return []
        raise RuntimeError(f"Unable to load table observation history for {source_id!r}: {exc}") from exc
    rows = (
        frame.where((frame.source_id == source_id) & (frame.observation_definition_id == observation_definition_id))
        .orderBy(frame.observed_at.desc())
        .select("partition_value", "is_present", "row_count", "max_change_value", "observed_at")
        .collect()
    )
    latest: dict[str, dict[str, Any]] = {}
    for row in rows:
        value = row.asDict(recursive=True) if hasattr(row, "asDict") else dict(row)
        latest.setdefault(str(value["partition_value"]), value)
    return list(latest.values())


def _persist(
    rows: list[dict[str, Any]], *, source_id: str, observation_definition_id: str,
    source_type: str, target: str, schema: str | None, table_name: str,
    observed_at: datetime, spark_session: Any, config: Any, env: str,
    context: dict[str, Any], metadata_schema: str | None,
) -> None:
    audit = build_runtime_audit_fields(config=config, env=env, runtime_context=context)
    values = [{
        **row, "source_id": source_id, "observation_definition_id": observation_definition_id,
        "source_type": source_type, "source_target": target, "source_schema": schema,
        "source_table": table_name, "observed_at": observed_at, **audit,
    } for row in rows]
    frame = spark_session.createDataFrame(
        [coerce_metadata_row_types(OBSERVATION_TABLE, row) for row in values],
        schema=metadata_table_schema_registry()[OBSERVATION_TABLE],
    )
    write_lakehouse_table_core(
        frame, OBSERVATION_TABLE, target="metadata", schema=metadata_schema,
        context=context, mode="append",
    )


def _read_predicate(partition_column: str, partition_values: list[str]) -> str | None:
    if not partition_values:
        return None
    escaped = [value.replace("'", "''") for value in partition_values]
    return f"[{partition_column}] IN ({', '.join(repr(value) for value in escaped)})"


def observe_table(
    table_name: str,
    *,
    target: str = "source",
    schema: str | None = None,
    partition_column: str,
    change_column: str,
) -> dict[str, Any]:
    """Cheaply identify changed source-table partitions before expensive work.

    ``observe_table()`` cheaply records row count and latest change value by
    source partition so FabricOps can decide whether more expensive source
    processing is required.

    Parameters
    ----------
    table_name : str
        Table name within the configured target.
    target : str, default="source"
        Logical Lakehouse or Warehouse target configured by ``00_env_config``.
    schema : str or None, default=None
        Optional Lakehouse schema. A schema is required for Warehouse targets.
    partition_column : str
        Column whose distinct values identify independently readable partitions.
    change_column : str
        Trustworthy column that advances when rows in a partition are inserted
        or updated, such as ``modified_at``, ``updated_at``, or
        ``last_changed_at``.

    Returns
    -------
    dict[str, Any]
        A restricted read plan containing compact observations, new, changed,
        and removed partitions, and whether a follow-up read is required.

    Raises
    ------
    ValueError
        If table identity, columns, target type, or a required Warehouse schema
        is invalid.
    RuntimeError
        If ``00_env_config`` has not initialized FabricOps or observation
        history cannot be read.

    Notes
    -----
    The stored evidence is only the partition, row count, and latest change
    value. This is a lightweight change signal, not proof that every cell is
    unchanged. Sources without a reliable change column require deeper change
    detection elsewhere. Warehouse aggregation is pushed into SQL; Lakehouse
    aggregation is distributed and projects only the two required columns.
    Compact history and removal tombstones are appended to the configured
    FabricOps metadata Lakehouse.

    Examples
    --------
    >>> plan = observe_table(
    ...     table_name="orders",
    ...     target="source",
    ...     schema="dbo",
    ...     partition_column="business_date",
    ...     change_column="modified_at",
    ... )
    >>> plan["requires_read"]
    True

    See Also
    --------
    check_changes, read_lakehouse_table, read_warehouse_query

    """
    table_value = _identifier(table_name, "table_name")
    target_value = str(target or "").strip()
    if not target_value:
        raise ValueError("target must be a configured target name.")
    schema_value = _identifier(schema, "schema") if schema is not None else None
    partition_value = _identifier(partition_column, "partition_column")
    change_value = _identifier(change_column, "change_column")

    config, env, context = resolve_fabric_context()
    store = get_store(config, env, target_value)
    source_type = str(store.kind).lower()
    if source_type not in {"lakehouse", "warehouse"}:
        raise ValueError(f"Target {target_value!r} must resolve to a Lakehouse or Warehouse.")
    if source_type == "warehouse" and schema_value is None:
        raise ValueError("schema is required for Warehouse observation.")
    spark = get_spark_session()
    source_id = f"{source_type}:{target_value}:{schema_value or ''}:{table_value}"
    definition = {
        "source_id": source_id,
        "partition_column": partition_value,
        "change_column": change_value,
    }
    observation_definition_id = hashlib.sha256(
        json.dumps(definition, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    metadata_schema = configured_lakehouse_schema(config, env, "metadata")
    previous = _load_previous(
        source_id, observation_definition_id, spark_session=spark,
        context=context, metadata_schema=metadata_schema,
    )
    if source_type == "warehouse":
        query = _warehouse_observation_query(
            schema_value, table_value, partition_value, change_value  # type: ignore[arg-type]
        )
        current = _compact_rows(read_warehouse_query_core(
            query, target=target_value, spark_session=spark, context=context,
        ))
    else:
        query = None
        current = _observe_lakehouse(
            table_value, target_value, schema_value, partition_value, change_value,
            spark_session=spark, context=context,
        )

    previous_by_partition = {str(row["partition_value"]): row for row in previous}
    current_partitions = {str(row["partition_value"]) for row in current}
    new_partitions: list[str] = []
    changed_partitions: list[str] = []
    for row in current:
        prior = previous_by_partition.get(row["partition_value"])
        if prior is None:
            new_partitions.append(row["partition_value"])
        elif (
            not prior.get("is_present", True)
            or int(prior.get("row_count") or 0) != row["row_count"]
            or prior.get("max_change_value") != row["max_change_value"]
        ):
            changed_partitions.append(row["partition_value"])
    removed_partitions = sorted(
        partition for partition, row in previous_by_partition.items()
        if row.get("is_present", True) and partition not in current_partitions
    )
    affected = [*changed_partitions, *new_partitions]
    tombstones = [{
        "partition_value": partition, "is_present": False,
        "row_count": 0, "max_change_value": None,
    } for partition in removed_partitions]
    _persist(
        [*current, *tombstones], source_id=source_id,
        observation_definition_id=observation_definition_id, source_type=source_type,
        target=target_value, schema=schema_value, table_name=table_value,
        observed_at=datetime.now(UTC), spark_session=spark, config=config, env=env,
        context=context, metadata_schema=metadata_schema,
    )
    return {
        "source_id": source_id,
        "observation_definition_id": observation_definition_id,
        "observations": current,
        "first_observation": not previous,
        "new_partitions": new_partitions,
        "changed_partitions": changed_partitions,
        "removed_partitions": removed_partitions,
        "requires_read": not previous or bool(affected) or bool(removed_partitions),
        "read_predicate": _read_predicate(partition_value, affected),
        "warehouse_observation_query": query,
    }
