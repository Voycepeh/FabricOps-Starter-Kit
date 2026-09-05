"""Internal owner for lightweight table observation evidence."""

from __future__ import annotations

import re
from typing import Any
from uuid import uuid4

from fabricops_kit.config.audit import build_runtime_audit_fields
from fabricops_kit.config.shared import build_table_id
from fabricops_kit.config.metadata_schemas import coerce_metadata_row_types, metadata_table_physical_schema, metadata_table_schema_registry
from fabricops_kit.config.shared import get_store, resolve_fabric_context
from fabricops_kit.io.shared import (
    get_spark_session,
    read_lakehouse_table_core,
    read_warehouse_query_core,
    resolve_lakehouse_table_location,
    resolve_warehouse_table_location,
    write_lakehouse_table_core,
)
from fabricops_kit.pipeline.shared import (
    load_table_guardrail_rules,
    resolve_change_rule_observation_columns,
    select_table_guardrail_rule,
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
        f"  MIN([{change_column}]) AS min_change_value,\n"
        f"  MAX([{change_column}]) AS max_change_value\n"
        f"FROM [{schema}].[{table_name}]\n"
        f"GROUP BY [{partition_column}]"
    )


def _compact_rows(frame: Any) -> list[dict[str, Any]]:
    compact = []
    for row in frame.collect():
        value = row.asDict(recursive=True) if hasattr(row, "asDict") else dict(row)
        minimum = value.get("min_change_value")
        maximum = value.get("max_change_value")
        compact.append(
            {
                "partition_value": str(value.get("partition_value", "")),
                "is_present": True,
                "row_count": int(value.get("row_count") or 0),
                "min_change_value": None if minimum is None else str(minimum),
                "max_change_value": None if maximum is None else str(maximum),
            }
        )
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
        table_name,
        target=target,
        schema=schema,
        spark_session=spark_session,
        context=context,
    ).select(partition_column, change_column)
    observed = frame.groupBy(partition_column).agg(
        F.count(F.lit(1)).alias("row_count"),
        F.min(F.col(change_column)).alias("min_change_value"),
        F.max(F.col(change_column)).alias("max_change_value"),
    ).select(
        F.col(partition_column).alias("partition_value"),
        "row_count",
        "min_change_value",
        "max_change_value",
    )
    return _compact_rows(observed)


def _persist(
    rows: list[dict[str, Any]],
    *,
    observation_id: str,
    table_id: str,
    spark_session: Any,
    config: Any,
    env: str,
    context: dict[str, Any],
    metadata_schema: str | None,
) -> Any:
    """Persist one normalized table observation without Guardrail-owned identity."""
    audit = build_runtime_audit_fields(config=config, env=env, runtime_context=context)
    values = [
        {
            **row,
            "observation_id": observation_id,
            "table_id": table_id,
            "environment_name": env,
            **audit,
        }
        for row in rows
    ]
    frame = spark_session.createDataFrame(
        [coerce_metadata_row_types(OBSERVATION_TABLE, row) for row in values],
        schema=metadata_table_schema_registry()[OBSERVATION_TABLE],
    )
    write_lakehouse_table_core(
        frame,
        OBSERVATION_TABLE,
        target="metadata",
        schema=metadata_schema,
        context=context,
        mode="append",
    )
    return frame


def _observe_table_core(
    table_name: str,
    *,
    target: str = "source",
    schema: str | None = None,
) -> Any:
    """Collect, persist, and return lightweight source-table evidence.

    This internal helper cheaply records row count plus earliest and latest
    change values by source partition so ``read_pipeline_prep()`` can determine
    the governed source-read scope without first reading the full business table.

    Parameters
    ----------
    table_name : str
        Table name within the configured target.
    target : str, default="source"
        Logical Lakehouse or Warehouse target configured by ``00_env_config``.
    schema : str or None, default=None
        Optional Lakehouse schema. A schema is required for Warehouse targets.

    Returns
    -------
    pyspark.sql.DataFrame
        The canonical observation rows written to
        ``METADATA_SOURCE_OBSERVATION``. Normal observation rows have
        ``is_present=True``.

    Raises
    ------
    ValueError
        If table identity, target type, or a required active source-change rule
        is invalid.
    RuntimeError
        If ``00_env_config`` has not initialized FabricOps or observation
        cannot be collected or persisted.

    Notes
    -----
    The stored evidence is the stable ``observation_id`` and ``table_id``, active
    ``environment_name``, partition value, row count, and earliest and latest
    change values. This is a lightweight change signal, not proof that every
    cell is unchanged: a middle value can change while all three signals remain
    identical. Sources without a reliable change column require deeper change
    detection elsewhere. Warehouse aggregation is pushed into SQL; Lakehouse
    aggregation is distributed and projects only the two required source
    columns.

    Evidence is appended only after collection succeeds. This function neither
    loads history nor makes guardrail decisions; ``check_changes`` owns
    comparison and removal tombstones. The stable ``table_id`` is built from the
    resolved physical identity with the same logical identity rules used by
    :func:`profile_and_register_table`. It is independent of Development or
    Production; ``environment_name`` keeps those operational observations
    separate without requiring a pre-existing catalogue row.

    """
    table_value = _identifier(table_name, "table_name")
    target_value = str(target or "").strip().lower()
    if not target_value:
        raise ValueError("target must be a configured target name.")
    schema_value = _identifier(schema, "schema") if schema is not None else None
    config, env, context = resolve_fabric_context()
    store = get_store(config, env, target_value)
    source_type = str(store.kind).lower()
    if source_type not in {"lakehouse", "warehouse"}:
        raise ValueError(f"Target {target_value!r} must resolve to a Lakehouse or Warehouse.")
    if source_type == "warehouse":
        configured_schema = schema_value if schema_value is not None else getattr(store, "schema", None)
        if configured_schema is None or not str(configured_schema).strip():
            raise ValueError("schema is required for Warehouse observation; pass it or configure a default schema.")
        schema_value, table_value, _object_name = resolve_warehouse_table_location(
            store, configured_schema, table_value
        )
    else:
        table_value, schema_value, _path = resolve_lakehouse_table_location(store, table_value, schema_value)
        if getattr(store, "schema_enabled", False) and schema_value is None:
            raise ValueError(
                "schema is required for schema-enabled Lakehouse observation; pass it or configure a default schema."
            )

    spark = get_spark_session()
    table_id = build_table_id(source_type, target_value, schema_value, table_value)

    rules_df = load_table_guardrail_rules(
        config, env, spark_session=spark, table_id=table_id, context=context,
    )
    rule = select_table_guardrail_rule(
        rules_df,
        guardrail_type="change",
        table_id=table_id,
        environment_name=env,
    )
    if rule is None:
        raise ValueError(
            f"No active approved source-change rule exists for {table_id!r}; "
            "Governance must author and activate one before read_pipeline_prep() can run."
        )
    partition_value, change_value = resolve_change_rule_observation_columns(rule)
    metadata_schema = metadata_table_physical_schema(config, OBSERVATION_TABLE)

    if source_type == "warehouse":
        query = _warehouse_observation_query(
            schema_value, table_value, partition_value, change_value  # type: ignore[arg-type]
        )
        current = _compact_rows(
            read_warehouse_query_core(
                query,
                target=target_value,
                spark_session=spark,
                context=context,
            )
        )
    else:
        current = _observe_lakehouse(
            table_value,
            target_value,
            schema_value,
            partition_value,
            change_value,
            spark_session=spark,
            context=context,
        )

    return _persist(
        current,
        observation_id=str(uuid4()),
        table_id=table_id,
        spark_session=spark,
        config=config,
        env=env,
        context=context,
        metadata_schema=metadata_schema,
    )
