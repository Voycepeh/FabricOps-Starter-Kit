# FabricStore


Configured Fabric lakehouse or warehouse connection details.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/config/public.py:24`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/public.py#L24-L61">View on GitHub</a>
</div>

<p class="reference-catalogue-item-meta reference-catalogue-item-badges">
<span class="reference-chip">Public Starter Kit function</span>
<span class="reference-chip">00_env_config</span>
</p>

**Used in notebooks:** `00_env_config`

## Usage guidance

### Additional context

Supports the public root import contract for FabricOps notebook configuration.


## Signature

<div class="reference-api-definition" markdown="1">

```python
class FabricStore
```

</div>

## Example usage

Example usage not documented yet.

## Parameters

No parameters.

## Returns

Validated FabricStore configuration object.

## Raises / Errors

ValueError for missing identifiers, unsupported store kind, or invalid schema names.

### Common failure causes

- Required configuration values are missing or invalid.

## Glossary

<div class="reference-glossary-term-list" aria-label="Glossary terms used on this page">
<span class="glossary-chip"><span class="glossary-chip-label">Metadata lakehouse</span><span class="glossary-chip-definition">Configured Fabric Lakehouse target where FabricOps stores metadata tables.</span> <a href="../../../reference/glossary/#metadata-lakehouse">Full definition</a></span>
</div>

See the [full glossary](../../../reference/glossary/) for more FabricOps terms.

## See also

No related guides documented.
