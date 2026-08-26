"""Public owner for governed source-read preparation."""

from __future__ import annotations

from typing import Any, Mapping

from fabricops_kit.config.shared import resolve_fabric_context
from fabricops_kit.pipeline.check_changes import _observation_changes
from fabricops_kit.pipeline.observe_table import _observe_table_core
from fabricops_kit.pipeline.shared import resolve_physical_table_identity, resolve_table_processing_definition


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
        Canonical ``source`` and ``target`` table identities, observation and
        change evidence, resolved processing, and the prepared ``skip``,
        ``full``, or ``incremental`` source-read scope. Each identity contains
        ``table_id``, ``target``, normalized ``schema`` and ``table_name``, and
        ``store_kind``. The active environment remains separate.

    Raises
    ------
    ValueError
        If identities, contract processing, or processing scope are invalid.

    Notes
    -----
    This function observes the source internally but does not physically read
    its business DataFrame and does not write the governed target.

    Examples
    --------
    >>> prep = read_pipeline_prep(
    ...     "student_enrolment", "students", source_schema="dbo", schema="dbo",
    ...     load_strategy="scd1", load_strategy_parameters={"key_columns": ["student_id"]},
    ... )
    >>> prep["read_strategy"] in {"skip", "full", "incremental"}
    True
    >>> prep["target"]["table_name"]
    'students'

    See Also
    --------
    write_pipeline_prep, check_changes, read_lakehouse_table

    """
    config, env, context = resolve_fabric_context()
    source_identity = resolve_physical_table_identity(
        config, env, target=source_target, schema=source_schema, table_name=source_table_name
    )
    target_identity = resolve_physical_table_identity(
        config, env, target=target, schema=schema, table_name=target_table_name
    )
    observation = _observe_table_core(
        source_identity["table_name"], target=source_identity["target"], schema=source_identity["schema"]
    )
    changes = _observation_changes(observation)
    processing = resolve_table_processing_definition(
        config,
        env,
        target_identity["table_id"],
        spark_session=getattr(observation, "sparkSession", None),
        context=context,
        authored_processing={"load_strategy": load_strategy, **(load_strategy_parameters or {})},
    )
    scope = _resolve_processing_scope(changes, processing)
    if (
        target_identity["store_kind"] == "warehouse"
        and processing["load_strategy"] == "overwrite"
        and scope["read_strategy"] == "incremental"
    ):
        scope = {"read_strategy": "full", "partition_column": None, "partition_values": []}
    return {
        "source": source_identity,
        "target": target_identity,
        "observation": observation,
        "changes": changes,
        "processing": processing,
        **scope,
    }
