"""Public widget entrypoint for ``widget_render_data_agreement``."""

from __future__ import annotations

from typing import Any

from fabricops_kit.config.shared import resolve_fabric_context
from fabricops_kit.widgets.shared import _render_maintenance_widget_shared_workflow


def widget_render_data_agreement(*, spark: Any, context: dict[str, Any] | None = None) -> dict[str, Any]:
    """Render append-only agreement create/update maintenance using active stewards.

    Parameters
    ----------
    spark : pyspark.sql.SparkSession
        Fabric Spark session used for metadata reads and append-only writes.
    context : dict[str, Any], optional
        Advanced override for the active Fabric context. When omitted, the
        helper uses ``FABRIC_CONTEXT`` initialized by ``00_env_config``.

    Returns
    -------
    dict[str, Any]
        Rendered controls, including read-only generated-identifier context.

    """
    config, env, _context = resolve_fabric_context(context=context)
    return _render_maintenance_widget_shared_workflow(spark=spark, config=config, env=env, kind="data_agreement_widget")
