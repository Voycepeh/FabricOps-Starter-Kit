"""Public owner for governed source-read preparation."""

from __future__ import annotations

from typing import Any, Mapping

from fabricops_kit.config.shared import build_table_id, get_store, resolve_fabric_context
from fabricops_kit.io.shared import resolve_lakehouse_table_location, resolve_warehouse_table_location
from fabricops_kit.pipeline.check_changes import _observation_changes
from fabricops_kit.pipeline.observe_table import _observe_table_core
from fabricops_kit.pipeline.shared import resolve_table_processing_definition


def _resolve_processing_scope(changes: Mapping[str, Any], processing: Mapping[str, Any]) -> dict[str, Any]:
    """Combine source-change evidence and one resolved load definition."""
    strategy = str(processing["load_strategy"])
    if not changes.get("changed"):
        return {"read_strategy": "skip", "partition_column": changes.get("partition_column"), "partition_values": []}
    if changes.get("first_observation"):
        return {"read_strategy": "full", "partition_column": changes.get("partition_column"), "partition_values": []}

    new = list(changes.get("new_partitions") or [])
    changed = list(changes.get("changed_partitions") or [])
    reappeared = list(changes.get("reappeared_partitions") or [])
    removed = list(changes.get("removed_partitions") or [])
    partition_column = str(changes.get("partition_column") or "").strip() or None
    existing_changes = [*changed, *reappeared]

    if removed:
        if strategy == "overwrite" and not processing.get("partition_column"):
            return {"read_strategy": "full", "partition_column": partition_column, "partition_values": []}
        raise ValueError(f"{strategy} cannot safely apply removed source partitions without explicit delete semantics.")
    if strategy == "append" and existing_changes:
        raise ValueError("append is unsafe when an existing source partition changed or reappeared.")

    affected = [*new, *existing_changes]
    if not affected or not partition_column:
        if strategy == "append":
            raise ValueError(
                "append requires a non-empty, partition-scoped additive source change; "
                "a full-source append is unsafe."
            )
        return {"read_strategy": "full", "partition_column": partition_column, "partition_values": []}
    if strategy == "overwrite" and processing.get("partition_column") != partition_column:
        return {"read_strategy": "full", "partition_column": partition_column, "partition_values": []}
    return {"read_strategy": "incremental", "partition_column": partition_column, "partition_values": affected}



def read_pipeline_prep(
    source_table_name: str,
    target_table_name: str,
    *,
    source_target: str = "source",
    source_schema: str | None = None,
    target: str = "unified",
    schema: str | None = None,
    load_strategy: str,
    load_strategy_parameters: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Prepare governed source observation and read scope without reading business data.

    Parameters
    ----------
    source_table_name : str
        Physical source table to observe before its visible notebook read.
    target_table_name : str
        Governed target table whose processing definition controls this run.
    source_target : str, default="source"
        Configured source Lakehouse or Warehouse target.
    source_schema : str or None, default=None
        Optional source schema.
    target : str, default="unified"
        Configured governed target.
    schema : str or None, default=None
        Optional governed target schema.
    load_strategy : {"overwrite", "append", "scd1", "scd2"}
        Current Development-authored target strategy. Frozen contract processing
        overrides it for selected Development and active Production contracts.
    load_strategy_parameters : dict, optional
        Parameters owned by the authored load strategy.

    Returns
    -------
    dict
        Observation and change evidence, resolved processing, and the prepared
        ``skip``, ``full``, or ``incremental`` source-read scope.

    Raises
    ------
    ValueError
        If identities, contract processing, or processing scope are invalid.

    Notes
    -----
    This function observes the source but does not physically read its business
    DataFrame and does not write the governed target.

    Examples
    --------
    >>> prep = read_pipeline_prep(
    ...     "student_enrolment", "students", source_schema="dbo", schema="dbo",
    ...     load_strategy="scd1", load_strategy_parameters={"key_columns": ["student_id"]},
    ... )
    >>> prep["read_strategy"] in {"skip", "full", "incremental"}
    True

    See Also
    --------
    write_pipeline_prep, observe_table, check_changes, read_lakehouse_table

    """
    config, env, context = resolve_fabric_context()
    store = get_store(config, env, target)
    store_type = str(store.kind).strip().lower()
    if store_type == "lakehouse":
        table_name, schema_name, _path = resolve_lakehouse_table_location(store, target_table_name, schema)
    elif store_type == "warehouse":
        schema_name, table_name, _object = resolve_warehouse_table_location(
            store, schema or getattr(store, "schema", None), target_table_name
        )
    else:
        raise ValueError(f"Target {target!r} must resolve to a Lakehouse or Warehouse.")
    table_id = build_table_id(store_type, target, schema_name, table_name)
    observation = _observe_table_core(source_table_name, target=source_target, schema=source_schema)
    changes = _observation_changes(observation)
    processing = resolve_table_processing_definition(
        config,
        env,
        table_id,
        spark_session=getattr(observation, "sparkSession", None),
        context=context,
        authored_processing={"load_strategy": load_strategy, **(load_strategy_parameters or {})},
    )
    scope = _resolve_processing_scope(changes, processing)
    if store_type == "warehouse" and processing["load_strategy"] == "overwrite":
        scope = {"read_strategy": "full", "partition_column": None, "partition_values": []}
    return {"observation": observation, "changes": changes, "processing": processing, **scope}
