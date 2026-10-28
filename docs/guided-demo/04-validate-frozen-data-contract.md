# Step 4. Preview and enforce frozen Data Contracts

Set `PIPELINE_MODE = "Dry Run"` to preview real reads and transformations without writing target data or operational state. In the setup interface, optionally choose an exact frozen Data Contract for each relevant table before the first Read. Expand a selection to inspect Schema, Grain, Data Quality, Freshness, Source Drift and Sensitive Data rules.

Run **Read → Transform → Write → Finalize**. Dry Run returns validation, profiling, processing and inspection outputs, marks publication as skipped, and returns a session-only `dry_run_completed` summary when the whole workflow succeeds. It does not register a new pipeline, update a target, advance a checkpoint, persist a profile, record lineage or write pipeline-run metadata.

To execute with enforcement, activate the required contract versions for this pipeline and environment through Governance, then set `PIPELINE_MODE = "Governed"`. Governed setup rejects missing, mismatched or inactive authority. Runtime checks revalidate the pinned activation so metadata changes after setup cannot bypass governance.

`PIPELINE_MODE = "Ungoverned"` deliberately skips contract-dependent checks. It still runs operational validation, profiling, lineage and mandatory safety boundaries, and it refuses to write any table that is already governed in the current environment.

After all Reads, transformations and Writes, run `pipeline_result = finalize_pipeline(pipeline)`. A successful cell or Write alone never establishes completion; stopped or failed runs remain incomplete. See [execution boundaries](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/templates/notebooks/README.md#source-participation-and-execution-boundaries).
