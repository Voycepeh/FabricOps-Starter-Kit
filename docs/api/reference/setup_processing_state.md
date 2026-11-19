# `setup_processing_state`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

Create or validate the private Processing State Delta store.

<p class="reference-catalogue-item-meta reference-catalogue-item-badges">
<span class="reference-chip">00_env_config</span>
</p>

## Usage notes

Run as the Lakehouse owner to initialize Processing State before running pipelines.


## Example usage

<div class="reference-example-usage" markdown="1">

```python
setup_processing_state(config=CONFIG, workspace_id=WORKSPACE_ID)
```

```text
{'status': 'created', 'path': 'Files/fabricops/misc/processing_state'}
```

</div>

<details class="reference-signature-details" markdown="1">
<summary>Signature</summary>

## Signature

<div class="reference-api-definition" markdown="1">

```python
def setup_processing_state(
    *,
    config: FrameworkConfig | dict[str, Any],
    workspace_id: str,
) -> dict[str, Any]:
```

</div>

</details>

## Parameters

Required describes the Python signature. An optional parameter may still be needed for the selected mode or identity form; see its description. `—` means no signature default.

<div class="reference-input-table" markdown="1">

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `config` | `FrameworkConfig \| dict[str, Any]` | Yes | `—` | Configuration containing the shared Metadata Lakehouse. |
| `workspace_id` | `str` | Yes | `—` | Configuration scope used to resolve that Lakehouse. |

</div>

## Returns

dict[str, Any]
    Status (created or validated) and the Lakehouse-relative path.

### Return interpretation

Created indicates an empty store was initialized. Validated indicates an existing store was checked.

## Raises / Errors

RuntimeError
    If the existing store has an incompatible schema.
    Spark and storage errors also propagate.

### Common failure causes

- The existing store has an incompatible schema.
- The caller lacks access to the shared Lakehouse.

## Notes

<div class="reference-docstring-notes" markdown="1">

Run under the Lakehouse owner's identity. Initial creation starts with empty
Processing State. Repeated setup preserves rows already in the private store.

</div>

## See also

- [Processing State setup](../../maintainer/processing-state.md)

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/config/setup_processing_state.py:12`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/setup_processing_state.py#L12-L71">View on GitHub</a>
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
