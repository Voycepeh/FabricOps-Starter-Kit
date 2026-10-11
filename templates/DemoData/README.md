# FabricOps Guided Demo data

These fixtures support one connected retail story across setup, Engineering, profiling, Guardrail validation, and later analytics consumption.

## Core data

| File | Purpose |
| --- | --- |
| `02A_full_refresh_demo.ipynb` | Ready-to-run Full → Overwrite pipeline using the canonical retail sources. |
| `02B_incremental_append_demo.ipynb` | Three-run Incremental → Append inventory demonstration. |
| `02C_scd_demo.ipynb` | Three-run Product Master SCD1 and SCD2 demonstration. |
| `00C_demo_setup.ipynb` | Demonstrates FabricOps file I/O and seeds the original managed sources. |
| `orders.csv` | Canonical valid Orders baseline used by 0C to seed `bronze.demo.orders` and by the main Guided Demo. |
| `products.csv` | Product reference data used by 0C to seed `bronze.demo.products`. |
| `order_history.csv` | Historical transactions used by 0C to seed `gold.demo.order_history` and demonstrate Warehouse reads. |

The existing Full → Overwrite demo continues to use these canonical files unchanged. `modified_datetime` remains available on Orders, but the optional processing-mode exercises use their own related Bronze sources so learners can author separate contracts without changing `demo.orders` or `demo.products`.

## Connected optional processing fixtures

All new files reuse exactly the eight canonical product IDs (`P001` through `P008`).

| File | Role | Expected behavior |
| --- | --- | --- |
| `incremental_inventory/inventory_day1.csv` | Opening stock receipt events | First Incremental → Append bootstrap, 8 movements |
| `incremental_inventory/inventory_day2.csv` | Later sale and replenishment movements | Append 4 additional events, then no-change rerun |
| `scd_product_master/products_day1.csv` | Full product master snapshot | Initial 8 SCD1 rows and 8 SCD2 versions |
| `scd_product_master/products_day2.csv` | Full product master snapshot | P002 list price changes, SCD2 grows to 9 versions |
| `scd_product_master/products_day3.csv` | Full product master snapshot | P001 category changes, SCD2 grows to 10 versions |

Proposed Bronze sources: `demo.inventory_movements` and `demo.product_master_updates`. Proposed Silver targets: `demo.inventory_movements_incremental`, `demo.product_master_scd1`, and `demo.product_master_scd2`.

The inventory batches are independent synthetic movement events, not a reconciled fulfillment log for existing `orders.csv`. A future unified dashboard must avoid treating them as one-to-one order fulfillment records. `quantity_change` is signed and cumulative balance is calculated by product. Initial inventory receipts provide the baseline. Day 2 has strictly later `modified_datetime` values and unique movement IDs.

For SCD, load each complete snapshot into the same Bronze product-master source using **overwrite**, then read it in Full mode and write both Silver targets separately. `product_id` is the business key; `product_category` and `list_price` are tracked attributes; `modified_datetime` is the effective timestamp. Unchanged products have later snapshot timestamps but must not create SCD2 history versions.

The master `list_price` is not the same as the transactional `unit_price` in Orders. Historic sales should use the recorded transaction price, never be repriced using the latest product master.

Run `python templates/DemoData/validate_connected_retail.py` from the repository root to validate shared keys, inventory chronology, complete product snapshots and expected changes. The full-refresh fixtures are not mutated by this addition.

## Guided Demo mutations

The original full-refresh and Guardrail examples derive their test conditions from the canonical Orders baseline inside the walkthrough. This keeps each mutation visible, reproducible, and attributable to the behavior being demonstrated; no separate incremental, partition, watermark, or Guardrail-failure Orders fixture is required.

The normal baseline remains valid so the first Engineering and contract-validation runs are deterministic.

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
- 2A owns the Full → Overwrite retail walkthrough, 2B owns incremental inventory ingestion, and 2C owns full-snapshot SCD ingestion.
- later Guardrail validation creates a temporary dirty transformed DataFrame in the notebook session and never modifies the canonical fixture.

Add new fixtures only when their owning demo/test scenario is documented alongside them.
