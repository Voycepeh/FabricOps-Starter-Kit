# `99_explore`: optional exploration support

**Use `99_explore` for discovery, investigation, troubleshooting, ad hoc analysis, exploratory profiling, and catalogue inspection around the governed workflow.**

It is not part of the required delivery loop. The required path remains:

**`01_governance` → `02_pipeline` → `01_governance`**

Keep repeatable project transformation and governed publication in `02_pipeline`. Keep Governance authoring, review, freezing, and activation in `01_governance`.

## 1. Load the configured environment

`99_explore` starts from the same shared configuration:

```python
%run 00_env_config
```

This lets exploratory work use the configured logical store names instead of embedding workspace IDs, item IDs, or physical paths.

## 2. Read configured Fabric data

The notebook provides examples for the foundational FabricOps readers, including:

- Lakehouse CSV, Excel, and Parquet files,
- Lakehouse tables,
- Warehouse tables,
- Warehouse SQL queries.

Use these examples as a solution bank when you need to inspect data outside the governed `02_pipeline` execution path.

For Warehouse exploration, prefer `read_warehouse_query()` when SQL filtering, projection, or aggregation should happen in the Warehouse before Spark receives the result.

## 3. Run exploratory profiling

`99_explore` can call:

```python
profile_result = profile_table(dataframe=source_df)
display(profile_result["profile"])
```

When `profile_table()` receives only a DataFrame, this is local exploratory output. It does not replace the canonical table profiling performed by `02_pipeline` against a governed `table_id`.

Use it to understand unfamiliar data before deciding what belongs in the repeatable engineering flow.

## 4. Browse existing catalogue context

The notebook can open the catalogue explorer and load the selected table's available catalogue, profile, and frequency views.

Use this for investigation and troubleshooting when you need to inspect the evidence FabricOps has already recorded.

Catalogue inspection does not approve a Data Contract and does not replace the Governance workflow in `01_governance`.

## 5. Keep exploration separate from delivery

The notebook contains reusable I/O examples for learning and smoke testing. In the Guided Demo, treat `99_explore` as optional support rather than a place to publish governed Production outputs.

When exploratory logic becomes repeatable delivery logic:

1. move the transformation into `02_pipeline`,
2. use the governed Read and Write blocks,
3. let the pipeline checks, contract context, lineage, source observation, and persisted target profiling run through the standard engineering path.

## Expected result

You should understand where `99_explore` fits without treating it as another lifecycle stage:

- `00_env_config` configures the environment,
- `01_governance` owns Governance,
- `02_pipeline` owns repeatable governed engineering,
- `99_explore` supports optional discovery and troubleshooting around them.

Return to the [Guided Demo overview](../guided-demo.md) or continue with the [Function Reference](../reference/index.md) when you need exact APIs.
