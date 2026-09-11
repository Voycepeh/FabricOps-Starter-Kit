"""Public owner for governed target-write preparation."""

from __future__ import annotations

from typing import Any

from fabricops_kit.config.shared import resolve_fabric_context
from fabricops_kit.pipeline.shared import (
    add_target_audit_fields,
    catalogue_authored_processing,
    resolve_catalogue_table_identity,
    resolve_physical_table_identity,
    resolve_table_processing_definition,
    resolve_target_audit_fields,
)


def _delta_literal(value: Any) -> str:
    """Return a safely encoded primitive Delta predicate literal."""
    if value is None:
        return "NULL"
    if isinstance(value, bool):
        return "TRUE" if value else "FALSE"
    if isinstance(value, int | float):
        return str(value)
    return "'" + str(value).replace("'", "''") + "'"


def _replace_where(partition_column: str, values: list[Any]) -> str:
    """Return a safely quoted Delta partition-replacement predicate."""
    quoted = str(partition_column).replace("`", "``")
    return f"`{quoted}` IN ({', '.join(_delta_literal(value) for value in values)})"


def _write_scope(source_preps: list[dict[str, Any]]) -> dict[str, Any]:
    """Validate source participation and return the default complete write scope."""
    if not source_preps:
        raise ValueError("source_preps must contain at least one read_pipeline_prep result.")
    for prep in source_preps:
        if not isinstance(prep, dict) or not prep.get("table_id") or not isinstance(prep.get("source"), dict):
            raise ValueError("source_preps must contain read_pipeline_prep result dictionaries.")
    return {"type": "full_dataset"}


def _validate_target_writer_ownership(
    *, table_id: str, processing: dict[str, Any], audit: dict[str, Any]
) -> None:
    """Require the current notebook to match the writer frozen in the contract."""
    if processing.get("source") != "data_contract":
        return
    owner_name = str(processing.get("owner_notebook_name") or "").strip()
    if not owner_name:
        raise ValueError(
            f"Data Contract for target table_id {table_id!r} has no owning notebook_name; "
            "freeze the contract from the target's owning pipeline before writing."
        )
    owner_id = str(processing.get("owner_notebook_id") or "").strip()
    current_name = str(audit.get("_notebook_name") or "").strip()
    current_id = str(audit.get("_notebook_id") or "").strip()
    if current_name != owner_name:
        raise ValueError(
            f"Target table_id {table_id!r} is owned by notebook {owner_name!r} "
            f"(contract notebook_id {owner_id!r}); current writer is {current_name or current_id!r} "
            f"(runtime notebook_id {current_id!r}). "
            "One governed target table_id must have one owning pipeline/notebook writer."
        )

def write_pipeline_prep(
    df,
    *,
    target_table_id: str | None = None,
    target: str | None = None,
    schema: str | None = None,
    table_name: str | None = None,
    load_strategy: str | None = None,
    load_strategy_parameters: dict[str, Any] | None = None,
    source_preps: list[dict[str, Any]],
) -> dict[str, Any]:
    """Prepare governed target write inputs without physically writing the target.

    Parameters
    ----------
    df : pyspark.sql.DataFrame
        Business target DataFrame after target schema and DQ checks pass.
    target_table_id : str, optional
        Canonical registered target identity used to resolve physical target
        metadata. A selected or active frozen Data Contract is authoritative
        for its load strategy, parameters, and owning logical notebook name.
    target : str, optional
        Configured target key supplied instead of ``target_table_id``.
    schema : str, optional
        Physical target schema, when the configured store uses schemas.
    table_name : str, optional
        Physical target table name. Required with ``target`` when
        ``target_table_id`` is omitted.
    load_strategy : {"overwrite", "append", "scd1", "scd2"}, optional
        Current authored load strategy when physical identity is supplied.
    load_strategy_parameters : dict, optional
        Parameters belonging to the authored load strategy.
    source_preps : list of dict
        Results returned by :func:`read_pipeline_prep` for the sources that fed
        this target.

    Returns
    -------
    dict
        Audited target DataFrame, physical writer mode/options, the unchanged
        resolved processing definition, prepared scope, and post-write success context.

    Raises
    ------
    ValueError
        If preparation is incomplete or an unsafe target/strategy combination
        is requested, or if a contract-backed target is invoked by a notebook
        other than its frozen owner.

    Notes
    -----
    FabricOps resolves one run-level audit record and adds only compact target
    provenance fields. This function does not call a Lakehouse or Warehouse
    writer. It does not persist successful target Lineage or accept Source Observations;
    the physical writer commits those records only after publication succeeds.
    Lakehouse and Warehouse targets use the same governed target strategy
    definition; each writer applies its engine-specific physical execution only
    after this preparation succeeds. One governed target ``table_id`` must have
    one owning pipeline/notebook writer because independent writers can race,
    duplicate writes, overwrite state, or break SCD history.

    Examples
    --------
    >>> write_prep = write_pipeline_prep(
    ...     transformed_df,
    ...     target_table_id="lakehouse:unified:dbo:students",
    ...     source_preps=[read_prep],
    ... )
    >>> write_prep["mode"]
    'append'

    See Also
    --------
    read_pipeline_prep, write_lakehouse_table, write_warehouse_table

    """
    config, env, context = resolve_fabric_context()
    coordinates = (target, schema, table_name)
    if target_table_id and any(value is not None for value in coordinates):
        raise ValueError("target_table_id cannot be combined with target, schema, or table_name.")
    if target_table_id:
        target_identity = resolve_catalogue_table_identity(config, env, target_table_id, context=context)
        authored_processing = catalogue_authored_processing(target_identity)
    else:
        target_identity = resolve_physical_table_identity(
            config, env, target=target, schema=schema, table_name=table_name
        )
        target_identity["store_type"] = target_identity["store_kind"]
        authored_processing = {"load_strategy": load_strategy, **(load_strategy_parameters or {})}
    processing = resolve_table_processing_definition(
        config,
        env,
        target_identity["table_id"],
        context=context,
        authored_processing=authored_processing,
    )
    prepared_scope = _write_scope(source_preps)
    store_kind = target_identity["store_type"]
    strategy = str(processing.get("load_strategy") or "")
    options: dict[str, Any] = {}
    partition_column = str(processing.get("partition_column") or "")
    if strategy == "overwrite" and partition_column:
        if store_kind != "lakehouse":
            raise ValueError("Partition-scoped overwrite is supported only for Lakehouse targets.")
        if partition_column not in df.columns:
            raise ValueError(f"Target partition column {partition_column!r} is missing from the prepared DataFrame.")
        from pyspark.sql import functions as F

        partition_rows = df.select(partition_column).distinct().collect()
        partition_values = [row[partition_column] for row in partition_rows]
        if not partition_values or any(value is None for value in partition_values):
            raise ValueError("Target partition-scoped overwrite requires non-null partition values.")
        if "_partition_bucket" in df.columns:
            raise ValueError("_partition_bucket is a reserved FabricOps technical column and must not be supplied.")
        df = df.withColumn("_partition_bucket", F.col(partition_column))
        prepared_scope = {"type": "partition", "column": partition_column, "values": partition_values}
        options = {"replaceWhere": _replace_where("_partition_bucket", partition_values)}
    audit = resolve_target_audit_fields(context)
    _validate_target_writer_ownership(
        table_id=str(target_identity["table_id"]), processing=processing, audit=audit
    )
    prepared_df = add_target_audit_fields(df, audit)
    if strategy == "scd2":
        from pyspark.sql import functions as F

        effective = str(processing["effective_column"])
        effective_type = prepared_df.schema[effective].dataType
        prepared_df = (
            prepared_df.withColumn("_effective_from", F.col(effective))
            .withColumn("_effective_to", F.lit(None).cast(effective_type))
            .withColumn("_is_current", F.lit(True))
        )

    mode = strategy if strategy in {"overwrite", "append"} else None
    context["_fabricops_active_profile_registration"] = {
        "profile_role": "target",
        "table": dict(target_identity),
        "load_strategy": strategy,
        "load_strategy_parameters": {
            name: value
            for name, value in processing.items()
            if name not in {
                "load_strategy", "source", "contract_id", "contract_version",
                "owner_notebook_id", "owner_notebook_name",
            }
        },
    }
    return {
        "df": prepared_df,
        "mode": mode,
        "options": options,
        "load_strategy": strategy,
        "load_strategy_parameters": {
            name: value
            for name, value in processing.items()
            if name not in {
                "load_strategy", "source", "contract_id", "contract_version",
                "owner_notebook_id", "owner_notebook_name",
            }
        },
        "processing": processing,
        "scope": prepared_scope,
        "target": target_identity,
        "target_kind": store_kind,
        "success_context": {
            "target_table_id": target_identity["table_id"],
            "source_table_ids": [str(prep["table_id"]) for prep in source_preps],
            "activity_id": audit["_activity_id"],
            "notebook_name": audit["_notebook_name"],
            "notebook_id": audit["_notebook_id"],
        },
        "lineage": {
            "table_id": target_identity["table_id"],
            "pipeline_role": "target",
            "activity_id": audit["_activity_id"],
            "environment_name": env,
        },
    }
