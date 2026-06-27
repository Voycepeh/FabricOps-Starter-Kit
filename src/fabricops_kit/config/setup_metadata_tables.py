"""Public owner file for FabricOps metadata table setup."""

from __future__ import annotations

from typing import Any

from .models import FrameworkConfig
from .shared import _setup_metadata_tables_workflow


def setup_metadata_tables(
    *,
    spark: Any,
    config: FrameworkConfig | dict[str, Any],
    env: str,
    metadata_schema: str | None = None,
    require_active_steward: bool = False,
) -> dict[str, Any]:
    """Prepare all FabricOps metadata tables for the configured environment.

    Parameters
    ----------
    spark : pyspark.sql.SparkSession
        Fabric Spark session used by the table setup helpers.
    config : FrameworkConfig or dict
        Shared ``00_env_config`` configuration containing the metadata target.
    env : str
        Environment key to prepare.
    metadata_schema : str or None, default=None
        Optional schema name for schema-enabled Fabric Lakehouses. Keep
        ``None`` for classic Lakehouses that store metadata tables under
        ``Tables/<table_name>``. Use a simple schema such as ``"METADATA"``
        to create and validate registered tables such as
        ``METADATA.METADATA_DATA_AGREEMENT``.
    require_active_steward : bool, default=False
        Forwarded to the agreement metadata setup to optionally require an
        active steward before returning success.

    Returns
    -------
    dict[str, Any]
        Combined setup summary keyed by ``data_agreement``,
        ``notebook_registry``, and ``governance``. The payload also includes
        ``metadata_schema`` and ``fully_qualified_tables`` for schema-enabled
        Lakehouse visibility.

    Notes
    -----
    This is the v1 notebook setup action for metadata provisioning. It keeps
    ``00_env_config`` simple while delegating to internal helpers that route all
    metadata reads and writes through the configured metadata target. With
    ``metadata_schema=None``, setup preserves classic path-based Lakehouse
    behavior under ``Tables/<table_name>``. With ``metadata_schema`` set, setup
    uses schema-aware Lakehouse paths such as ``Tables/<schema>/<table>`` and
    does not bake the schema into configured metadata table names. FabricOps may warn about
    legacy nested or unidentified Delta folders, but it does not delete or
    migrate user data automatically.

    """
    return _setup_metadata_tables_workflow(
        spark=spark,
        config=config,
        env=env,
        metadata_schema=metadata_schema,
        require_active_steward=require_active_steward,
    )


__all__ = ["setup_metadata_tables"]
