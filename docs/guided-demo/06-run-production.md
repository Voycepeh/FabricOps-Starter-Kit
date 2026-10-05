# Step 6. Run the pipeline in Production

**Run the promoted engineering workflow in Engineering Production, publish the governed Production output, then hand direct data access to consumers through native Microsoft Fabric permissions and interfaces.**

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

The same source reads, transformations, Guardrail checks, governed write logic, profiling, [Lineage](../reference/metadata/metadata_data_lineage.md), and [Source Observation](../reference/metadata/metadata_source_observation.md) flow run again against Production resources.

The key difference is Data Contract resolution:

* Development can explicitly select an eligible frozen version for validation.
* Production automatically resolves the single active Data Contract for each governed `table_id`.

The same Guardrail functions therefore enforce the Production-active definition, and [`pipeline_write()`](../api/reference/pipeline_write.md) uses the active governed Processing configuration for each target.

## 3. Grant direct consumer access

Once the governed Production output exists, consumers do not need a FabricOps exploration notebook to use it.

Grant the required access through the appropriate native Fabric path, such as Workspace roles, SQL endpoint grants, or OneLake security roles. Keep access scoped to the approved Production data the consumer needs.

Consumers can then use the standard Fabric experience that fits their work: connect a notebook to the permitted Lakehouse, query the Warehouse or SQL analytics endpoint, use SQL tooling, or connect another supported Fabric consumer. They should not need to recreate the Production engineering pipeline or use FabricOps readers merely to access an already-published table.

FabricOps remains relevant to the access boundary through its effective-access scanning and governance context. It does not need to own the consumer's exploration interface.

## Expected result

Engineering Production completes the validated pipeline workflow, publishes governed Production outputs using the active Data Contract, and approved consumers can reach those outputs through native Fabric access controls and interfaces.

**Next:** [Step 7. Publish governed data to a Fabric Data Agent](07-consume-production-data.md)
