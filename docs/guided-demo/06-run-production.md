# Step 6. Run the pipeline in Production

**Run the promoted engineering workflow again in Engineering Production using the Production environment configuration and the active Data Contract.**

There is no new engineering pattern in this step. The point is to execute the same tested workflow in the Production environment.

## 1. Load the Production configuration

Run the Production copy of `00_env_config`:

```python
%run 00_env_config
```

The same logical store names now resolve to the Production Lakehouses, Warehouses, schemas, paths, and SQL endpoints.

## 2. Run the promoted pipeline

Run the promoted `02_pipeline` from start to finish.

Production follows the same visible lifecycle used in Development:

```text
Read → Transform → Write
```

The same source reads, transformations, Guardrail checks, governed write logic, profiling, Lineage, and Source Observation flow run again against Production resources.

The key difference is Data Contract resolution:

* Development can explicitly select an eligible frozen version for validation.
* Production automatically resolves the single active Data Contract for each governed `table_id`.

The same Guardrail functions therefore enforce the Production-active definition, and `pipeline_write()` uses the active governed Processing configuration for each target.

## Expected result

Engineering Production completes the same validated pipeline workflow against Production-configured Fabric items and publishes governed Production outputs using the active Data Contract.

**Next:** [Step 7. Consume approved Production data](07-consume-production-data.md)
