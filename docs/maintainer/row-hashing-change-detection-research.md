# Row Hashing and Unified Change Detection Research

This research audits the current implementation, records a reproducible local Spark simulation, and recommends a deliberately narrow next step. It does not change FabricOps runtime behaviour.

!!! warning
    The recorded timings are synthetic local Spark 4.1.1 results on two worker threads. They are **not Microsoft Fabric capacity benchmarks** and do not validate Fabric Lakehouse or Warehouse service performance.

## Decision

**Evolve the existing Source Observation and Source Drift path into an optional three-tier optimization; do not create a parallel change-detection lifecycle.** Keep watermark processing, standardize one internal canonical row-hash contract, and consider an **opt-in physical `_row_hash` for keyed SCD1/SCD2 tables** only after a Fabric capacity benchmark confirms a benefit for the actual target sizes, file layout, Delta `MERGE`, and Warehouse staging path.

| Tier | Evidence | Processing decision |
| --- | --- | --- |
| 1 | Delta version or change metadata | Identify candidate partitions without scanning the complete source, then stop if no relevant commits exist. |
| 2 | Partition fingerprint | Confirm which candidate or observed partitions changed; unchanged partitions stop here. |
| 3 | Business key plus row hash | Resolve inserts, updates, and missing keys only when the write strategy needs row-level decisions. |

Partition detection is an optimization, not a mandatory Data Contract requirement. A table without reliable change metadata or a suitable partition key continues to use its existing watermark or full-data path.

The local measurements do not justify universal persistence:

- At 1M rows, an unchanged overwrite took 2.40 seconds. The current fingerprint-and-skip path took 8.28 seconds, even though it wrote zero rows.
- Computing, caching, and persisting `_row_hash` took 12.11 seconds on first load versus 12.41 seconds for the cache-aligned current fingerprint path and 3.59 seconds for overwrite without hashing. Reuse produced no material timing advantage in this run.
- The 64-character SHA-256 column increased the highly compressible synthetic Parquet target from 20.2 MB to 86.7 MB, a 66.6 MB or 330% increase. Real business data will have a different percentage, but the hash itself remains high-entropy and poorly compressible.
- The reduced 10M run exhausted the local Java heap after the hashed DataFrame spilled to disk. The scale is supported by the script but was not recordable on this machine.
- Existing watermark processing wrote only the 10% incremental scope in 0.93 seconds at 1M rows. A full keyed hash comparison scanned both source and target and took 7.77–8.69 seconds. These workloads are not equivalent, but they show why row-hash comparison must not replace a usable watermark.

Persisted row hashes remain potentially useful when a keyed target is already being scanned for SCD matching and the hash replaces a wide null-safe comparison. That hypothesis needs a Fabric-native Delta and Warehouse benchmark; this local Parquet simulation does not prove it.

### Partition-tier result

The added 30-day simulation confirms the expected distinction between read avoidance and downstream avoidance:

| 1M-row case | Approach | Rows scanned | Rows written | Total |
| --- | --- | ---: | ---: | ---: |
| Unchanged | Full fingerprint | 1,000,000 | 0 | 7.41 s |
| Unchanged | Partition fingerprints | 1,000,000 | 0 | 7.57 s |
| One changed day | Full fingerprint | 1,000,000 | 1,000,000 | 15.20 s |
| One changed day | Partition fingerprints | 1,000,000 | 33,333 | 8.73 s |
| One changed day | Simulated candidate metadata + partition + row | 66,666 | 33,333 | 2.35 s |
| Late update to day 5 | Full fingerprint | 1,000,000 | 1,000,000 | 15.05 s |
| Late update to day 5 | Partition fingerprints | 1,000,000 | 33,333 | 8.15 s |
| Late update to day 5 | Simulated candidate metadata + partition + row | 66,666 | 33,333 | 1.85 s |
| Missing rows in day 10 | Full fingerprint | 999,667 | 999,667 | 13.93 s |
| Missing rows in day 10 | Partition fingerprints | 999,667 | 33,000 | 8.38 s |
| Missing rows in day 10 | Simulated candidate metadata + partition + row | 66,333 | 33,000 | 1.77 s |

Partition fingerprints saved transformation and write work but did not avoid the complete read/hash scan. For one changed day they reduced elapsed time by 42.6% and writes by 96.7%. The simulated candidate tier was 84.5% faster than full processing, but it used an in-memory candidate list. No Delta library or Fabric runtime was available, so its metadata lookup time, commit semantics, retention, delete records, and partition mapping remain unmeasured. The unchanged candidate case is therefore recorded as a logical early stop, not a performance result.

### Target has `_row_hash`, source does not

This is a valid asymmetric design. FabricOps hashes each incoming source row ephemerally, reads the persisted target key/hash projection, and joins on the business key. It avoids target serialization and hashing, but it does **not** avoid the source scan, source hashing, target scan, or key join.

| 1M-row case | Hash source and target | Reuse target hash | Saving |
| --- | ---: | ---: | ---: |
| Unchanged | 5.55 s | 5.17 s | 0.38 s / 6.8% |
| 1% updated | 7.12 s | 4.68 s | 2.44 s / 34.3% |
| 1% missing | 7.57 s | 4.54 s | 3.03 s / 40.1% |

Both approaches scanned about 2M logical rows at the 1M scale. Persisting the target hash reduced CPU and input bytes but did not reduce the roughly 140 MB keyed-join shuffle in this local run. Each case was measured once, so the varying percentage is directional rather than a stable service-level expectation.

### Scale and the billion-row question

The algorithms are not exponential. Full scans, row hashing, and full writes are approximately **O(N)** in row count; a distributed key join is also nominally O(N) but can degrade because of shuffle, skew, spill, file counts, throttling, and insufficient partitions. Selective processing changes the downstream term from O(N) to O(changed partitions or rows), but full partition fingerprinting retains the O(N) source scan/hash term.

The local 10× scale increase from 100K to 1M was sublinear rather than exponential:

| Path | 100K | 1M | Increase for 10× rows |
| --- | ---: | ---: | ---: |
| No-hash unchanged overwrite | 0.65 s | 2.21 s | 3.4× |
| Fingerprint unchanged and skip | 1.26 s | 7.21 s | 5.7× |
| Hash both sides, unchanged | 1.85 s | 5.55 s | 3.0× |
| Hash source, reuse target hash | 1.20 s | 5.17 s | 4.3× |

At 1M rows, hashing was not free compared with doing no detection:

| Workload | No hashing | With fingerprint | Difference |
| --- | ---: | ---: | ---: |
| Unchanged rerun | 2.21 s and 1M rows rewritten | 7.21 s and zero rows written | +5.00 s / 3.26× total time |
| 1% changed rerun | 2.44 s and 1M rows rewritten | 9.13 s and 1M rows rewritten | +6.69 s / 3.75× total time |

The fingerprint path lost locally because hashing cost more than rewriting the small, highly compressible synthetic target. Partition processing changed that balance: for one changed day, read time remained about 2.3–2.5 seconds and hashing cost about 5.5–5.8 seconds, but transformation fell from 3.97 to 0.41 seconds and write time from 3.23 to 0.22 seconds.

The table below is **arithmetic only**: 1M timings multiplied by 1,000. It is not a prediction for a Fabric capacity, because a billion-row run would use different executors, parallelism, files, shuffle topology, caching, and service limits.

| Two-thread local-equivalent path | Linear 1B arithmetic |
| --- | ---: |
| No-hash unchanged overwrite | 36.9 minutes |
| Fingerprint unchanged and skip | 120.2 minutes |
| No-hash 1% changed overwrite | 40.6 minutes |
| Fingerprint plus full write | 152.1 minutes |
| Hash both source and target for comparison | 118.7 minutes |
| Hash source and reuse target hash | 78.0 minutes |

A one-billion-row 64-character hash also implies roughly 64 GB of raw hex characters before columnar encoding and file overhead. The measured compressed increment was 66.6 bytes per synthetic row, which would arithmetically be about 66.6 GB at one billion rows. A binary 32-byte digest would reduce storage but needs separate Lakehouse SQL endpoint and Warehouse compatibility validation.

**Conclusion:** the design can be made to operate at a billion rows only with partition pruning/change metadata, adequate Spark capacity, controlled file layout, and a small changed scope. A mandatory full re-hash of one billion rows on every run is technically linear, but operationally unattractive. A Fabric-native 100M/1B benchmark is required before setting thresholds or promising elapsed time.

## Current implementation audit

### Publication identity

`PublicationBatch` in `src/fabricops_kit/pipeline/shared.py` performs the current publication calculation:

1. It caches the prepared DataFrame with `MEMORY_AND_DISK`.
2. It sorts top-level business column names and excludes `_TARGET_TECHNICAL_COLUMNS`.
3. It canonicalizes nested maps by sorting entries, preserves array order, renders a JSON struct with null fields included and UTC timestamp formatting, and calculates SHA-256 for every row.
4. It reduces the row hashes into row count plus four decimal sums of the four 64-bit hash segments. This bounded aggregate is independent of row order and preserves duplicate multiplicity.
5. It hashes a boundary containing workspace, target, sorted sources, processing definition, schema, and the content aggregate to create `publication_batch_id`.

The per-row hashes are transient. Only the final `publication_batch_id`, input row count, publication strategy, activity, timestamp, and run identity are persisted in the `publication_receipt` row of `METADATA_PROCESSING_STATE`. A matching receipt plus a verified target marker allows an exact batch retry to skip the physical write.

The current aggregate can be derived from a persisted `_row_hash` without another per-row SHA-256 or serialization pass: project `_row_hash`, calculate the same four sums and row count, and build the existing boundary on the driver. It still requires a scan and aggregate. The additive multiset aggregate is bounded and practical, but it is not a collision-free proof that two arbitrary multisets are equal.

### Source Observation and Processing State

`METADATA_PROCESSING_STATE` has four record types:

| Record type | Persisted purpose |
| --- | --- |
| `source_observation` | Current captured source rows or partitions; never accepted progress by itself. |
| `incremental_checkpoint` | Accepted target-specific watermark progress after publication verification. |
| `drift_baseline` | Accepted target-specific Source Drift comparison baseline. |
| `publication_receipt` | Exact target publication identity and physical verification link. |

The write path stages one receipt and all associated checkpoint/baseline members before target mutation. It commits them together only after the Lakehouse Delta commit marker or Warehouse audit-column marker is verified. Lost metadata acknowledgement is recoverable by re-verifying the physical target. The targeted regression suite covering incremental progress, Source Observation commit/recovery, Source Drift, publication retry, Lakehouse processing, and Warehouse SCD passed 147 tests.

The current schema already accommodates Level 2 observations: `partition_column`, `partition_value`, `row_count`, `content_fingerprint`, min/max change values, and `is_present` are structured fields. No new table is needed. The retired `METADATA_SOURCE_OBSERVATION` name must not be revived; current source observations and accepted baselines belong in `METADATA_PROCESSING_STATE`.

Level 1 is not represented completely. `METADATA_PROCESSING_STATE` has publication identity but no source Delta table version, change-commit range, or observation method. If Fabric-native measurements justify Level 1, use a small compatible schema addition such as nullable `observation_method`, `source_version_from`, and `source_version_through` fields rather than encoding versions into unrelated strings or adding another metadata table.

Incremental observation deliberately does not hash content. It aggregates the full source to a maximum watermark and row count, resolves the last accepted target-specific watermark, and filters the read to `(accepted, observed]`. Lakehouse filtering remains a Spark predicate; Warehouse filtering is framework-owned SQL pushdown. Empty incremental scope does not publish or advance a checkpoint.

### Source Drift hashing

Source Drift is a separate calculation and cannot safely reuse the current publication hash as-is:

- Lakehouse Source Drift sorts top-level columns, SHA-256 hashes a JSON row, collects and sorts all row hashes in each governed partition, concatenates them, then hashes again. This can create a large per-partition array and is not a bounded aggregate.
- Warehouse Source Drift uses `FOR JSON PATH` over `source_row.*`, SHA-256 through `HASHBYTES`, and ordered `STRING_AGG` per partition.
- `content_fingerprint`, row count, min/max change value, partition identity, and presence are persisted on Source Observation and accepted `drift_baseline` rows.
- Source Drift detects new, changed, removed, and reappeared **partitions**. It does not detect an individual missing business key inside a still-present partition.

The Lakehouse and Warehouse encodings are not defined as cross-engine equivalent. The Warehouse encoding also depends on physical column order, while the Lakehouse path sorts top-level names.

FabricOps therefore already has most of the Level 2 evidence model. The missing connection is processing scope: `check_source_drift_for_target()` reports affected partitions and stages the accepted baseline, but `pipeline_read()` and `pipeline_write()` do not turn those partitions into a selective read/replace scope. Source Observation should continue to record the facts. Source Drift should decide whether those facts violate policy. A normal changed partition may be eligible for processing without being a Guardrail failure.

### Append, overwrite, SCD1, and SCD2

| Strategy | Current change behaviour | Source absence behaviour |
| --- | --- | --- |
| Append | Writes the prepared scope; initial incremental append refuses a populated target without an accepted baseline. | Never deletes. |
| Overwrite | Replaces the full target; incremental input is rejected. | Whole-table replacement naturally removes absent rows only for a complete input. |
| SCD1 | Rejects null or duplicate incoming business keys; Lakehouse/ Warehouse `MERGE` uses null-safe comparisons of every business and technical column. | Does not delete target rows missing from the incoming scope. |
| SCD2 | Rejects null or duplicate incoming business keys; compares tracked columns, closes changed current rows, and inserts new current versions. | Does not expire a current version merely because its key is missing from the incoming scope. |

Default SCD business/tracked-column resolution already excludes `_row_hash`, audit fields, SCD2 lifecycle fields, `_fabricops_*`, and `_dq_*`. `_row_hash` is already recognized as a technical column even though FabricOps does not currently create or persist it.

Lakehouse SCD uses Delta `MERGE` with commit metadata. Warehouse SCD writes a staging table, verifies exact stage/target schema compatibility, then runs transactional T-SQL. Adding a physical column later must update both inputs and existing target schemas consistently; Warehouse exact schema checks make a partial rollout fail closed.

### Target audit columns and SQL access

Managed target rows receive `_committed_at`, `_committed_by`, `_activity_id`, `_workspace_id`, `_notebook_id`, and `_notebook_name`. SCD2 also owns `_effective_from`, `_effective_to`, and `_is_current`. These columns are excluded from business change detection but can be refreshed on otherwise unchanged matched rows.

For a future cross-target hash, use a lowercase 64-character hexadecimal SHA-256 string. Spark `string` is readable through a Lakehouse SQL endpoint and maps naturally to Warehouse character storage. A binary digest would save space but introduces more connector, SQL endpoint, display, and migration variability. Fabric verification is still required before declaring the exact Warehouse physical type supported.

## Reproducible simulation

Run the benchmark from the repository root:

```bash
.venv/bin/python scripts/benchmark_row_hashing.py \
  --scales 100000,1000000 \
  --output /tmp/row-hashing-results.json
```

The script creates a new temporary directory, generates realistic strings, fixed-scale decimals, UTC timestamps, nulls, arrays, structs, and maps, and removes the directory after success. Use `--keep-work-dir` to inspect the Parquet outputs. It records elapsed time and Spark event-log job, stage, task, input/output, and shuffle metrics, plus logical rows scanned/written and physical target bytes.

The scenarios are:

1. Full read and overwrite without hashing.
2. Current publication-style row hashing and skip.
3. `_row_hash` calculated once in the prepared DataFrame, reused for the aggregate, and physically persisted.
4. Full source/target comparison by business key and row hash.
5. Watermark-filtered incremental write.
6. Hash-based SCD1 delta detection.
7. Hash-based SCD2 close-and-insert mutation generation.
8. Source without a hash compared with a target containing a persisted `_row_hash`.
9. Thirty daily partitions tested with full fingerprinting, full-scan partition fingerprints plus selective processing, and simulated change-metadata candidates followed by partition and row checks.

The SCD simulations measure detection and mutation output, not Delta or Warehouse `MERGE`. Publication receipt persistence and recovery are validated by the production unit tests instead of being reimplemented in the benchmark.

The persisted-hash scenario calculates the hash once per prepared source batch, reuses it for that batch's aggregate, and writes it to the target. A later run still has to hash a source that does not already supply the same governed hash. Physical target persistence therefore avoids target-side re-hashing during keyed comparison; it does not make arbitrary future source snapshots free to hash.

### Recorded timing summary

| Scale | Scenario | First load | Unchanged rerun | 1% changed rerun | Rows written on unchanged |
| ---: | --- | ---: | ---: | ---: | ---: |
| 100K | Overwrite, no hash | 1.63 s | 0.77 s | 0.99 s | 100K |
| 100K | Current fingerprint | 3.17 s | 1.49 s | 2.25 s | 0 |
| 100K | Persisted `_row_hash` | 2.57 s | 1.38 s | 2.32 s | 0 |
| 1M | Overwrite, no hash | 3.59 s | 2.40 s | 2.99 s | 1M |
| 1M | Current fingerprint | 12.41 s | 8.28 s | 10.85 s | 0 |
| 1M | Persisted `_row_hash` | 12.11 s | 8.25 s | 10.93 s | 0 |

The cache-aligned current and persisted-hash paths were effectively tied at 1M, while physical persistence still carried substantial storage cost. Small differences in either direction are local execution noise, not evidence of a universal threshold.

### Keyed comparison and mutation results

| Scale | Case | Key/hash compare | Detected result |
| ---: | --- | ---: | --- |
| 1M | Unchanged | 7.77 s | no changes |
| 1M | 1% changed | 7.85 s | 10K updates |
| 1M | 10% changed | 7.81 s | 100K updates |
| 1M | 1% new | 8.69 s | 10K inserts |
| 1M | 1% deleted | 8.25 s | 10K missing keys |
| 1M | 1% duplicates | 0.93 s | rejected before comparison |
| 1M | Reordered | 7.95 s | no changes |

The 1M full key/hash joins used about 139–210 MB of shuffle read. Spark used broadcast joins for the separate SCD simulations on this local dataset, so their event-log shuffle was negligible and should not be extrapolated to large Fabric targets.

| Scale | Scenario | 1% changed | Rows written | 10% changed | Rows written |
| ---: | --- | ---: | ---: | ---: | ---: |
| 100K | Hash SCD1 detection | 3.14 s | 1K | 2.26 s | 10K |
| 100K | Hash SCD2 mutations | 4.57 s | 2K | 3.78 s | 20K |
| 1M | Hash SCD1 detection | 14.01 s | 10K | 14.77 s | 100K |
| 1M | Hash SCD2 mutations | 24.46 s | 20K | 25.81 s | 200K |

SCD2 writes two mutation records per changed existing key: one expired version and one inserted version. Variation between 1% and 10% timings is ordinary local execution noise and cache/JIT effects; each scenario was run once, not as a statistically powered trial.

The machine-readable results are in `docs/maintainer/benchmarks/row-hashing-local-results.json`, `docs/maintainer/benchmarks/partition-change-detection-local-results.json`, and `docs/maintainer/benchmarks/asymmetric-row-hash-local-results.json`.

## Correctness findings

### Canonical serialization contract required

A reusable hash must freeze all of the following:

- sorted top-level business column names and sorted nested struct field names;
- recursive map-entry sorting; array order remains significant;
- explicit null fields and a distinction between null, empty string, empty array/map, and missing schema fields;
- UTC timestamp rendering, while preserving the separate wall-clock semantics of `timestamp_ntz`;
- declared decimal scale and a stable non-scientific representation;
- data type plus column name in a versioned schema contract;
- exclusion of `_row_hash`, target audit columns, SCD2 lifecycle columns, `_fabricops_*`, `_dq_*`, and other approved technical columns;
- lowercase 64-character SHA-256 hex output.

The benchmark implementation passed same-engine tests for nulls, timestamps, decimals, nested values, top-level column reordering, technical-column exclusion, and duplicate multiplicity. It does not establish byte-for-byte equivalence with T-SQL `FOR JSON PATH`; cross-engine golden vectors are required before Warehouse adoption.

### Business keys and duplicates

Row hash is content identity, not row identity. SCD comparison must join on the governed business key and compare the hash only after matching. Null or duplicate incoming keys must continue to fail before mutation. Duplicate rows are meaningful to publication and Source Drift fingerprints because multiplicity changes the aggregate, while duplicate business keys remain invalid for SCD1/SCD2.

### Disappearance and incomplete snapshots

Missing-key detection is safe only when the input is an attested complete snapshot for the governed source/target boundary. An incremental batch, filtered query, failed extract, truncated snapshot, or incomplete partition set must never expire/delete unseen target records.

Do not extend Source Drift to mutate records. Source Drift should keep its existing role of detecting unexpected source partition mutation/removal. If record disappearance becomes a governed feature, first model it as an explicit keyed processing policy such as `source_scope=complete_snapshot` plus `missing_key_action=ignore|warn|delete|expire`. Reuse `METADATA_PROCESSING_STATE` receipts and accepted Source Observation state; do not add a metadata table. If Governance later needs an independent approval decision, add a dedicated disappearance Guardrail rather than overloading Source Drift.

## Recommended implementation scope

### Phase A: Source Observation partition scope

1. Introduce one versioned internal canonical row-hash expression and golden test vectors.
2. Make `PublicationBatch` consume an already-prepared internal hash when present, otherwise calculate it exactly as today.
3. Replace Source Drift's unbounded `collect_list` aggregation with a measured bounded aggregate derived from the same row hashes only after accepting the aggregate-collision trade-off and migrating baselines explicitly.
4. Return normalized changed/new/removed/reappeared partition scope from the existing Source Observation comparison, independently of whether Source Drift warns or blocks.
5. Allow selective processing only when the source partition column and write strategy can safely apply that scope. Append, SCD1, and SCD2 retain their strategy rules. Overwrite requires a new atomic partition-replacement capability; whole-table overwrite must continue to reject a partial input.
6. Keep the row hash internal and ephemeral in this phase. Preserve current receipts, retry verification, checkpoint staging/commit, and watermark behaviour.

This phase uses the existing `source_observation` and `drift_baseline` records in `METADATA_PROCESSING_STATE`. Partition selection remains optional; tables without an eligible partition key continue unchanged.

### Phase B: Fabric-native candidate metadata experiment

Benchmark Delta table versions, commit metadata, file actions, and Change Data Feed in Fabric. Verify late updates, deletes, retention gaps, schema changes, table replacement, vacuum, and commits that touch multiple logical partitions. Candidate metadata may narrow the partitions to inspect, but it must not be treated as proof of unchanged content unless the selected Delta mechanism provides that guarantee.

If justified, add nullable observation-method and source-version fields to `METADATA_PROCESSING_STATE`; do not add a metadata table. Stop at Level 1 for a trustworthy no-change result. Otherwise fingerprint only candidate partitions, then use row comparison only for strategies that require row-level decisions.

### Phase C: optional keyed persistence and disappearance

Add physical `_row_hash` only for explicitly enabled SCD1/SCD2 targets. Benchmark on Fabric with Delta `MERGE` and Warehouse staging at representative widths, cardinalities, partition/file layouts, 1%/10% change rates, and concurrency. Require a meaningful end-to-end improvement that includes first-load hash cost and storage, not only a faster comparison predicate.

Migration must be additive and repeatable:

1. stop or coordinate writers;
2. add the nullable string column;
3. backfill under the frozen hash-contract version;
4. validate all current rows have a 64-character value;
5. enable hash comparison only after validation;
6. keep rollback able to return to column-wise comparisons without dropping history.

No new metadata table is necessary. The processing definition or existing target registration must record whether physical hashing is enabled and which hash-contract version applies. Existing Data Contracts and Catalogue validation would need an intentional schema evolution before runtime implementation.

Implement only for keyed, explicitly complete snapshots. Default to `ignore` or `warn`; destructive SCD1 deletion and SCD2 expiration require explicit Governance authoring, a complete-snapshot assertion, duplicate/key validation, and an absence threshold or fail-closed safeguard against unexpectedly empty/truncated snapshots. Stage and accept the result with the same publication receipt and Processing State transaction.

## Rejected options

| Option | Decision | Reason |
| --- | --- | --- |
| Physical `_row_hash` on every managed target | Reject | Adds high-entropy storage and first-load work to append/overwrite and unkeyed tables with no measured benefit. |
| Optional on keyed tables | Preferred experiment | Can serve publication aggregation and SCD comparison, but requires Fabric-native evidence and migration controls. |
| Internal-only hash | Recommended now | Shares canonicalization and avoids target schema/migration cost while evidence is incomplete. |
| Replace watermark reads with hash comparison | Reject | Watermarks avoid full target comparison; local results strongly favour retaining them. |
| Require a partition key in every Data Contract | Reject | Partition detection is an optimization and many valid tables have no safe partition scope. |
| Treat simulated candidates as Delta evidence | Reject | The local candidate list does not measure or prove Fabric Delta semantics. |
| Extend Source Drift to delete/expire rows | Reject | Conflates source stability detection with destructive target reconciliation and is unsafe for partial snapshots. |
| New metadata table | Reject | Existing Processing State receipts and baselines can carry acceptance and recovery semantics. |

## Verification performed

```text
.venv/bin/python -m py_compile scripts/benchmark_row_hashing.py
.venv/bin/python scripts/benchmark_row_hashing.py --correctness-only --output /tmp/row-hash-correctness.json
uv run pytest -q tests/unit/test_incremental_pipeline.py tests/unit/test_source_observation_commit.py tests/unit/test_source_target_drift.py tests/unit/test_source_drift.py tests/unit/test_pipeline_prep.py tests/unit/test_load_strategy_execution.py tests/unit/test_warehouse_scd.py
```

Result: all executable correctness checks passed and 147 production regression tests passed.
