# Read & Write Modes

Read Mode and Write Mode define the two sides of governed pipeline processing:

- **Read Mode** answers: *how much source data should this run process?*
- **Write Mode** answers: *how should the prepared data change the target?*

They are configured independently per source and target, which lets one `02_pipeline` mix different processing patterns.

## Where this appears in the pipeline

```text
Source
→ orchestrate_read(... read_mode=...)
→ PySpark transformation
→ orchestrate_write(... write_mode=...)
→ Target
```

The standard choices are:

| Side | Options |
| --- | --- |
| **Read Mode** | Full, Incremental |
| **Write Mode** | Overwrite, Append All, Append New Only, SCD1, SCD2 |

## Common combinations

| Read → Load | Typical use |
| --- | --- |
| **Full → Overwrite** | Rebuild the complete target from the complete source. |
| **Full / Incremental → Append All** | Append every incoming row, including identical duplicates. |
| **Full / Incremental → Append New Only** | Append hashes not already present in the target. |
| **Full / Incremental → SCD1** | Maintain the latest state for each business key. |
| **Full / Incremental → SCD2** | Maintain historical versions for each business key. |

---

# Read Modes

## Full

??? example "Full — example and behavior"

    ### What it does

    `read_mode="full"` reads the complete governed source.

    ### When to use it

    Use Full when the complete source is required for the transformation, the source is small enough to reread, or the target strategy intentionally rebuilds/merges from complete state.

    ### Example

    Source `orders`:

    | order_id | modified_datetime | status |
    | --- | --- | --- |
    | O001 | 2026-09-01 09:00 | New |
    | O002 | 2026-09-02 10:00 | Shipped |
    | O003 | 2026-09-03 11:00 | Delivered |

    ```python
    orders = orchestrate_read(
        store="Bronze",
        schema="demo",
        table_name="orders",
        read_mode="full",
    )
    ```

    Returned DataFrame:

    | order_id | modified_datetime | status |
    | --- | --- | --- |
    | O001 | 2026-09-01 09:00 | New |
    | O002 | 2026-09-02 10:00 | Shipped |
    | O003 | 2026-09-03 11:00 | Delivered |

    All three rows are in scope.

    **Try it:** [Guided Demo — Full Read → Overwrite](../guided-demo/02-build-and-run-etl.md)

## Incremental

??? example "Incremental — example, bootstrap, and progress"

    ### What it does

    `read_mode="incremental"` resolves work not yet committed for the **exact source-to-target relationship**.

    A `target_table_id` is required because two targets can consume the same source to different points.

    ### When to use it

    Use Incremental when only rows after the last successfully committed watermark should be processed instead of rereading the complete source every run. The governed processing definition must provide `watermark_column`, or `effective_column` where SCD2 processing already uses it as the watermark.

    ### Watermark example

    Assume the target has successfully consumed source changes through:

    ```text
    modified_datetime = 2026-09-02 10:00
    ```

    Current source:

    | order_id | modified_datetime | status |
    | --- | --- | --- |
    | O001 | 2026-09-01 09:00 | New |
    | O002 | 2026-09-02 10:00 | Shipped |
    | O003 | 2026-09-03 11:00 | Delivered |
    | O004 | 2026-09-04 12:00 | New |

    An Incremental read returns only unconsumed work:

    | order_id | modified_datetime | status | Why |
    | --- | --- | --- | --- |
    | O003 | 2026-09-03 11:00 | Delivered | After committed watermark. |
    | O004 | 2026-09-04 12:00 | New | After committed watermark. |

    ```python
    orders = orchestrate_read(
        store="Bronze",
        schema="demo",
        table_name="orders",
        read_mode="incremental",
        target_table_id=TARGET_TABLE_ID,
    )
    ```

    ### First run

    If no committed source-to-target baseline exists, FabricOps performs a **full bootstrap read**.

    Using the same four-row source, the first Incremental run therefore returns O001–O004. The target Write Mode determines whether that bootstrap can be published safely.

    ### Progress is committed after successful publication

    Reading data does **not** advance the accepted watermark.

    ```text
    Observe source
    → resolve incremental scope
    → read scope
    → transform
    → governed write succeeds
    → commit accepted Source Observation
    ```

    If the pipeline fails before publication, the unconsumed source work remains eligible for the next run.

    ### Notes

    - Lakehouse incremental scope is applied to the Spark DataFrame.
    - Warehouse incremental scope is pushed down using FabricOps-owned SQL.
    - Caller-owned Warehouse `query` SQL cannot be combined with Incremental mode because FabricOps owns the incremental predicate.
    - `has_data` / `should_process` indicate whether the resolved scope contains work.

    **Try it:** [Guided Demo — Incremental → Append](../guided-demo/02B-build-and-run-incremental-append-etl.md)

---

# Write Modes

## Overwrite

??? example "Overwrite — before and after"

    ### What it does

    `write_mode="overwrite"` replaces the entire target with the prepared DataFrame. Every new full execution performs the replacement, including identical content. Incoming duplicates are retained; FabricOps does not convert this operation into MERGE.

    ### When to use it

    Use it when the incoming DataFrame represents the complete authoritative state.

    ### Example

    Existing target:

    | order_id | status |
    | --- | --- |
    | O001 | New |
    | O002 | Shipped |

    Prepared DataFrame:

    | order_id | status |
    | --- | --- |
    | O001 | Delivered |
    | O003 | New |

    After Overwrite:

    | order_id | status |
    | --- | --- |
    | O001 | Delivered |
    | O003 | New |

    O002 disappears because the prepared DataFrame becomes the complete target state.

    A partial Incremental input cannot use whole-table Overwrite. FabricOps rejects that combination because unaffected target rows would otherwise be lost.

---

## Append All

`write_mode="append_all"` appends every incoming record, including identical duplicates. A new Full Read execution appends the complete incoming data again. Publication receipts protect retries of the same publication; they do not turn a new full run into a content no-op.

The first Incremental Read bootstraps the complete source. Append All requires a new or empty target if that relationship has no accepted checkpoint, preserving existing bootstrap safety.

## Append New Only

`write_mode="append_new_only"` compares incoming `_row_hash` values with hashes already published in the target. It collapses identical incoming hashes and appends only unseen hashes using a distributed Spark anti-join. No business key or extra Data Contract setting is required.

A changed Job ID, timestamp or other included value produces a new hash and an additional row. It does not update an old row or infer a deletion. Full Read compares the complete incoming scope; Incremental Read compares only the selected scope.

For a target containing `A` and incoming rows `A, A, B`:

| Strategy | Target after the write |
| --- | --- |
| Overwrite | `A, A, B` |
| Append All | `A, A, A, B` |
| Append New Only | `A, B` |

---

## SCD1

??? example "SCD1 — keep the latest mapping"

    ### What it does

    `load_strategy="scd1"` keeps **one current row per governed business key**.

    Matching keys are updated in place; new keys are inserted.

    ### Required parameters

    ```yaml
    load_strategy: scd1
    key_columns:
      - product_id
    ```

    ### When to use it

    Use SCD1 when a mapping or master table should represent the **latest truth** and historical mappings are not required.

    ### Example

    Day 1 mapping snapshot:

    | product_id | category |
    | --- | --- |
    | P001 | Laptop |
    | P002 | Monitor |

    Day 2 mapping snapshot:

    | product_id | category |
    | --- | --- |
    | P001 | Computing |
    | P002 | Monitor |
    | P003 | Accessories |

    After SCD1:

    | product_id | category | What happened |
    | --- | --- | --- |
    | P001 | Computing | Existing P001 updated. |
    | P002 | Monitor | Existing value unchanged. |
    | P003 | Accessories | New product inserted. |

    There is still one row per product. The old `P001 → Laptop` mapping is no longer stored.

    **Try it:** [Guided Demo — SCD Type 1 vs Type 2](../guided-demo/02C-build-and-run-scd-etl.md)

---

## SCD2

??? example "SCD2 — preserve mapping history"

    ### What it does

    `load_strategy="scd2"` keeps historical versions when governed values change.

    ### Required parameters

    ```yaml
    load_strategy: scd2
    key_columns:
      - product_id
    effective_column: modified_datetime
    tracked_columns:
      - category
    ```

    `key_columns` and `effective_column` are required. `tracked_columns` is optional.

    FabricOps maintains:

    - `_effective_from`
    - `_effective_to`
    - `_is_current`

    ### When to use it

    Use SCD2 when consumers need the current mapping **and** the mapping that was valid historically.

    ### Example

    Day 1 mapping snapshot:

    | product_id | category | modified_datetime |
    | --- | --- | --- |
    | P001 | Laptop | 2026-10-06 09:00 |
    | P002 | Monitor | 2026-10-06 09:00 |

    Day 2 mapping snapshot:

    | product_id | category | modified_datetime |
    | --- | --- | --- |
    | P001 | Computing | 2026-10-07 09:00 |
    | P002 | Monitor | 2026-10-07 09:00 |
    | P003 | Accessories | 2026-10-07 09:00 |

    After SCD2:

    | product_id | category | _effective_to | _is_current | What happened |
    | --- | --- | --- | --- | --- |
    | P001 | Laptop | 2026-10-07 09:00 | false | Previous mapping closed. |
    | P001 | Computing | null | true | New current mapping inserted. |
    | P002 | Monitor | null | true | Mapping unchanged. |
    | P003 | Accessories | null | true | New product inserted. |

    **Try it:** [Guided Demo — SCD Type 1 vs Type 2](../guided-demo/02C-build-and-run-scd-etl.md)

---

# Choosing the combination

The two settings should be reasoned about separately.

For example, **Incremental does not automatically mean an append strategy**. If changed rows can arrive for existing business keys, Incremental + SCD1 or Incremental + SCD2 may be the correct target behavior.

Likewise, Full does not automatically mean Overwrite. A Full source can still feed an SCD merge when the target needs keyed current-state or history semantics.

## Safety rules worth remembering

- Incremental requires a target identity because progress is source-to-target specific.
- Incremental requires a governed `watermark_column`, or the SCD2 `effective_column` fallback.
- A missing Incremental baseline bootstraps with a Full read.
- Incremental + whole-table Overwrite is rejected.
- Incremental + Append All bootstrap requires a new/empty target when no accepted baseline exists.
- SCD1 requires `key_columns`.
- SCD2 requires `key_columns` and `effective_column`.
- Multiple `orchestrate_write()` calls publish independently; they are not one atomic transaction.

## Mandatory row hashes

Every managed pipeline output row contains a lowercase, 64-character SHA256 `_row_hash`. Hash contract v1 covers values **after transformations and Sensitive Data treatment**. New/replaced rows hash final incoming values; matched SCD rows hash their resulting stored values, including retained effective times and refreshed ingestion fields. All incoming data columns participate, including source Job IDs, `loaded_at`, `pipeline_run_id` and ingestion timestamps.

The excluded fields are `_row_hash`, the FabricOps audit fields `_committed_at`, `_committed_by`, `_activity_id`, `_workspace_id`, `_notebook_id`, `_notebook_name`, SCD2 lifecycle fields `_effective_from`, `_effective_to`, `_is_current`, and reserved generated `_fabricops_*` / `_dq_*` fields. Supplied row hashes are recalculated.

Column and nested struct names are sorted; map entries are sorted recursively; array order remains significant. The versioned schema includes column names and logical types. Serialization uses Spark JSON with explicit null fields, UTC timestamps at microsecond precision, and wall-clock `timestamp_ntz` values. Null, empty values and absent fields differ; schema nullability annotations do not change a value's logical type.

An existing target without `_row_hash`, or with missing/invalid historical hashes, fails explicitly before non-overwrite publication. Non-overwrite publication requires valid hashes for every existing row; failed validation preserves the target. A complete overwrite is a separate explicit publication choice requiring reviewed complete input and matching Contract authority. Accepted checkpoints and publication receipts must remain consistent with the target. New writes use one of the five explicit strategies. Historical receipts and Run facts retain their recorded names for verification. Existing SCD key, tracked-column and ingestion-field rules still decide updates and new versions; a changed hash alone does not create SCD2 history. Retained effective values and refreshed technical values participate in the resulting stored-row hash.

## Full Source Observation

Configure this independently of each Read Mode near pipeline setup:

```python
pipeline = setup_pipeline(
    pipeline_mode="Ungoverned",
    observe_source=False,       # True requests observation in this execution.
    source_observation_days=7,   # None disables automatic observation.
)
```

When due, the next Read observes the **entire configured physical source**, ignoring incremental SQL predicates and custom query filters for observation. A complete physical Read is reused where available. The processing DataFrame keeps its normal full or incremental scope.

The result is exposed as `read_result["full_source_observation"]` and reports first observation, changed, unchanged or skipped. It compares with the previous successfully accepted full observation for this pipeline and source. Disappearing hashes change the fingerprint but never authorize row deletion or SCD expiration. A changed fingerprint does not add a blocking policy; existing explicitly configured Source Drift policies still apply.

`METADATA_PROCESSING_STATE` stores captured `source_observation` rows and publication-bound `full_source_baseline` records. A failed or nonpublishing/no-op Write does not accept a newer full baseline or consume its interval. Exact recovery accepts the original publication's source records. Full observation scans and hashes the source, so choose its interval to match source size and operational needs.

## Retry and concurrency boundaries

The existing Serializable Pipeline Registry target lease excludes concurrent managed writers, including physical aliases, until finalization. A competing attempt fails before comparing/publishing a target snapshot. A crashed lease requires reconciliation; do not bypass it with an independent writer.

Publication receipts and physical target markers protect interrupted publication and metadata recovery. Completed new Full Read runs with Overwrite or Append All execute again. Whole-table Overwrite remains prohibited for incremental input. SCD1 and SCD2 retain key-based semantics and do not delete or expire missing keys solely from source absence.

Lakehouse verification uses Delta commit receipts. Warehouse verification uses the exact count of rows carrying the publication audit marker. Empty Warehouse publication fails closed when no durable row marker can prove it; inspect the target before retrying. Append New Only with no unseen hashes returns an explicit nonpublishing no-op.

## Contract and metadata lifecycle

The notebook-facing setting is `write_mode`. FabricOps resolves that public Write Mode to the governed `load_strategy` stored in processing metadata and applied by the internal physical Write stage within `orchestrate_write()`.

The applicable Data Contract remains authoritative for governed processing. Development can propose processing settings; selected/frozen contract validation governs Development, and the active approved contract governs Production.

After successful publication, FabricOps persists the resolved target processing definition and commits Lineage plus accepted Source Observation state. This keeps future Incremental scope aligned with data that was actually published.

## Related documentation

- [Plug-and-Play pipelines and orchestration](../engineering.md#plug-and-play-pipelines-and-orchestration)
- [`orchestrate_read()`](../api/reference/orchestrate_read.md)
- [`orchestrate_write()`](../api/reference/orchestrate_write.md)
- [Guided Demo: Full Read Pipeline](../guided-demo/02-build-and-run-etl.md)
- [Guided Demo: Incremental → Append](../guided-demo/02B-build-and-run-incremental-append-etl.md)
- [Guided Demo: SCD Type 1 vs Type 2](../guided-demo/02C-build-and-run-scd-etl.md)
