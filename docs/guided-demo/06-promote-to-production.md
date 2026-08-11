# Step 6: Promote the validated pipeline to Production

**Promote the validated `02_pipeline` into Engineering Production only after Step 5 has completed the Data Contract and Governance sign-off.**

Engineering Production owns stable recurring execution and durable Production outputs.

## Before you begin

Confirm that:

- the Step 5 Data Contract is complete
- Governance sign-off is recorded
- the Development `02_pipeline` has passed its required Guardrails

## What to do

1. Copy or deploy the validated `02_pipeline` from Engineering Development to Engineering Production using your team's normal Fabric promotion process.
2. Confirm the promoted notebook uses the Production `00_env_config`.
3. Confirm Production source, unified, and product targets resolve correctly.
4. Run or schedule the promoted pipeline according to the required operational cadence.
5. Confirm downstream AI, BI, and other consumers use the approved Production outputs with the appropriate access controls.

!!! important "Production rule"

    Do not treat the Development notebook or Development outputs as the durable Production workflow. The promoted `02_pipeline` should run against Production configuration and remain tied to the approved Data Contract.

## Expected result

You should now have:

- the validated `02_pipeline` in Engineering Production
- Production configuration and targets in use
- durable Production outputs
- runtime metadata still connected to the approved governance context

**Previous:** [Step 5: Create the Data Contract and prepare for promotion](05-create-data-contract.md)  
**Next:** [Step 7: Consume approved Production data](99-explore-via-notebook.md)

See also: [How FabricOps Works](../how-fabricops-works.md) and [Notebook Templates](../notebook-templates.md).
