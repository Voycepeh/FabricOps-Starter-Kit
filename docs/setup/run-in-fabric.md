# Setup: Run in Fabric

This page explains how to configure and verify Fabric runtime execution after the FabricOps wheel is ready.

Next read: [Setup / Create Wheel](create-wheel.md), [Quick Start](../quick-start.md), [Workspace Operating Model](../how-fabricops-works/workspace-operating-model.md).

## Install and configure

1. Upload/install the package wheel in the target Fabric Environment.
2. Attach the Environment to copied `00_env_config`, `01_da`, `02_ex`, `03_pc`, and `04_gov` notebooks.
3. Restart notebook sessions if needed so the installed wheel is available.
4. Configure required runtime values in `00_env_config`.

## Required config checks

- Lakehouse/warehouse targets resolve in the selected environment.
- Metadata target is configured for `metadata` routing.
- Notebook runtime dependencies are available.
- `00_env_config` can create or validate all active metadata tables.

## First-run verification

Run the Fabric smoke-test sequence from the [Quick Start](../quick-start.md):

1. Run `00_env_config`.
2. Run `01_da` to capture agreement, steward, and evidence metadata.
3. Run `02_ex` to demonstrate example source/topic setup and profiling evidence.
4. Run `03_pc` to validate implemented guardrails, write outputs, write profiles, and record lineage.
5. Run `04_gov` to review and commit column context, DQ expectations, and classifications.
6. Rerun `03_pc`.
7. Deliberately test blocking schema and data-change failures.

In v1.0.0, `03_pc` is the production guardrail notebook. `04_gov` does not enforce production rules; reviewed DQ expectations are advisory unless manually implemented inside the relevant `03_pc` notebook.
