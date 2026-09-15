# Step 2. Build and run the ETL

**This is the main Engineering walkthrough. Run the current `02_pipeline` in Development before any Data Contract exists so you can see what FabricOps already standardizes, what remains project-owned, and what Governance adds later.**

The template is a **full-read pipeline**. Every governed source is read as the complete persisted table on each run. Target publication is a separate concern: each Write block can use its own Development processing proposal now and its governed Data Contract strategy later.

## What this step should teach

By the end of Step 2 you should understand the complete reusable shape:

```text
00_env_config
      ↓
Data Contract context
      ↓
READ 1 ─┐
READ 2 ─┼─→ Transform ─→ WRITE 1
READ 3 ─┘              └→ WRITE 2
```

This is a genuine many-to-many pattern. A project can clone Read blocks for more sources, create multiple transformed outputs, and clone Write blocks for additional targets. Each target declares the exact source `table_id` values that feed it so Lineage stays target-specific.

## 0. Environment

`02_pipeline` begins with:

```python
%run 00_env_config
```

The notebook then imports the public FabricOps boundaries and checks used by the template.

## 1. Data Contract context: deliberately empty on the first run

Run the Data Contract selection section, but do not select a contract for the new demo targets because none exists yet.

This is not an error. Development is allowed to build the real pipeline before Governance has authored the first contract.

The important behaviour is that the check functions still run. When there is no selected Data Contract in Development they return a safe skipped result instead of forcing engineers to comment the checks out. For example, governed DQ returns:

```text
status = skipped
can_continue = True
reason = No Data Contract selected; Development only.
```

That means the notebook shape is stable from the first run onward. You do not create a separate ungoverned pipeline and later replace it with a governed one.

## 2. Full Read: three governed sources

The supplied template demonstrates three independent source reads:

| Read | Store | Table | Role |
| --- | --- | --- | --- |
| Orders | Source Lakehouse | `demo.orders` | Current transactional Orders. |
| Products | Source Lakehouse | `demo.products` | Product reference data. |
| Order History | Product Warehouse | `demo.order_history` | Historical customer context. |

Each Read block follows the same structure:

1. `pipeline_read()` resolves the configured store, reads the complete table, and returns the canonical `table_id`.
2. `check_freshness()` runs or safely skips when no contract is selected.
3. `check_schema()` runs or safely skips.
4. `check_dq()` runs or safely skips.
5. `profile_table(table_id=...)` refreshes the canonical profile for the complete physical source.

The orchestration is intentionally visible. FabricOps abstracts repetitive routing and metadata work, but the notebook still shows the lifecycle so it is not a black box.

### Why profiling still matters before the Data Contract

The first Development run gives Governance something real to govern. `profile_table()` records the observed physical table structure and statistics so Step 3 can author Enrichment, Guardrails, and Processing against an actual `table_id` rather than an imagined schema.

## 3. Transform: ordinary PySpark

The template keeps project logic in the middle.

The supplied example combines Orders, Products, and Order History and produces two outputs:

1. `transformed_df`: detailed curated Orders.
2. `customer_summary_df`: customer-level summary.

FabricOps does not introduce a transformation DSL. Join, filter, aggregate, derive columns, and reshape data with normal PySpark.

This is where the many-to-many shape becomes visible:

```text
orders ───────┐
products ─────┼─→ curated_orders
order_history ┘

curated_orders ─→ customer_summary
```

## 4. Write: two independent target flows

Each Write block is a complete target publication boundary. The current template demonstrates a Lakehouse target and a Warehouse target so users see that the same FabricOps pattern works across store types.

For every target, the block performs the explicit sequence:

1. `resolve_table_id()` once for the target.
2. `check_schema()`.
3. `check_sensitive_data()` and carry its returned DataFrame forward.
4. `check_source_drift()` for each exact source-to-target relationship.
5. `check_dq()`.
6. `check_guardrail_coverage()`.
7. `pipeline_write()` using the target's Development processing proposal when no contract exists.
8. `profile_table(table_id=...)` after publication so profiling represents the persisted target.

On the first run, contract-backed checks skip in Development because there is no selected contract. `pipeline_write()` can still use the Development load strategy proposal supplied by the Write block, publish the target, and record the successful technical metadata.

## Show different load strategies instead of only talking about them

Use the two target blocks to make target processing concrete.

A simple first-run configuration is:

| Target | Development strategy | What the user sees |
| --- | --- | --- |
| `unified.demo.curated_orders` | `overwrite` | The persisted target always represents the latest complete transformed result. |
| Product Warehouse customer summary | `overwrite` initially | A clean baseline summary that can later be governed with another strategy if desired. |

Then in Step 3, author the target Processing definition in the Data Contract. One useful demonstration is to keep the curated table as `overwrite` while configuring another suitable target as `append`, SCD1, or SCD2 with the required strategy parameters. The point is not to show every strategy in one notebook. It is to show that **each target has its own governed processing contract** even when both targets come from the same transformation flow.

## Day 1: run the pipeline

At the start of the demo, `source.demo.orders` contains the 120 rows loaded from `orders.csv`.

Run `02_pipeline` from top to bottom and verify:

- all three sources are read in full,
- checks visibly skip where no Data Contract is selected,
- source profiles are refreshed,
- the transformation produces both outputs,
- both targets are published,
- each target receives its own canonical `table_id`, Lineage, and post-write profile.

This is the evidence Governance will use in Step 3.

## Day 2: change the source and rerun

Before the later validation run, return to the simple setup notebook from 0B and append `orders_incremental.csv` to `source.demo.orders`.

That adds 12 later Orders rows, moving the managed source from 120 to 132 rows.

On the next `02_pipeline` execution:

- `pipeline_read()` still reads the entire 132-row Orders source,
- the transformations recompute from the complete current sources,
- an `overwrite` target is replaced with the newly computed complete result,
- an `append` target would append its current publication rows,
- SCD1/SCD2 targets, when governed with the required keys and parameters, apply their respective update/history semantics.

This is the key distinction the demo should leave users with:

**Full read is the source-processing model. Load strategy is the target-publication model.**

## Multiple writes and parallelism

The canonical notebook shows independent Write blocks sequentially because that is easiest to inspect, retry, and debug.

FabricOps keeps those writes independent by requiring each target to provide the exact source `table_id` values that feed it. That independence is what makes wider orchestration possible.

If a project chooses to execute independent target publications concurrently through Fabric orchestration or Spark job scheduling, keep each complete Write block intact. Concurrency is an execution optimisation around the same FabricOps contract, not a separate API or hidden `parallel_write()` feature.

Also distinguish target concurrency from Spark write parallelism. `pipeline_write(..., repartition_by=...)` can control partitioning for a physical write, but that is not the same thing as running two target Write blocks concurrently.

## What FabricOps recorded

After the first run, inspect the technical evidence rather than relying only on printed success messages. You should now have real table identities and refreshed technical metadata such as Catalogue, Profiled/Profiled Frequency where applicable, Lineage, and successful write/source-observation state created by the pipeline functions.

Step 3 uses those real target identities to author Governance.

## Expected result

You have now run a complete FabricOps ETL without a Data Contract and seen that:

- the same notebook shape works before and after Governance,
- checks safely skip in Development when no contract exists,
- multiple source tables can feed multiple targets,
- project transformation remains plain PySpark,
- each target owns an independent publication flow and load strategy,
- FabricOps records the technical evidence Governance needs next.

**Next:** [Step 3. Author and freeze the Data Contract](03-enrich-guardrails.md)
