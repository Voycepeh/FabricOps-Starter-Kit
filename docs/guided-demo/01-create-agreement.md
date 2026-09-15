# Step 1. Establish Governance context

**Use `01_governance` only for the first Governance job: create the accountable Data Stewards and the Data Agreement.**

Do not author Guardrails or a Data Contract yet. Engineering first needs to produce the real tables and profiling evidence that Governance will govern in Step 3.

## Load the shared environment

Run `01_governance` from the top so it loads:

```python
%run 00_env_config
```

## Create the Data Stewards

Use the Data Steward widget to create the producer and consumer steward records required by the demo.

![Steward](../assets/01/Steward.png)

The important outcome is not the widget itself. FabricOps persists the steward metadata into the Governance schema of the metadata Lakehouse.

## Create the Data Agreement

Use the Data Agreement widget to create the relationship between the accountable producer and consumer stewards.

Capture the purpose, scope, permitted use, validity, supporting information, and other governance context required by your organisation.

![Agreement](../assets/01/Agreement.png)

## See what FabricOps actually recorded

With the metadata Lakehouse attached, query the Governance tables directly so the demo makes the persistence model visible:

```python
stewards_df = spark.sql("SELECT * FROM governance.METADATA_DATA_STEWARD")
agreements_df = spark.sql("SELECT * FROM governance.METADATA_DATA_AGREEMENT")

display(stewards_df)
display(agreements_df)
```

You should be able to identify the records you just created. This is the first important FabricOps idea: the widgets are authoring interfaces, while the governed state is persisted as ordinary Lakehouse metadata that can be inspected and audited.

## Stop here

At the end of Step 1 you should have:

- producer and consumer Data Steward records,
- one Data Agreement between them,
- visible persisted rows in the Governance metadata tables,
- no table-specific Data Contract yet.

That is intentional. Step 2 now lets Engineering create the real physical tables and technical evidence.

**Next:** [Step 2. Build and run the ETL](02-run-pipeline.md)
