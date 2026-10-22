# Step 4. Evaluate frozen Data Contracts

Set `PIPELINE_MODE = "Test"` and run Setup Pipeline. Review each table's frozen versions or select No Contract in the setup interface before Read. Expand the selected definition to inspect Schema, Grain, Data Quality, Freshness, Source Drift and Sensitive Data rules. Choices lock when execution begins.

Run **Read → Transform → Write**. Test reads real data and evaluates transformations and configured Guardrails. Warn permits continuation; Block remains a diagnostic in Test and prevents Live publication. Empty or inactive optional definitions impose no additional requirement. Guardrail enforcement is independent of statistical profiling.

The report updates automatically. Read and Write results retain `schema_result`, `grain_result`, `dq_result`, `source_drift_results`, `sensitive_result`, publication metrics and dry-run limits where applicable. Advanced `dq_diagnostics="full"` preserves lazy violation inspection when needed.

Test does not publish business data or commit any operational metadata, mappings, checkpoints or activation changes. Results are in memory until the final `finalize_pipeline(CONTRACTS)` cell publishes run and Guardrail results. Overwrite, append, incremental, SCD1 and SCD2 processing retain their input and safety checks, but actual publication permissions and transaction behavior require Live validation.

After all Reads, transformations and Writes, run `pipeline_result = finalize_pipeline(CONTRACTS)`. It publishes `METADATA_GUARDRAIL_RESULTS` and the final `METADATA_PIPELINE_RUN` snapshot. A successful cell or Write alone never establishes completion; stopped runs remain incomplete. Publication requires the configured Metadata store and complete Fabric runtime audit identity.

Only complete successful Testing with exact frozen contracts for every participant can proceed to activation review. Failed, incomplete and No Contract runs cannot authorize Live. See [execution boundaries](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/templates/notebooks/README.md#source-participation-and-execution-boundaries).
