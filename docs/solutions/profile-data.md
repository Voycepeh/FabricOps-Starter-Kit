# Profile data and inspect frequency distributions

## Problem

Notebook workflows need repeatable column statistics and useful value-frequency evidence, not only an ad hoc DataFrame preview. That evidence also needs to be registered in the FabricOps metadata model for later review.

## How FabricOps solves it

**FabricOps separates the profiling calculations and provides an integrated registration workflow.**

- [`profile_dataframe()`](../api/reference/profile_dataframe.md) produces column-level profiling statistics such as row, null, distinct, numeric summary, minimum, and maximum values.
- [`profile_frequency_distribution()`](../api/reference/profile_frequency_distribution.md) produces ranked value-frequency information for selected or eligible scalar columns.
- [`profile_and_register_table()`](../api/reference/profile_and_register_table.md) profiles the supplied table DataFrame and registers the resulting metadata in Data Profiled, Data Profiled Frequency, and the Data Catalogue. It also registers the table's source or target participation as Data Lineage.

## Use it in FabricOps

**Notebook:** [`02_pipeline`](../guided-demo/02-run-pipeline.md)

**Functions:**

- [`profile_dataframe()`](../api/reference/profile_dataframe.md)
- [`profile_frequency_distribution()`](../api/reference/profile_frequency_distribution.md)
- [`profile_and_register_table()`](../api/reference/profile_and_register_table.md)

## What it produces

The integrated workflow returns the compact profile DataFrame: one summary row for each eligible column. It writes that snapshot to **Data Profiled**, writes flattened selected or eligible value-frequency rows to **Data Profiled Frequency**, and updates or adds the corresponding table and column records in the **Data Catalogue**.

!!! important "Compact profiles and frequency records are different outputs"

    Displaying the compact profile DataFrame does not display the full frequency-profile records. Inspect Data Profiled Frequency when the individual retained values, counts, percentages, and ranks are required.

## Related documentation

- [`02_pipeline`: write and profile the target](../guided-demo/02-run-pipeline.md#write-and-profile-the-target)
- [Data Catalogue](../reference/metadata/metadata_data_catalogue.md)
- [Data Profiled](../reference/metadata/metadata_data_profiled.md)
- [Data Profiled Frequency](../reference/metadata/metadata_data_profiled_frequency.md)
