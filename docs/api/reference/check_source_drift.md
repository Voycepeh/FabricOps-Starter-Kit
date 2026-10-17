# `check_source_drift`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

Validate source changes against one target consumption baseline using the source's governed load behaviour.


## Usage notes

Call explicitly during pre-write preparation after the consuming target identity is known.


## Example usage

<div class="reference-example-usage" markdown="1">

```python
drift_result = check_source_drift(source_table_id, target_table_id=target_table_id)
```

</div>


<details class="reference-signature-details" markdown="1">
<summary>Signature</summary>

## Signature

<div class="reference-api-definition" markdown="1">

```python
def check_source_drift(
    source_table_id: str,
    *,
    target_table_id: str,
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
| `source_table_id` | `str` | Yes | `—` | Canonical governed source identity returned by :func:`pipeline_read`. |
| `target_table_id` | `str` | Yes | `—` | Canonical governed target identity used to select the last successfully consumed Source Observation baseline. |
| `enabled` | `bool` | No | `True` | Explicitly skip the check when ``False``. |
| `raise_on_failure` | `bool` | No | `False` | Raise ``RuntimeError`` when a blocking result cannot continue. |
| `spark_session` | `object` | No | `None` | Spark session to use. When omitted, FabricOps resolves the active session. |
| `verbose` | `bool` | No | `True` | Print the concise normalized check outcome when ``True``. |

</div>

## Advanced examples

<div class="reference-example-usage" markdown="1">

```python
result = check_source_drift(
    source_result["table_id"],
    target_table_id=target_table_id,
)
result["target_table_id"] == target_table_id
```

```text
True
```

</div>

## Returns

dict
    Source Drift evidence for the source-to-target relationship and its
    compatibility with the source's governed load behaviour.

## Raises / Errors

ValueError
    If either identity, transient observation, rule, or source processing
    definition is invalid.
RuntimeError
    If metadata history cannot be read, or ``raise_on_failure=True`` and
    the target cannot safely reconcile the observed source change.

## Notes

<div class="reference-docstring-notes" markdown="1">

Notebook orchestration calls this function explicitly for every governed
source before :func:`pipeline_write`. A successful write then commits the
accepted source-to-target baseline in ``METADATA_SOURCE_OBSERVATION``.

</div>

## Behavior and scope

<div class="reference-docstring-intro" markdown="1">

Compare the current source observation with the last source observation
successfully consumed by this target and detect source changes that violate
the source table's governed load behaviour.

</div>

## See also

No related guides documented.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/pipeline/check_source_drift.py:17`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline/check_source_drift.py#L17-L201">View on GitHub</a>
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
