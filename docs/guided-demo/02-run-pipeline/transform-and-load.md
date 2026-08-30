# Unit 4: Transform and load

**Keep business transformation logic visible, then let the template handle the standard FabricOps load boundary.**

## Add project-specific transformation

Use the **User defined transformation** section in `02_pipeline` for joins, filters, derivations, aggregations, enrichment, and reshaping.

![Transform DataFrame](../../assets/02/Transform_DF.png)

FabricOps standardises the governed boundary around ETL. It does not replace the transformation logic that belongs to the project.

## Choose the target

The template supports managed Lakehouse and Warehouse targets, but each governed pipeline publishes exactly one target table.

### Lakehouse target

![Write Lakehouse](../../assets/02/Write_LH.png)

After persistence, read the complete physical target back and profile/register it so the catalogue represents the stored result rather than only an intermediate DataFrame.

![Read written Lakehouse table](../../assets/02/Read_Written_LH.png)

### Warehouse target

Create the target schema first when required:

```sql
CREATE SCHEMA demo
```

![Create Warehouse schema](../../assets/02/create_schema.png)

Then execute the Warehouse target section.

![Write Warehouse](../../assets/02/Write_WH.png)

## Need another persisted output?

Create a separate downstream pipeline rather than adding another governed target write to the same pipeline.

This keeps each pipeline responsible for one publication boundary and avoids a partial-success state where one target write succeeds but another fails. The output of the first pipeline can become an upstream source for the next pipeline when another persisted stage is needed.

Do not use a pipeline's own target as an engineer-authored source inside the same pipeline. Persisted intermediate tables should form explicit stages between separate pipelines.

## Partitioning and parallelism

`partition_by` controls physical Lakehouse storage layout. `repartition_by` can change Spark write parallelism. Use either only when it fits the real data shape because poor partition choices can create small files or unnecessary shuffle overhead.

![Write Lakehouse in parallel](../../assets/02/Write_LH_Parallel.png)

These physical write choices are separate from FabricOps incremental processing strategy, which determines which logical source data should be processed during a run.

## Function details

Use the [Function Reference](../../reference/index.md) for exact parameters for `write_lakehouse_table()`, `write_warehouse_table()`, `profile_dataframe()`, `profile_frequency_distribution()`, and `profile_and_register_table()`.

**Previous:** [Unit 3: Configure sources](configure-sources.md)  
**Next:** [Unit 5: Choose processing behaviour and review results](processing-and-results.md)
