# `write_lakehouse_file`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

Write CSV, Parquet or newline-delimited JSON to configured Lakehouse Files.


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
    mode='errorifexists',
    write_options=None,
    repartition_by=None,
    single_file=False,
    max_single_file_rows=1000000,
    max_single_file_bytes=134217728,
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
| `mode` | `{"errorifexists", "overwrite", "append", "ignore"}` | No | `'errorifexists'` | Spark collision policy. Append is supported only for dataset folders. |
| `write_options` | `dict` | No | `None` | Spark writer options, such as header, sep or compression. Destination, mode and output layout overrides are rejected. |
| `repartition_by` | `int or str or list or tuple` | No | `None` | Same Spark repartitioning conventions as write_lakehouse_table. |
| `single_file` | `bool` | No | `False` | Explicitly produce one named artifact with a matching format extension. Otherwise the path is a dataset directory, even if it has an extension. |
| `max_single_file_rows` | `int` | No | `1000000` | Single-file input row limit, checked with a bounded Spark count. |
| `max_single_file_bytes` | `int` | No | `134217728` | Maximum staged output bytes before publishing one artifact. |
| `verbose` | `bool` | No | `True` | Print logical destination on completion. |
| `context` | `dict` | No | `None` | Fabric runtime override; Spark belongs to the supplied DataFrame. |

</div>

## Advanced examples

<div class="reference-example-usage" markdown="1">

```python
write_lakehouse_file(dataframe=final_df, relative_path="Exports/orders.csv",
    store="Silver", file_format="csv", write_options={"header": True})
write_lakehouse_file(final_df, "Exports/orders.json", file_format="json",
    single_file=True, mode="overwrite")
```

</div>

## Returns

dict
    Actual resolved_path, relative_path, published, publication_status,
    file_format, output_layout, mode and write_metrics. Row commit counts
    are unknown; file_count and output_bytes describe the resulting target.

## Raises / Errors

ValueError for invalid arguments, FileExistsError for collisions, RuntimeError for destination failures.

## Notes

<div class="reference-docstring-notes" markdown="1">

Single-file output uses one executor, a bounded count, temporary Spark output
and a filesystem rename. It never collects business rows on the driver.
Coalescing limits parallelism and can exhaust executor memory for wide rows;
row and encoded-byte safeguards do not bound executor working memory. The
byte check occurs after staging, before publication. Single CSV/JSON uses uncompressed
output; compressed CSV/JSON requires dataset-folder output. Overwrite replaces an existing
artifact only after staging succeeds; rename/replace is not transactional.
Writers to the same path must be externally serialized. Temporary output is
removed on success and failure. Empty frames use Spark's native empty output.
Permission and read-only/unsupported shortcut failures propagate with a clear
destination error. SharePoint shortcuts are not assumed writable; no fallback
destination is used. Fabric Hadoop rename semantics require live validation.

</div>

## See also

No related guides documented.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/io/write_lakehouse_file.py:16`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/write_lakehouse_file.py#L16-L149">View on GitHub</a>
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
