# `check_freshness`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

Check whether source timing satisfies direct or approved freshness intent.


## Usage notes

Use directly for targeted freshness validation or through run_table_guardrails.


## Example usage

<div class="reference-example-usage" markdown="1">

```python
freshness_result = check_freshness(table_id)
```

</div>


<details class="reference-signature-details" markdown="1">
<summary>Signature</summary>

## Signature

<div class="reference-api-definition" markdown="1">

```python
def check_freshness(
    table_id: str,
    *,
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
| `table_id` | `str` | Yes | `—` | Canonical governed source identity returned by :func:`pipeline_read`. |
| `enabled` | `bool` | No | `True` | Explicitly disable this check when ``False``. Normally omit this value; FabricOps enforces the resolved pipeline Data Contract automatically. |
| `raise_on_failure` | `bool` | No | `False` | Raise ``RuntimeError`` when a blocking freshness result cannot continue. |
| `spark_session` | `object` | No | `None` | Spark session to use. When omitted, FabricOps resolves the active session. |
| `verbose` | `bool` | No | `True` | Print the concise normalized check outcome when ``True``. |

</div>

## Advanced examples

<div class="reference-example-usage" markdown="1">

```python
result = check_freshness(source_result["table_id"])
```

</div>

## Returns

dict
    Structured freshness evidence and continuation decision. Governed
    observation checks append the outcome to ``METADATA_GUARDRAIL_RESULTS``.

## Raises / Errors

ValueError
    If the observation or configured freshness rule is invalid.
RuntimeError
    If ``raise_on_failure=True`` and a blocking freshness result cannot
    continue.

## Notes

<div class="reference-docstring-notes" markdown="1">

Production resolves expectations from the active Data Contract. Development
uses an explicitly selected immutable version, or safely skips when none is
selected.

</div>

## See also

No related guides documented.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/pipeline/check_freshness.py:20`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline/check_freshness.py#L20-L207">View on GitHub</a>
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
