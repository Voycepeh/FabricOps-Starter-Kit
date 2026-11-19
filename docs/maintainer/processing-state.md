# Set up Processing State

FabricOps stores source observations, incremental checkpoints, Source Drift baselines, and publication receipts in a private Delta table at `Files/fabricops/misc/processing_state` in the configured Metadata Lakehouse. Workspaces that share this Lakehouse use the same Delta store. Grant pipeline identities read and write access to this folder and its Delta log through the Lakehouse's OneLake roles.

## Initialize the store

Run `00_env_config` directly as the Lakehouse owner with `INITIALIZE_PROCESSING_STATE = True`. This calls `setup_processing_state(config=CONFIG, workspace_id=WORKSPACE_ID)`. The first run creates an empty Delta store. Later runs validate its schema and Serializable isolation and preserve its rows. Restore the setting to `False` for routine configuration runs.

## Switch an existing installation

Pause and drain all pipelines sharing the Lakehouse before switching runtimes. The new store starts with empty Processing State, so prior checkpoints, baselines, and publication receipts are unavailable to the upgraded runtime. FabricOps evaluates new observations against the state it captures after the switch. An incremental append to a populated target without a checkpoint is blocked. For that workload, use a new or empty target to bootstrap a fresh checkpoint. Finish any in-flight publication recovery on the prior runtime before switching.

## Verify cross-workspace writes in Fabric

Use an isolated Fabric Lakehouse and two Engineering workspaces with the intended folder permissions. Run overlapping publications to different targets and verify that both workspaces retain their distinct records. Retry a publication interrupted after a target write and verify that FabricOps acknowledges the existing write. Confirm the Files Delta store is absent from the SQL table inventory.
