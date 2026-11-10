"""Bounded notebook presentation of already calculated statistical profiles."""

from __future__ import annotations

# Preview bounds apply to column-level aggregates, never to source profiling.
_PREVIEW_COLUMNS = 100
_CELL_CHARACTERS = 120
_METRICS = (
    ("COLUMN_NAME", "column_name", "Column", "text"),
    ("DATA_TYPE", "data_type", "Type", "text"),
    ("ROW_COUNT", "row_count", "Rows", "count"),
    ("NON_NULL_COUNT", "non_null_count", "Non-null", "count"),
    ("NULL_COUNT", "null_count", "Nulls", "count"),
    ("NULL_PERCENT", "null_percent", "Null %", "percent"),
    ("DISTINCT_COUNT", "distinct_count", "Distinct", "count"),
    ("DISTINCT_PERCENT", "distinct_percent", "Distinct % (all rows)", "percent"),
    ("MEAN", "mean_value", "Mean", "number"),
    ("STDDEV", "stddev_value", "Std. deviation", "number"),
    ("MIN_VALUE", "min_value", "Minimum", "text"),
    ("PERCENTILE_25", "percentile_25_value", "25th percentile", "number"),
    ("MEDIAN", "median_value", "Median", "number"),
    ("PERCENTILE_75", "percentile_75_value", "75th percentile", "number"),
    ("MAX_VALUE", "max_value", "Maximum", "text"),
)


def _format_value(value, kind):
    """Format a preview cell without changing the statistical result."""
    if value is None:
        return "—"
    if kind == "count":
        return f"{value:,}"
    if kind == "percent":
        return f"{value:,.2f}%"
    if kind == "number":
        return f"{value:,.4g}"
    return str(value).replace("\n", " ").replace("\r", " ").replace("\t", " ")


def capture_profile_presentation(profile, *, scope, dry_run=False, table=None):
    """Detach at most 101 compact aggregate rows while their cache is owned.

    One row per profiled column is read, with one sentinel to detect truncation.
    String projection is bounded in Spark before collection. No source rows,
    frequency values, count action, pandas conversion or metadata read is needed.
    Presentation errors never change the profiling outcome.
    """
    try:
        from pyspark.sql import functions as F

        columns = set(profile.columns)
        selected = []
        for raw, persisted, label, kind in _METRICS:
            name = raw if raw in columns else persisted
            expression = F.col(name)
            if kind == "text":
                expression = F.substring(expression.cast("string"), 1, _CELL_CHARACTERS)
            selected.append(expression.alias(label))
        rows = profile.select(*selected).limit(_PREVIEW_COLUMNS + 1).collect()
        formatted = [tuple(_format_value(row[label], kind) for _, _, label, kind in _METRICS)
                     for row in rows[:_PREVIEW_COLUMNS]]
        if scope["profile_scope"] == "bounded_selection":
            coverage = f"Bounded selection (at most {scope['profiling_max_rows']:,} rows); not the entire table"
        elif scope["profile_scope"] == "full_table":
            coverage = "Complete table"
        else:
            coverage = "Supplied DataFrame; complete-table coverage not asserted"
        title = f"Statistical profile · {coverage}"
        if table:
            title += f" · {table}"
        if dry_run:
            title += " · Dry Run (not persisted)"
        if len(rows) > _PREVIEW_COLUMNS:
            title += f" · First {_PREVIEW_COLUMNS} columns shown (presentation limit only)"
        title += f" · Text cells limited to {_CELL_CHARACTERS} characters"
        return {"title": title, "headers": [item[2] for item in _METRICS], "rows": formatted,
                "spark_session": profile.sparkSession}
    except Exception:
        return None


def display_profile_presentations(presentations):
    """Prefer Fabric's native display, with a bounded text fallback."""
    for presentation in presentations:
        if presentation is None:
            continue
        try:
            print(presentation["title"])
            if not presentation["rows"]:
                print("No statistical profile rows.")
                continue
            try:
                import builtins

                from IPython import get_ipython

                shell = get_ipython()
                native_display = None
                if shell is not None and getattr(shell, "kernel", None) is not None:
                    native_display = shell.user_ns.get("display") or getattr(builtins, "display", None)
                # Generic IPython display only prints a Spark DataFrame repr.
                if callable(native_display) and not getattr(native_display, "__module__", "").startswith("IPython."):
                    from pyspark.sql.types import StringType, StructField, StructType

                    schema = StructType([StructField(name, StringType(), False) for name in presentation["headers"]])
                    native_display(presentation["spark_session"].createDataFrame(presentation["rows"], schema))
                    continue
            except Exception:
                pass
            rows = [presentation["headers"], *presentation["rows"]]
            widths = [max(len(row[index]) for row in rows) for index in range(len(rows[0]))]
            for index, row in enumerate(rows):
                print(" | ".join(value.ljust(width) for value, width in zip(row, widths)))
                if index == 0:
                    print("-+-".join("-" * width for width in widths))
        except Exception:
            # A notebook renderer or output stream must not invalidate a write.
            pass
