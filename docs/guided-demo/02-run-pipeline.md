# `02_pipeline`: run the governed engineering pipeline

**Use `02_pipeline` as the reusable Engineering template in Development and Production. It reads governed sources in full, keeps project transformation logic as ordinary PySpark, and standardizes the governed checks and publication work around the Read and Write boundaries.**

The current template is a **full-read pipeline**. It does not implement source-side incremental processing. Target publication can still use the governed load strategy defined in the Data Contract, such as overwrite, append, partition overwrite, SCD1, or SCD2.

## Before you begin

Complete [`00_env_config`](00-env-config.md) and establish the initial steward/agreement context in [`01_governance`](01-governance.md).

For the supplied walkthrough, confirm these managed source tables exist:

```text
Source Lakehouse
  demo.orders
  demo.products

Product Warehouse
  demo.order_history
```

## 0. Environment

`02_pipeline` begins by loading the shared configuration:

```python
%run 00_env_config
```

The template then imports the public FabricOps functions used by the pipeline. Keep the Fabric-specific routing in the reusable FabricOps boundaries and keep your project transformation logic in the Transform section.

## 1. Data Contract

Development uses `widget_select_data_contract()` to establish the contract context for the tables being tested.

On the first engineering run, Governance may not yet have a frozen Data Contract for the new target. That is acceptable in Development: run the pipeline to establish the real table identity and profiling evidence Governance needs. Missing configured Guardrail coverage warns in Development rather than turning this into a separate baseline workflow.

After Governance freezes a contract version, return to this same section, select that immutable version, and rerun the same pipeline against it.

In Production, FabricOps resolves the active Data Contract automatically rather than using a Development override.

## 2. Full Read

Each Read block handles one complete governed source.

For the supplied demo, the template contains three cloneable Read blocks:

- Orders from `source.demo.orders`,
- Products from `source.demo.products`,
- Order History from `product.demo.order_history`.

A Read block calls `pipeline_read()` to return the source DataFrame and canonical `table_id`, then keeps the governed checks and profiling visible in the notebook.

For each source, the current template performs:

1. `pipeline_read()` to read the complete governed table and resolve its `table_id`,
2. `check_freshness()` to enforce the configured Freshness expectation when present,
3. `check_schema()` against the returned DataFrame,
4. `check_dq()` against the same DataFrame,
5. `profile_table(table_id=...)` to refresh the canonical profile for the complete persisted source.

Optional `display()` calls and caller-owned failure persistence remain commented out in the template so the normal run stays uncluttered. Uncomment them only when you need development inspection or project-owned failure tables.

### Clone a Read block

To add another governed source, clone a complete Read block and change the small variable set at the top:

```python
READ_NAME = "orders"
READ_STORE = "source"
READ_SCHEMA = "demo"
READ_TABLE = "orders"
READ_QUERY = None
```

Do not rewrite the internal check/profile sequence for every source.

## 3. Transform

The Transform section is project-owned PySpark.

The supplied example reads the named source DataFrames from the `sources` dictionary, joins Orders and Products, adds historical customer context, and creates two outputs:

- detailed curated Orders,
- a customer-level summary.

This section is intentionally ordinary PySpark. FabricOps standardizes the operating boundaries without introducing a transformation DSL.

Replace the example transformation with your project logic while keeping the surrounding Read and Write contracts intact.

## 4. Write

Each Write block is one complete governed target flow. Clone the block for additional outputs.

The template demonstrates both a Lakehouse target and a Warehouse target. Each target declares its DataFrame, source relationships, configured store, schema, table name, and Development fallback load strategy.

The current Write sequence is explicit:

1. resolve the target `table_id` with `resolve_table_id()`,
2. enforce target Schema with `check_schema()`,
3. enforce Sensitive Data requirements with `check_sensitive_data()` and carry its returned DataFrame forward,
4. enforce Source Drift for each source-to-target relationship with `check_source_drift()`,
5. enforce target Data Quality with `check_dq()`,
6. call `check_guardrail_coverage()` so the publication has the expected governed checks,
7. publish through `pipeline_write()`, which resolves the governed target load strategy and records successful technical metadata only after the physical write succeeds,
8. call `profile_table(table_id=...)` after the write so profiling reflects the complete persisted target rather than only the input DataFrame.

The Write block is intentionally not a black box. The public functions abstract the repetitive plumbing while the notebook still shows the checks that run and the order they run in.

### Development load strategy

The example Write block includes a Development fallback such as:

```python
WRITE_LOAD_STRATEGY = "overwrite"
```

Once the selected Data Contract defines the target processing strategy, the governed contract is the operational definition. The fallback is not a second processing model.

### Clone a Write block

Change the target-specific variables at the top of the cloned block and keep the governed sequence intact.

For example:

```python
WRITE_NAME = "curated_orders_lakehouse"
WRITE_DATAFRAME = transformed_df
WRITE_SOURCE_NAMES = ("orders", "products", "history")
WRITE_STORE = "unified"
WRITE_SCHEMA = "demo"
WRITE_TABLE = "curated_orders"
WRITE_LOAD_STRATEGY = "overwrite"
```

## First Development run

Run the notebook from top to bottom.

The purpose of the first run is to prove the engineering path and establish real table/catalogue/profile evidence. Governance can then use the resulting target `table_id` in `01_governance` rather than authoring a contract against an imagined table definition.

After the run, return to [`01_governance`](01-governance.md), select the governed target, author the Data Contract, and freeze the first immutable version.

## Validate the frozen contract in Development

After Governance freezes a version:

1. return to the Data Contract section of the same `02_pipeline`,
2. select the frozen version,
3. rerun the full pipeline,
4. review any Warn or Block outcomes from the configured Guardrails,
5. confirm the physical outputs and persisted technical metadata are correct.

If the governed definition needs changes, return to `01_governance`, refine it, freeze a new version, and test that new immutable version. Do not create a separate Guardrail pipeline.

## Production run

After Development validation, Governance links the tested contract version to the required Data Agreement version and activates it.

Promote the validated `02_pipeline` through your organisation's normal Fabric deployment process. In Engineering Production:

1. run the Production `00_env_config`,
2. use the promoted `02_pipeline`,
3. run the same full-read pipeline structure,
4. allow FabricOps to resolve the active contract automatically,
5. publish governed Production outputs using the active processing definition.

Only the validated pipeline logic is promoted. Do not copy Development output tables or draft Governance metadata into Production as part of the promotion step.

## Expected result

You now have one engineering notebook pattern that:

- reads every governed source in full,
- keeps the source checks and profiling explicit,
- leaves project transformation as normal PySpark,
- enforces target governance before publication,
- writes using the governed target strategy,
- records technical metadata around successful publication,
- profiles the complete persisted target after the write,
- moves from Development testing to Production without inventing a second pipeline template.

**Next:** return to [`01_governance`](01-governance.md) to complete contract authoring or activation as appropriate. Use [`99_explore`](99-explore.md) only when optional discovery or troubleshooting support is useful.
