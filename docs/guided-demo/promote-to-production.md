# Step 6: Promote the validated pipeline to Production

Promote the validated `02_pipeline` from Engineering Development into the Engineering Production workspace only after the Step 5 Data Contract is signed off.

This step moves the approved, repeatable pipeline into the workspace that owns stable recurring execution and durable Production outputs.

## What to do

1. Confirm Step 5 is complete and the Data Contract has steward sign-off.
2. Copy or deploy the validated `02_pipeline` from Engineering Development to Engineering Production using your team's normal Fabric promotion process.
3. Confirm the Production `02_pipeline` uses the Production `00_env_config` and Production data targets.
4. Run or schedule the promoted pipeline according to the required operational cadence.
5. Confirm downstream AI, BI, or other consumers use the trusted Production outputs, subject to the appropriate access controls.

## Expected evidence

The promoted Production run uses the approved contract context and writes durable Production outputs. Runtime metadata remains routed through the configured metadata target so Production operation stays connected to the signed-off governance evidence.

Previous: [Step 5: Create the Data Contract and record steward sign-off](create-data-contract.md).

You have completed the required Guided Demo workflow. Optional inspection can continue in [Explore Metadata Outputs](explore-metadata-outputs.md).

See also: [How FabricOps Works](../how-fabricops-works.md) and [Notebook Templates](../notebook-templates-implementation-guide/index.md).
