# Step 6. Promote and run Production

**Promote the validated `02_pipeline` logic and run the same engineering pattern in Engineering Production.**

Production should not receive Development output tables, draft metadata, or a hand-edited copy of the contract. The promoted asset is the validated pipeline logic; Production resolves its own configured stores and the active governed definition.

## Promote the pipeline

Use your organisation's Fabric deployment process to make the validated `02_pipeline` available in Engineering Production.

Keep environment-specific identities in `00_env_config` so promotion does not require rewriting workspace IDs, item IDs, paths, or SQL endpoints inside the pipeline notebook.

## Run Production `00_env_config`

The Production notebook loads its own configured context:

```python
%run 00_env_config
```

The same logical names now resolve to Production Fabric items.

## Run the same `02_pipeline`

Production follows the same visible Read → Transform → Write structure used in Development.

The key difference is contract resolution:

- Development can explicitly select an eligible immutable version for testing.
- Production resolves the active Data Contract automatically for each governed `table_id`.

The same Guardrail functions execute the active expectations, and `pipeline_write()` uses the active governed Processing definition for each target.

## What should feel familiar

By this stage there should be no new FabricOps engineering pattern to learn. The user has already seen:

- configured stores in 0B,
- the same full Read blocks in Steps 2 and 4,
- the same ordinary PySpark transformation,
- the same independent Write blocks,
- the same Guardrail locations,
- the same target load-strategy boundary.

Production is the validated workflow running under stricter contract resolution, not a separate implementation.

## Expected result

Engineering Production has published governed outputs using the active Data Contract and the Production environment configuration.

**Next:** [Step 7. Consume approved Production data](99-explore.md)
