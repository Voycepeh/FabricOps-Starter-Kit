# `read_lakehouse_json`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-live reference-lifecycle-chip-prominent">Live</span>
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-live reference-lifecycle-chip-prominent">Live since 0.2.0</span>
</p>

> This function is part of the supported FabricOps public contract. Changes to its signature, behaviour, public export, or Live-critical dependencies require Live-contract review.

Read JSON data from a configured Lakehouse Files path through Spark JSON.

<p class="reference-catalogue-item-meta reference-catalogue-item-badges">
<span class="reference-chip">00C_demo_setup</span>
</p>

## Usage notes

Use when reading JSON files or folders from a configured Lakehouse Files path.


## Example usage

<div class="reference-example-usage" markdown="1">

```python
df = read_lakehouse_json(relative_path="incoming/events.json", store="Bronze", multiLine=True)
```

</div>


<details class="reference-signature-details" markdown="1">
<summary>Signature</summary>

## Signature

<div class="reference-api-definition" markdown="1">

```python
def read_lakehouse_json(
    relative_path: str,
    *,
    store: str='Bronze',
    context: dict[str, Any] | None=None,
    **options,
):
```

</div>

</details>

## Parameters

Required describes the Python signature. An optional parameter may still be needed for the selected mode or identity form; see its description. `—` means no signature default.

<div class="reference-input-table" markdown="1">

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `relative_path` | `str` | Yes | `—` | JSON file or folder path underneath the configured Lakehouse ``Files`` area. Root-level and nested paths are supported. |
| `store` | `str` | No | `'Bronze'` | Logical Lakehouse store key configured by ``00_env_config``. |
| `context` | `dict[str, Any] \| None` | No | `None` | Active Fabric context override. |
| `**options` | `—` | No | `—` | Options forwarded unchanged to Spark's JSON reader, such as ``multiLine``, ``mode``, ``columnNameOfCorruptRecord``, ``dateFormat``, ``timestampFormat``, ``encoding``, ``recursiveFileLookup``, ``pathGlobFilter``, ``primitivesAsString``, ``allowComments``, ``allowSingleQuotes``, and ``allowUnquotedFieldNames``. |

</div>

## Advanced examples

<div class="reference-example-usage" markdown="1">

``df = read_lakehouse_json("incoming/events.json", store="Bronze")``

``df = read_lakehouse_json("incoming/events.json", store="Bronze", multiLine=True)``

This function does not read managed Delta tables, register metadata,
profile data, convert JSON to Delta, mutate source files, or automatically
cache or persist the returned DataFrame.

</div>

## Returns

pyspark.sql.DataFrame
    A lazy Spark DataFrame backed by the resolved JSON file or compatible
    files in the supplied folder path.

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

## Behavior and scope

<div class="reference-docstring-intro" markdown="1">

Spark is resolved automatically from the existing execution session.
No session is created; Spark-dependent work raises
``RuntimeError`` when no session is available.

FabricOps resolves ``store`` and ``relative_path`` to the configured
Lakehouse ``Files`` area, then delegates JSON parsing to Spark's native
JSON reader. Use ``read_lakehouse_table`` instead for managed Delta tables
in the Lakehouse ``Tables`` area.

</div>

## See also

- [Templates](https://github.com/Voycepeh/FabricOps-Starter-Kit/tree/main/templates/notebooks)

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/io/read_lakehouse_json.py:10`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/read_lakehouse_json.py#L10-L73">View on GitHub</a>
</div>


<details class="reference-implementation-details" markdown="1">
<summary>Maintainer architecture details</summary>

## Contract impact

| Property | Value |
| --- | --- |
| Lifecycle | <span class="reference-chip reference-lifecycle-chip reference-lifecycle-live">Live</span> |
| Live since | 0.2.0 |
| Discontinued in | — |
| Contract classification | Live public function |
| Contract risk | Live |
| Live-critical dependencies | 16 |

### Release history

| Status | Version |
| --- | --- |
| Live | 0.2.0 |
| Live | 0.2.5 |
| Live | 0.3.0 |

### Live-critical dependencies

<ul class="reference-compact-list">
<li><code>fabricops_kit.config.shared._get_fabric_runtime_context</code></li>
<li><code>fabricops_kit.config.shared._get_fabric_runtime_metadata</code></li>
<li><code>fabricops_kit.config.shared._normalize_path_config</code></li>
<li><code>fabricops_kit.config.shared.get_default_fabric_context</code></li>
<li><code>fabricops_kit.config.shared.get_store</code></li>
<li><code>fabricops_kit.config.shared.resolve_fabric_context</code></li>
<li><code>fabricops_kit.io.shared._join_lakehouse_area_path</code></li>
<li><code>fabricops_kit.io.shared._validate_lakehouse_store</code></li>
<li><code>fabricops_kit.io.shared._validate_relative_path</code></li>
<li><code>fabricops_kit.io.shared._validate_warehouse_store</code></li>
<li><code>fabricops_kit.io.shared.get_spark_session</code></li>
<li><code>fabricops_kit.io.shared.read_json_path</code></li>
<li><code>fabricops_kit.io.shared.resolve_configured_file_path</code></li>
<li><code>fabricops_kit.io.shared.resolve_lakehouse_file_location</code></li>
<li><code>fabricops_kit.io.shared.resolve_lakehouse_file_path</code></li>
<li><code>fabricops_kit.io.shared.resolve_store</code></li>
</ul>


</details>
