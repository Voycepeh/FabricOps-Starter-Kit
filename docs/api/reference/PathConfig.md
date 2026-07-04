# PathConfig


Environment-to-target mapping used for lakehouse and warehouse routing.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/config/shared.py:257`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/shared.py#L257-L278">View on GitHub</a>
</div>

<p class="reference-catalogue-item-meta reference-catalogue-item-badges">
<span class="reference-chip">Public config class</span>
<span class="reference-chip">00_env_config</span>
</p>

**Used in notebooks:** `00_env_config`

## Usage guidance

### Use when

- Use through the supported FabricOps root import surface.

### Additional context

Supports the public root import contract for FabricOps notebook configuration.


## Signature

<div class="reference-api-definition" markdown="1">

```python
class PathConfig
```

</div>

## Example usage

Example usage not documented yet.

## Parameters

No parameters.

## Returns

Validated PathConfig object.

### Return interpretation

Use the returned value as part of the supported FabricOps configuration surface.

## Raises / Errors

ValueError when paths is empty or not a mapping.

### Common failure causes

- Required configuration values are missing or invalid.

## See also

No related guides documented.
