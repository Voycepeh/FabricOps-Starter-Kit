"""Owner file for compact source observation and incremental read planning."""

from __future__ import annotations

from datetime import UTC, datetime
import hashlib
import json
import re
from typing import Any

from fabricops_kit.config.audit import build_runtime_audit_fields
from fabricops_kit.config.metadata_schemas import coerce_metadata_row_types, metadata_table_schema_registry
from fabricops_kit.config.shared import is_table_not_found_error
from fabricops_kit.io.shared import (
    configured_lakehouse_schema,
    get_spark_session,
    read_lakehouse_table_core,
    read_warehouse_query_core,
    write_lakehouse_table_core,
)

OBSERVATION_TABLE = "METADATA_SOURCE_OBSERVATION"
_IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_WRITE_SQL = re.compile(r"\b(insert|update|delete|merge|create|alter|drop|truncate|execute|exec)\b", re.IGNORECASE)


def _identifier(value: str, label: str) -> str:
    text = str(value or "").strip()
    if not _IDENTIFIER.fullmatch(text):
        raise ValueError(f"{label} must be a simple SQL identifier containing letters, numbers, and underscores.")
    return text


def _columns(values: list[str] | tuple[str, ...] | None, label: str) -> list[str]:
    result = [_identifier(value, label) for value in (values or [])]
    if not result:
        raise ValueError(f"{label} must contain at least one column.")
    if len(set(result)) != len(result):
        raise ValueError(f"{label} must not contain duplicate columns.")
    return result


def _partition_predicate(value: Any) -> str | None:
    if value in (None, ""):
        return None
    predicate = str(value).strip()
    if not predicate or ";" in predicate or "--" in predicate or "/*" in predicate or _WRITE_SQL.search(predicate):
        raise ValueError("source.partition_predicate must be one read-only filter expression without comments or statements.")
    return predicate


def _warehouse_observation_query(
    schema: str,
    table: str,
    partition_columns: list[str],
    range_column: str,
    fingerprint_columns: list[str],
    partition_predicate: str | None,
) -> str:
    qualified = f"[{_identifier(schema, 'schema')}].[{_identifier(table, 'table_name')}]"
    partition_sql = ", ".join(f"[{column}]" for column in partition_columns)
    checksum_inputs = ", ".join(f"[{column}]" for column in fingerprint_columns)
    where = f"\nWHERE {partition_predicate}" if partition_predicate else ""
    return (
        "SELECT\n"
        f"  {partition_sql},\n"
        "  COUNT_BIG(*) AS row_count,\n"
        f"  MIN([{range_column}]) AS observed_min,\n"
        f"  MAX([{range_column}]) AS observed_max,\n"
        f"  CHECKSUM_AGG(BINARY_CHECKSUM({checksum_inputs})) AS aggregate_checksum\n"
        f"FROM {qualified}{where}\nGROUP BY {partition_sql}"
    )


def _compact_rows(frame: Any, partition_columns: list[str]) -> list[dict[str, Any]]:
    rows = frame.collect()
    compact = []
    for row in rows:
        value = row.asDict(recursive=True) if hasattr(row, "asDict") else dict(row)
        partition_value = "|".join(str(value.get(column, "")) for column in partition_columns)
        count = int(value.get("row_count") or 0)
        minimum = value.get("observed_min")
        maximum = value.get("observed_max")
        checksum = value.get("aggregate_checksum", value.get("fingerprint_input", ""))
        evidence = f"{partition_value}|{count}|{minimum}|{maximum}|{checksum}"
        compact.append({
            "partition_value": partition_value,
            "is_present": True,
            "row_count": count,
            "observed_min": None if minimum is None else str(minimum),
            "observed_max": None if maximum is None else str(maximum),
            "fingerprint": hashlib.sha256(evidence.encode("utf-8")).hexdigest(),
        })
    return compact


def _observe_lakehouse(
    source: dict[str, Any],
    partition_columns: list[str],
    range_column: str,
    fingerprint_columns: list[str],
    *,
    spark_session: Any,
    context: dict[str, Any],
) -> list[dict[str, Any]]:
    from pyspark.sql import functions as F

    selected = list(dict.fromkeys([*partition_columns, range_column, *fingerprint_columns]))
    frame = read_lakehouse_table_core(
        source["table_name"], target=source["target"], schema=source.get("schema"),
        spark_session=spark_session, context=context,
    ).select(*selected)
    if source.get("partition_predicate"):
        frame = frame.where(str(source["partition_predicate"]))
    fingerprint_values = [F.coalesce(F.col(column).cast("string"), F.lit("<null>")) for column in fingerprint_columns]
    observed = frame.groupBy(*partition_columns).agg(
        F.count(F.lit(1)).alias("row_count"),
        F.min(F.col(range_column)).alias("observed_min"),
        F.max(F.col(range_column)).alias("observed_max"),
        F.sum(F.xxhash64(*fingerprint_values)).alias("fingerprint_input"),
    )
    return _compact_rows(observed, partition_columns)


def _load_previous(
    source_id: str, observation_definition_id: str, *, spark_session: Any, config: Any, env: str,
    metadata_schema: str | None,
) -> list[dict[str, Any]]:
    try:
        frame = read_lakehouse_table_core(
            OBSERVATION_TABLE, target="metadata", schema=metadata_schema,
            spark_session=spark_session, context={"config": config, "env": env},
        )
    except Exception as exc:
        if is_table_not_found_error(exc):
            return []
        raise RuntimeError(f"Unable to load source observation history for {source_id!r}: {exc}") from exc
    rows = (
        frame.where(
            (frame.source_id == source_id)
            & (frame.observation_definition_id == observation_definition_id)
        )
        .orderBy(frame.observed_at.desc())
        .select("partition_value", "is_present", "row_count", "observed_min", "observed_max", "fingerprint", "observed_at")
        .collect()
    )
    latest: dict[str, dict[str, Any]] = {}
    for row in rows:
        value = row.asDict(recursive=True) if hasattr(row, "asDict") else dict(row)
        latest.setdefault(str(value["partition_value"]), value)
    return list(latest.values())


def _persist(
    rows: list[dict[str, Any]], source: dict[str, Any], source_id: str,
    observation_definition_id: str, observed_at: datetime,
    *, spark_session: Any, config: Any, env: str, metadata_schema: str | None,
) -> None:
    audit = build_runtime_audit_fields(config=config, env=env)
    values = [{
        **row, "source_id": source_id, "observation_definition_id": observation_definition_id,
        "source_type": source["source_type"],
        "source_target": source["target"], "source_schema": source.get("schema"),
        "source_table": source["table_name"], "observed_at": observed_at, **audit,
    } for row in rows]
    frame = spark_session.createDataFrame(
        [coerce_metadata_row_types(OBSERVATION_TABLE, row) for row in values],
        schema=metadata_table_schema_registry()[OBSERVATION_TABLE],
    )
    write_lakehouse_table_core(
        frame, OBSERVATION_TABLE, target="metadata", schema=metadata_schema,
        context={"config": config, "env": env}, mode="append",
    )


def _read_predicate(partition_columns: list[str], partition_values: list[str]) -> str | None:
    if not partition_values:
        return None
    column = partition_columns[0]
    escaped = [value.replace("'", "''") for value in partition_values]
    return f"[{column}] IN ({', '.join(repr(value) for value in escaped)})"


def observe_source(
    source: dict[str, Any], *, partition_columns: list[str], range_column: str,
    fingerprint_columns: list[str], config: Any, env: str,
    spark_session: Any | None = None, context: dict[str, Any] | None = None,
    persist: bool = True,
) -> dict[str, Any]:
    """Observe a Fabric source cheaply and plan a restricted follow-up read.

    Parameters
    ----------
    source : dict[str, Any]
        Explicit source configuration with ``source_type`` (``warehouse`` or
        ``lakehouse``), logical ``target``, ``table_name``, and optional
        ``schema`` and ``partition_predicate`` values.
    partition_columns : list[str]
        A one-item list defining independently readable source partitions.
        Composite partition definitions are not supported in this Preview API.
    range_column : str
        Column used for compact minimum and maximum evidence.
    fingerprint_columns : list[str]
        Narrow columns used by the distributed aggregate checksum.
    config : FrameworkConfig | dict
        FabricOps configuration containing the source and metadata targets.
    env : str
        Selected FabricOps environment.
    spark_session : object, optional
        Spark session to use instead of the notebook global ``spark``.
    context : dict[str, Any], optional
        Fabric context override. ``config`` and ``env`` are supplied by this
        function to ensure configured target routing.
    persist : bool, default=True
        Append the compact observation to FabricOps-owned metadata after a
        successful comparison.

    Returns
    -------
    dict[str, Any]
        Compact observations, changed, new, and removed partitions, and a
        read-only ``read_predicate``. ``requires_read`` is false only when the
        current partition set and every fingerprint match the latest stored
        observation under the same observation definition.

    Raises
    ------
    ValueError
        If source type, identity, or observation columns are invalid.

    Notes
    -----
    Warehouse grouping and checksums execute in the SQL serving engine, so
    Spark receives only aggregate rows. ``CHECKSUM_AGG`` is a cheap change
    signal rather than collision-proof row evidence; use :func:`check_changes`
    on the restricted source slice when deeper comparison is required.
    Lakehouse aggregation remains distributed and projects only observation
    columns. The source is always read-only; history is appended to
    ``METADATA_SOURCE_OBSERVATION`` in the configured metadata Lakehouse.
    A deterministic ``observation_definition_id`` binds history to the chosen
    partition, range, fingerprint columns, and partition predicate. Removed
    partitions are persisted as absence tombstones so a later reappearance is
    detected as a change.

    Examples
    --------
    >>> plan = observe_source(
    ...     {"source_type": "warehouse", "target": "warehouse", "schema": "dbo", "table_name": "orders"},
    ...     partition_columns=["business_date"], range_column="order_id",
    ...     fingerprint_columns=["order_id", "modified_at"], config=CONFIG, env=ENV,
    ... )
    >>> plan["requires_read"]
    True

    See Also
    --------
    check_changes

    """
    if not isinstance(source, dict):
        raise ValueError("source must be a dictionary with an explicit source_type.")
    source_type = str(source.get("source_type") or "").lower()
    if source_type not in {"warehouse", "lakehouse"}:
        raise ValueError("source.source_type must be either 'warehouse' or 'lakehouse'.")
    normalized = {**source, "source_type": source_type}
    normalized["target"] = str(source.get("target") or "").strip()
    normalized["table_name"] = _identifier(source.get("table_name"), "table_name")
    normalized["partition_predicate"] = _partition_predicate(source.get("partition_predicate"))
    if not normalized["target"]:
        raise ValueError("source.target is required.")
    partitions = _columns(partition_columns, "partition_columns")
    if len(partitions) != 1:
        raise ValueError("partition_columns must contain exactly one column in this Preview API.")
    range_value = _identifier(range_column, "range_column")
    fingerprints = _columns(fingerprint_columns, "fingerprint_columns")
    spark = get_spark_session(spark_session)
    runtime_context = {**(context or {}), "config": config, "env": env}
    source_id = str(source.get("source_id") or f"{source_type}:{normalized['target']}:{source.get('schema') or ''}:{normalized['table_name']}")
    definition = {
        "fingerprint_columns": fingerprints,
        "partition_column": partitions[0],
        "partition_predicate": normalized["partition_predicate"],
        "range_column": range_value,
    }
    observation_definition_id = hashlib.sha256(
        json.dumps(definition, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    metadata_schema = configured_lakehouse_schema(config, env, "metadata")
    previous = _load_previous(
        source_id, observation_definition_id, spark_session=spark, config=config,
        env=env, metadata_schema=metadata_schema,
    )
    if source_type == "warehouse":
        if not source.get("schema"):
            raise ValueError("source.schema is required for Warehouse observation.")
        query = _warehouse_observation_query(source["schema"], normalized["table_name"], partitions, range_value, fingerprints, normalized["partition_predicate"])
        current = _compact_rows(read_warehouse_query_core(query, target=normalized["target"], spark_session=spark, context=runtime_context), partitions)
    else:
        current = _observe_lakehouse(normalized, partitions, range_value, fingerprints, spark_session=spark, context=runtime_context)
        query = None
    previous_by_partition = {str(row["partition_value"]): row for row in previous}
    current_partitions = {str(row["partition_value"]) for row in current}
    new_partitions, changed_partitions = [], []
    for row in current:
        prior = previous_by_partition.get(row["partition_value"])
        if prior is None:
            new_partitions.append(row["partition_value"])
        elif not prior.get("is_present", True) or prior["fingerprint"] != row["fingerprint"]:
            changed_partitions.append(row["partition_value"])
    removed_partitions = sorted(
        partition for partition, row in previous_by_partition.items()
        if row.get("is_present", True) and partition not in current_partitions
    )
    affected = [*changed_partitions, *new_partitions]
    observed_at = datetime.now(UTC)
    if persist:
        tombstones = [{
            "partition_value": partition, "is_present": False, "row_count": 0,
            "observed_min": None, "observed_max": None, "fingerprint": "removed",
        } for partition in removed_partitions]
        _persist(
            [*current, *tombstones], normalized, source_id, observation_definition_id, observed_at,
            spark_session=spark, config=config, env=env, metadata_schema=metadata_schema,
        )
    return {
        "source_id": source_id, "observation_definition_id": observation_definition_id,
        "observations": current,
        "first_observation": not previous, "new_partitions": new_partitions,
        "changed_partitions": changed_partitions, "removed_partitions": removed_partitions,
        "requires_read": not previous or bool(affected) or bool(removed_partitions),
        "read_predicate": _read_predicate(partitions, affected),
        "warehouse_observation_query": query,
    }
