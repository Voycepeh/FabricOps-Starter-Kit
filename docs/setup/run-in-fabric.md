# Setup: Run in Fabric

This page explains: how to configure and verify Fabric runtime execution.
Use this when: your wheel is ready and you need environment/library setup plus first-run checks.
Next read: [Setup / Create Wheel](create-wheel.md), [Guided Demo](../guided-demo.md), [How FabricOps Works](../how-fabricops-works/).

## Install and configure

1. Upload/install the package wheel in the target Fabric workspace environment.
2. Attach required libraries and restart session if needed.
3. Configure required runtime values in `00_env_config`.

## Required config checks

- Lakehouse/warehouse targets resolve in the selected environment.
- Metadata target is configured for `metadata` routing.
- `FABRICOPS_AUDIT_TIMEZONE` is either `UTC` or another valid IANA timezone such as `Asia/Singapore`.
- Notebook runtime dependencies are available.

## First-run verification

- Run `00_env_config` and confirm metadata table validation passes. The active setup registry contains the current 11 Lakehouse Delta metadata tables, including `METADATA_DATA_ACCESS` as an empty optional/manual/offline governance table when it is present in the active schema registry. Metadata setup writes missing tables to the configured `metadata` lakehouse target and does not require a default lakehouse attachment.
- If schema validation reports missing columns, recreate or manually migrate the affected metadata table; setup does not automatically migrate older or malformed schemas. If you inspect the metadata lakehouse catalog manually, run the check against the configured metadata lakehouse target and confirm every active metadata table appears as a registered table.
- Execute a minimal `01_agreement` → `02_pipeline` → `03_governance` path to verify end-to-end metadata writes. Use `99_explore` only when optional discovery or troubleshooting is needed.
