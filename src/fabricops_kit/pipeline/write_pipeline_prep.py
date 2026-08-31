"""Public owner for governed target-write preparation."""

from __future__ import annotations

from typing import Any

from fabricops_kit.config.shared import resolve_fabric_context
from fabricops_kit.pipeline.shared import (
    add_target_audit_fields,
    catalogue_authored_processing,
    resolve_catalogue_table_identity,
    resolve_table_processing_definition,
    resolve_target_audit_fields,
)


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


def _source_completion(source_preps: list[dict[str, Any]]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Validate source preparation and return one truthful target scope plus completion rows."""
    if not source_preps:
        raise ValueError("source_preps must contain at least one read_pipeline_prep result.")
    scopes = []
    completion_sources = []
    for prep in source_preps:
        if not isinstance(prep, dict):
            raise ValueError("source_preps must contain read_pipeline_prep result dictionaries.")
        read_mode = prep.get("read_mode")
        scope = prep.get("scope")
        if read_mode not in {"full_dataset", "incremental_subset"} or not isinstance(scope, dict):
            raise ValueError("Each source prep must contain a non-skipped canonical read_mode and scope.")
        scopes.append({"read_mode": read_mode, "scope": scope})
        candidate = prep.get("candidate_checkpoint")
        if candidate is not None:
            completion_sources.append({
                "type": "watermark",
                "source": prep.get("source"),
                "source_processing": prep.get("source_processing"),
                "candidate": candidate,
            })
        observation = prep.get("observation")
        changes = prep.get("changes")
        if observation is not None and isinstance(changes, dict):
            completion_sources.append({
                "type": "partition",
                "table_id": changes.get("table_id"),
                "environment_name": changes.get("environment_name"),
                "observation_id": changes.get("observation_id"),
            })
    if all(scope == scopes[0] for scope in scopes[1:]):
        return scopes[0], completion_sources
    return {
        "read_mode": "incremental_subset",
        "scope": {"type": "multiple_sources"},
    }, completion_sources


def write_pipeline_prep(
    df,
    *,
    target_table_id: str,
    source_preps: list[dict[str, Any]],
) -> dict[str, Any]:
    """Prepare governed target write inputs without physically writing the target.

    Parameters
    ----------
    df : pyspark.sql.DataFrame
        Business target DataFrame after target schema and DQ checks pass.
    target_table_id : str
        Canonical registered target identity used to resolve physical target
        metadata and target-owned processing.
    source_preps : list of dict
        Results returned by :func:`read_pipeline_prep` for the sources that fed
        this target. Candidate checkpoint state is committed only after the
        physical target writer succeeds.

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
    Warehouse overwrite requires a full-dataset source result because Warehouse
    has no Lakehouse-style partition replacement. Lakehouse partition overwrite
    remains scoped with ``replaceWhere``.

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
    target_identity = resolve_catalogue_table_identity(config, env, target_table_id, context=context)
    processing = resolve_table_processing_definition(
        config,
        env,
        target_identity["table_id"],
        context=context,
        authored_processing=catalogue_authored_processing(target_identity),
    )
    prepared_scope, completion_sources = _source_completion(source_preps)
    scope = prepared_scope["scope"]
    store_kind = target_identity["store_type"]
    strategy = str(processing.get("load_strategy") or "")
    if strategy == "overwrite" and scope.get("type") == "multiple_sources":
        raise ValueError(
            "overwrite cannot infer one safe target scope from differing source scopes; "
            "publish this target from one complete source scope."
        )
    if store_kind == "warehouse" and strategy == "overwrite" and prepared_scope["read_mode"] != "full_dataset":
        raise ValueError(
            "Warehouse overwrite requires a full-dataset source result; "
            "incremental subsets cannot safely replace the complete target."
        )
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
        "scope": prepared_scope,
        "target": target_identity,
        "target_kind": store_kind,
        "completion": {"sources": completion_sources} if completion_sources else None,
    }
