# `01_governance`: establish and manage Governance

**Use `01_governance` as the persistent Governance notebook for the complete lifecycle: establish steward and agreement context, return after Engineering creates catalogue/profile evidence, author and freeze the Data Contract, then return again after Development validation to activate the tested version.**

The notebook is deliberately reused. FabricOps does not require separate Governance notebooks for agreement creation, contract authoring, freezing, and activation.

## 1. Load the configured environment

Attach the Fabric Environment containing FabricOps, then run the notebook from the top.

`01_governance` starts with:

```python
%run 00_env_config
```

This gives the Governance notebook the same configured metadata target and reusable Fabric context as the engineering notebooks.

## 2. Create the Data Stewards

Run the Data Steward widget and create or update the accountable parties required by the demo.

![Steward](../assets/01/Steward.png)

For the supplied agreement flow, create the active producer and consumer steward records before creating the agreement.

## 3. Create the Data Agreement

Run the Data Agreement widget and establish the governed relationship between the accountable stewards.

Record the governance context required by your organisation, such as purpose, scope, ownership, permitted use, validity, and supporting information.

![Agreement](../assets/01/Agreement.png)

At this point the agreement exists, but there is not yet a table-specific contract to activate. Engineering first needs to produce the real governed table and its profiling evidence.

## 4. Move to Engineering Development

Open `02_pipeline` in Engineering Development and run the pipeline against the configured managed sources.

The engineering run establishes the real `table_id` and refreshes the technical evidence Governance needs, including catalogue and profiling context.

Do not create a separate "baseline pipeline" notebook. The current `02_pipeline` is the reusable engineering template used throughout Development and Production.

[Continue with `02_pipeline`](02-run-pipeline.md)

## 5. Return to `01_governance` after the engineering run

After `02_pipeline` has registered and profiled the target, return to the same `01_governance` notebook.

Use its catalogue selection section to choose the governed `table_id` and review the available catalogue/profile evidence for that table.

The selected `table_id` is the identity the Data Contract is authored against.

## 6. Author the Data Contract

Open the unified Data Contract editor for the selected `table_id`.

Use it to define the governed table as one versioned contract:

- **Enrichment** for descriptive table and column metadata and classifications,
- **Guardrails** for enforceable expectations such as Schema, Freshness, Source Drift, Data Quality, and Sensitive Data handling,
- **Processing** for the governed target write strategy and parameters,
- the logical notebook ownership required by the contract.

Review the complete definition before freezing it.

## 7. Freeze the version

Freeze the reviewed draft to create an immutable Data Contract version.

Freezing does not activate the contract and does not promote the pipeline. It creates the version that Engineering Development can explicitly select and validate.

## 8. Validate the frozen version in `02_pipeline`

Return to `02_pipeline` in Engineering Development.

Use the Data Contract selection section to select the frozen version for the governed table, then rerun the same full pipeline. The Read and Write blocks execute the governed checks around the project transformation instead of switching to a separate "guardrail pipeline".

If the definition needs changes, return to `01_governance`, refine the draft, and freeze a new immutable version. Do not edit a frozen version in place.

## 9. Link the tested version and activate it

After the frozen version has been successfully validated in Development, return to `01_governance` again.

Use the activation section to:

1. select the tested contract version,
2. select the exact Data Agreement version it belongs to,
3. review the linkage,
4. activate the contract for Production.

Activation designates the governed version Production should resolve. It does not deploy `02_pipeline` to Production; promotion remains an engineering/deployment responsibility.

## Expected result

By the end of the Governance loop you have:

- active Data Steward context,
- the required Data Agreement,
- a real governed `table_id` backed by engineering catalogue/profile evidence,
- an immutable Data Contract version that was tested in Development,
- that tested version linked to the correct Data Agreement and activated for Production.

**Next:** promote the validated [`02_pipeline`](02-run-pipeline.md#production-run) through your normal Fabric deployment process and run it in Engineering Production.
