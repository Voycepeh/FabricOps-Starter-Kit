"""Public notebook-facing frequency profiling callable."""

from __future__ import annotations

from functools import reduce

from fabricops_kit.pipeline.shared import resolve_profiled_columns

FREQUENCY_PROFILE_COLUMNS = [
    "COLUMN_NAME",
    "DATA_TYPE",
    "VALUE",
    "FREQUENCY_COUNT",
    "FREQUENCY_PERCENT",
    "FREQUENCY_RANK",
    "PROFILED_ROW_COUNT",
    "PROFILED_NON_NULL_COUNT",
]



def _frequency_profile_schema():
    """Return the frequency profile output schema."""
    from pyspark.sql import types as T

    return T.StructType(
        [
            T.StructField("COLUMN_NAME", T.StringType(), False),
            T.StructField("DATA_TYPE", T.StringType(), False),
            T.StructField("VALUE", T.StringType(), True),
            T.StructField("FREQUENCY_COUNT", T.LongType(), False),
            T.StructField("FREQUENCY_PERCENT", T.DoubleType(), True),
            T.StructField("FREQUENCY_RANK", T.IntegerType(), False),
            T.StructField("PROFILED_ROW_COUNT", T.LongType(), False),
            T.StructField("PROFILED_NON_NULL_COUNT", T.LongType(), False),
        ]
    )


def _column(name: str):
    from pyspark.sql import functions as F

    return F.col(f"`{name.replace('`', '``')}`")


def profile_frequency_distribution(df, *, columns=None, top_n: int = 20):
    """Return top-N value frequencies for selected Spark DataFrame columns.

    Parameters
    ----------
    df : pyspark.sql.DataFrame
        Spark DataFrame to profile exactly as supplied by the caller.
    columns : list[str] or set[str] or tuple[str, ...], optional
        Source columns to profile. By default, eligible non-technical scalar
        columns are selected.
    top_n : int, default=20
        Maximum ranked values to retain per source column.

    Returns
    -------
    pyspark.sql.DataFrame
        Spark DataFrame containing one row per retained top value per profiled
        source column.

    Raises
    ------
    ValueError
        If ``top_n`` is not greater than zero or a requested column is missing.

    """
    from pyspark.sql import functions as F
    from pyspark.sql.window import Window
    from pyspark.sql.types import ArrayType, BinaryType, MapType, StructType

    if top_n <= 0:
        raise ValueError("top_n must be greater than zero.")

    fields = {field.name: field for field in df.schema.fields}
    if columns is None:
        selected_columns = [
            name
            for name in resolve_profiled_columns(df)
            if not isinstance(fields[name].dataType, ArrayType | MapType | StructType | BinaryType)
        ]
    else:
        selected_columns = list(columns)
        missing = [name for name in selected_columns if name not in fields]
        if missing:
            raise ValueError(f"Requested columns do not exist: {', '.join(missing)}")

    if not selected_columns:
        return df.sparkSession.createDataFrame([], _frequency_profile_schema())

    metric_exprs = [F.count(F.lit(1)).cast("long").alias("PROFILED_ROW_COUNT")]
    for column_name in selected_columns:
        metric_exprs.append(F.count(_column(column_name)).cast("long").alias(f"__{column_name}__PROFILED_NON_NULL_COUNT"))
    metrics_df = df.agg(*metric_exprs)
    row_count = F.col("PROFILED_ROW_COUNT")
    branches = []
    rank_window = Window.orderBy(F.col("FREQUENCY_COUNT").desc(), F.col("VALUE").asc_nulls_first())
    for column_name in selected_columns:
        value = _column(column_name).cast("string")
        grouped = (
            df.groupBy(value.alias("VALUE"))
            .agg(F.count(F.lit(1)).cast("long").alias("FREQUENCY_COUNT"))
            .crossJoin(metrics_df)
            .withColumn("FREQUENCY_PERCENT", F.when(row_count == 0, F.lit(0.0)).otherwise(F.round((F.col("FREQUENCY_COUNT").cast("double") / row_count.cast("double")) * 100, 3)))
            .withColumn("FREQUENCY_RANK", F.row_number().over(rank_window))
            .where(F.col("FREQUENCY_RANK") <= F.lit(top_n))
            .select(
                F.lit(column_name).alias("COLUMN_NAME"),
                F.lit(fields[column_name].dataType.simpleString()).alias("DATA_TYPE"),
                F.col("VALUE"),
                F.col("FREQUENCY_COUNT"),
                F.col("FREQUENCY_PERCENT"),
                F.col("FREQUENCY_RANK"),
                F.col("PROFILED_ROW_COUNT"),
                F.col(f"__{column_name}__PROFILED_NON_NULL_COUNT").alias("PROFILED_NON_NULL_COUNT"),
            )
        )
        branches.append(grouped.select(*FREQUENCY_PROFILE_COLUMNS))

    return reduce(lambda left, right: left.unionByName(right), branches).select(*FREQUENCY_PROFILE_COLUMNS)
