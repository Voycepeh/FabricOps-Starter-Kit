# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {"name": "synapse_pyspark"},
# META   "dependencies": {}
# META }

# MARKDOWN ********************

# # Bronze to Silver orders
#
# Keep the latest non-null order per order ID using update time and event ID.
# Dry Run previews a keyed Silver SCD1 write.

# MARKDOWN ********************

# ## Setup

# CELL ********************

"""Deduplicate Bronze order events for a Silver SCD1 Write."""

from fabricops_kit import finalize_pipeline, orchestrate_read, orchestrate_write, setup_notebook, setup_pipeline

context = setup_notebook()
pipeline = setup_pipeline(pipeline_mode="Dry Run")

# METADATA ********************

# META {"language": "python", "language_group": "synapse_pyspark"}

# MARKDOWN ********************

# ## Read

# CELL ********************

sources = {}
sources["orders"] = orchestrate_read(
    store="Bronze",
    schema="demo",
    table_name="order_events",
    read_mode="full",
    dq_diagnostics="none",
)

# METADATA ********************

# META {"language": "python", "language_group": "synapse_pyspark"}

# MARKDOWN ********************

# ## Transform

# CELL ********************

from pyspark.sql import Window, functions as F

latest_order = Window.partitionBy("order_id").orderBy(F.col("updated_at").desc(), F.col("event_id").desc())
transformed_df = (
    sources["orders"]["dataframe"]
    .filter(F.col("order_id").isNotNull() & F.col("updated_at").isNotNull() & F.col("event_id").isNotNull())
    .withColumn("latest_row", F.row_number().over(latest_order))
    .filter(F.col("latest_row") == 1)
    .select("order_id", "status", "updated_at")
)

# METADATA ********************

# META {"language": "python", "language_group": "synapse_pyspark"}

# MARKDOWN ********************

# ## Write

# CELL ********************

writes = {}
writes["orders"] = orchestrate_write(
    transformed_df,
    store="Silver",
    schema="demo",
    table_name="orders",
    write_mode="scd1",
    write_parameters={"key_columns": ["order_id"]},
    dq_diagnostics="none",
)

# METADATA ********************

# META {"language": "python", "language_group": "synapse_pyspark"}

# MARKDOWN ********************

# ## Finalize

# CELL ********************

pipeline_result = finalize_pipeline(pipeline)

# METADATA ********************

# META {"language": "python", "language_group": "synapse_pyspark"}
