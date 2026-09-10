# FabricOps Guided Demo data

These fixtures support one Orders-domain story across ingestion, incremental processing, profiling, and later Guardrail validation.

## Core data

| File | Purpose |
| --- | --- |
| `orders.csv` | Canonical valid Orders baseline used by the main Guided Demo. |
| `orders_incremental.csv` | Later Orders batch for watermark incremental testing. |
| `products.csv` | Product reference data used to seed the Lakehouse lookup table. |
| `order_history.csv` | Historical transactions used to seed the Warehouse and demonstrate `read_warehouse_query()`. |

## Incremental-processing scenarios

### Watermark

Use `modified_datetime` as the watermark.

1. Load `orders.csv` into the source: first run should resolve to `full_dataset`.
2. Run again without changing the source: it should resolve to `skip`.
3. Append `orders_incremental.csv`: the next run should resolve to `incremental_subset` containing only the later watermark range.

Negative fixtures:

- `orders_watermark_duplicate.csv` contains a duplicate watermark and should be rejected by watermark preparation.
- `orders_watermark_null.csv` contains a null watermark and should be rejected by watermark preparation.

### Partition

Use `order_date` as the partition column.

1. `orders_partition_baseline.csv` contains three complete source partitions.
2. `orders_partition_new.csv` represents a new partition.
3. `orders_partition_changed.csv` represents the complete replacement content for an existing partition with deterministic changes.

These files are intentionally separate from the main Orders baseline so watermark and partition acceptance tests can be reset independently.

## Guardrail scenario

`orders_guardrail_failures.csv` contains deliberate independent failures for later contract/Guardrail testing, including missing identifiers, duplicate identifiers, negative quantity/price, invalid discount, invalid status, unknown product, missing customer, null watermark, and invalid country.

The normal baseline remains valid so the engineering demo is deterministic. Failure fixtures should only be introduced when explicitly testing validation behaviour.

## File-format variants

The canonical logical Orders baseline is `orders.csv`. Equivalent JSON, Parquet, and Excel copies should be generated from this exact dataset so readers can be swapped without changing the downstream ETL story. Those binary/file-format copies are maintained separately from this scenario-definition change.
