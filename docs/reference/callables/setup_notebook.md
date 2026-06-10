# setup_notebook

Shared environment setup and runtime validation for notebook templates.

## What this is for and when to use it

Prepare a FabricOps notebook by validating configuration, resolving environment targets, and returning reusable runtime context.

- Starting a FabricOps notebook from 00_env_config
- Validating configured environment targets before downstream helpers run
- Capturing runtime metadata for later lineage, review, or handover steps

## When not to use it

- Do not use as a replacement for metadata table setup or per-table governance writes; call setup_metadata_tables for metadata storage preparation.

## Example

```python
context = setup_notebook(CONFIG, env="Sandbox", required_targets=["Source", "Unified"], notebook_name="00_env_config")
```

## Inputs

<div class="module-table-scroll reference-input-table">
<table class="reference-function-table">
  <thead>
    <tr>
      <th>Parameter</th>
      <th>Required</th>
      <th>Meaning</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td data-label="Parameter"><code>config</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">Framework configuration object or compatible mapping. The setup flow validates required sections and configured Fabric targets before running readiness checks.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>env</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Environment key used to resolve target paths.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>required_targets</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Target names that must resolve for ``env``. Defaults to ``[&quot;Source&quot;, &quot;Unified&quot;]``.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>notebook_name</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Explicit notebook name used for runtime metadata and naming checks.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>run_id_prefix</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Prefix used when a Fabric runtime run identifier is unavailable.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>local_fallback_name</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Notebook name used when neither ``notebook_name`` nor Fabric runtime context provides one.</td>
    </tr>
  </tbody>
</table>
</div>

## Output

NotebookSetupContext with resolved configuration paths, runtime metadata, smoke-check results, and readiness status.

## Errors and side effects

**Errors:** ValueError for invalid configuration sections, missing required paths, or unresolved required targets.

**Side effects:** Runs configuration validation and Fabric readiness checks; it does not write FabricOps metadata tables.

## Related functions

- <a href="../setup_metadata_tables/"><code>fabricops_kit.config.setup_metadata_tables</code></a>

<details class="reference-implementation-details">
<summary>Implementation details</summary>

- <a href="../internal/config_NotebookSetupContext/"><code>fabricops_kit.config.NotebookSetupContext</code></a>
- <a href="../internal/config__get_store/"><code>fabricops_kit.config._get_store</code></a>
- <a href="../internal/config__run_config_smoke_tests/"><code>fabricops_kit.config._run_config_smoke_tests</code></a>
- <a href="../internal/config__validate_framework_config/"><code>fabricops_kit.config._validate_framework_config</code></a>

</details>

## Source

- Source file path: `src/fabricops_kit/config.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/6d8de4b3e35399458b9ee2a79568a6d6f1831a4e/src/fabricops_kit/config.py#L707-L816">View setup_notebook on GitHub</a>

<details class="reference-source-details">
<summary>Show source code</summary>

```python
def setup_notebook(
    config: FrameworkConfig | dict[str, Any],
    env: str = "Sandbox",
    required_targets: list[str] | None = None,
    notebook_name: str | None = None,
    run_id_prefix: str = "run",
    local_fallback_name: str | None = None,
) -> NotebookSetupContext:
    """Run consolidated FabricOps startup for delivery and optional support notebooks.

    Parameters
    ----------
    config : FrameworkConfig | dict[str, Any]
        Framework configuration object or compatible mapping. The setup flow
        validates required sections and configured Fabric targets before
        running readiness checks.
    env : str, default="Sandbox"
        Environment key used to resolve target paths.
    required_targets : list[str] | None, optional
        Target names that must resolve for ``env``. Defaults to
        ``["Source", "Unified"]``.
    notebook_name : str | None, optional
        Explicit notebook name used for runtime metadata and naming checks.
    run_id_prefix : str, default="run"
        Prefix used when a Fabric runtime run identifier is unavailable.
    local_fallback_name : str | None, optional
        Notebook name used when neither ``notebook_name`` nor Fabric runtime
        context provides one.

    Returns
    -------
    NotebookSetupContext
        Validated runtime context with resolved paths, smoke-check results,
        runtime metadata, and overall readiness status.

    Raises
    ------
    ValueError
        Raised when config sections are invalid or required targets cannot be
        resolved for the selected environment.

    Notes
    -----
    Validation and smoke checks are local to notebook startup. This helper does
    not provision Fabric resources or persist metadata.
    """
    from uuid import uuid4
    from datetime import datetime, timezone

    normalized = _validate_framework_config(config)
    required_targets = required_targets or ["Source", "Unified"]
    resolved_paths = {target: _get_store(config=normalized, env=env, target=target) for target in required_targets}

    context = None
    try:
        import notebookutils.runtime as nb_runtime  # type: ignore

        context = getattr(nb_runtime, "context", None)
    except Exception:
        context = None

    def ctx(key: str) -> Any:
        if context is None:
            return None
        if isinstance(context, dict):
            return context.get(key)
        get_method = getattr(context, "get", None)
        if callable(get_method):
            try:
                return get_method(key)
            except Exception:
                return None
        return getattr(context, key, None)

    resolved_notebook_name = notebook_name or ctx("currentNotebookName") or local_fallback_name
    user_name = ctx("userName") or ctx("userId") or "unknown"
    run_id = (
        ctx("currentRunId")
        or f"{run_id_prefix}_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}_{uuid4().hex[:8]}"
    )

    runtime_meta = {
        "notebook_name": resolved_notebook_name,
        "workspace_name": ctx("currentWorkspaceName"),
        "workspace_id": ctx("currentWorkspaceId"),
        "user_name": user_name,
        "user_id": ctx("userId"),
        "current_run_id": ctx("currentRunId"),
        "is_for_pipeline": ctx("isForPipeline"),
        "is_for_interactive": ctx("isForInteractive"),
        "is_reference_run": ctx("isReferenceRun"),
        "runtime_available": context is not None,
    }

    checks = _run_config_smoke_tests(
        config=normalized, env=env, required_targets=required_targets, notebook_name=resolved_notebook_name
    )
    readiness_status = "ready" if all(r.status in {"pass", "warn", "skipped"} for r in checks) else "not_ready"

    return NotebookSetupContext(
        run_id=str(run_id),
        notebook_name=resolved_notebook_name,
        workspace_name=runtime_meta.get("workspace_name"),
        user_name=str(user_name),
        environment=env,
        paths=resolved_paths,
        validation_results=checks,
        runtime_metadata=runtime_meta,
        readiness_status=readiness_status,
    )
```

</details>

<details class="reference-metadata-details">
<summary>AI / machine-readable metadata — skip this if you are reading the docs normally</summary>

These generated fields are for automation, AI agents, maintainers, and doc tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.config.setup_notebook`
- Short name: `setup_notebook`
- Module: `config`
- Classification: Callable
- Related module: `config`
- Source file path: `src/fabricops_kit/config.py`
- Source line: `707`
- Inbound references count: 0
- Outbound references count: 4

### AI implementation contract

- **required_context:** Requires the FrameworkConfig or compatible CONFIG from 00_env_config plus the intended env name; never hardcode Fabric workspace or item identifiers.
- **inputs:** config, env, optional required_targets, notebook_name, run_id_prefix, and local_fallback_name that define the runtime setup context.
- **output:** NotebookSetupContext with resolved configuration paths, runtime metadata, smoke-check results, and readiness status.
- **side_effects:** Runs configuration validation and Fabric readiness checks; it does not write FabricOps metadata tables.
- **failure_modes:** ValueError for invalid configuration sections, missing required paths, or unresolved required targets.
- **verification:** Verify the returned context is ready before generating downstream notebook code and confirm required targets resolve for the selected env.

### Inbound references

Not documented yet

### Outbound references

- <a href="../internal/config_NotebookSetupContext/"><code>fabricops_kit.config.NotebookSetupContext</code></a>
- <a href="../internal/config__get_store/"><code>fabricops_kit.config._get_store</code></a>
- <a href="../internal/config__run_config_smoke_tests/"><code>fabricops_kit.config._run_config_smoke_tests</code></a>
- <a href="../internal/config__validate_framework_config/"><code>fabricops_kit.config._validate_framework_config</code></a>

### Raw source metadata

- Source file path: `src/fabricops_kit/config.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/6d8de4b3e35399458b9ee2a79568a6d6f1831a4e/src/fabricops_kit/config.py#L707-L816">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/6d8de4b3e35399458b9ee2a79568a6d6f1831a4e/src/fabricops_kit/config.py#L707-L816</a>
- Start line: `707`
- End line: `816`
- Signature:

```python
def setup_notebook(config: FrameworkConfig | dict[str, Any], env: str='Sandbox', required_targets: list[str] | None=None, notebook_name: str | None=None, run_id_prefix: str='run', local_fallback_name: str | None=None) -> NotebookSetupContext
```

### Internal relationship graph

### Public related functions

- <a href="../setup_metadata_tables/"><code>fabricops_kit.config.setup_metadata_tables</code></a>

### Internal implementation helpers

- <a href="../internal/config_NotebookSetupContext/"><code>fabricops_kit.config.NotebookSetupContext</code></a>
- <a href="../internal/config__get_store/"><code>fabricops_kit.config._get_store</code></a>
- <a href="../internal/config__run_config_smoke_tests/"><code>fabricops_kit.config._run_config_smoke_tests</code></a>
- <a href="../internal/config__validate_framework_config/"><code>fabricops_kit.config._validate_framework_config</code></a>

</details>
