"""Public owner for governed target-write preparation."""

from __future__ import annotations

from typing import Any

from fabricops_kit.config.shared import get_store, resolve_fabric_context
from fabricops_kit.pipeline.shared import add_target_audit_fields, resolve_target_audit_fields


def _replace_where(partition_column: str, values: list[Any]) -> str:
    """Return a safely quoted Delta partition-replacement predicate."""

    def literal(value: Any) -> str:
        if value is None:
            return "NULL"
        if isinstance(value, bool):
            return "TRUE" if value else "FALSE"
        if isinstance(value, int | float):
            return str(value)
        return "'" + str(value).replace("'", "''") + "'"

    quoted = str(partition_column).replace("`", "``")
    return f"`{quoted}` IN ({', '.join(literal(value) for value in values)})"


def write_pipeline_prep(df, read_prep: dict[str, Any], *, target: str = "unified") -> dict[str, Any]:
    """Prepare governed target write inputs without physically writing the target.

    Parameters
    ----------
    df : pyspark.sql.DataFrame
        Business target DataFrame after target schema and DQ checks pass.
    read_prep : dict
        Exact result returned by :func:`read_pipeline_prep`. Its canonical
        ``processing`` definition is reused without contract re-resolution.
    target : str, default="unified"
        Configured Lakehouse or Warehouse target used to prepare physical
        writer settings.

    Returns
    -------
    dict
        Audited target DataFrame, physical writer mode/options, the unchanged
        resolved processing definition, its prepared scope, and an optional
        governed completion context for the physical writer.

    Raises
    ------
    ValueError
        If preparation is incomplete or an unsafe target/strategy combination
        is requested.

    Notes
    -----
    FabricOps resolves one run-level audit record and adds only compact target
    provenance fields. This function does not call a Lakehouse or Warehouse
    writer or commit source progress. The completion context has no effect
    unless explicitly passed to a FabricOps writer. Lakehouse and Warehouse
    targets use the same governed strategy definition; each writer applies its
    engine-specific physical execution only after this preparation succeeds.

    Examples
    --------
    >>> write_prep = write_pipeline_prep(transformed_df, read_prep, target="unified")
    >>> write_prep["mode"]
    'append'

    See Also
    --------
    read_pipeline_prep, write_lakehouse_table, write_warehouse_table

    """
    processing = read_prep.get("processing")
    if not isinstance(processing, dict):
        raise ValueError("read_prep must contain the resolved processing definition.")
    read_mode = read_prep.get("read_mode")
    scope = read_prep.get("scope")
    if read_mode not in {"skip", "full_dataset", "incremental_subset"} or not isinstance(scope, dict):
        raise ValueError("read_prep must contain a canonical read_mode and scope.")
    if read_mode == "skip":
        raise ValueError("A skipped pipeline run has no target write to prepare.")
    config, env, context = resolve_fabric_context()
    store_kind = str(get_store(config, env, target).kind).strip().lower()
    strategy = str(processing.get("load_strategy") or "")
    audit = resolve_target_audit_fields(context)
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
    options: dict[str, Any] = {}
    if store_kind == "lakehouse" and strategy == "overwrite" and scope.get("type") == "partition":
        options["replaceWhere"] = _replace_where(str(scope["column"]), list(scope.get("values") or []))
    completion_sources = []
    candidate = read_prep.get("candidate_checkpoint")
    if candidate is not None:
        completion_sources.append({
            "type": "watermark",
            "source": read_prep.get("source"),
            "source_processing": read_prep.get("source_processing"),
            "candidate": candidate,
        })
    observation = read_prep.get("observation")
    changes = read_prep.get("changes")
    if observation is not None and isinstance(changes, dict):
        completion_sources.append({
            "type": "partition",
            "table_id": changes.get("table_id"),
            "environment_name": changes.get("environment_name"),
            "observation_id": changes.get("observation_id"),
        })
    return {
        "df": prepared_df,
        "mode": mode,
        "options": options,
        "load_strategy": strategy,
        "load_strategy_parameters": {
            name: value
            for name, value in processing.items()
            if name not in {"load_strategy", "source", "contract_id", "contract_version"}
        },
        "processing": processing,
        "scope": {"read_mode": read_mode, "scope": scope},
        "target_kind": store_kind,
        "completion": {"sources": completion_sources} if completion_sources else None,
    }
