# Step 2C. Run the SCD1 and SCD2 Demo

**Send three complete Product Master snapshots through one governed Full Read and compare current-state SCD1 with historical SCD2.**

## Before you begin

Download and import these assets:

- [`02C_scd_demo.ipynb`](https://raw.githubusercontent.com/Voycepeh/FabricOps-Starter-Kit/main/templates/DemoData/02C_scd_demo.ipynb)
- [`products_day1.csv`](https://raw.githubusercontent.com/Voycepeh/FabricOps-Starter-Kit/main/templates/DemoData/scd_product_master/products_day1.csv)
- [`products_day2.csv`](https://raw.githubusercontent.com/Voycepeh/FabricOps-Starter-Kit/main/templates/DemoData/scd_product_master/products_day2.csv)
- [`products_day3.csv`](https://raw.githubusercontent.com/Voycepeh/FabricOps-Starter-Kit/main/templates/DemoData/scd_product_master/products_day3.csv)

Attach the same Fabric Environment used in Steps 00B and 2A. Keep `00_env_config` beside the notebook, and keep the CSV files under `Files/Demo/scd_product_master` in the Bronze Lakehouse.

The notebook uses one governed source and two governed targets throughout all three runs:

| Role | Store | Table | Processing |
| --- | --- | --- | --- |
| Source | `Bronze` | `demo.product_master_updates` | Full Read |
| SCD1 target | `Silver` | `demo.product_master_scd1` | Key: `product_id` |
| SCD2 target | `Silver` | `demo.product_master_scd2` | Effective: `modified_datetime`; tracked: `product_category`, `list_price` |

## What to do

### 1. Run Day 1

Leave the day cell unchanged:

```python
DEMO_DAY = 1
```

Run every cell from top to bottom. The notebook:

1. runs `%run 00_env_config` and imports public FabricOps APIs;
2. reads the complete Day 1 CSV snapshot;
3. overwrites Bronze `demo.product_master_updates`;
4. runs the Data Contract selector;
5. calls `orchestrate_read()` in `full` mode;
6. normalizes Product Master types with PySpark;
7. calls `orchestrate_write()` once with `scd1` and once with `scd2`, passing the same governed Read result to both for lineage;
8. displays current SCD1 rows and current/historical SCD2 versions.

Expect **8 SCD1 rows** and **8 SCD2 versions**.

### 2. Run Day 2

Change only the day value and rerun every cell:

```python
DEMO_DAY = 2
```

The Bronze source is replaced by the complete Day 2 snapshot. Product `P002` changes `list_price`, so SCD1 updates its single current row and SCD2 closes the old version and inserts a new current version. Unchanged products do not gain history solely because their snapshot timestamp is later.

Expect **8 SCD1 rows** and **9 SCD2 versions**.

### 3. Run Day 3

Change only the day value and rerun every cell:

```python
DEMO_DAY = 3
```

Product `P001` changes `product_category`. SCD1 keeps one latest row for the product; SCD2 retains the former category as historical and creates a new current version.

Expect **8 SCD1 rows** and **10 SCD2 versions**.

!!! warning "Keep the days in order"

    Run Day 1 → Day 2 → Day 3. The notebook verifies the expected prior SCD2 version count before Days 2 and 3 and stops if a day was skipped or the targets contain an unexpected state. Replaying the current day is safe because unchanged tracked values do not create another SCD2 version.

## Expected result

| Day | Business change | SCD1 rows | SCD2 versions |
| --- | --- | ---: | ---: |
| 1 | Initial eight products | 8 | 8 |
| 2 | `P002.list_price` changes | 8 | 9 |
| 3 | `P001.product_category` changes | 8 | 10 |

The final inspection orders SCD2 by `product_id` and `_effective_from` and shows `_effective_to` and `_is_current`, making current and historical records explicit.

### Reset the demo

Remove Bronze `demo.product_master_updates` and both Silver demo targets, then set `DEMO_DAY = 1` and rerun from the top. If you authored Data Contracts or other Governance metadata specifically for these identities, reset them only through the normal FabricOps Governance workflow or use a fresh Guided Demo environment. Never restart Day 1 against retained SCD targets.

**Next:** [Step 3. Author and freeze the Data Contract](03-author-and-freeze-data-contract.md)
