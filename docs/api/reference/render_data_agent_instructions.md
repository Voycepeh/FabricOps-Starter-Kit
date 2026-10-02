# `render_data_agent_instructions`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
<span class="reference-chip reference-chip-muted">Public function</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

Render concise deterministic instructions for a native Fabric Data Agent.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/data_agent/render_data_agent_instructions.py:8`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agent/render_data_agent_instructions.py#L8-L43">View on GitHub</a>
</div>

<p class="reference-catalogue-item-meta reference-catalogue-item-badges">
<span class="reference-chip">Public Starter Kit function</span>
<span class="reference-chip">Usage detection may exclude indirect or generated references.</span>
</p>

**Used in notebooks:** Usage detection may exclude indirect or generated references.

## Usage notes

Do not use to reinterpret or author governed metadata.


## Signature

<div class="reference-api-definition" markdown="1">

```python
def render_data_agent_instructions(
    consumer_context: Mapping[str, Any],
) -> dict[str, str]:
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

>>> instructions = render_data_agent_instructions({"source": {"table": "orders", "schema": "dbo"}, "columns": []})
>>> "dbo.orders" in instructions["datasource"]
True

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `consumer_context` | `Mapping[str, Any]` | Yes | Context returned by :func:`build_consumer_context`. |

## Returns

Separate agent-level and datasource-level instruction strings.

## Raises / Errors

Raises KeyError for missing required source context.

## Notes

<div class="reference-docstring-notes" markdown="1">

Rendering is deterministic and invokes no AI service. The output contains no
tokens, credentials, or profile sample values.

</div>

## See also

No related guides documented.


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
