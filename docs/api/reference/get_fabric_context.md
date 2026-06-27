# get_fabric_context

??? info "Downstream callables: 1"

    Dependency data is generated from the callable architecture inventory.

    <div class="reference-call-tree" role="tree" data-callable-architecture-flow="true">
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix"></span><code>get_fabric_context(...)</code></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">└── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/shared.py#L25-L82"><code>get_default_fabric_context(...)</code></a></div>
    </div>

Build a Fabric context from explicit values or the active default.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/config/get_fabric_context.py:12`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/get_fabric_context.py#L12-L64">View on GitHub</a>
</div>

<p class="reference-catalogue-item-meta reference-catalogue-item-badges">
<span class="reference-chip">Public Starter Kit function</span>
<span class="reference-chip">Usage detection may exclude indirect or generated references.</span>
</p>

**Used in notebooks:** Usage detection may exclude indirect or generated references.

## Usage guidance

### Use when

- Use through the supported FabricOps root import surface.

### Additional context

Supports the public root import contract for FabricOps notebook configuration.


## Signature

<div class="reference-api-definition" markdown="1">

```python
def get_fabric_context(
    env: str | None=None,
    config: Any=None,
    workspace_id: str | None=None,
    lakehouse_id: str | None=None,
    workspace_name: str | None=None,
    lakehouse_name: str | None=None,
    **values: Any,
) -> dict[str, Any]:
```

</div>

## Example usage

Example usage not documented yet.

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `env` | `str \| None` | No | Environment key to use. Defaults to the active ``00_env_config`` value. |
| `config` | `Any` | No | FrameworkConfig or compatible config object. Defaults to the active ``00_env_config`` value. |
| `workspace_id` | `str \| None` | No | Workspace ID override for advanced cross-workspace usage. |
| `lakehouse_id` | `str \| None` | No | Lakehouse item ID override for advanced usage. |
| `workspace_name` | `str \| None` | No | Workspace name override. |
| `lakehouse_name` | `str \| None` | No | Lakehouse name override. **values Additional context values to merge into the returned dictionary. |

## Returns

Fabric context dictionary containing config and env.

### Return interpretation

Use the returned value as part of the supported FabricOps configuration surface.

## Raises / Errors

RuntimeError when config or env cannot be resolved.

### Common failure causes

- Required configuration values are missing or invalid.

## Glossary

<div class="reference-glossary-term-list" aria-label="Glossary terms used on this page">
<span class="glossary-chip"><span class="glossary-chip-label">Notebook template</span><span class="glossary-chip-definition">Reusable starter notebook workflow that shows how to run a FabricOps phase.</span> <a href="../../../reference/glossary/#notebook-template">Full definition</a></span>
</div>

See the [full glossary](../../../reference/glossary/) for more FabricOps terms.

## See also

No related guides documented.
