# FabricOps glossary

Simple definitions for repeated FabricOps terms used across generated callable references and workflow documentation.

## accepted catalogue profile evidence

**Plain language:** The approved profile record that FabricOps treats as the trusted baseline for a table.

**Technical:** Reviewed catalogue profile metadata stored in the configured metadata target and used by guardrails to compare current runtime behavior with accepted evidence.

**Example:** A governance reviewer accepts a target table profile, and later pipeline runs compare new profiles against that accepted record.

**Related terms:** `baseline profile`, `catalogue evidence`, `metadata lakehouse`

## append

**Plain language:** Add new rows to an existing target without replacing existing rows.

**Technical:** A physical Spark write mode, not a FabricOps profile behavior mode.

**Example:** Use append as a write mode when new pipeline output should be added to the target table.

**Related terms:** `overwrite`, `profile behavior`

## baseline profile

**Plain language:** The previous approved profile used as the comparison point.

**Technical:** The accepted profile row selected for the same dataset, table, and stage before evaluating current pipeline behavior.

**Example:** The target table profile accepted last week becomes the baseline for today's target guardrail check.

**Related terms:** `accepted catalogue profile evidence`, `profile behavior check`

## can_continue

**Plain language:** A returned true/false value that tells downstream code whether the pipeline should keep running.

**Technical:** Boolean field in guardrail result dictionaries that is false when blocking checks should stop downstream work.

**Example:** If can_continue is false, call stop_if_failed before writing the table.

**Related terms:** `guardrail`

## catalogue evidence

**Plain language:** Reviewed metadata that explains what FabricOps knows about a dataset or table.

**Technical:** Governed records such as profile, column context, classification, DQ rule, or lineage evidence stored for review and enforcement workflows.

**Example:** A governance review records catalogue evidence that later pipeline guardrails can read.

**Related terms:** `accepted catalogue profile evidence`, `metadata lakehouse`

## changing_data

**Plain language:** New groups may arrive, but previously seen groups should not change or disappear.

**Technical:** Profile behavior mode that groups current data by watermark_column and compares each previous watermark value with accepted catalogue evidence.

**Example:** A table partitioned by business date uses changing_data to allow new dates while protecting prior dates.

**Related terms:** `profile behavior`, `static_data`, `skip`

## guardrail

**Plain language:** A check that tells the notebook whether it is safe to continue.

**Technical:** A validation result with status and continuation fields used before downstream writes or metadata recording.

**Example:** A freshness guardrail can stop a pipeline before stale data is written.

**Related terms:** `can_continue`, `profile behavior check`

## metadata lakehouse

**Plain language:** The configured Fabric lakehouse where FabricOps stores governance and runtime metadata.

**Technical:** The metadata target resolved from 00_env_config and used for FabricOps metadata tables instead of relying on a default attached lakehouse.

**Example:** Profile evidence and DQ approvals are read from the metadata lakehouse configured for the selected environment.

**Related terms:** `accepted catalogue profile evidence`, `catalogue evidence`

## notebook template

**Plain language:** A starter notebook that shows where and how FabricOps helpers are used.

**Technical:** A reusable Fabric notebook under templates/notebooks that demonstrates environment setup, agreement, pipeline, governance, or exploration workflows.

**Example:** 02_pipeline is the notebook template for production-style guardrails, lineage, and writes.

**Related terms:** `guardrail`, `stage`

## overwrite

**Plain language:** Replace existing target data during a physical write.

**Technical:** A physical Spark write mode, not a FabricOps profile behavior mode.

**Example:** Use overwrite as a write mode when the target table should be replaced by the latest output.

**Related terms:** `append`, `profile behavior`

## profile behavior

**Plain language:** The expected way a table profile should behave over time.

**Technical:** The approved profile mode used by guardrail checks: static_data, changing_data, or skip.

**Example:** A changing-data table may add a new business-date group while previous groups remain unchanged.

**Related terms:** `static_data`, `changing_data`, `skip`, `profile behavior check`

## profile behavior check

**Plain language:** A check that confirms the current table load pattern still matches the approved pattern.

**Technical:** A guardrail comparison between current profile_mode evidence and accepted catalogue profile evidence.

**Example:** A changing_data table fails if a previously accepted watermark group changes or disappears.

**Related terms:** `profile behavior`, `guardrail`, `can_continue`

## skip

**Plain language:** Do not run that behavior check or write step for the table.

**Technical:** A configured behavior value that tells FabricOps to bypass a specific profile behavior enforcement path.

**Example:** A table can be marked skip while it is being onboarded and is not ready for enforcement.

**Related terms:** `profile behavior`, `static_data`, `changing_data`

## source table

**Plain language:** An input table or file read by the pipeline.

**Technical:** A configured upstream dataset entry processed before transformation and target writes.

**Example:** The pipeline reads source tables before applying transformation logic.

**Related terms:** `stage`, `target table`

## stage

**Plain language:** The part of the pipeline being checked, such as source or target.

**Technical:** A table-processing phase recorded with profile or guardrail evidence so FabricOps compares like-for-like evidence.

**Example:** Source guardrails run before transformation, while target guardrails run before writes.

**Related terms:** `source table`, `target table`

## static_data

**Plain language:** The full table should keep the same profile unless governance accepts a change.

**Technical:** Profile behavior mode that compares one full-table profile group with watermark_value=__FULL_TABLE__.

**Example:** A reference table uses static_data when row count, schema, and profile hash should remain stable.

**Related terms:** `profile behavior`, `changing_data`, `skip`

## target table

**Plain language:** An output table written by the pipeline.

**Technical:** A configured downstream dataset entry validated before write helpers persist the transformed output.

**Example:** Target guardrails run before the target table is written.

**Related terms:** `stage`, `source table`
