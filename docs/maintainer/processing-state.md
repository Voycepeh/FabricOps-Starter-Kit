# Set up Processing State

FabricOps stores source observations, incremental checkpoints, Source Drift baselines, and publication receipts in the operational Delta table `misc.PROCESSING_STATE` in the configured Metadata Lakehouse. Workspaces that share this Lakehouse use the same Delta store. Grant pipeline identities read and write access to `misc.PROCESSING_STATE` through the Lakehouse’s OneLake roles.

## Initialize the store

Run `00_env_config` directly as the Lakehouse owner with `INITIALIZE_METADATA = True`. Bootstrap creates `misc.PROCESSING_STATE` alongside the canonical metadata tables. A repeat bootstrap validates the schema and Serializable isolation and preserves existing rows. Configuration loads from `setup_notebook()` skip bootstrap.

## Switch an existing installation

Pause and drain all pipelines sharing the Lakehouse before switching runtimes. The new store starts with empty Processing State, so prior checkpoints, baselines, and publication receipts are unavailable to the upgraded runtime. FabricOps evaluates new observations against the state it captures after the switch. An incremental `append_all` to a populated target without a checkpoint is blocked. For that workload, use a new or empty target to bootstrap a fresh checkpoint. Finish any in-flight publication recovery on the prior runtime before switching.

## Verify cross-workspace writes in Fabric

Use an isolated Fabric Lakehouse and two Engineering workspaces with the intended table permissions. Run overlapping publications to different targets and verify that both workspaces retain their distinct records. Retry a publication interrupted after a target write and verify that FabricOps acknowledges the existing write. Confirm that Fabric exposes `misc.PROCESSING_STATE` in the Lakehouse table inventory.
