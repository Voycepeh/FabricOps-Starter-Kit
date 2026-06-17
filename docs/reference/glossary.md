# Glossary

Concise FabricOps terms used across the docs and notebook templates.

## Profile

Measure source data or pipeline outputs for schema, row counts, nulls, distinct values, and other reusable facts.

## Enrichment

Reviewed descriptive metadata such as business meaning, ownership, sensitivity, classification, and usage context.

## Guardrails

Approved checks that evaluate schema, freshness, profile behavior, or data quality expectations during a pipeline run.

## Enforcement

Running active guardrails and deciding whether the pipeline can continue, continue with warnings, or stop.

## Metadata lakehouse

The configured `metadata` target from `00_env_config` where FabricOps stores agreements, profiles, enrichment records, guardrail rules, guardrail results, lineage, and run summaries.

## Source data

Data read from configured upstream Lakehouse or Warehouse targets before transformation.

## Pipeline output

A DataFrame or table produced by `02_pipeline` after transformation and checked before publishing.

## Target DataFrame

The in-memory Spark DataFrame produced by the pipeline before it is written as an output table.

## Target table

The physical Lakehouse or Warehouse table written from a target DataFrame after blocking guardrails pass.

## Profile mode

The configured profile behavior mode used by profile guardrails: `static_data`, `changing_data`, or `skip`.

## static_data

Profile mode for data that should remain stable compared with the accepted baseline.

## changing_data

Profile mode for data that changes by watermark value and should be compared by watermark group.

## skip

Profile mode that records the profile without enforcing profile behavior.

## can_continue

Boolean outcome that tells a notebook whether the next critical step may run after guardrail evaluation.
