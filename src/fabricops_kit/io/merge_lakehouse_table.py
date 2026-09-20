"""Internal owner for routed Lakehouse Delta merge mutations."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from .shared import resolve_configured_lakehouse_table


def lakehouse_table_exists(
    table_name: str, *, store: str, schema: str | None, spark_session, context: Mapping[str, Any] | None = None
) -> bool:
    """Return whether the configured physical target is an existing Delta table."""
    try:
        from delta.tables import DeltaTable
    except Exception as exc:  # pragma: no cover
        raise RuntimeError("Delta Lake support is required for Lakehouse inspection.") from exc
    _store, _table, _schema, path = resolve_configured_lakehouse_table(
        store, table_name, schema, context=dict(context or {}),
    )
    return DeltaTable.isDeltaTable(spark_session, path)


def merge_lakehouse_table(
    dataframe,
    table_name: str,
    *,
    store: str,
    schema: str | None,
    condition: str,
    actions: Sequence[Mapping[str, Any]],
    context: Mapping[str, Any] | None = None,
    spark_session=None,
) -> None:
    """Apply an ordered set of Delta merge actions to a configured table.

    This is an Internal foundational I/O function. Callers own the domain merge
    condition and action expressions; this owner resolves the physical target
    and exclusively performs the Delta mutation.
    """
    if not isinstance(condition, str) or not condition.strip():
        raise ValueError("condition must be a non-empty Delta merge expression.")
    if not actions:
        raise ValueError("actions must contain at least one Delta merge action.")
    try:
        from delta.tables import DeltaTable
    except Exception as exc:  # pragma: no cover - Fabric/Delta runtime dependency
        raise RuntimeError("Delta Lake merge support is required for Lakehouse mutations.") from exc

    spark = spark_session or dataframe.sparkSession
    _store, _table, _schema, path = resolve_configured_lakehouse_table(
        store, table_name, schema, context=dict(context or {}),
    )
    builder = DeltaTable.forPath(spark, path).alias("target").merge(dataframe.alias("source"), condition)
    for action in actions:
        kind = action["action"]
        action_condition = action.get("condition")
        values = action.get("values")
        if kind == "matched_update_all":
            builder = builder.whenMatchedUpdateAll(condition=action_condition)
        elif kind == "matched_update":
            builder = builder.whenMatchedUpdate(condition=action_condition, set=values)
        elif kind == "matched_delete":
            builder = builder.whenMatchedDelete(condition=action_condition)
        elif kind == "not_matched_insert_all":
            builder = builder.whenNotMatchedInsertAll(condition=action_condition)
        elif kind == "not_matched_insert":
            builder = builder.whenNotMatchedInsert(condition=action_condition, values=values)
        elif kind == "not_matched_by_source_delete":
            builder = builder.whenNotMatchedBySourceDelete(condition=action_condition)
        elif kind == "not_matched_by_source_update":
            builder = builder.whenNotMatchedBySourceUpdate(condition=action_condition, set=values)
        else:
            raise ValueError(f"Unsupported Lakehouse merge action: {kind}.")
    builder.execute()
