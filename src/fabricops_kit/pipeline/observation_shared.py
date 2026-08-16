"""Shared helpers for the normalized source-observation model."""

from __future__ import annotations

from typing import Any

from fabricops_kit.io.shared import configured_lakehouse_schema, read_lakehouse_table_core

SOURCE_OBSERVATION_COLUMNS = frozenset(
    {
        "observation_id",
        "table_id",
        "environment_name",
        "partition_value",
        "row_count",
        "min_change_value",
        "max_change_value",
        "is_present",
        "observed_at",
    }
)


def _observation_rows(dataframe: Any) -> list[dict[str, Any]]:
    """Return canonical observation rows as dictionaries."""
    values = dataframe.collect() if hasattr(dataframe, "collect") else dataframe
    return [row.asDict(recursive=True) if hasattr(row, "asDict") else dict(row) for row in values or []]


def _is_source_observation(dataframe: Any) -> bool:
    """Return whether a value exposes the normalized observation contract."""
    columns = set(getattr(dataframe, "columns", ()))
    if not columns and isinstance(dataframe, (list, tuple)) and dataframe:
        columns = set(dict(dataframe[0]))
    return SOURCE_OBSERVATION_COLUMNS <= columns


def _catalogue_table_identity(
    *, config: Any, env: str, table_id: str, spark_session: Any
) -> dict[str, Any] | None:
    """Resolve physical table attributes from the environment-specific Catalogue row."""
    catalogue = read_lakehouse_table_core(
        "METADATA_DATA_CATALOGUE",
        target="metadata",
        schema=configured_lakehouse_schema(config, env, "metadata"),
        spark_session=spark_session,
        context={"config": config, "env": env},
    )
    if hasattr(catalogue, "where"):
        from pyspark.sql import functions as F

        matches = catalogue.where(
            (F.col("environment_name") == env)
            & (F.col("table_id") == table_id)
            & (F.col("metadata_level") == "table")
        )
        if "is_active" in getattr(matches, "columns", ()):  # pragma: no branch - Spark schema contract
            matches = matches.where(F.col("is_active") == F.lit(True))
        rows = matches.orderBy(F.col("last_profiled_at").desc_nulls_last()).limit(1).collect()
        return rows[0].asDict(recursive=True) if rows else None

    rows = _observation_rows(catalogue)
    candidates = [
        row
        for row in rows
        if str(row.get("environment_name") or "") == env
        and str(row.get("table_id") or "") == table_id
        and str(row.get("metadata_level") or "") == "table"
        and row.get("is_active", True) is not False
    ]
    if not candidates:
        return None
    candidates.sort(key=lambda row: str(row.get("last_profiled_at") or ""), reverse=True)
    return candidates[0]


def _guardrail_compatibility_observation(
    observation: Any, *, table_id: str, change_column: str
) -> Any:
    """Add legacy in-memory aliases required by the not-yet-migrated Guardrail core.

    These aliases are never persisted. They isolate the staged Stage 2
    observation schema from the Stage 4 Guardrail migration.
    """
    if hasattr(observation, "withColumn"):
        from pyspark.sql import functions as F

        return observation.withColumn("metadata_table_key", F.lit(table_id)).withColumn(
            "change_column", F.lit(change_column)
        )
    return [
        {**row, "metadata_table_key": table_id, "change_column": change_column}
        for row in _observation_rows(observation)
    ]


__all__ = [
    "SOURCE_OBSERVATION_COLUMNS",
    "_catalogue_table_identity",
    "_guardrail_compatibility_observation",
    "_is_source_observation",
    "_observation_rows",
]
