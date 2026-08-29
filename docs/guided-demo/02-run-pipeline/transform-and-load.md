# Unit 4: Transform and load

**Keep business transformation logic visible, then let the template handle the standard FabricOps load boundary.**

## Add project-specific transformation

Use the **User defined transformation** section in `02_pipeline` for joins, filters, derivations, aggregations, enrichment, and reshaping.

![Transform DataFrame](../../assets/02/Transform_DF.png)

FabricOps standardises the governed boundary around ETL. It does not replace the transformation logic that belongs to the project.

## Choose the target

The template supports managed Lakehouse and Warehouse targets.

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

## Partitioning and parallelism

`partition_by` controls physical Lakehouse storage layout. `repartition_by` can change Spark write parallelism. Use either only when it fits the real data shape because poor partition choices can create small files or unnecessary shuffle overhead.

![Write Lakehouse in parallel](../../assets/02/Write_LH_Parallel.png)

These physical write choices are separate from FabricOps incremental processing strategy, which determines which logical source data should be processed during a run.

## Function details

Use the [Function Reference](../../reference/index.md) for exact parameters for `write_lakehouse_table()`, `write_warehouse_table()`, `profile_dataframe()`, `profile_frequency_distribution()`, and `profile_and_register_table()`.

**Previous:** [Unit 3: Configure sources](configure-sources.md)  
**Next:** [Unit 5: Choose processing behaviour and review results](processing-and-results.md)
