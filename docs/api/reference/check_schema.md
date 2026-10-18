# `check_schema`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

Check observed table schema against direct or approved schema intent.


## Usage notes

Use directly for targeted schema validation or through run_table_guardrails.


## Example usage

<div class="reference-example-usage" markdown="1">

```python
schema_result = check_schema(table_id=table_id, dataframe=df)
```

</div>


<details class="reference-signature-details" markdown="1">
<summary>Signature</summary>

## Signature

<div class="reference-api-definition" markdown="1">

```python
def check_schema(
    dataframe=None,
    *,
    table_id: str,
    enabled: bool=True,
    raise_on_failure: bool=False,
    spark_session=None,
    verbose: bool=True,
) -> dict:
```

</div>

</details>

## Parameters

Required describes the Python signature. An optional parameter may still be needed for the selected mode or identity form; see its description. `—` means no signature default.

<div class="reference-input-table" markdown="1">

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `dataframe` | `DataFrame` | No | `None` | Incoming DataFrame whose schema should be checked. When omitted, the schema of the configured physical table is checked. |
| `table_id` | `str` | Yes | `—` | Canonical identity of an active registered Catalogue table. |
| `enabled` | `bool` | No | `True` | Explicitly disable this check when ``False``. Normally omit this value; FabricOps enforces the resolved pipeline Data Contract automatically. |
| `raise_on_failure` | `bool` | No | `False` | Raise ``RuntimeError`` when a blocking schema result cannot continue. |
| `spark_session` | `object` | No | `None` | Spark session to use. When omitted, FabricOps resolves the active session. |
| `verbose` | `bool` | No | `True` | Print the concise normalized check outcome when ``True``. |

</div>

## Advanced examples

<div class="reference-example-usage" markdown="1">

```python
result = check_schema(table_id="lakehouse||source||dbo||orders")
result["can_continue"]
```

```text
True
```

</div>

## Returns

dict
    Structured guardrail status, continuation decision, checks, and schema
    differences. Governed configured-table checks append the outcome to
    ``METADATA_GUARDRAIL_RESULTS``.

## Raises / Errors

ValueError
    If the target is unsupported or no active approved Schema guardrail
    exists for the resolved table.
RuntimeError
    If ``raise_on_failure=True`` and a blocking schema result cannot
    continue.

## Notes

<div class="reference-docstring-notes" markdown="1">

Production uses the active Data Contract. Development uses an explicitly
selected immutable version, or safely skips when no contract is selected.

</div>

## See also

No related guides documented.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/pipeline/check_schema.py:22`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline/check_schema.py#L22-L227">View on GitHub</a>
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

### Release history

| Status | Version |
| --- | --- |
| Preview | 0.2.0 |
| Preview | 0.2.5 |


</details>
