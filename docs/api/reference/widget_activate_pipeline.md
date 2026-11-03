# `widget_activate_pipeline`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

Inspect direct activations and the pending Governed deployment gate.


## Usage notes

Use to inspect migrated pipeline candidates and independent Contract activations.


## Example usage

<div class="reference-example-usage" markdown="1">

```python
review = widget_activate_pipeline()
reviewed_token = review["token"]
```

</div>

<details class="reference-signature-details" markdown="1">
<summary>Signature</summary>

## Signature

<div class="reference-api-definition" markdown="1">

```python
def widget_activate_pipeline(*, pipeline_id=None, context=None) -> dict[str, Any]
```

</div>

</details>

## Parameters

Required describes the Python signature. An optional parameter may still be needed for the selected mode or identity form; see its description. `—` means no signature default.

<div class="reference-input-table" markdown="1">

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `pipeline_id` | `str \| None` | No | `None` | Filter pipeline records by stable logical UUIDv4. |
| `context` | `dict \| None` | No | `None` | Existing FabricOps context; central Metadata routing is preserved. |

</div>

## Returns

dict
    Widget, scoped activation records, reviewed control token and readiness
    reason. Opening the widget changes no metadata or publication authority.

## Raises / Errors

ValueError
    If identity or the Registry is missing, corrupt or ambiguous.
RuntimeError
    If notebook/Spark/widget services are unavailable.

## Notes

<div class="reference-docstring-notes" markdown="1">

Use activate_data_contract for independent frozen Contract activation after
review. Tenant permissions must restrict governance writes to trusted actors.
This inspection UI does not authenticate or attest a deployment.

</div>

## Behavior and scope

<div class="reference-docstring-intro" markdown="1">

The previous Test/approval/version-selection lifecycle is removed. Migrated
pipelines are requires_reactivation candidates, never verified deployments.
Pipeline activation and Governed publication remain disabled until a tenant-
proven trusted deployment mechanism is integrated. A Git SHA typed into a
widget cannot satisfy this requirement.

</div>

## See also

No related guides documented.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/widgets/widget_activate_pipeline.py:13`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/widgets/widget_activate_pipeline.py#L13-L82">View on GitHub</a>
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
| Preview | 0.3.0 |
| Preview | 0.3.1 |


</details>
