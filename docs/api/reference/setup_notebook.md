# setup_notebook

Shared environment setup and runtime validation for notebook templates.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/config.py:674`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/5b9215c3af8eef0a6cb6a107b64631a41feb48a4/src/fabricops_kit/config.py#L674-L784">View on GitHub</a>
</div>

<details class="reference-usage-details">
<summary>Usage guidance</summary>

**Use when:**

- Starting a FabricOps notebook from 00_env_config
- Validating configured environment targets before downstream helpers run
- Capturing runtime metadata for later lineage, review, or handover steps

**Do not use when:**

- Do not use as a replacement for metadata table setup or per-table governance writes; call setup_metadata_tables for metadata storage preparation.

**Additional context:**

Validates the selected FabricOps environment, resolves configured runtime targets, and returns the notebook context that downstream helpers depend on.

</details>

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

## Relationships

### Used by

Not documented yet

### Calls

- `fabricops_kit.config.NotebookSetupContext`
- `fabricops_kit.config._get_store`
- `fabricops_kit.config._run_config_smoke_tests`
- `fabricops_kit.config._validate_framework_config`

## Implementation details

<details class="reference-implementation-details">
<summary>Notes, side effects, and template usage</summary>

**Used in templates:**

Direct starter notebook code-cell invocations only; import-only, markdown-only, generated metadata, and internal helper calls are not counted.

- `00_env_config`

**Side effects:**

Runs configuration validation and Fabric readiness checks; it does not write FabricOps metadata tables.

**Notes:**

Validation and smoke checks are local to notebook startup. This helper does
not provision Fabric resources or persist metadata.

</details>

??? info "Call flow"

    ```text
    setup_notebook(...)
    ├── _get_store(...)
    │   └── _normalize_path_config(...)
    │       └── PathConfig(...)
    ├── _run_config_smoke_tests(...)
    │   ├── _check_spark_session(...)
    │   ├── _get_fabric_runtime_metadata(...)
    │   ├── _get_store(...)
    │   │   └── _normalize_path_config(...)
    │   │       └── PathConfig(...)
    │   ├── _validate_notebook_name(...)
    │   └── ConfigSmokeCheckResult(...)
    ├── _validate_framework_config(...)
    │   ├── _validate_audit_timezone(...)
    │   └── FrameworkConfig(...)
    └── NotebookSetupContext(...)
    ```

??? info "Internal helpers used: 8"

    This callable uses 8 internal helpers for audit timestamp, metadata loading, validation, rule parsing, and fabric or spark access.

    <div class="reference-helper-groups">
      <section class="reference-helper-group">
        <h4>Audit timestamp</h4>
        <p>Resolve and stamp audit time consistently.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/5b9215c3af8eef0a6cb6a107b64631a41feb48a4/src/fabricops_kit/config.py#L23-L55"><code>_validate_audit_timezone</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Metadata loading</h4>
        <p>Load and identify the metadata or table context needed by the callable.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/5b9215c3af8eef0a6cb6a107b64631a41feb48a4/src/fabricops_kit/config.py#L1167-L1206"><code>_get_fabric_runtime_metadata</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Validation</h4>
        <p>Validate inputs and guard conditions before the workflow continues.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/5b9215c3af8eef0a6cb6a107b64631a41feb48a4/src/fabricops_kit/config.py#L1159-L1164"><code>_check_spark_session</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/5b9215c3af8eef0a6cb6a107b64631a41feb48a4/src/fabricops_kit/config.py#L571-L671"><code>_run_config_smoke_tests</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/5b9215c3af8eef0a6cb6a107b64631a41feb48a4/src/fabricops_kit/config.py#L398-L469"><code>_validate_framework_config</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/5b9215c3af8eef0a6cb6a107b64631a41feb48a4/src/fabricops_kit/config.py#L557-L568"><code>_validate_notebook_name</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Rule parsing</h4>
        <p>Normalize stored or user-provided values before applying rules.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/5b9215c3af8eef0a6cb6a107b64631a41feb48a4/src/fabricops_kit/config.py#L472-L512"><code>_normalize_path_config</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Fabric or Spark access</h4>
        <p>Access Fabric or Spark runtime services used by the implementation.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/5b9215c3af8eef0a6cb6a107b64631a41feb48a4/src/fabricops_kit/config.py#L515-L554"><code>_get_store</code></a>
        </div>
      </section>
    </div>

<details class="reference-metadata-details">
<summary>Machine-readable metadata / metadata details</summary>

These generated fields are for automation tooling, maintainers, and documentation tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.config.setup_notebook`
- Short name: `setup_notebook`
- Module: `config`
- Classification: Callable
- Related module: `config`
- Source file path: `src/fabricops_kit/config.py`
- Source line: `674`
- Inbound references count: 0
- Outbound references count: 4
- Used in templates: 00_env_config
- Glossary terms: notebook template, metadata lakehouse

### Implementation contract

- **required_context:** Requires the FrameworkConfig or compatible CONFIG from 00_env_config plus the intended env name; never hardcode Fabric workspace or item identifiers.
- **inputs:** config, env, optional required_targets, notebook_name, run_id_prefix, and local_fallback_name that define the runtime setup context.
- **output:** NotebookSetupContext with resolved configuration paths, runtime metadata, smoke-check results, and readiness status.
- **side_effects:** Runs configuration validation and Fabric readiness checks; it does not write FabricOps metadata tables.
- **failure_modes:** ValueError for invalid configuration sections, missing required paths, or unresolved required targets.
- **verification:** Verify the returned context is ready before generating downstream notebook code and confirm required targets resolve for the selected env.

### Inbound references

Not documented yet

### Outbound references

- `fabricops_kit.config.NotebookSetupContext`
- `fabricops_kit.config._get_store`
- `fabricops_kit.config._run_config_smoke_tests`
- `fabricops_kit.config._validate_framework_config`

### Raw source metadata

- Source file path: `src/fabricops_kit/config.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/5b9215c3af8eef0a6cb6a107b64631a41feb48a4/src/fabricops_kit/config.py#L674-L784">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/5b9215c3af8eef0a6cb6a107b64631a41feb48a4/src/fabricops_kit/config.py#L674-L784</a>
- Start line: `674`
- End line: `784`
- Signature:

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

### Internal relationship graph

### Public related functions

- <a href="../setup_metadata_tables/"><code>fabricops_kit.config.setup_metadata_tables</code></a>

### Internal implementation summary

- Internal helper count: 8
- Grouped helper summary is rendered in the page-level Implementation details section; helper chips link to source.

</details>

## Glossary

- **Notebook template:** A starter notebook that shows where and how FabricOps helpers are used.
- **Metadata lakehouse:** The configured Fabric lakehouse where FabricOps stores governance and runtime metadata.

See the [full glossary](../../../reference/glossary/) for more FabricOps terms.

## See also

- [Notebook Templates](../../how-fabricops-works/notebook-templates.md)
- [Metadata Tables](../../how-fabricops-works/metadata-tables.md)
