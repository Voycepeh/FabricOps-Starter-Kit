"""Convert a stopped, version-pinned Pipeline Run table into a new Delta location.

Run in a configured Spark/Delta environment with the matching package installed.
The source is read only; destination must not exist. Cutover is an operator step.
"""
from __future__ import annotations

import argparse

from fabricops_kit.config.metadata_schemas import coerce_metadata_row_types, metadata_table_schema_registry
from fabricops_kit.pipeline.shared import pipeline_run_row, pipeline_run_result


def convert_run(row):
    """Validate and transform one historical run without inventing missing facts."""
    logical = row.asDict(recursive=True) if hasattr(row, "asDict") else dict(row)
    physical = pipeline_run_row(logical)
    restored = pipeline_run_result(physical)
    if any(restored.get(key) != value for key, value in logical.items() if key != "operation_summary_json"):
        raise ValueError("Historical Pipeline Run has unsupported fields; reconcile before conversion.")
    import json
    if json.loads(restored["operation_summary_json"]) != json.loads(logical["operation_summary_json"]):
        raise ValueError("Historical operation evidence cannot be reconstructed losslessly.")
    return physical


def main():
    """Write validated typed history to a separate destination, never in place."""
    from pyspark.sql import SparkSession
    from pyspark.sql import functions as F
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-path", required=True)
    parser.add_argument("--source-version", required=True, type=int)
    parser.add_argument("--destination-path", required=True)
    args = parser.parse_args()
    if args.source_path.rstrip("/") == args.destination_path.rstrip("/"):
        parser.error("Destination must be a separate, new Delta location.")
    spark = SparkSession.builder.getOrCreate()
    source = spark.read.format("delta").option("versionAsOf", args.source_version).load(args.source_path)
    if "operation_summary_json" not in source.columns or "record_type" in source.columns:
        raise ValueError("Expected the pre-Workstream D Pipeline Run schema.")
    if source.groupBy("run_id").count().filter(F.col("count") != 1).limit(1).count():
        raise ValueError("Historical run IDs are duplicated; reconcile before conversion.")
    converted = spark.createDataFrame(source.rdd.map(convert_run),
        metadata_table_schema_registry()["METADATA_PIPELINE_RUN"]).persist()
    try:
        converted.count()  # Fail every ambiguous row before attempting destination publication.
        converted.write.format("delta").mode("errorifexists").save(args.destination_path)
    finally:
        converted.unpersist()


if __name__ == "__main__":
    main()
