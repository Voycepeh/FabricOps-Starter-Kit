# `write_lakehouse_file`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

Write CSV, Parquet or newline-delimited JSON to configured Lakehouse Files.

<p class="reference-catalogue-item-meta reference-catalogue-item-badges">
<span class="reference-chip">00C_demo_setup</span>
</p>

## Usage notes

Use for standalone physical output without pipeline profiling or metadata persistence.


## Example usage

<div class="reference-example-usage" markdown="1">

```python
write_lakehouse_file(dataframe=final_df, relative_path="Exports/orders.csv", store="Silver", file_format="csv", write_options={"header": True})
```

</div>


<details class="reference-signature-details" markdown="1">
<summary>Signature</summary>

## Signature

<div class="reference-api-definition" markdown="1">

```python
def write_lakehouse_file(
    dataframe,
    relative_path,
    *,
    store='Silver',
    file_format='parquet',
    mode='overwrite',
    write_options=None,
    repartition_by=None,
    verbose=True,
    context=None,
):
```

</div>

</details>

## Parameters

Required describes the Python signature. An optional parameter may still be needed for the selected mode or identity form; see its description. `—` means no signature default.

<div class="reference-input-table" markdown="1">

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `dataframe` | `pyspark.sql.DataFrame` | Yes | `—` | Prepared input; no profiling, scanning or metadata persistence occurs. |
| `relative_path` | `str` | Yes | `—` | Exact nested path beneath Files, without absolute paths or selectors. |
| `store` | `str` | No | `'Silver'` | Lakehouse key from 00_env_config. |
| `file_format` | `{"csv", "parquet", "json"}` | No | `'parquet'` | Spark output format. |
| `mode` | `{"overwrite", "append_all"}` | No | `'overwrite'` | Overwrite replaces the destination; append_all adds data to a dataset folder only. |
| `write_options` | `dict` | No | `None` | Spark writer options, such as header, sep or compression. Destination, mode and output layout overrides are rejected. |
| `repartition_by` | `int or str or list or tuple` | No | `None` | Same Spark repartitioning conventions as write_lakehouse_table. Applied before staging; a small export then coalesces to one part, while distributed overflow and append_all preserve the requested repartitioning. |
| `verbose` | `bool` | No | `True` | Print logical destination on completion. |
| `context` | `dict` | No | `None` | Fabric runtime override; Spark belongs to the supplied DataFrame. |

</div>

## Advanced examples

<div class="reference-example-usage" markdown="1">

```python
write_lakehouse_file(dataframe=final_df, relative_path="Exports/orders.csv",
    store="Silver", file_format="csv", write_options={"header": True})
write_lakehouse_file(final_df, "Exports/orders.json", file_format="json",
    mode="overwrite")
```

</div>

## Returns

dict
    Actual resolved_path, relative_path, published, publication_status,
    file_format, actual output_layout, mode, file_count, output_bytes,
    overflow_occurred, overflow_reason
    (row_limit, byte_limit or None) and write_metrics. Row commit counts
    are unknown; file_count and output_bytes describe the resulting target.

## Raises / Errors

ValueError for invalid arguments or append_all targeting a physical file; RuntimeError for destination failures.

## Notes

<div class="reference-docstring-notes" markdown="1">

Overwrite automatically attempts one physical file. Internal safety policy
selects a distributed dataset folder at the exact same path above 1,000,000
rows or 100,000,000 encoded bytes (100 MB). These limits are implementation
policy, not a Microsoft OneLake file-size limit. append_all always writes a
dataset folder and rejects an existing physical file. No rows are truncated.
Use deterministic input from stable sources across the count and write actions;
byte overflow re-executes the original DataFrame after discarding staging.
Lazy reads from the destination finish before overwrite moves that destination.
Single-file output uses one executor, a bounded count, temporary Spark output
and a filesystem rename. It never collects business rows on the driver.
Coalescing limits parallelism and can exhaust executor memory for wide rows;
row and encoded-byte safeguards do not bound executor working memory. The
byte check occurs after staging, before publication. Only row/byte limit
checks trigger overflow; unrelated failures propagate without fallback. Single CSV/JSON uses uncompressed
output; compressed CSV/JSON requires dataset-folder output. Overwrite replaces an existing
file or folder only after staging succeeds; rename/replace is not transactional.
Dataset overwrite also stages all rows before replacing the target, so lazy
reads of that target finish before it is moved. Existing output is renamed to
a unique backup and restored when publication fails and the target is absent.
Failed/ambiguous publication retains staging and backup recovery paths on the
raised exception; never delete these until the output has been inspected.
Concurrent writers to the same physical path or overlapping folders are
unsupported, including aliases through different stores. There is no distributed
lock. Serialize writers externally and coordinate readers: replacement can
expose a temporary gap between renames. Resolve ambiguous failures before
retrying. Production use requires signed-in Fabric validation of permissions,
shortcut support, rename outcomes, rollback and recovery.
Temporary output is
removed after successful publication or failures before publication begins. Empty frames use Spark's native empty output.
Permission and read-only/unsupported shortcut failures propagate with a clear
destination error. SharePoint shortcuts are not assumed writable; no fallback
destination is used. Fabric Hadoop rename semantics require live validation.

</div>

## See also

No related guides documented.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/io/write_lakehouse_file.py:20`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/write_lakehouse_file.py#L20-L195">View on GitHub</a>
</div>


<details class="reference-implementation-details" markdown="1">
<summary>Maintainer architecture details</summary>

## Contract impact

| Property | Value |
| --- | --- |
| Lifecycle | <span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview">Preview</span> |
| Live since | — |
| Discontinued in | — |
| Contract classification | Preview public function |
| Contract risk | Preview |
| Live-critical dependencies | 0 |


</details>
