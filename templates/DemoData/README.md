# FabricOps Guided Demo data

These fixtures support one Orders-domain story across setup, Engineering, incremental-load behaviour, profiling, and later Guardrail validation.

## Core data

| File | Purpose |
| --- | --- |
| `orders.csv` | Canonical valid Orders baseline used by 0C to seed `bronze.demo.orders` and by the main Guided Demo. |
| `orders_incremental.csv` | Later Orders batch intentionally left untouched in 0C and revisited during the later `02_pipeline` source-change/load-strategy story. |
| `products.csv` | Product reference data used by 0C to seed `bronze.demo.products`. |
| `order_history.csv` | Historical transactions used by 0C to seed `gold.demo.order_history` and demonstrate Warehouse reads. |

## Incremental-load scenarios

These fixtures are intentionally retained for the later incremental/load-strategy showcase rather than loaded by 0C:

| File | Scenario |
| --- | --- |
| `orders_partition_baseline.csv` | Baseline partitioned target state used before demonstrating partition overwrite behaviour. |
| `orders_partition_changed.csv` | Changed rows for an existing partition so the walkthrough can demonstrate replacing only the affected partition. |
| `orders_partition_new.csv` | Rows for a new partition so the walkthrough can demonstrate adding a new partition alongside existing data. |
| `orders_watermark_duplicate.csv` | Negative incremental-watermark fixture containing duplicate `modified_datetime` values. |
| `orders_watermark_null.csv` | Negative incremental-watermark fixture containing a null `modified_datetime`. |

These files should remain untouched during 0C. They belong to the later Engineering walkthrough where load strategy and incremental processing are demonstrated explicitly.

## Guardrail scenario

`orders_guardrail_failures.csv` contains deliberate independent failures for the later contract/Guardrail validation story, including missing identifiers, duplicate identifiers, negative quantity/price, invalid discount, invalid status, unknown product, missing customer, null watermark, and invalid country.

The normal baseline remains valid so the first Engineering run is deterministic. Failure fixtures should only be introduced when explicitly testing validation behaviour.

## File-format variants

`orders.csv` is the canonical logical Orders baseline. The following files contain the same 120 logical rows and columns so `00C_demo_setup.ipynb` can demonstrate the FabricOps file readers without changing the downstream data story:

| File | FabricOps reader |
| --- | --- |
| `orders.csv` | `read_lakehouse_csv()` |
| `orders.json` | `read_lakehouse_json()` |
| `orders.parquet` | `read_lakehouse_parquet()` |
| `orders.xlsx` | `read_lakehouse_excel()` |

`orders.json` uses JSON Lines, which matches Spark's normal JSON-reader behaviour. `orders.xlsx` contains the same canonical table on a worksheet. When `orders.csv` changes, regenerate all three variants from it and verify row, column, and value equivalence.

## Demo-data ownership

Every retained fixture has an explicit Guided Demo owner:

- 0C owns the canonical file-format reads plus the initial Lakehouse/Warehouse seed tables.
- the later `02_pipeline` walkthrough owns `orders_incremental.csv` and the partition/watermark incremental-load fixtures.
- the later Guardrail validation walkthrough owns `orders_guardrail_failures.csv`.

Add new fixtures only when their owning demo/test scenario is documented alongside them.
