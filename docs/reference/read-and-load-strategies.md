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
→ orchestrate_write(... load_strategy=...)
→ Target
```

The standard choices are:

| Side | Options |
| --- | --- |
| **Read Mode** | Full, Incremental |
| **Write Mode** | Overwrite, Append, SCD1, SCD2 |

## Common combinations

| Read → Load | Typical use |
| --- | --- |
| **Full → Overwrite** | Rebuild the complete target from the complete source. |
| **Incremental → Append** | Process only new source work and append it. |
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

## Incremental

??? example "Incremental — example, bootstrap, and progress"

    ### What it does

    `read_mode="incremental"` resolves work not yet committed for the **exact source-to-target relationship**.

    A `target_table_id` is required because two targets can consume the same source to different points.

    ### When to use it

    Use Incremental when only rows after the last successfully committed watermark should be processed instead of rereading the complete source every run.

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

---

# Write Modes

## Overwrite

??? example "Overwrite — before and after"

    ### What it does

    `load_strategy="overwrite"` publishes the prepared DataFrame as the target state.

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

## Append

??? example "Append — before and after"

    ### What it does

    `load_strategy="append"` adds the prepared rows to the existing target.

    ### When to use it

    Use Append for new immutable/event-like rows where an incoming batch should be added rather than matched against existing business keys.

    ### Example

    Existing target:

    | order_id | status |
    | --- | --- |
    | O001 | New |
    | O002 | Shipped |

    Prepared DataFrame:

    | order_id | status |
    | --- | --- |
    | O003 | Delivered |
    | O004 | New |

    After Append:

    | order_id | status |
    | --- | --- |
    | O001 | New |
    | O002 | Shipped |
    | O003 | Delivered |
    | O004 | New |

    ### Incremental bootstrap safety

    On the first Incremental → Append run, the Read side has no baseline and therefore returns the full source.

    FabricOps allows that bootstrap only when the target is new or empty. If the target is already populated but no committed source-to-target baseline exists, publication fails rather than silently duplicating the source.

---

## SCD1

??? example "SCD1 — update and insert example"

    ### What it does

    `load_strategy="scd1"` keeps **one current row per governed business key**.

    Matching keys are updated in place; new keys are inserted.

    ### Required parameters

    ```yaml
    load_strategy: scd1
    key_columns:
      - customer_id
    ```

    ### When to use it

    Use SCD1 when consumers need the latest state but do not need historical versions.

    ### Example

    Existing target:

    | customer_id | tier | country |
    | --- | --- | --- |
    | C001 | Basic | SG |
    | C002 | Premium | MY |

    Prepared DataFrame:

    | customer_id | tier | country |
    | --- | --- | --- |
    | C001 | Premium | SG |
    | C003 | Basic | AU |

    After SCD1:

    | customer_id | tier | country | What happened |
    | --- | --- | --- | --- |
    | C001 | Premium | SG | Existing C001 updated. |
    | C002 | Premium | MY | Existing key not present in the batch remains. |
    | C003 | Basic | AU | New key inserted. |

    There is no historical Basic version of C001 after the merge.

---

## SCD2

??? example "SCD2 — history example"

    ### What it does

    `load_strategy="scd2"` keeps historical versions when governed values change.

    ### Required parameters

    ```yaml
    load_strategy: scd2
    key_columns:
      - customer_id
    effective_column: modified_datetime
    tracked_columns:
      - tier
      - country
    ```

    `key_columns` and `effective_column` are required. `tracked_columns` is optional.

    FabricOps maintains:

    - `_effective_from`
    - `_effective_to`
    - `_is_current`

    ### When to use it

    Use SCD2 when consumers need both the current state and the history of changes.

    ### Example

    Existing target:

    | customer_id | tier | _effective_from | _effective_to | _is_current |
    | --- | --- | --- | --- | --- |
    | C001 | Basic | 2026-01-01 | null | true |
    | C002 | Premium | 2026-01-01 | null | true |

    Prepared DataFrame:

    | customer_id | tier | modified_datetime |
    | --- | --- | --- |
    | C001 | Premium | 2026-09-15 |
    | C003 | Basic | 2026-09-15 |

    After SCD2:

    | customer_id | tier | _effective_from | _effective_to | _is_current | What happened |
    | --- | --- | --- | --- | --- | --- |
    | C001 | Basic | 2026-01-01 | 2026-09-15 | false | Previous C001 version closed. |
    | C001 | Premium | 2026-09-15 | null | true | New current C001 version inserted. |
    | C002 | Premium | 2026-01-01 | null | true | Unchanged existing key remains current. |
    | C003 | Basic | 2026-09-15 | null | true | New key inserted. |

---

# Choosing the combination

The two settings should be reasoned about separately.

For example, **Incremental does not automatically mean Append**. If changed rows can arrive for existing business keys, Incremental + SCD1 or Incremental + SCD2 may be the correct target behavior.

Likewise, Full does not automatically mean Overwrite. A Full source can still feed an SCD merge when the target needs keyed current-state or history semantics.

## Safety rules worth remembering

- Incremental requires a target identity because progress is source-to-target specific.
- A missing Incremental baseline bootstraps with a Full read.
- Incremental + whole-table Overwrite is rejected.
- Incremental + Append bootstrap requires a new/empty target when no accepted baseline exists.
- SCD1 requires `key_columns`.
- SCD2 requires `key_columns` and `effective_column`.
- Multiple `orchestrate_write()` calls publish independently; they are not one atomic transaction.

## Contract and metadata lifecycle

The notebook-facing setting is `write_mode`. FabricOps resolves that public Write Mode to the governed `load_strategy` stored in processing metadata and passed to the lower-level `pipeline_write()` implementation.

The applicable Data Contract remains authoritative for governed processing. Development can propose processing settings; selected/frozen contract validation governs Development, and the active approved contract governs Production.

After successful publication, FabricOps persists the resolved target processing definition and commits Lineage plus accepted Source Observation state. This keeps future Incremental scope aligned with data that was actually published.

## Related documentation

- [Plug-and-Play Data Pipelines with Data Contract Enforcement](../solutions/plug-and-play-data-pipelines.md)
- [`orchestrate_read()`](../api/reference/orchestrate_read.md)
- [`orchestrate_write()`](../api/reference/orchestrate_write.md)
- [`pipeline_read()`](../api/reference/pipeline_read.md)
- [`pipeline_write()`](../api/reference/pipeline_write.md)
- [Guided Demo: Full Read Pipeline](../guided-demo/02-build-and-run-etl.md)
- [Guided Demo: Incremental → Append](../guided-demo/02B-build-and-run-incremental-append-etl.md)
- [Guided Demo: SCD Type 1 vs Type 2](../guided-demo/02C-build-and-run-scd-etl.md)
