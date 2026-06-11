# setup_notebook

Shared environment setup and runtime validation for notebook templates.

## Purpose

Prepare a FabricOps notebook by validating configuration, resolving environment targets, and returning reusable runtime context.

## At a glance

**Use when:**

- Starting a FabricOps notebook from 00_env_config
- Validating configured environment targets before downstream helpers run
- Capturing runtime metadata for later lineage, review, or handover steps

**Do not use when:**

- Do not use as a replacement for metadata table setup or per-table governance writes; call setup_metadata_tables for metadata storage preparation.

**Example:**

```python
context = setup_notebook(CONFIG, env="Sandbox", required_targets=["Source", "Unified"], notebook_name="00_env_config")
```

**Errors:**

ValueError for invalid configuration sections, missing required paths, or unresolved required targets.

**Side effects:**

Runs configuration validation and Fabric readiness checks; it does not write FabricOps metadata tables.

## Used by

Not documented yet

## Calls

- `fabricops_kit.config.NotebookSetupContext`
- `fabricops_kit.config._get_store`
- `fabricops_kit.config._run_config_smoke_tests`
- `fabricops_kit.config._validate_framework_config`

??? info "Call flow"

    ```text
    setup_notebook(...)
    ├── _get_store(...)
    ├── _run_config_smoke_tests(...)
    │   ├── _check_spark_session(...)
    │   ├── _get_fabric_runtime_metadata(...)
    │   ├── _get_store(...)
    │   ├── _validate_notebook_name(...)
    │   └── ConfigSmokeCheckResult(...)
    ├── _validate_framework_config(...)
    │   ├── _validate_audit_timezone(...)
    │   └── FrameworkConfig(...)
    └── NotebookSetupContext(...)
    ```

## Callable implementation

### Function details

- Module: `config`
- Classification: Callable
- Source file path: `src/fabricops_kit/config.py`
- Source line: `786`
- Signature:

```python
def setup_notebook(config: FrameworkConfig | dict[str, Any], env: str='Sandbox', required_targets: list[str] | None=None, notebook_name: str | None=None, run_id_prefix: str='run', local_fallback_name: str | None=None) -> NotebookSetupContext
```

### Parameters

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

### Returns

NotebookSetupContext with resolved configuration paths, runtime metadata, smoke-check results, and readiness status.

### Notes

Validation and smoke checks are local to notebook startup. This helper does
not provision Fabric resources or persist metadata.

### Public callable source code

- Source file path: `src/fabricops_kit/config.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1e1b315d5b95935a662818da57af236b37c14595/src/fabricops_kit/config.py#L786-L895">View setup_notebook on GitHub</a>

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

## Internal implementation summary

??? info "Internal helpers used: 7"

    This callable uses 7 internal helpers for audit timestamp, metadata loading, validation, and fabric or spark access.

    <div class="module-table-scroll reference-input-table">
    <table class="reference-function-table">
      <thead>
        <tr>
          <th>Area</th>
          <th>Helpers</th>
          <th>What they do</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td data-label="Area">Audit timestamp</td>
          <td data-label="Helpers"><code>_validate_audit_timezone</code></td>
          <td data-label="What they do">Resolve and stamp audit time consistently.</td>
        </tr>
        <tr>
          <td data-label="Area">Metadata loading</td>
          <td data-label="Helpers"><code>_get_fabric_runtime_metadata</code></td>
          <td data-label="What they do">Load and identify the metadata or table context needed by the callable.</td>
        </tr>
        <tr>
          <td data-label="Area">Validation</td>
          <td data-label="Helpers"><code>_check_spark_session</code>, <code>_run_config_smoke_tests</code>, <code>_validate_framework_config</code>, <code>_validate_notebook_name</code></td>
          <td data-label="What they do">Validate inputs and guard conditions before the workflow continues.</td>
        </tr>
        <tr>
          <td data-label="Area">Fabric or Spark access</td>
          <td data-label="Helpers"><code>_get_store</code></td>
          <td data-label="What they do">Access Fabric or Spark runtime services used by the implementation.</td>
        </tr>
      </tbody>
    </table>
    </div>

    ??? example "View helper source by area"

        ??? example "Audit timestamp helpers"

            **`def _validate_audit_timezone(timezone_name: str | None) -> str`**

            Source: [`src/fabricops_kit/config.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1e1b315d5b95935a662818da57af236b37c14595/src/fabricops_kit/config.py#L27-L58)

            ```python
            def _validate_audit_timezone(timezone_name: str | None) -> str:
                """Return a valid IANA audit timezone name.

                Parameters
                ----------
                timezone_name : str or None
                    IANA timezone name to validate. Blank values default to ``"UTC"``.

                Returns
                -------
                str
                    Validated timezone name.

                Raises
                ------
                ValueError
                    If a non-blank value is not a valid IANA timezone name.
                """
                value = str(timezone_name or DEFAULT_AUDIT_TIMEZONE).strip() or DEFAULT_AUDIT_TIMEZONE
                if value != DEFAULT_AUDIT_TIMEZONE and "/" not in value:
                    raise ValueError(
                        f'Invalid FABRICOPS_AUDIT_TIMEZONE: "{value}". '
                        'Use a valid IANA timezone name such as "Asia/Singapore" or keep the default "UTC".'
                    )
                try:
                    ZoneInfo(value)
                except ZoneInfoNotFoundError as exc:
                    raise ValueError(
                        f'Invalid FABRICOPS_AUDIT_TIMEZONE: "{value}". '
                        'Use a valid IANA timezone name such as "Asia/Singapore" or keep the default "UTC".'
                    ) from exc
                return value
            ```

        ??? example "Metadata loading helpers"

            **`def _get_fabric_runtime_metadata(notebook_name: str | None=None) -> dict[str, Any]`**

            Source: [`src/fabricops_kit/config.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1e1b315d5b95935a662818da57af236b37c14595/src/fabricops_kit/config.py#L1119-L1158)

            ```python
            def _get_fabric_runtime_metadata(notebook_name: str | None = None) -> dict[str, Any]:
                """Best-effort retrieval of Fabric runtime metadata."""
                metadata: dict[str, Any] = {
                    "notebook_name": notebook_name,
                    "workspace_name": None,
                    "user_name": None,
                    "runtime_available": False,
                }
                try:
                    import notebookutils.runtime as nb_runtime  # type: ignore

                    metadata["runtime_available"] = True
                    context = getattr(nb_runtime, "context", None)
                    if context is not None:

                        def _ctx_value(*keys: str) -> Any:
                            for key in keys:
                                if hasattr(context, key):
                                    value = getattr(context, key, None)
                                    if value is not None:
                                        return value
                                if isinstance(context, dict):
                                    value = context.get(key)
                                    if value is not None:
                                        return value
                                get_method = getattr(context, "get", None)
                                if callable(get_method):
                                    value = get_method(key)
                                    if value is not None:
                                        return value
                            return None

                        metadata["notebook_name"] = metadata["notebook_name"] or _ctx_value(
                            "currentNotebookName", "current_notebook_name"
                        )
                        metadata["workspace_name"] = _ctx_value("currentWorkspaceName", "workspaceName", "workspace_name")
                        metadata["user_name"] = _ctx_value("userName", "user_name")
                except Exception:
                    pass
                return metadata
            ```

        ??? example "Validation helpers"

            **`def _check_spark_session() -> tuple[bool, str]`**

            Source: [`src/fabricops_kit/config.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1e1b315d5b95935a662818da57af236b37c14595/src/fabricops_kit/config.py#L1111-L1116)

            ```python
            def _check_spark_session() -> tuple[bool, str]:
                """Check whether a Spark session is available."""
                spark_obj = globals().get("spark")
                if spark_obj is not None:
                    return True, "Spark session is available."
                return False, "Spark session not found; local fallback mode."
            ```

            **`def _run_config_smoke_tests(config: FrameworkConfig, env: str='Sandbox', required_targets: list[str] | None=None, check_io_import: bool=False, notebook_name: str | None=None) -> list[ConfigSmokeCheckResult]`**

            Source: [`src/fabricops_kit/config.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1e1b315d5b95935a662818da57af236b37c14595/src/fabricops_kit/config.py#L684-L783)

            ```python
            def _run_config_smoke_tests(
                config: FrameworkConfig,
                env: str = "Sandbox",
                required_targets: list[str] | None = None,
                check_io_import: bool = False,
                notebook_name: str | None = None,
            ) -> list[ConfigSmokeCheckResult]:
                """Run 00_env_config readiness smoke checks for configuration bootstrap.

                Use this during environment bootstrap to verify Spark availability, Fabric
                runtime context access, required path mappings, notebook naming policy, and
                optional IO import readiness before executing downstream notebook steps.

                Parameters
                ----------
                config : FrameworkConfig
                    Validated framework configuration to evaluate.
                env : str, default="Sandbox"
                    Environment key used when resolving required target paths.
                required_targets : list[str] | None, optional
                    Required targets expected in ``config.path_config``. Defaults to
                    ``["Source", "Unified"]`` when not provided.
                check_io_import : bool, default=False
                    Whether to test importability of ``fabric_input_output`` helpers.
                notebook_name : str | None, optional
                    Notebook name to validate against configured naming prefixes.

                Returns
                -------
                list[ConfigSmokeCheckResult]
                    Ordered check results with ``pass``, ``warn``, ``fail``, or ``skipped``
                    statuses for each readiness dimension.

                Raises
                ------
                ValueError
                    Propagated from config/path validation helpers when required targets or
                    configured environments are invalid.

                Notes
                -----
                This helper performs validation and lightweight import/runtime checks only.
                It does not create or mutate Fabric resources.

                Examples
                --------
                >>> checks = _run_config_smoke_tests(config=my_config, env="Sandbox", notebook_name="00_env_config")
                >>> any(c.status == "fail" for c in checks)
                False
                """
                results: list[ConfigSmokeCheckResult] = []
                required_targets = required_targets or ["Source", "Unified"]
                spark_ready, spark_message = _check_spark_session()
                results.append(ConfigSmokeCheckResult("spark_session", "pass" if spark_ready else "warn", spark_message))

                runtime_meta = _get_fabric_runtime_metadata(notebook_name=notebook_name)
                runtime_status = "pass" if runtime_meta.get("runtime_available") else "skipped"
                runtime_message = (
                    "Fabric runtime context is readable."
                    if runtime_meta.get("runtime_available")
                    else "notebookutils.runtime unavailable outside Fabric runtime."
                )
                results.append(ConfigSmokeCheckResult("fabric_runtime_context", runtime_status, runtime_message))
                try:
                    for target in required_targets:
                        p = _get_store(config=config, env=env, target=target)
                        missing = [attr for attr in ("workspace_id", "item_id", "name", "kind") if not getattr(p, attr, None)]
                        if missing:
                            results.append(ConfigSmokeCheckResult(f"path:{target}", "fail", f"Missing required fields: {missing}"))
                        elif p.kind == "lakehouse" and str(p.root).startswith("abfss://"):
                            results.append(
                                ConfigSmokeCheckResult(
                                    f"path:{target}", "pass", "Lakehouse store is populated and ABFSS root is derivable."
                                )
                            )
                        else:
                            results.append(ConfigSmokeCheckResult(f"path:{target}", "pass", "Store is populated."))
                except Exception as exc:
                    results.append(ConfigSmokeCheckResult("path_resolution", "fail", str(exc)))

                if notebook_name:
                    errors = _validate_notebook_name(notebook_name, config=config)
                    results.append(
                        ConfigSmokeCheckResult(
                            "notebook_naming", "pass" if not errors else "fail", "; ".join(errors) or "Notebook name is valid."
                        )
                    )
                else:
                    results.append(ConfigSmokeCheckResult("notebook_naming", "skipped", "Notebook name check skipped."))

                if check_io_import:
                    try:
                        from .fabric_input_output import read_lakehouse_table  # noqa: F401

                        results.append(ConfigSmokeCheckResult("fabric_io_import", "pass", "fabric_io helpers are importable."))
                    except Exception as exc:
                        results.append(ConfigSmokeCheckResult("fabric_io_import", "fail", str(exc)))
                else:
                    results.append(ConfigSmokeCheckResult("fabric_io_import", "skipped", "IO import check disabled."))
                return results
            ```

            **`def _validate_framework_config(config: FrameworkConfig | dict[str, Any]) -> FrameworkConfig`**

            Source: [`src/fabricops_kit/config.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1e1b315d5b95935a662818da57af236b37c14595/src/fabricops_kit/config.py#L551-L624)

            ```python
            def _validate_framework_config(config: FrameworkConfig | dict[str, Any]) -> FrameworkConfig:
                """Validate and normalize framework configuration input.

                Parameters
                ----------
                config : FrameworkConfig | dict[str, Any]
                    Existing framework config object or compatible mapping containing the
                    required user-facing component configs. Framework-only sections may be
                    omitted and will use package defaults.

                Returns
                -------
                FrameworkConfig
                    Normalized, validated framework config object.

                Raises
                ------
                ValueError
                    Raised when required sections are missing, component types are invalid,
                    or configured path targets are incomplete.

                Notes
                -----
                Validation checks configuration shape and required FabricStore fields.
                It does not perform external IO or provision Fabric resources.

                Examples
                --------
                >>> normalized = _validate_framework_config(framework_config)
                >>> isinstance(normalized, FrameworkConfig)
                True
                """
                if isinstance(config, FrameworkConfig):
                    normalized = config
                elif isinstance(config, dict):
                    required_keys = {
                        "path_config",
                        "notebook_runtime_config",
                        "ai_prompt_config",
                    }
                    missing_keys = sorted(required_keys.difference(config.keys()))
                    if missing_keys:
                        raise ValueError(f"Framework config is missing required keys: {', '.join(missing_keys)}.")
                    normalized = FrameworkConfig(**config)
                else:
                    raise ValueError("config must be a FrameworkConfig object or compatible mapping.")

                if not isinstance(normalized.path_config, PathConfig):
                    raise ValueError("path_config must be a PathConfig object.")
                if not isinstance(normalized.notebook_runtime_config, NotebookRuntimeConfig):
                    raise ValueError("notebook_runtime_config must be a NotebookRuntimeConfig object.")
                if not isinstance(normalized.ai_prompt_config, AIPromptConfig):
                    raise ValueError("ai_prompt_config must be an AIPromptConfig object.")
                if not isinstance(normalized.quality_config, QualityConfig):
                    raise ValueError("quality_config must be a QualityConfig object.")
                if not isinstance(normalized.governance_config, GovernanceConfig):
                    raise ValueError("governance_config must be a GovernanceConfig object.")
                if not isinstance(normalized.review_workflow_config, ReviewWorkflowConfig):
                    raise ValueError("review_workflow_config must be a ReviewWorkflowConfig object.")
                if not isinstance(normalized.lineage_config, LineageConfig):
                    raise ValueError("lineage_config must be a LineageConfig object.")
                if not isinstance(normalized.data_agreement_config, DataAgreementConfig):
                    raise ValueError("data_agreement_config must be a DataAgreementConfig object.")
                _validate_audit_timezone(normalized.audit_timezone)

                for env_name, targets in normalized.path_config.paths.items():
                    if not isinstance(targets, dict) or not targets:
                        raise ValueError(f"Environment '{env_name}' must contain at least one target.")
                    for target_name, housepath in targets.items():
                        required = ("workspace_id", "item_id", "name", "kind")
                        if not all(hasattr(housepath, attr) for attr in required):
                            raise ValueError(f"Target '{env_name}/{target_name}' must provide FabricStore fields: {required}.")

                return normalized
            ```

            **`def _validate_notebook_name(notebook_name: str, config: FrameworkConfig | None=None) -> list[str]`**

            Source: [`src/fabricops_kit/config.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1e1b315d5b95935a662818da57af236b37c14595/src/fabricops_kit/config.py#L670-L681)

            ```python
            def _validate_notebook_name(notebook_name: str, config: FrameworkConfig | None = None) -> list[str]:
                name = "_".join(str(notebook_name or "").strip().lower().split())
                patterns = [
                    r"^00_env_config$",
                    r"^01_agreement(?:_[a-z0-9_]+)?$",
                    r"^02_pipeline(?:_[a-z0-9_]+)?$",
                    r"^03_governance(?:_[a-z0-9_]+)?$",
                    r"^99_explore(?:_[a-z0-9_]+)?$",
                ]
                if any(__import__("re").match(p, name) for p in patterns):
                    return []
                return ["Notebook name does not match accepted FabricOps naming patterns."]
            ```

        ??? example "Fabric or Spark access helpers"

            **`def _get_store(config: FrameworkConfig | PathConfig | None, env: str, target: str) -> Any`**

            Source: [`src/fabricops_kit/config.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1e1b315d5b95935a662818da57af236b37c14595/src/fabricops_kit/config.py#L627-L667)

            ```python
            def _get_store(config: FrameworkConfig | PathConfig | None, env: str, target: str) -> Any:
                """Resolve a configured Fabric path for an environment and target.

                Parameters
                ----------
                env : str
                    Environment key such as ``Sandbox``, ``DE``, or ``Prod``.
                target : str
                    Target key such as ``Source``, ``Unified``, ``Product``, or ``Warehouse``.
                config : FrameworkConfig | PathConfig | None
                    Configuration that contains environment-to-target path mappings.

                Returns
                -------
                Any
                    FabricStore object with ``workspace_id``, ``house_id``, ``house_name``, and ``root``.

                Raises
                ------
                ValueError
                    If config is missing, or if the environment/target mapping does not exist.

                Examples
                --------
                >>> get_path("Sandbox", "Source", config=CONFIG)
                Housepath(...)
                """
                if config is None:
                    raise ValueError("No Fabric config was provided. Pass a FrameworkConfig or PathConfig instance.")
                paths = config.path_config.paths if isinstance(config, FrameworkConfig) else config.paths
                if env not in paths:
                    available_envs = ", ".join(sorted(paths.keys())) or "<none>"
                    raise ValueError(
                        f"Environment '{env}' was not found in Fabric config. Available environments: {available_envs}."
                    )
                if target not in paths[env]:
                    available_targets = ", ".join(sorted(paths[env].keys())) or "<none>"
                    raise ValueError(
                        f"Target '{target}' was not found under environment '{env}'. Available targets: {available_targets}."
                    )
                return paths[env][target]
            ```


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
- Source line: `786`
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

- `fabricops_kit.config.NotebookSetupContext`
- `fabricops_kit.config._get_store`
- `fabricops_kit.config._run_config_smoke_tests`
- `fabricops_kit.config._validate_framework_config`

### Raw source metadata

- Source file path: `src/fabricops_kit/config.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1e1b315d5b95935a662818da57af236b37c14595/src/fabricops_kit/config.py#L786-L895">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1e1b315d5b95935a662818da57af236b37c14595/src/fabricops_kit/config.py#L786-L895</a>
- Start line: `786`
- End line: `895`
- Signature:

```python
def setup_notebook(config: FrameworkConfig | dict[str, Any], env: str='Sandbox', required_targets: list[str] | None=None, notebook_name: str | None=None, run_id_prefix: str='run', local_fallback_name: str | None=None) -> NotebookSetupContext
```

### Internal relationship graph

### Public related functions

- <a href="../setup_metadata_tables/"><code>fabricops_kit.config.setup_metadata_tables</code></a>

### Internal implementation summary

- Internal helper count: 7
- Grouped helper summary and optional source snippets are rendered in the page-level Internal implementation summary section.

</details>
