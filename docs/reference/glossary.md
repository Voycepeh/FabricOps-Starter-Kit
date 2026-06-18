# FabricOps glossary

Concise FabricOps terms used across generated callable references and workflow documentation.

## accepted catalogue profile evidence

**Plain language:** Technical baseline term for accepted profile rows used by profile behavior checks.

**Technical:** Technical baseline term for accepted profile rows used by profile behavior checks.

## can_continue

**Plain language:** A returned true/false value that tells downstream code whether the pipeline should keep running.

**Technical:** A returned true/false value that tells downstream code whether the pipeline should keep running.

## catalogue evidence

**Plain language:** Reviewed metadata that explains what FabricOps knows about a dataset or table.

**Technical:** Reviewed metadata that explains what FabricOps knows about a dataset or table.

## changing_data

**Plain language:** Profile mode for data that changes by watermark value and should be compared by watermark group.

**Technical:** Profile mode for data that changes by watermark value and should be compared by watermark group.

## enforcement

**Plain language:** Running active guardrails and deciding whether the pipeline can continue, continue with warnings, or stop.

**Technical:** Running active guardrails and deciding whether the pipeline can continue, continue with warnings, or stop.

## enrichment

**Plain language:** Reviewed descriptive metadata such as business meaning, ownership, sensitivity, classification, and usage context.

**Technical:** Reviewed descriptive metadata such as business meaning, ownership, sensitivity, classification, and usage context.

## guardrail

**Plain language:** A check that tells the notebook whether it is safe to continue.

**Technical:** A check that tells the notebook whether it is safe to continue.

## guardrails

**Plain language:** Approved checks that evaluate schema, freshness, profile behavior, or data quality expectations during a pipeline run.

**Technical:** Approved checks that evaluate schema, freshness, profile behavior, or data quality expectations during a pipeline run.

## metadata lakehouse

**Plain language:** The configured Fabric lakehouse where FabricOps stores governance and runtime metadata.

**Technical:** The configured Fabric lakehouse where FabricOps stores governance and runtime metadata.

## notebook template

**Plain language:** A starter notebook that shows where and how FabricOps helpers are used.

**Technical:** A starter notebook that shows where and how FabricOps helpers are used.

## pipeline output

**Plain language:** A DataFrame or table produced by 02_pipeline after transformation and checked before publishing.

**Technical:** A DataFrame or table produced by 02_pipeline after transformation and checked before publishing.

## profile

**Plain language:** Measure source data or pipeline outputs for schema, row counts, nulls, distinct values, and other reusable facts.

**Technical:** Measure source data or pipeline outputs for schema, row counts, nulls, distinct values, and other reusable facts.

## profile behavior

**Plain language:** The expected way a table profile should behave over time.

**Technical:** The expected way a table profile should behave over time.

## profile mode

**Plain language:** The configured profile behavior mode used by profile guardrails: static_data, changing_data, or skip.

**Technical:** The configured profile behavior mode used by profile guardrails: static_data, changing_data, or skip.

## skip

**Plain language:** Profile mode that records the profile without enforcing profile behavior.

**Technical:** Profile mode that records the profile without enforcing profile behavior.

## source data

**Plain language:** Data read from configured upstream Lakehouse or Warehouse targets before transformation.

**Technical:** Data read from configured upstream Lakehouse or Warehouse targets before transformation.

## source table

**Plain language:** An input table or file read by the pipeline.

**Technical:** An input table or file read by the pipeline.

## stage

**Plain language:** The part of the pipeline being checked, such as source or target.

**Technical:** The part of the pipeline being checked, such as source or target.

## static_data

**Plain language:** Profile mode for data that should remain stable compared with the accepted baseline.

**Technical:** Profile mode for data that should remain stable compared with the accepted baseline.

## target DataFrame

**Plain language:** The in-memory Spark DataFrame produced by the pipeline before it is written as an output table.

**Technical:** The in-memory Spark DataFrame produced by the pipeline before it is written as an output table.

## target table

**Plain language:** An output table written by the pipeline.

**Technical:** An output table written by the pipeline.
