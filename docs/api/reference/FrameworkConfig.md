# FrameworkConfig


Top-level FabricOps framework configuration.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/config/shared.py:395`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/shared.py#L395-L424">View on GitHub</a>
</div>

<p class="reference-catalogue-item-meta reference-catalogue-item-badges">
<span class="reference-chip">Public Starter Kit function</span>
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
class FrameworkConfig
```

</div>

## Example usage

Example usage not documented yet.

## Parameters

No parameters.

## Returns

Validated FrameworkConfig object.

### Return interpretation

Use the returned value as part of the supported FabricOps configuration surface.

## Raises / Errors

ValueError for invalid audit timezone.

### Common failure causes

- Required configuration values are missing or invalid.

## Glossary

<div class="reference-glossary-term-list" aria-label="Glossary terms used on this page">
<span class="glossary-chip"><span class="glossary-chip-label">Metadata lakehouse</span><span class="glossary-chip-definition">Configured Fabric Lakehouse target where FabricOps stores metadata tables.</span> <a href="../../../reference/glossary/#metadata-lakehouse">Full definition</a></span>
</div>

See the [full glossary](../../../reference/glossary/) for more FabricOps terms.

## See also

No related guides documented.
