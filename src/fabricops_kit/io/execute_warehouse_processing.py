"""Internal owner for governed Warehouse physical mutations."""

from __future__ import annotations

from typing import Any, Mapping

from .shared import execute_warehouse_processing as _execute_warehouse_processing


def execute_warehouse_processing(
    df,
    *,
    schema: str,
    table_name: str,
    store: str,
    processing: Mapping[str, Any],
    context: Mapping[str, Any] | None = None,
    options: dict[str, Any] | None = None,
) -> None:
    """Apply a validated governed definition through the Warehouse transport owner."""
    _execute_warehouse_processing(
        df, schema=schema, table_name=table_name, store=store,
        processing=processing, context=context, options=options,
    )
