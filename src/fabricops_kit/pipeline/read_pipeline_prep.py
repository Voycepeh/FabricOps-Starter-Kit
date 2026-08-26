"""Public owner for governed source-read preparation."""

from __future__ import annotations

import re
from typing import Any, Mapping

from fabricops_kit.config.shared import is_table_not_found_error, resolve_fabric_context
from fabricops_kit.io.shared import (
    configured_lakehouse_schema,
    get_spark_session,
    read_lakehouse_table_core,
    read_warehouse_query_core,
)
from fabricops_kit.pipeline.check_changes import _observation_changes
from fabricops_kit.pipeline.observe_table import _observe_table_core
from fabricops_kit.pipeline.shared import resolve_physical_table_identity, resolve_table_processing_definition


_CHECKPOINT_TABLE = "METADATA_SOURCE_WATERMARK_CHECKPOINT"
_PARTITION_CHECKPOINT_TABLE = "METADATA_SOURCE_PARTITION_CHECKPOINT"
_SOURCE_STRATEGIES = {"full_dataset", "incremental_watermark", "incremental_partition"}
_IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def _source_processing_definition(
    read_strategy: str,
    *,
    watermark_column: str | None,
    partition_column: str | None,
) -> dict[str, Any]:
    """Normalize and validate the engineer-authored source strategy once."""
    strategy = str(read_strategy or "").strip().lower()
    if strategy not in _SOURCE_STRATEGIES:
        raise ValueError(
            "source_read_strategy must be one of: full_dataset, incremental_watermark, incremental_partition."
        )
    watermark = str(watermark_column or "").strip() or None
    partition = str(partition_column or "").strip() or None
    if strategy == "incremental_watermark":
        if watermark is None or not _IDENTIFIER.fullmatch(watermark):
            raise ValueError("source_watermark_column must be a simple identifier for incremental_watermark.")
        if partition is not None:
            raise ValueError("source_partition_column is not valid for incremental_watermark.")
        return {"read_strategy": strategy, "watermark_column": watermark}
    if strategy == "incremental_partition":
        if partition is None or not _IDENTIFIER.fullmatch(partition):
            raise ValueError("source_partition_column must be a simple identifier for incremental_partition.")
        if watermark is not None:
            raise ValueError("source_watermark_column is not valid for incremental_partition.")
        return {"read_strategy": strategy, "partition_column": partition}
    if watermark is not None or partition is not None:
        raise ValueError("full_dataset does not accept watermark or partition columns.")
    return {"read_strategy": strategy}


def _partition_scope(changes: Mapping[str, Any], processing: Mapping[str, Any], column: str) -> dict[str, Any]:
    """Resolve existing partition-change evidence to one canonical runtime scope."""
    strategy = str(processing["load_strategy"])
    observed_column = str(changes.get("partition_column") or "").strip() or None
    if observed_column != column:
        raise ValueError(
            f"incremental_partition configured {column!r}, but the active change rule observes "
            f"{observed_column or '<none>'!r}."
        )
    if changes.get("first_observation"):
        return {"read_mode": "full_dataset", "scope": {"type": "full_dataset"}}

    new = list(changes.get("new_partitions") or [])
    changed = list(changes.get("changed_partitions") or [])
    reappeared = list(changes.get("reappeared_partitions") or [])
    removed = list(changes.get("removed_partitions") or [])
    existing_changes = [*changed, *reappeared]
    if removed:
        if strategy == "overwrite" and not processing.get("partition_column"):
            return {"read_mode": "full_dataset", "scope": {"type": "full_dataset"}}
        raise ValueError(f"{strategy} cannot safely apply removed source partitions without explicit delete semantics.")
    if strategy == "append" and existing_changes:
        raise ValueError("append is unsafe when an existing source partition changed or reappeared.")

    affected = [*new, *existing_changes]
    if not affected:
        return {"read_mode": "skip", "scope": {"type": "skip"}}
    if strategy == "overwrite" and processing.get("partition_column") != column:
        return {"read_mode": "full_dataset", "scope": {"type": "full_dataset"}}
    return {
        "read_mode": "incremental_subset",
        "scope": {"type": "partition", "column": column, "values": affected},
    }


def _checkpoint_value(config: Any, env: str, table_id: str, column: str, *, spark_session: Any, context: Any) -> Any:
    """Return the latest successfully committed watermark, or None on first run."""
    metadata_schema = configured_lakehouse_schema(config, env, "metadata")
    try:
        frame = read_lakehouse_table_core(
            _CHECKPOINT_TABLE,
            target="metadata",
            schema=metadata_schema,
            spark_session=spark_session,
            context=context,
        )
    except (FileNotFoundError, RuntimeError) as exc:
        message = str(exc).lower()
        if "not found" in message or "does not exist" in message:
            return None
        raise
    rows = (
        frame.where((frame.environment_name == env) & (frame.table_id == table_id) & (frame.watermark_column == column))
        .orderBy(frame._committed_at.desc())
        .limit(1)
        .collect()
    )
    return None if not rows else rows[0]["watermark_value"]


def _successful_partition_observation_id(
    config: Any, env: str, table_id: str, *, spark_session: Any, context: Any
) -> str | None:
    """Return the observation from the last successfully published partition run."""
    try:
        frame = read_lakehouse_table_core(
            _PARTITION_CHECKPOINT_TABLE,
            target="metadata",
            schema=configured_lakehouse_schema(config, env, "metadata"),
            spark_session=spark_session,
            context=context,
        )
    except Exception as exc:
        if is_table_not_found_error(exc):
            return None
        raise
    rows = (
        frame.where((frame.environment_name == env) & (frame.table_id == table_id))
        .orderBy(frame._committed_at.desc())
        .limit(1)
        .collect()
    )
    return None if not rows else str(rows[0]["observation_id"])


def _source_upper_watermark(
    identity: Mapping[str, Any], column: str, *, spark_session: Any, context: Any
) -> dict[str, Any]:
    """Capture and validate a unique upper watermark without loading a Warehouse table."""
    if identity["store_kind"] == "warehouse":
        query = (
            f"SELECT MAX([{column}]) AS upper_watermark, COUNT_BIG(*) AS row_count, "
            f"COUNT_BIG([{column}]) AS non_null_count, "
            f"COUNT_BIG(DISTINCT [{column}]) AS distinct_count "
            f"FROM [{identity['schema']}].[{identity['table_name']}]"
        )
        frame = read_warehouse_query_core(
            query, target=str(identity["target"]), spark_session=spark_session, context=context
        )
    else:
        from pyspark.sql import functions as F

        source = read_lakehouse_table_core(
            str(identity["table_name"]),
            target=str(identity["target"]),
            schema=identity.get("schema"),
            spark_session=spark_session,
            context=context,
        )
        if column not in source.columns:
            raise ValueError(f"Watermark column {column!r} does not exist in the source.")
        frame = source.agg(
            F.max(F.col(column)).alias("upper_watermark"),
            F.count(F.lit(1)).alias("row_count"),
            F.count(F.col(column)).alias("non_null_count"),
            F.count_distinct(F.col(column)).alias("distinct_count"),
        )
    fields = {field.name: field.dataType.simpleString() for field in frame.schema.fields}
    rows = frame.collect()
    values = {} if not rows else rows[0].asDict(recursive=True)
    return {
        "upper_watermark": values.get("upper_watermark"),
        "data_type": fields.get("upper_watermark", "unknown"),
        "row_count": int(values.get("row_count") or 0),
        "non_null_count": int(values.get("non_null_count") or 0),
        "distinct_count": int(values.get("distinct_count") or 0),
    }


def _coerce_checkpoint(value: Any, data_type: str, *, spark_session: Any) -> Any:
    """Parse a stored checkpoint with Spark so comparisons use the source type."""
    if value is None:
        return None
    from pyspark.sql import functions as F

    row = spark_session.range(1).select(F.lit(str(value)).cast(data_type).alias("value")).collect()[0]
    parsed = row["value"]
    if parsed is None:
        raise ValueError(f"Stored watermark checkpoint {value!r} is invalid for source type {data_type!r}.")
    return parsed


def _watermark_scope(
    identity: Mapping[str, Any],
    column: str,
    *,
    config: Any,
    env: str,
    spark_session: Any,
    context: Any,
) -> dict[str, Any]:
    """Resolve a bounded ``(lower, upper]`` watermark scope."""
    previous_value = _checkpoint_value(
        config, env, str(identity["table_id"]), column, spark_session=spark_session, context=context
    )
    state = _source_upper_watermark(identity, column, spark_session=spark_session, context=context)
    upper = state["upper_watermark"]
    data_type = state["data_type"]
    if state["non_null_count"] != state["row_count"]:
        raise ValueError("Watermark values must be non-null for every source row.")
    if state["distinct_count"] != state["row_count"]:
        raise ValueError(
            "incremental_watermark requires a strictly increasing, globally unique watermark value for every row; "
            "duplicate values could cause late-arriving rows to be skipped."
        )
    if upper is None:
        if previous_value is None:
            return {"read_mode": "full_dataset", "scope": {"type": "full_dataset"}, "candidate_checkpoint": None}
        raise ValueError(
            "The source is empty or all watermark values are null; an existing checkpoint cannot be compared."
        )
    previous = _coerce_checkpoint(previous_value, data_type, spark_session=spark_session)
    candidate = {"column": column, "value": upper, "data_type": data_type, "status": "candidate"}
    if previous is None:
        return {"read_mode": "full_dataset", "scope": {"type": "full_dataset"}, "candidate_checkpoint": candidate}
    try:
        if upper < previous:
            raise ValueError("Current upper watermark is earlier than the last successful checkpoint.")
        if upper == previous:
            return {"read_mode": "skip", "scope": {"type": "skip"}, "candidate_checkpoint": None}
    except TypeError as exc:
        raise ValueError("Stored checkpoint type does not match the source watermark type.") from exc
    return {
        "read_mode": "incremental_subset",
        "scope": {
            "type": "watermark",
            "column": column,
            "lower_bound": previous,
            "upper_bound": upper,
            "lower_inclusive": False,
            "upper_inclusive": True,
        },
        "candidate_checkpoint": candidate,
    }


def read_pipeline_prep(
    source_table_name: str,
    target_table_name: str,
    *,
    source_read_strategy: str,
    source_watermark_column: str | None = None,
    source_partition_column: str | None = None,
    source_target: str = "source",
    source_schema: str | None = None,
    target: str = "unified",
    schema: str | None = None,
    load_strategy: str,
    load_strategy_parameters: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Prepare an explicit governed source read without reading business rows.

    Parameters
    ----------
    source_table_name : str
        Physical source table to prepare.
    target_table_name : str
        Governed target table whose target processing definition controls this run.
    source_read_strategy : {"full_dataset", "incremental_watermark", "incremental_partition"}
        Engineer-authored rule for identifying source data to process.
    source_watermark_column : str or None, default=None
        Checkpoint column required by ``incremental_watermark``.
    source_partition_column : str or None, default=None
        Logical bucket column required by ``incremental_partition``.
    source_target : str, default="source"
        Configured source Lakehouse or Warehouse target.
    source_schema : str or None, default=None
        Optional source schema.
    target : str, default="unified"
        Configured governed target.
    schema : str or None, default=None
        Optional governed target schema.
    load_strategy : {"overwrite", "append", "scd1", "scd2"}
        Independent target application strategy.
    load_strategy_parameters : dict, optional
        Parameters owned by the target strategy.

    Returns
    -------
    dict
        Canonical identities, ``source_processing``, resolved target
        ``processing``, and one runtime ``read_mode`` plus ``scope``. A
        watermark candidate is returned separately and is never committed by
        this function.

    Raises
    ------
    ValueError
        If source configuration, checkpoint state, contract processing, or the
        resulting processing scope is invalid.

    Notes
    -----
    Watermark subsets use the bounded interval ``(lower_bound, upper_bound]``.
    The successful checkpoint remains unchanged until a later post-write commit
    succeeds. Partition subsets reuse FabricOps source observation and change
    detection; full-dataset reads do not observe the source merely to skip it.

    Examples
    --------
    >>> prep = read_pipeline_prep(
    ...     "bookings", "bookings_curated", source_schema="dbo", schema="dbo",
    ...     source_read_strategy="incremental_watermark",
    ...     source_watermark_column="modified_datetime", load_strategy="scd1",
    ...     load_strategy_parameters={"key_columns": ["booking_id"]},
    ... )
    >>> prep["read_mode"] in {"skip", "full_dataset", "incremental_subset"}
    True

    See Also
    --------
    write_pipeline_prep, check_changes, read_lakehouse_table

    """
    source_processing = _source_processing_definition(
        source_read_strategy,
        watermark_column=source_watermark_column,
        partition_column=source_partition_column,
    )
    config, env, context = resolve_fabric_context()
    source_identity = resolve_physical_table_identity(
        config, env, target=source_target, schema=source_schema, table_name=source_table_name
    )
    target_identity = resolve_physical_table_identity(
        config, env, target=target, schema=schema, table_name=target_table_name
    )
    processing = resolve_table_processing_definition(
        config,
        env,
        target_identity["table_id"],
        context=context,
        authored_processing={"load_strategy": load_strategy, **(load_strategy_parameters or {})},
    )
    strategy = source_processing["read_strategy"]
    observation = None
    changes = None
    if strategy == "full_dataset":
        runtime = {"read_mode": "full_dataset", "scope": {"type": "full_dataset"}}
    elif strategy == "incremental_watermark":
        spark = get_spark_session()
        runtime = _watermark_scope(
            source_identity,
            source_processing["watermark_column"],
            config=config,
            env=env,
            spark_session=spark,
            context=context,
        )
    else:
        observation = _observe_table_core(
            source_identity["table_name"], target=source_identity["target"], schema=source_identity["schema"]
        )
        successful_observation_id = _successful_partition_observation_id(
            config,
            env,
            str(source_identity["table_id"]),
            spark_session=getattr(observation, "sparkSession", None) or get_spark_session(),
            context=context,
        )
        changes = _observation_changes(observation, successful_observation_id=successful_observation_id)
        runtime = _partition_scope(changes, processing, source_processing["partition_column"])
        if (
            target_identity["store_kind"] == "warehouse"
            and processing["load_strategy"] == "overwrite"
            and runtime["read_mode"] == "incremental_subset"
        ):
            runtime = {"read_mode": "full_dataset", "scope": {"type": "full_dataset"}}
    return {
        "source": source_identity,
        "target": target_identity,
        "source_processing": source_processing,
        "observation": observation,
        "changes": changes,
        "processing": processing,
        **runtime,
    }
