"""Operator entry point for initializing the private Processing State store."""

from __future__ import annotations

from typing import Any

from fabricops_kit.io.shared import get_spark_session, read_delta_path, write_delta_path

from .shared import FrameworkConfig, validate_framework_config


def setup_processing_state(
    *,
    config: FrameworkConfig | dict[str, Any],
    workspace_id: str,
) -> dict[str, Any]:
    """Create an empty private Delta store or validate the existing store.

    Parameters
    ----------
    config : FrameworkConfig | dict[str, Any]
        Configuration containing the shared Metadata Lakehouse.
    workspace_id : str
        Configuration scope used to resolve that Lakehouse.

    Returns
    -------
    dict[str, Any]
        Status (created or validated) and the Lakehouse-relative path.

    Raises
    ------
    RuntimeError
        If the existing store has an incompatible schema or lacks Serializable isolation.
        Spark and storage errors also propagate.

    Notes
    -----
    Run under the Lakehouse owner's identity. Initial creation starts with empty
    Processing State. Repeated setup preserves rows already in the private store.

    Examples
    --------
    >>> setup_processing_state(config=CONFIG, workspace_id=WORKSPACE_ID)
    {'status': 'created', 'path': 'Files/fabricops/misc/processing_state'}

    """
    from fabricops_kit.pipeline.shared import (
        PROCESSING_STATE_PATH,
        processing_state_path,
        processing_state_schema,
        validate_processing_state_isolation,
        validate_processing_state_schema,
    )

    normalized = validate_framework_config(config)
    spark = get_spark_session()
    context = {"config": normalized, "scope_workspace_id": workspace_id}
    path = processing_state_path(context)
    status = "validated"
    try:
        state = read_delta_path(spark, path)
    except Exception as exc:
        get_condition = getattr(exc, "getCondition", None) or getattr(exc, "getErrorClass", None)
        if not callable(get_condition) or get_condition() not in {"PATH_NOT_FOUND", "DELTA_PATH_DOES_NOT_EXIST"}:
            raise
        empty = spark.createDataFrame([], processing_state_schema())
        write_delta_path(empty, path, mode="errorifexists", options={"delta.isolationLevel": "Serializable"})
        state = read_delta_path(spark, path)
        status = "created"
    validate_processing_state_schema(state.schema)
    from delta.tables import DeltaTable

    validate_processing_state_isolation(DeltaTable.forPath(spark, path))
    return {"status": status, "path": f"Files/{PROCESSING_STATE_PATH}"}


__all__ = ["setup_processing_state"]
