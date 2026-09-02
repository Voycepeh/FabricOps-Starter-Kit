# `read_lakehouse_json`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
<span class="reference-chip reference-chip-muted">Public function</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

Read JSON data from a configured Lakehouse Files path through Spark JSON.

<div class="reference-docstring-intro" markdown="1">

FabricOps resolves ``target`` and ``relative_path`` to the configured
Lakehouse ``Files`` area, then delegates JSON parsing to Spark's native
JSON reader. Use ``read_lakehouse_table`` instead for managed Delta tables
in the Lakehouse ``Tables`` area.

</div>

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/io/read_lakehouse_json.py:10`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/read_lakehouse_json.py#L10-L68">View on GitHub</a>
</div>

<p class="reference-catalogue-item-meta reference-catalogue-item-badges">
<span class="reference-chip">Public Starter Kit function</span>
<span class="reference-chip">Usage detection may exclude indirect or generated references.</span>
</p>

**Used in notebooks:** Usage detection may exclude indirect or generated references.

## Usage notes

These IO helpers exist because Fabric notebooks can only attach to one lakehouse or warehouse at a time. Use them when a notebook needs a supported and repeatable way to read from or write to the configured Fabric store.

They keep IO behavior consistent across Starter Kit notebooks and avoid ad hoc connection logic.


## Signature

<div class="reference-api-definition" markdown="1">

```python
def read_lakehouse_json(
    relative_path: str,
    target: str='source',
    spark_session=None,
    context: dict[str, Any] | None=None,
    **options,
):
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

``df = read_lakehouse_json("incoming/events.json", target="source")``

``df = read_lakehouse_json("incoming/events.json", target="source", multiLine=True)``

This function does not read managed Delta tables, register metadata,
profile data, convert JSON to Delta, mutate source files, or automatically
cache or persist the returned DataFrame.

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `relative_path` | `str` | Yes | JSON file or folder path underneath the configured Lakehouse ``Files`` area. Root-level and nested paths are supported. |
| `target` | `str` | No | Logical Lakehouse target configured by ``00_env_config``. |
| `spark_session` | `object` | No | Spark session to use instead of the notebook global ``spark``. |
| `context` | `dict[str, Any] \| None` | No | Active Fabric context override. **options Options forwarded unchanged to Spark's JSON reader, such as ``multiLine``, ``mode``, ``columnNameOfCorruptRecord``, ``dateFormat``, ``timestampFormat``, ``encoding``, ``recursiveFileLookup``, ``pathGlobFilter``, ``primitivesAsString``, ``allowComments``, ``allowSingleQuotes``, and ``allowUnquotedFieldNames``. |

## Returns

Lazy Spark DataFrame backed by the Fabric-resolved JSON path.

### Return interpretation

The returned DataFrame is lazy and reflects Spark JSON parsing behavior and supplied options.

## Raises / Errors

Raises ValueError for invalid file paths and configuration/Spark errors when the path cannot be read.

### Common failure causes

- The path is missing or inaccessible.
- JSON content does not match the supplied Spark options.
- The configured Lakehouse target is unavailable.
- Some Spark errors are deferred until an action evaluates the DataFrame.

## Notes

<div class="reference-docstring-notes" markdown="1">

Spark normally treats each line as a separate JSON record (JSON Lines or
newline-delimited JSON). Standard multi-line JSON documents may require
``multiLine=True``. Folder paths are passed directly to Spark; FabricOps
does not iterate through files or eagerly validate or collect the data.

</div>

## See also

- [Templates](../../notebook-templates.md)


<details>
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
