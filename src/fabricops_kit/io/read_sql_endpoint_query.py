"""Internal owner for configured Fabric SQL endpoint reads."""

from __future__ import annotations

from typing import Any

from .shared import read_sql_endpoint_query_core


def read_sql_endpoint_query(
    query: str,
    *,
    store: str,
    spark_session=None,
    context: dict[str, Any] | None = None,
    options: dict[str, Any] | None = None,
):
    """Read a SELECT query from a configured Warehouse or Lakehouse SQL endpoint."""
    return read_sql_endpoint_query_core(
        query, store=store, spark_session=spark_session, context=context, options=options,
    )

