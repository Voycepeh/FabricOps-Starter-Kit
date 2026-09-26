# Step 6. Promote and run Production

**Promote the validated `02_pipeline` logic and run the same engineering pattern in Engineering Production.**

FabricOps keeps engineering promotion simple. The pipeline tested in Development is promoted unchanged to Production. Environment specific Fabric items are resolved through `00_env_config`, so Production does not need a separate copy of the pipeline logic.

## 1. Same pipeline, different environment

The same `02_pipeline` code runs in Development and Production.

`00_env_config` controls which configured Lakehouses, Warehouses, schemas, paths, and SQL endpoints are used for the current environment.

![Development to Production promotion](../assets/06/Promotion_Overview.png)

The important boundary is:

* promote the validated pipeline logic
* keep environment specific identities in `00_env_config`
* do not move Development output tables or draft metadata into Production

## 2. Select the pipeline artifact in Fabric

In the Fabric Deployment Pipeline, select the tested notebook or engineering artifact from Development and deploy it to the Production stage.

![Select the pipeline artifact for Production](../assets/06/Deployment_Pipeline.png)

The promotion should move the tested engineering asset itself. Workspace IDs, item IDs, paths, and SQL endpoints should continue to come from the Production environment configuration.

## 3. Review and deploy

Review the selected item in the Fabric deployment confirmation, then complete the deployment.

![Confirm the Fabric deployment](../assets/06/Deployment_Confirm.png)

At this point the same validated engineering code is available in Production.

## Run Production

Run the Production `00_env_config` first:

```python
%run 00_env_config
```

Then run the promoted `02_pipeline`.

Production follows the same visible Read → Transform → Write structure used in Development. The difference is contract resolution:

* Development can explicitly select an eligible immutable version for validation.
* Production resolves the active Data Contract automatically for each governed `table_id`.

The same Guardrail functions evaluate the active expectations, and `pipeline_write()` uses the active governed Processing definition for each target.

## Expected result

Engineering Production runs the same validated pipeline logic against Production configured Fabric items and publishes governed outputs using the active Data Contract.

**Next:** [Step 7. Consume approved Production data](99-explore.md)
