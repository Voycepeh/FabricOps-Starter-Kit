"""Public widget entrypoint for ``widget_render_agreement_evidence``."""

from __future__ import annotations

from typing import Any

from fabricops_kit.config.shared import resolve_fabric_context
from fabricops_kit.widgets.shared import _render_agreement_evidence_widget_workflow


def widget_render_agreement_evidence(*, spark: Any, context: dict[str, Any] | None = None) -> dict[str, Any]:
    """Render standalone agreement evidence upload controls.

    Parameters
    ----------
    spark : pyspark.sql.SparkSession
        Fabric Spark session used for metadata reads, file writes, and
        append-only evidence metadata writes.
    context : dict[str, Any], optional
        Advanced override for the active Fabric context. When omitted, the
        helper uses ``FABRIC_CONTEXT`` initialized by ``00_env_config``.

    Returns
    -------
    dict[str, Any]
        Rendered controls for selecting an agreement version, pasting
        metadata lakehouse evidence file paths, refreshing agreement options,
        and saving evidence metadata rows.

    """
    config, env, _context = resolve_fabric_context(context=context)
    return _render_agreement_evidence_widget_workflow(spark=spark, config=config, env=env)
