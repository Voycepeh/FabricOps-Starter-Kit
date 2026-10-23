# `migrate_workspace_config`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

Convert existing mappings into reviewed registrations without writing metadata.



## Example usage

<div class="reference-example-usage" markdown="1">

```python
registrations = migrate_workspace_config(old_config, assignments=assignments)
```

</div>

<details class="reference-signature-details" markdown="1">
<summary>Signature</summary>

## Signature

<div class="reference-api-definition" markdown="1">

```python
def migrate_workspace_config(config, *, assignments: list[dict]) -> list[dict]
```

</div>

</details>

## Parameters

Required describes the Python signature. An optional parameter may still be needed for the selected mode or identity form; see its description. `—` means no signature default.

<div class="reference-input-table" markdown="1">

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `config` | `FrameworkConfig` | Yes | `—` | Existing environment mappings and governance settings. |
| `assignments` | `list[dict]` | Yes | `—` | Explicit workspace and deployment environment assignments; no inference. |

</div>

## Returns

list[dict]
    Complete validated registrations for administrator review and publication.

## Raises / Errors

Not documented yet

## Behavior and scope

<div class="reference-docstring-intro" markdown="1">

Preserve contract identities, frozen payloads and historical records. Each
assignment supplies legacy_environment, workspace_id, display_name,
environment (DEV/TEST/PROD), notebooks and status. Multiple assignments may
reference one legacy environment, but approvals are never copied implicitly.
Publish reviewed registrations through register_workspace. Physical Warehouse
names fall back to their previous logical key during migration.

</div>

## See also

No related guides documented.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/config/migrate_workspace_config.py:7`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/migrate_workspace_config.py#L7-L49">View on GitHub</a>
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
