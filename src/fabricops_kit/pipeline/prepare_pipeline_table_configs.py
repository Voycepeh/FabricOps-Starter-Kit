"""Public notebook-facing pipeline callable."""

from __future__ import annotations

from typing import Any, Mapping

from fabricops_kit.pipeline.shared import _prepare_pipeline_table_configs_workflow


def prepare_pipeline_table_configs(
    table_configs: list[dict[str, Any]],
    default_settings: Mapping[str, Any],
    *,
    table_role: str,
    run_id: str = "",
    pipeline_name: str = "",
) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    """Prepare source or target table configs for a pipeline notebook."""
    return _prepare_pipeline_table_configs_workflow(
        table_configs,
        default_settings,
        table_role=table_role,
        run_id=run_id,
        pipeline_name=pipeline_name,
    )


prepare_pipeline_table_configs.__doc__ = _prepare_pipeline_table_configs_workflow.__doc__
