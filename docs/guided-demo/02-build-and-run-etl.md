# Step 2. Build a Pipeline

**Use the reusable `02_pipeline` scaffold to understand and customize the standard governed pipeline lifecycle.**

This page explains the template itself. The ready-to-run retail walkthrough starts in [Step 2A](02A-full-refresh-demo.md).

## Before you begin

1. Download [`02_pipeline.ipynb`](https://raw.githubusercontent.com/Voycepeh/FabricOps-Starter-Kit/main/templates/notebooks/02_pipeline.ipynb) and import it into the Engineering Development workspace.
2. Import `00_env_config.ipynb` beside it.
3. Attach the same Fabric Environment configured in [Step 00B](00B-configure-environment-and-load-assets.md).
4. Replace the example source and target table names before running the Read or Write cells.

## What to do

Follow the notebook from top to bottom. Its migration-friendly structure stays deliberately small:

| Section | What you customize | FabricOps boundary |
| --- | --- | --- |
| Environment | Shared `%run 00_env_config` and public imports | Resolves configured Fabric stores and metadata routing. |
| Data Contract | Per-table **Enforce** or **Validate** selection | [`widget_select_data_contract()`](../api/reference/widget_select_data_contract.md) chooses the governed contract mode. |
| Governed Read | Source store, schema, table, and read mode | [`orchestrate_read()`](../api/reference/orchestrate_read.md) runs the standard source lifecycle. |
| PySpark Transform | Project-specific joins, filters, columns, or aggregations | Ordinary project-owned PySpark remains between Read and Write. |
| Governed Write | Target identity, write mode, and processing parameters | [`orchestrate_write()`](../api/reference/orchestrate_write.md) validates, publishes, profiles, and records lineage. |
| Optional inspection | Commented `display()` calls | Lets you inspect results without mixing display logic into orchestration. |

### 1. Run Environment and Data Contract

Run `%run 00_env_config`, the import cell, and the Data Contract selector. A new Development target can remain unselected until Governance authors a Data Contract. When a frozen candidate exists, **Validate** evaluates it without publishing; **Enforce** allows publication when Guardrails pass.

### 2. Configure the Governed Read

Edit the arguments directly in the `orchestrate_read()` call. Keep the complete result in `sources`, because the transformation uses its DataFrame and the Write uses its governed identity for lineage.

```python
source = orchestrate_read(
    name="source",
    store="Bronze",
    schema="demo",
    table_name="source_table",
    read_mode="full",
    query=None,
    spark_session=spark,
)
sources["source"] = source
```

For Incremental reads, use the public `read_parameters` API and supply the governed target identity. See [Read and Load Strategies](../reference/read-and-load-strategies.md) and the ready-to-run [Step 2B demo](02B-build-and-run-incremental-append-etl.md).

### 3. Replace the PySpark transformation

The template starts with an identity selection so the cell is executable after its table names are configured:

```python
transformed_df = sources["source"]["dataframe"].select("*")
```

Replace it with the PySpark logic owned by your project. Keep orchestration calls outside this cell.

### 4. Configure the Governed Write

Edit the target arguments directly. Pass every contributing Read result through `sources`; FabricOps uses those governed source identities to record `METADATA_DATA_LINEAGE` and evaluate source-aware Guardrails.

```python
writes["target"] = orchestrate_write(
    transformed_df,
    name="target",
    sources=[sources["source"]],
    store="Silver",
    schema="demo",
    table_name="target_table",
    write_mode="overwrite",
    contracts=CONTRACTS,
    repartition_by=None,
    spark_session=spark,
)
```

### 5. Use the optional inspections

Uncomment only the Read or Write results you need while developing. The inspection cells stay outside `orchestrate_read()` and `orchestrate_write()` so the standard lifecycle remains easy to identify and migrate.

## Expected result

You now have a reusable governed pipeline scaffold with one clear customization surface for each Read, transformation, and Write. It contains no retail-demo-specific logic.

**Next:** [Step 2A. Run the Full Refresh Demo](02A-full-refresh-demo.md)
