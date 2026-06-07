# Setup: Run in Fabric

This page explains: how to configure and verify Fabric runtime execution.
Use this when: your wheel is ready and you need environment/library setup plus first-run checks.
Next read: [Setup / Create Wheel](create-wheel.md), [Start](../quick-start.md), [How FabricOps Works](../how-fabricops-works/).

## Install and configure

1. Upload/install the package wheel in the target Fabric workspace environment.
2. Attach required libraries and restart session if needed.
3. Configure required runtime values in `00_env_config`.

## Required config checks

- Lakehouse/warehouse targets resolve in the selected environment.
- Metadata target is configured for `metadata` routing.
- Notebook runtime dependencies are available.

## First-run verification

- Run `00_env_config` and confirm validation output.
- Execute a minimal `01_agreement` → `02_pipeline` → `03_review` path to verify end-to-end metadata writes. Use `99_explore` only when optional discovery or troubleshooting is needed.
