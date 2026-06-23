# setup_notebook


Shared environment setup and runtime validation for notebook templates.

<p class="reference-catalogue-item-meta reference-catalogue-item-badges">
<span class="reference-chip">Public Starter Kit function</span>
<span class="reference-chip">00_env_config</span>
</p>

**Used in notebooks:** `00_env_config`

## Source

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L1016-L1070">View source on GitHub</a>

Implemented in `src/fabricops_kit/config.py`:1016.

## Usage guidance

### Use when

- Starting a FabricOps notebook from 00_env_config
- Validating configured environment targets before downstream helpers run
- Capturing runtime metadata for later lineage, review, or handover steps

### Do not use when

- Do not use as a replacement for metadata table setup or per-table governance writes; call setup_metadata_tables for metadata storage preparation.

### Additional context

Validates the selected FabricOps environment, resolves configured runtime targets, and returns the notebook context that downstream helpers depend on.


## Signature

<div class="reference-api-definition" markdown="1">

```python
def setup_notebook(
    config: FrameworkConfig | dict[str, Any],
    env: str='Sandbox',
    required_targets: list[str] | None=None,
    notebook_name: str | None=None,
    run_id_prefix: str='run',
    local_fallback_name: str | None=None,
) -> NotebookSetupContext:
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

```python
context = setup_notebook(CONFIG, env="Sandbox", required_targets=["Source", "Unified"], notebook_name="00_env_config")
```

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `config` | `FrameworkConfig \| dict[str, Any]` | Yes | Framework configuration object or compatible mapping. The setup flow validates required sections and configured Fabric targets before running readiness checks. |
| `env` | `str` | No | Environment key used to resolve target paths. |
| `required_targets` | `list[str] \| None` | No | Target names that must resolve for ``env``. Defaults to ``["Source", "Unified"]``. |
| `notebook_name` | `str \| None` | No | Explicit notebook name used for runtime metadata and naming checks. |
| `run_id_prefix` | `str` | No | Prefix used when a Fabric runtime run identifier is unavailable. |
| `local_fallback_name` | `str \| None` | No | Notebook name used when neither ``notebook_name`` nor Fabric runtime context provides one. |

## Returns

NotebookSetupContext with resolved configuration paths, runtime metadata, smoke-check results, and readiness status.

### Return interpretation

A ready context means required targets resolved and runtime checks passed. Review validation messages before running downstream cells when readiness is not successful.

## Raises / Errors

ValueError for invalid configuration sections, missing required paths, or unresolved required targets.

### Common failure causes

- The environment name is not present in CONFIG.
- Required targets are missing from path configuration.
- Fabric runtime metadata is unavailable and no local fallback was provided.
- Configured lakehouse or warehouse targets cannot be resolved.

## Glossary

<div class="reference-glossary-term-list" aria-label="Glossary terms used on this page">
<span class="glossary-chip"><span class="glossary-chip-label">Notebook template</span><span class="glossary-chip-definition">Reusable starter notebook workflow that shows how to run a FabricOps phase.</span> <a href="../../../reference/glossary/#notebook-template">Full definition</a></span>
<span class="glossary-chip"><span class="glossary-chip-label">Metadata lakehouse</span><span class="glossary-chip-definition">Configured Fabric Lakehouse target where FabricOps stores metadata tables.</span> <a href="../../../reference/glossary/#metadata-lakehouse">Full definition</a></span>
</div>

See the [full glossary](../../../reference/glossary/) for more FabricOps terms.

## See also

- [Notebook Templates Implementation Guide](../../notebook-templates-implementation-guide/index.md)
- [Metadata Tables](../../reference/metadata.md)
