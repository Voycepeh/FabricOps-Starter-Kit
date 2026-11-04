# `restore_pipeline`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

Preserve changed code and restore the exact active notebook snapshot.



## Example usage

<div class="reference-example-usage" markdown="1">

```python
result = restore_pipeline(PIPELINE_ID, expected_active_version=1,
    governance_confirmed=True)
```

</div>

<details class="reference-signature-details" markdown="1">
<summary>Signature</summary>

## Signature

<div class="reference-api-definition" markdown="1">

```python
def restore_pipeline(
    pipeline_id: str,
    *,
    expected_active_version: int,
    workspace_id: str | None=None,
    governance_confirmed: bool=False,
) -> dict:
```

</div>

</details>

## Parameters

Required describes the Python signature. An optional parameter may still be needed for the selected mode or identity form; see its description. `—` means no signature default.

<div class="reference-input-table" markdown="1">

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `pipeline_id` | `str` | Yes | `—` | Stable logical Pipeline ID. |
| `expected_active_version` | `int` | Yes | `—` | Reviewed active version; an intervening promotion cancels restoration. |
| `workspace_id` | `str \| None` | No | `None` | Destination execution workspace, defaulting to the notebook scope. |
| `governance_confirmed` | `bool` | No | `False` | Explicit review confirmation; actual Fabric permissions authorize repair. |

</div>

## Returns

dict
    Existing promotion/version, preserved changed-copy URI and readiness gate.

## Raises / Errors

ValueError
    If review is stale, ambiguous or unconfirmed.
RuntimeError
    If archive, bindings, preservation, update or readback verification fails.

## Notes

<div class="reference-docstring-notes" markdown="1">

No approval is rewritten and no new version is created. Different code needs
a new manual Dry Run and promotion. Imported dependencies are not restored.
Tenant permissions remain the security boundary; saved-code checks have TOCTOU.

</div>

## See also

No related guides documented.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/activated_pipeline/restore_pipeline.py:5`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/activated_pipeline/restore_pipeline.py#L5-L51">View on GitHub</a>
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
