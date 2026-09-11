# FabricOps Guided Demo data

These fixtures support one Orders-domain story across ingestion, target processing, profiling, and later Guardrail validation.

## Core data

| File | Purpose |
| --- | --- |
| `orders.csv` | Canonical valid Orders baseline used by the main Guided Demo. |
| `orders_incremental.csv` | Later Orders batch for an explicit project-owned filtered query and append target write. |
| `products.csv` | Product reference data used to seed the Lakehouse lookup table. |
| `order_history.csv` | Historical transactions used to seed the Warehouse and demonstrate `read_warehouse_query()`. |

## Target-processing scenarios

`orders_incremental.csv` can be selected by explicit project query logic before an `append` target write. The partition fixtures can exercise a governed target `overwrite` whose `partition_column` is `order_date`. These inputs do not configure a separate source-read strategy; the target Data Contract remains authoritative for `overwrite`, `append`, `scd1`, or `scd2`.

## Guardrail scenario

`orders_guardrail_failures.csv` contains deliberate independent failures for later contract/Guardrail testing, including missing identifiers, duplicate identifiers, negative quantity/price, invalid discount, invalid status, unknown product, missing customer, null watermark, and invalid country.

The normal baseline remains valid so the engineering demo is deterministic. Failure fixtures should only be introduced when explicitly testing validation behaviour.

## File-format variants

`orders.csv` is the canonical logical Orders baseline. The following files contain the same 120 logical rows and columns so the Guided Demo can swap file readers without changing downstream ETL logic:

| File | FabricOps reader |
| --- | --- |
| `orders.csv` | `read_lakehouse_csv()` |
| `orders.json` | `read_lakehouse_json()` |
| `orders.parquet` | `read_lakehouse_parquet()` |
| `orders.xlsx` | `read_lakehouse_excel()` |

`orders.json` uses JSON Lines, which matches Spark's normal JSON-reader behaviour. `orders.xlsx` contains the same canonical table on a worksheet. When `orders.csv` changes, regenerate all three variants from it and verify row, column, and value equivalence.

The previous standalone `*_demo` fixtures were removed. The canonical Orders scenario above now owns the Guided Demo data surface.
