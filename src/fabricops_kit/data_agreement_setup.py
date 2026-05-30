"""Setup and readiness checks for data-agreement metadata prerequisites.

The framework owns the physical metadata-table schema. Users own the reference
values inside those tables, especially real steward rows maintained in
``METADATA_DATA_STEWARD``.
"""

from __future__ import annotations

from typing import Any

from .data_agreement import (
    DATA_AGREEMENT_TABLE,
    DATA_STEWARD_TABLE,
    DATA_STEWARD_FIELDS,
    load_active_data_steward_profiles,
    setup_data_agreement_tables,
)
from .fabric_input_output import read_lakehouse_table

DATA_STEWARD_REQUIRED_FIELDS = [
    "steward_id",
    "data_steward_name",
    "data_steward_email",
    "domain",
    "faculty",
    "department",
    "effective_from",
    "effective_to",
    "is_active",
]

DATA_STEWARD_SYSTEM_FIELDS = ["created_at", "updated_at"]


def _column_names(rows_or_df: Any) -> list[str]:
    """Return column names from a Spark DataFrame or row collection."""
    if hasattr(rows_or_df, "columns"):
        return list(rows_or_df.columns)
    if rows_or_df is None:
        return []
    rows = rows_or_df.collect() if hasattr(rows_or_df, "collect") else rows_or_df
    rows = list(rows)
    if not rows:
        return []
    first = rows[0].asDict(recursive=True) if hasattr(rows[0], "asDict") else dict(rows[0])
    return list(first.keys())


def validate_data_agreement_prerequisites(
    *,
    spark: Any,
    config: Any,
    env: str,
    require_active_steward: bool = False,
) -> dict[str, Any]:
    """Validate tables needed before the ``01_da`` intake form can render.

    ``00_env_config`` should call this with ``require_active_steward=False`` so
    environment bootstrap can warn without failing. ``01_da`` should call this
    with ``require_active_steward=True`` so the intake widget fails early with a
    clear prerequisite message when no active steward has been maintained.

    Parameters
    ----------
    spark : pyspark.sql.SparkSession
        Active Fabric Spark session.
    config : FrameworkConfig | dict
        Framework config with the metadata lakehouse target.
    env : str
        Environment key configured by ``00_env_config``.
    require_active_steward : bool, default=False
        Whether missing active steward rows should raise instead of returning a
        ``not_ready`` status.

    Returns
    -------
    dict[str, Any]
        Readiness summary containing table names, required fields, status,
        message, and active steward count when available.
    """
    tables = setup_data_agreement_tables(spark=spark, config=config, env=env)

    steward_df = read_lakehouse_table(
        config,
        env,
        "metadata",
        DATA_STEWARD_TABLE,
        spark_session=spark,
    )
    columns = _column_names(steward_df)
    required_physical_fields = list(dict.fromkeys(DATA_STEWARD_REQUIRED_FIELDS + DATA_STEWARD_SYSTEM_FIELDS))
    missing = [field for field in required_physical_fields if field not in columns]
    if missing:
        raise ValueError(
            f"{DATA_STEWARD_TABLE} is missing required column(s): {', '.join(missing)}. "
            "Run 00_env_config to recreate/check the metadata schema before rendering 01_da."
        )

    try:
        active_profiles = load_active_data_steward_profiles(spark=spark, config=config, env=env)
    except ValueError as exc:
        if f"{DATA_STEWARD_TABLE} has no active steward rows" not in str(exc):
            raise
        message = (
            f"WARNING: {DATA_STEWARD_TABLE} has no active steward rows. "
            "01_da cannot render until real steward rows are maintained with is_active = true. "
            "No fake steward profiles are seeded."
        )
        if require_active_steward:
            raise ValueError(message) from exc
        return {
            "status": "not_ready",
            "message": message,
            "tables": tables,
            "agreement_table": DATA_AGREEMENT_TABLE,
            "steward_table": DATA_STEWARD_TABLE,
            "steward_required_fields": DATA_STEWARD_REQUIRED_FIELDS,
            "steward_system_fields": DATA_STEWARD_SYSTEM_FIELDS,
            "active_steward_count": 0,
        }

    return {
        "status": "ready",
        "message": f"{DATA_STEWARD_TABLE} contains active steward rows. 01_da can render its intake form.",
        "tables": tables,
        "agreement_table": DATA_AGREEMENT_TABLE,
        "steward_table": DATA_STEWARD_TABLE,
        "steward_required_fields": DATA_STEWARD_REQUIRED_FIELDS,
        "steward_system_fields": DATA_STEWARD_SYSTEM_FIELDS,
        "active_steward_count": len(active_profiles),
    }
