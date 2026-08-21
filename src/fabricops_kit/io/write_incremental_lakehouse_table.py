"""Owner file for strategy-aware incremental Lakehouse writes."""

from typing import Any

from .shared import (
    get_spark_session,
    resolve_configured_lakehouse_table,
    write_delta_path,
)


def _quoted(name: str) -> str:
    return f"`{name.replace('`', '``')}`"


def _assert_columns(df, names: list[str], label: str) -> None:
    missing = [name for name in names if name not in df.columns]
    if missing:
        raise ValueError(f"{label} column(s) missing from dataframe: {', '.join(missing)}.")


def _assert_unique(df, keys: list[str]) -> None:
    from pyspark.sql import functions as F

    if df.groupBy(*keys).agg(F.count(F.lit(1)).alias("_count")).where(F.col("_count") > 1).limit(1).count():
        raise ValueError("Incremental source contains duplicate business keys.")


def _merge(df, delta_target, keys: list[str]) -> None:
    condition = " AND ".join(f"target.{_quoted(key)} <=> source.{_quoted(key)}" for key in keys)
    (delta_target.alias("target").merge(df.alias("source"), condition).whenMatchedUpdateAll().whenNotMatchedInsertAll().execute())


def _scd2(df, delta_target, keys: list[str], effective: str, tracked_columns: list[str] | None) -> None:
    from pyspark.sql import functions as F

    technical = {"valid_from", "valid_to", "is_current"}
    audit = {name for name in df.columns if name.startswith("_")}
    tracked = list(tracked_columns or [name for name in df.columns if name not in {*keys, effective, *technical, *audit}])
    _assert_columns(df, tracked, "tracked")
    current = delta_target.toDF().where(F.col("is_current") == F.lit(True))
    if current.groupBy(*keys).count().where(F.col("count") > 1).limit(1).count():
        raise ValueError("SCD2 target contains more than one current row for a business key.")
    join_condition = [df[key].eqNullSafe(current[key]) for key in keys]
    joined = df.alias("source").join(current.alias("target"), join_condition, "left")
    missing = F.col(f"target.{keys[0]}").isNull()
    changed = F.lit(False)
    for name in tracked:
        changed = changed | ~F.col(f"source.{name}").eqNullSafe(F.col(f"target.{name}"))
    versions = joined.where(missing | changed).select("source.*").cache()
    versions.count()  # Materialize before current rows are expired.
    expire_condition = " AND ".join(f"target.{_quoted(key)} <=> source.{_quoted(key)}" for key in keys)
    expire_condition += " AND target.is_current = true"
    (
        delta_target.alias("target")
        .merge(versions.alias("source"), expire_condition)
        .whenMatchedUpdate(set={"valid_to": f"source.{_quoted(effective)}", "is_current": "false"})
        .execute()
    )
    output = versions
    for name in technical & set(output.columns):
        output = output.drop(name)
    output = output.withColumn("valid_from", F.col(effective)).withColumn(
        "valid_to", F.lit(None).cast(df.schema[effective].dataType)
    ).withColumn("is_current", F.lit(True))
    output.write.mode("append").format("delta").save(delta_target.detail().select("location").first()["location"])
    versions.unpersist()


def write_incremental_lakehouse_table(
    df,
    table_name: str,
    plan: dict,
    *,
    target: str = "target",
    schema: str | None = None,
    tracked_columns: list[str] | tuple[str, ...] | None = None,
    spark_session=None,
    context: dict[str, Any] | None = None,
) -> None:
    """Apply an incremental processing plan to a Fabric Lakehouse Delta target.

    Parameters
    ----------
    df : pyspark.sql.DataFrame
        Transformed and validated rows in the read scope selected by ``plan``.
    table_name : str
        Configured target Lakehouse table name.
    plan : dict
        Result returned by :func:`plan_incremental_processing`.
    target : str, default="target"
        Logical Lakehouse target from ``00_env_config``.
    schema : str, optional
        Lakehouse schema, when schema support is enabled.
    tracked_columns : list of str or tuple of str, optional
        SCD2 business columns to compare. By default non-key, non-effective,
        non-technical, non-audit input columns are compared.
    spark_session : pyspark.sql.SparkSession, optional
        Explicit Spark session; the active Fabric session is used by default.
    context : dict, optional
        Resolved FabricOps runtime context.

    Returns
    -------
    None
        The function writes or merges the target, or returns without writing
        when the plan says ``skip``.

    Raises
    ------
    ValueError
        If plan fields, required columns, or key uniqueness are invalid.
    RuntimeError
        If Delta Lake operations are unavailable in the runtime.

    Notes
    -----
    Merge implements current-state/SCD Type 1 upserts. SCD2 maintains
    ``valid_from``, ``valid_to``, and ``is_current`` and never infers deletes.

    Examples
    --------
    >>> write_incremental_lakehouse_table(transformed, "orders", plan, target="curated")

    See Also
    --------
    plan_incremental_processing, write_lakehouse_table

    """
    read_strategy = plan.get("read_strategy")
    strategy = plan.get("write_strategy")
    if read_strategy == "skip":
        return
    if read_strategy not in {"full", "incremental"} or strategy not in {"overwrite", "append", "merge", "scd2"}:
        raise ValueError("plan must be returned by plan_incremental_processing().")
    _store, _table, _schema, path = resolve_configured_lakehouse_table(target, table_name, schema, context=context)
    if strategy in {"overwrite", "append"}:
        options = None
        mode = strategy
        if strategy == "overwrite" and read_strategy == "incremental":
            column = plan.get("partition_column")
            values = list(plan.get("partition_values") or [])
            if not column or not values:
                raise ValueError("Incremental overwrite requires partition_column and partition_values.")
            _assert_columns(df, [column], "partition")
            literals = ", ".join("'" + str(value).replace("'", "''") + "'" for value in values)
            options = {"replaceWhere": f"{_quoted(column)} IN ({literals})"}
        write_delta_path(df, path, mode=mode, partition_by=plan.get("partition_column"), options=options)
        return

    keys = list(plan.get("key_columns") or [])
    _assert_columns(df, keys, "key")
    _assert_unique(df, keys)
    spark = get_spark_session(spark_session or getattr(df, "sparkSession", None))
    try:
        from delta.tables import DeltaTable
    except Exception as exc:
        raise RuntimeError("Delta Lake MERGE support is required in the Fabric Spark runtime.") from exc
    if not DeltaTable.isDeltaTable(spark, path):
        if strategy == "merge":
            write_delta_path(df, path, mode="overwrite")
        else:
            effective = plan.get("effective_column")
            _assert_columns(df, [effective], "effective")
            from pyspark.sql import functions as F

            initialized = df.withColumn("valid_from", F.col(effective)).withColumn(
                "valid_to", F.lit(None).cast(df.schema[effective].dataType)
            ).withColumn("is_current", F.lit(True))
            write_delta_path(initialized, path, mode="overwrite")
        return
    delta_target = DeltaTable.forPath(spark, path)
    if strategy == "merge":
        _merge(df, delta_target, keys)
    else:
        effective = plan.get("effective_column")
        _assert_columns(df, [effective], "effective")
        _scd2(df, delta_target, keys, effective, list(tracked_columns) if tracked_columns else None)
