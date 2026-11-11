# Step 4. Preview and enforce frozen Data Contracts

Set `PIPELINE_MODE = "Dry Run"` to preview real reads and transformations without writing target data or operational state. In the setup interface, optionally choose an exact frozen Data Contract for each relevant table before the first Read. Expand a selection to inspect Schema, Data Quality (including managed Grain), Freshness and Sensitive Data rules. Configure optional Source Drift independently in `setup_pipeline()`.

Run **Read → Transform → Write → Finalize**. Dry Run returns validation, profiling, processing and inspection outputs, marks publication as skipped, and returns a session-only `dry_run_completed` summary when the whole workflow succeeds. It does not register a new pipeline, update a target, advance a checkpoint, persist a profile, record lineage or write pipeline-run metadata.

To execute with enforcement, activate the required contract versions for this pipeline and environment through Governance, then set `PIPELINE_MODE = "Governed"`. Governed setup rejects missing, mismatched or inactive authority. Runtime checks revalidate the pinned activation so metadata changes after setup cannot bypass governance.

`PIPELINE_MODE = "Ungoverned"` deliberately skips contract-dependent checks. It still runs operational validation, profiling, lineage and mandatory safety boundaries, and it refuses to write any table that is already governed in the current environment.

After all Reads, transformations and Writes, run `pipeline_result = finalize_pipeline(pipeline)`. A successful cell or Write alone never establishes completion; stopped or failed runs remain incomplete. See [execution boundaries](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/templates/notebooks/README.md#source-participation-and-execution-boundaries).

For 02A, select the exact frozen **orders.csv — Bronze / demo — File** contract in Setup Pipeline's Dry Run controls, alongside Products, Order History and both target contracts. Orders is a file source with a Source ID; there is no Bronze Orders table to register, profile or activate. Match the CSV reader settings from 02A when authoring. A changed path, location or reader option cannot reuse a different frozen or approved source configuration.

File Freshness supports metadata from the declared selection or a configured timestamp column. Metadata uses every selected data file and the oldest member modification time; missing or unsupported membership evidence remains explicitly unavailable. Column-based aggregation scans the loaded DataFrame and is never described as metadata-only. Both methods retain approved thresholds, scopes and Warn/Block policy. Files support Full Read only. Local and mocked tests do not satisfy the separate signed-in Fabric Governed-release acceptance gate.
