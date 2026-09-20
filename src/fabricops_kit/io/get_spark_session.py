"""Internal owner for Fabric Spark session resolution."""

from importlib import import_module


def get_spark_session(spark_session=None):
    """Return the explicit or active Spark session."""
    if spark_session is not None:
        return spark_session
    module_spark = globals().get("spark")
    if module_spark is not None:
        return module_spark
    try:
        spark_type = getattr(import_module("pyspark.sql"), "SparkSession")
        active_session = spark_type.getActiveSession()
    except (ImportError, AttributeError):
        active_session = None
    if active_session is not None:
        return active_session
    raise RuntimeError(
        "Spark session was not provided and no active Spark session was found. "
        "Run this inside Fabric/Spark or pass spark_session explicitly."
    )
