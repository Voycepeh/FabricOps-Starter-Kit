# FabricOps Guided Demo data

These fixtures support one Orders-domain story across setup, Engineering, profiling, and Guardrail validation.

## Core data

| File | Purpose |
| --- | --- |
| `orders.csv` | Canonical valid Orders baseline used by 0C to seed `bronze.demo.orders` and by the main Guided Demo. |
| `products.csv` | Product reference data used by 0C to seed `bronze.demo.products`. |
| `order_history.csv` | Historical transactions used by 0C to seed `gold.demo.order_history` and demonstrate Warehouse reads. |

The later Engineering scenarios reuse the canonical Orders baseline and create their source changes directly in the walkthrough. `modified_datetime` is available as the incremental watermark, and `order_date` can be derived from `order_datetime` when a partition column is needed. Separate incremental, partition, and watermark fixture files are therefore not required.

## Guided Demo mutations

Later Engineering and Guardrail scenarios derive their test conditions from the canonical Orders baseline inside the walkthrough. This keeps each mutation visible, reproducible, and attributable to the behavior being demonstrated; no separate incremental, partition, watermark, or Guardrail-failure Orders fixture is required.

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
- later Engineering scenarios mutate the canonical Orders source in the walkthrough rather than relying on separate fixture files.
- later Guardrail validation creates a temporary dirty transformed DataFrame in the notebook session and never modifies the canonical fixture.

Add new fixtures only when their owning demo/test scenario is documented alongside them.
