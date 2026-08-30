# Unit 5: Choose processing behaviour and review results

**Configure how much source data the template should process, then review what the completed run produced.**

## Choose a source processing strategy

FabricOps separates the configured source strategy from the runtime read mode and from the target write strategy.

| Source strategy | Meaning | Typical use |
| --- | --- | --- |
| `full_dataset` | Read the complete source each run. | Small files and reference data. |
| `incremental_watermark` | Read rows newer than the last successfully committed checkpoint. | Transactional sources with a reliable unique increasing value. |
| `incremental_partition` | Read whole logical buckets that are new or changed. | Daily, monthly, snapshot, or history data. |

The runtime can then resolve to `skip`, `full_dataset`, or `incremental_subset` depending on what the current execution needs.

## Watermark processing

For a Warehouse source using `modified_datetime`, a successful checkpoint at `2026-08-26 10:00` and a captured upper watermark of `2026-08-26 12:00` produces this bounded range:

```text
modified_datetime > 2026-08-26 10:00
AND modified_datetime <= 2026-08-26 12:00
```

The interval is `(lower_bound, upper_bound]`. The checkpoint advances only after the target write succeeds.

!!! warning "Use a safe watermark"

    The watermark must be non-null and globally unique for each source row as well as increasing. If the source cannot guarantee that, prefer partition processing.

## Partition processing

For a snapshot source configured on `snapshot_date`:

```text
25 Aug → unchanged
26 Aug → changed
27 Aug → new
```

FabricOps prepares the complete 26 Aug and 27 Aug buckets. This is a strong fit for historical corrections and data that naturally arrives by date, month, snapshot, or batch.

| Situation | Recommended strategy |
| --- | --- |
| Small or reference data | `full_dataset` |
| Transactional source with a reliable unique increasing ID | `incremental_watermark` |
| Large fact/history table with natural logical partitions | `incremental_partition` |
| Daily, monthly, or snapshot delivery | `incremental_partition` |
| Historical periods can be corrected | `incremental_partition` |

## Keep canonical profiles complete

A complete `full_dataset` DataFrame may refresh the canonical registered source profile. An `incremental_subset` can be profiled diagnostically, but it should not replace the profile of the complete physical source.

## Review the completed run

After the baseline pipeline succeeds, confirm that the target exists and that the expected metadata was written. Depending on the path exercised, this includes `METADATA_DATA_CATALOGUE`, `METADATA_DATA_PROFILED`, `METADATA_DATA_PROFILED_FREQUENCY`, and `METADATA_DATA_LINEAGE` records.

Those concrete metadata records are the handoff to Governance in Step 3.

!!! important "What happens next"

    Do not add Guardrail checks manually to this module. Step 3 reads `METADATA_DATA_CATALOGUE` and `METADATA_DATA_PROFILED`, then writes `METADATA_ENRICHMENT` and `METADATA_GUARDRAIL`. Step 4 returns to the same `02_pipeline`, evaluates those Guardrails, and writes `METADATA_GUARDRAIL_RESULTS` plus `METADATA_GUARDRAIL_ROW_RESULTS` where row-level failures are recorded. Step 5 freezes approved expectations into a Data Contract, and Step 6 runs Production against the active contract.

For exact APIs such as `read_pipeline_prep()`, `check_changes()`, `write_pipeline_prep()`, and `commit_pipeline_checkpoint()`, use the [Function Reference](../../reference/index.md). The template is the normal learning-path entry point.

**Previous:** [Unit 4: Transform and load](transform-and-load.md)  
**Next:** [Step 3: Enrich the Data Catalogue and define Guardrails](../03-enrich-guardrails.md)
