"""Public owner for table-specific PII token-map persistence."""

from __future__ import annotations

import hashlib
from typing import Any

from fabricops_kit.config.shared import resolve_fabric_context
from fabricops_kit.io.shared import (
    get_spark_session,
    resolve_configured_lakehouse_table,
    write_delta_path,
)
from fabricops_kit.pipeline.shared import (
    add_target_audit_fields,
    resolve_catalogue_table_identity,
    resolve_target_audit_fields,
)


def _token_map_table_name(table_id: str, table_name: str) -> str:
    """Return one deterministic, readable token-map table name per governed table."""
    digest = hashlib.sha256(str(table_id).encode("utf-8")).hexdigest()[:8]
    return f"{table_name}__{digest}__pii_token_map"


def _build_token_map_frame(
    df,
    *,
    table_id: str,
    column_id: str,
    original_column: str,
    token_column: str,
    context: dict[str, Any],
):
    """Return one validated, deduplicated token-map frame for persistence."""
    available = list(getattr(df, "columns", []) or [])
    missing = [name for name in (original_column, token_column) if name not in available]
    if missing:
        raise ValueError(f"PII token-map column(s) do not exist in df: {', '.join(missing)}.")
    if original_column == token_column:
        raise ValueError("original_column and token_column must be different columns.")

    from pyspark.sql import functions as F

    original_field = next(field for field in df.schema.fields if field.name == original_column)
    original_data_type = original_field.dataType.simpleString()
    pairs = (
        df.select(
            F.col(original_column).cast("string").alias("original_value"),
            F.col(token_column).cast("string").alias("token_value"),
        )
        .dropDuplicates(["original_value", "token_value"])
    )
    if pairs.where(F.col("original_value").isNull() | F.col("token_value").isNull()).limit(1).count():
        raise ValueError("PII token-map original and token values must be non-null.")
    original_conflict = (
        pairs.groupBy("original_value")
        .agg(F.countDistinct("token_value").alias("token_count"))
        .where(F.col("token_count") > 1)
        .limit(1)
        .count()
    )
    if original_conflict:
        raise ValueError("One original value cannot map to multiple token values in the same token-map write.")
    token_conflict = (
        pairs.groupBy("token_value")
        .agg(F.countDistinct("original_value").alias("original_count"))
        .where(F.col("original_count") > 1)
        .limit(1)
        .count()
    )
    if token_conflict:
        raise ValueError("One token value cannot map to multiple original values in the same token-map write.")

    mapping = (
        pairs.withColumn("table_id", F.lit(table_id))
        .withColumn("column_id", F.lit(column_id))
        .withColumn("original_data_type", F.lit(original_data_type))
        .select(
            "table_id",
            "column_id",
            "original_value",
            "token_value",
            "original_data_type",
        )
    )
    return add_target_audit_fields(mapping, resolve_target_audit_fields(context))


def _upsert_token_map(mapping_df, path: str) -> str:
    """Create or idempotently merge one Delta token-map table."""
    spark = getattr(mapping_df, "sparkSession", None) or get_spark_session()
    try:
        from delta.tables import DeltaTable
    except Exception as exc:  # pragma: no cover - Fabric runtime dependency
        raise RuntimeError("Delta Lake support is required to persist a PII token map.") from exc

    if not DeltaTable.isDeltaTable(spark, path):
        write_delta_path(mapping_df, path, mode="errorifexists")
        return "created"

    from pyspark.sql import functions as F

    delta = DeltaTable.forPath(spark, path)
    existing = delta.toDF()
    required = {"table_id", "column_id", "original_value", "token_value"}
    missing = sorted(required - set(existing.columns))
    if missing:
        raise ValueError(
            "Existing PII token-map table has an incompatible schema; missing column(s): "
            + ", ".join(missing)
            + "."
        )

    original_conflict = (
        mapping_df.alias("incoming")
        .join(
            existing.alias("existing"),
            on=["table_id", "column_id", "original_value"],
            how="inner",
        )
        .where(F.col("incoming.token_value") != F.col("existing.token_value"))
        .limit(1)
        .count()
    )
    if original_conflict:
        raise ValueError("Existing PII token map already assigns a different token to an original value.")

    token_conflict = (
        mapping_df.alias("incoming")
        .join(
            existing.alias("existing"),
            on=["table_id", "column_id", "token_value"],
            how="inner",
        )
        .where(F.col("incoming.original_value") != F.col("existing.original_value"))
        .limit(1)
        .count()
    )
    if token_conflict:
        raise ValueError("Existing PII token map already assigns a token to a different original value.")

    (
        delta.alias("target")
        .merge(
            mapping_df.alias("source"),
            "target.table_id = source.table_id AND "
            "target.column_id = source.column_id AND "
            "target.original_value = source.original_value",
        )
        .whenNotMatchedInsertAll()
        .execute()
    )
    return "merged"


def write_pii_token_map(
    df,
    *,
    table_id: str,
    column_id: str,
    original_column: str,
    token_column: str,
    target: str = "support",
    schema: str | None = None,
) -> dict[str, Any]:
    """Persist reversible PII mappings for one governed table outside metadata.

    ``write_pii_token_map`` is a Preview pipeline helper intended for
    ``02_pipeline`` after project code has produced an approved tokenised
    representation of a Direct PII column. It writes only the mapping needed to
    recover the original value; it does not tokenise values itself.

    The governed ``table_id`` is resolved through the Data Catalogue to obtain
    the physical table name. FabricOps then derives one deterministic support
    table name from that physical name and ``table_id`` and writes the mapping
    to a caller-selected configured Lakehouse target. The support target may be
    the same Lakehouse as the governed table with a separate schema, or a
    different configured Lakehouse with tighter permissions.

    Parameters
    ----------
    df : pyspark.sql.DataFrame
        DataFrame containing both the original PII values and their approved
        token values. Only the selected mapping columns are persisted.
    table_id : str
        Canonical governed table identity from ``METADATA_DATA_CATALOGUE``.
        It identifies which physical table this support asset belongs to.
    column_id : str
        Canonical Catalogue column identity for the PII column represented by
        this mapping.
    original_column : str
        Column in ``df`` containing the original PII value.
    token_column : str
        Column in ``df`` containing the tokenised value that replaces the
        original value in the governed physical table.
    target : str, default="support"
        Logical Lakehouse target configured in ``00_env_config`` for support
        assets. This can point to the governed table's Lakehouse or to a
        separate restricted Lakehouse.
    schema : str or None, default=None
        Optional support-schema override. When omitted, the configured schema
        for ``target`` is used when that Lakehouse is schema-enabled.

    Returns
    -------
    dict[str, Any]
        Resolved support location containing ``table_id``, ``column_id``,
        ``target``, ``schema``, ``table_name``, ``path``, and ``action``.
        ``action`` is ``created`` for a new map or ``merged`` when an existing
        map was idempotently extended.

    Raises
    ------
    ValueError
        If the governed ``table_id`` cannot be resolved, mapping columns are
        missing or invalid, mappings are not one-to-one, the configured support
        target is not a Lakehouse, or an existing token map conflicts with the
        incoming mapping.
    RuntimeError
        If Delta Lake support is unavailable in the active Fabric Spark runtime.

    Notes
    -----
    The persisted support table contains ``table_id``, ``column_id``,
    ``original_value``, ``token_value``, ``original_data_type``, and FabricOps
    audit fields. Original and token values are stored as strings so one
    table-specific map can hold mappings for multiple governed columns while
    retaining the original Spark datatype for reconstruction.

    Repeated writes are idempotent for an existing mapping. FabricOps never
    changes an established token for an original value and never reuses one
    token for a different original value within the same table and column.

    This table contains sensitive reversible mappings and must be placed in a
    Lakehouse/schema with permissions appropriate to that sensitivity. It is an
    operational support asset for ``02_pipeline`` and is not written to the
    FabricOps metadata schema.

    Examples
    --------
    >>> result = write_pii_token_map(
    ...     transformed_df,
    ...     table_id=TARGET_TABLE_ID,
    ...     column_id=EMAIL_COLUMN_ID,
    ...     original_column="email_address",
    ...     token_column="email_address_token",
    ...     target="support",
    ...     schema="fabricops_support",
    ... )
    >>> result["table_name"].endswith("__pii_token_map")
    True

    """
    if not str(table_id or "").strip():
        raise ValueError("table_id is required.")
    if not str(column_id or "").strip():
        raise ValueError("column_id is required.")
    if not str(original_column or "").strip():
        raise ValueError("original_column is required.")
    if not str(token_column or "").strip():
        raise ValueError("token_column is required.")
    if not str(target or "").strip():
        raise ValueError("target is required.")

    config, env, context = resolve_fabric_context()
    spark_session = getattr(df, "sparkSession", None)
    identity = resolve_catalogue_table_identity(
        config,
        env,
        table_id,
        spark_session=spark_session,
        context=context,
    )
    support_table = _token_map_table_name(identity["table_id"], identity["table_name"])
    _store, table_name, schema_name, path = resolve_configured_lakehouse_table(
        target,
        support_table,
        schema,
        context=context,
    )
    mapping_df = _build_token_map_frame(
        df,
        table_id=identity["table_id"],
        column_id=column_id,
        original_column=original_column,
        token_column=token_column,
        context=context,
    )
    action = _upsert_token_map(mapping_df, path)
    return {
        "table_id": identity["table_id"],
        "column_id": column_id,
        "target": target,
        "schema": schema_name,
        "table_name": table_name,
        "path": path,
        "action": action,
    }
