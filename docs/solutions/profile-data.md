# Standardized data profiling

## Problem

Before deciding how to transform, validate, or govern a dataset, users need to understand what it contains. A few sample rows do not reveal the full picture for nulls, distinct values, minimum and maximum values, or common values.

## How FabricOps solves it

FabricOps creates a repeatable profile of the supplied DataFrame:

- [`profile_dataframe()`](../api/reference/profile_dataframe.md) produces the compact column-level profile.
- [`profile_frequency_distribution()`](../api/reference/profile_frequency_distribution.md) produces value-frequency information for selected or eligible columns.
- [`profile_and_register_table()`](../api/reference/profile_and_register_table.md) brings profiling into the standard workflow and registers the results in the **Data Catalogue**, **Data Profiled**, and **Data Profiled Frequency** metadata.

For automatic frequency selection, the integrated workflow skips columns when more than 80% of their non-null values are distinct. This avoids large, noisy frequency output for IDs and other mostly unique columns. Explicit column selections can override this threshold.

The compact profile DataFrame is not the full Data Profiled Frequency output. Frequency records contain the retained values, counts, percentages, and ranks.

## Use it with

**Notebook:** [`02_pipeline`](../guided-demo/02-run-pipeline.md)

**Functions:** [`profile_dataframe()`](../api/reference/profile_dataframe.md), [`profile_frequency_distribution()`](../api/reference/profile_frequency_distribution.md), and [`profile_and_register_table()`](../api/reference/profile_and_register_table.md)

## Related documentation

- [Data Catalogue](../reference/metadata/metadata_data_catalogue.md)
- [Data Profiled](../reference/metadata/metadata_data_profiled.md)
- [Data Profiled Frequency](../reference/metadata/metadata_data_profiled_frequency.md)
