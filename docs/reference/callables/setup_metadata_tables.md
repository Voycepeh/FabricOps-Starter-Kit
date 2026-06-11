# setup_metadata_tables

Create or validate all FabricOps metadata tables through one setup action.

## What this is for and when to use it

Create or validate all FabricOps metadata tables through one setup action.

- Use after setup_notebook in 00_env_config to create or validate the FabricOps metadata tables required by agreement, profiling, lineage, stability, and governance workflows.

## When not to use it

- Do not use for writing business data or pipeline target tables; use write_lakehouse_table or write_warehouse_table for data outputs.

## Example

```python
setup_metadata_tables(CONFIG, env="Sandbox", spark_session=spark)
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
      <td data-label="Parameter"><code>spark</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">Fabric Spark session used by the table setup helpers.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>config</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">Shared ``00_env_config`` configuration containing the metadata target.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>env</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">Environment key to prepare.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>require_active_steward</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Forwarded to the agreement metadata setup to optionally require an active steward before returning success.</td>
    </tr>
  </tbody>
</table>
</div>

## Output

Setup result describing metadata table creation or validation status.

## Errors and side effects

**Errors:** Raises configuration, Spark, or storage errors when metadata routing or table preparation fails.

**Side effects:** Creates or validates FabricOps metadata tables in the configured metadata lakehouse target.

## Related functions

- <a href="../setup_notebook/"><code>fabricops_kit.config.setup_notebook</code></a>
- <a href="../record_table_governance/"><code>fabricops_kit.governance_review.record_table_governance</code></a>

<details class="reference-implementation-details">
<summary>Implementation details</summary>

- <a href="../internal/config__get_active_metadata_tables/"><code>fabricops_kit.config._get_active_metadata_tables</code></a>
- <a href="../internal/config__metadata_tables_from_setup_results/"><code>fabricops_kit.config._metadata_tables_from_setup_results</code></a>
- <a href="../internal/config__validate_metadata_table_registration/"><code>fabricops_kit.config._validate_metadata_table_registration</code></a>
- <a href="../internal/data_agreement__setup_data_agreement_tables/"><code>fabricops_kit.data_agreement._setup_data_agreement_tables</code></a>
- `fabricops_kit.data_agreement.get`
- <a href="../internal/governance_review__setup_governance_metadata_tables/"><code>fabricops_kit.governance_review._setup_governance_metadata_tables</code></a>
- <a href="../internal/metadata__setup_notebook_registry_table/"><code>fabricops_kit.metadata._setup_notebook_registry_table</code></a>

</details>

## Source

- Source file path: `src/fabricops_kit/config.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1bac7913a070db1a771a2991ff5421c37ffc9d94/src/fabricops_kit/config.py#L1035-L1099">View setup_metadata_tables on GitHub</a>

<details class="reference-source-details">
<summary>Show source code</summary>

```python
def setup_metadata_tables(
    *,
    spark: Any,
    config: FrameworkConfig | dict[str, Any],
    env: str,
    require_active_steward: bool = False,
) -> dict[str, Any]:
    """Prepare all FabricOps metadata tables for the configured environment.

    Parameters
    ----------
    spark : pyspark.sql.SparkSession
        Fabric Spark session used by the table setup helpers.
    config : FrameworkConfig or dict
        Shared ``00_env_config`` configuration containing the metadata target.
    env : str
        Environment key to prepare.
    require_active_steward : bool, default=False
        Forwarded to the agreement metadata setup to optionally require an
        active steward before returning success.

    Returns
    -------
    dict[str, Any]
        Combined setup summary keyed by ``data_agreement``,
        ``notebook_registry``, and ``governance``.

    Notes
    -----
    This is the v1 notebook setup action for metadata provisioning. It keeps
    ``00_env_config`` simple while delegating to internal helpers that route all
    metadata reads and writes through the configured metadata lakehouse target.
    """
    from fabricops_kit.data_agreement import _setup_data_agreement_tables
    from fabricops_kit.governance_review import _setup_governance_metadata_tables
    from fabricops_kit.metadata import _setup_notebook_registry_table

    data_agreement = _setup_data_agreement_tables(
        spark=spark,
        config=config,
        env=env,
        require_active_steward=require_active_steward,
    )
    notebook_registry = _setup_notebook_registry_table(spark=spark, config=config, env=env)
    governance = _setup_governance_metadata_tables(spark=spark, config=config, env=env)
    expected_tables = _get_active_metadata_tables(config)
    created_or_checked = _metadata_tables_from_setup_results(data_agreement, notebook_registry, governance)
    registration_validation = _validate_metadata_table_registration(
        spark=spark,
        config=config,
        env=env,
        expected_tables=expected_tables,
    )
    statuses = [data_agreement.get("status"), notebook_registry.get("status"), governance.get("status")]
    registration_status = registration_validation.get("status")
    return {
        "status": "ready" if all(status == "ready" for status in statuses) and registration_status in {"ready", "skipped"} else "not_ready",
        "data_agreement": data_agreement,
        "notebook_registry": notebook_registry,
        "governance": governance,
        "active_metadata_tables": expected_tables,
        "active_metadata_table_count": len(expected_tables),
        "created_or_checked_tables": created_or_checked,
        "registration_validation": registration_validation,
    }
```

</details>

<details class="reference-metadata-details">
<summary>AI / machine-readable metadata — skip this if you are reading the docs normally</summary>

These generated fields are for automation, AI agents, maintainers, and doc tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.config.setup_metadata_tables`
- Short name: `setup_metadata_tables`
- Module: `config`
- Classification: Callable
- Related module: `config`
- Source file path: `src/fabricops_kit/config.py`
- Source line: `1035`
- Inbound references count: 0
- Outbound references count: 7

### AI implementation contract

- **required_context:** Requires the metadata target from 00_env_config; metadata tables must be routed through CONFIG.path_config paths for the selected env.
- **inputs:** config, env, optional spark_session, and mode/check options used to prepare metadata storage through configured metadata routing.
- **output:** Setup result describing metadata table creation or validation status.
- **side_effects:** Creates or validates FabricOps metadata tables in the configured metadata lakehouse target.
- **failure_modes:** Raises configuration, Spark, or storage errors when metadata routing or table preparation fails.
- **verification:** Verify metadata setup completes before recommending agreement, profiling, lineage, stability, or governance workflows that persist evidence.

### Inbound references

Not documented yet

### Outbound references

- <a href="../internal/config__get_active_metadata_tables/"><code>fabricops_kit.config._get_active_metadata_tables</code></a>
- <a href="../internal/config__metadata_tables_from_setup_results/"><code>fabricops_kit.config._metadata_tables_from_setup_results</code></a>
- <a href="../internal/config__validate_metadata_table_registration/"><code>fabricops_kit.config._validate_metadata_table_registration</code></a>
- <a href="../internal/data_agreement__setup_data_agreement_tables/"><code>fabricops_kit.data_agreement._setup_data_agreement_tables</code></a>
- <a href="../internal/governance_review__setup_governance_metadata_tables/"><code>fabricops_kit.governance_review._setup_governance_metadata_tables</code></a>
- <a href="../internal/metadata__setup_notebook_registry_table/"><code>fabricops_kit.metadata._setup_notebook_registry_table</code></a>

### Raw source metadata

- Source file path: `src/fabricops_kit/config.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1bac7913a070db1a771a2991ff5421c37ffc9d94/src/fabricops_kit/config.py#L1035-L1099">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1bac7913a070db1a771a2991ff5421c37ffc9d94/src/fabricops_kit/config.py#L1035-L1099</a>
- Start line: `1035`
- End line: `1099`
- Signature:

```python
def setup_metadata_tables(*, spark: Any, config: FrameworkConfig | dict[str, Any], env: str, require_active_steward: bool=False) -> dict[str, Any]
```

### Internal relationship graph

### Public related functions

- <a href="../setup_notebook/"><code>fabricops_kit.config.setup_notebook</code></a>
- <a href="../record_table_governance/"><code>fabricops_kit.governance_review.record_table_governance</code></a>

### Internal implementation helpers

- <a href="../internal/config__get_active_metadata_tables/"><code>fabricops_kit.config._get_active_metadata_tables</code></a>
- <a href="../internal/config__metadata_tables_from_setup_results/"><code>fabricops_kit.config._metadata_tables_from_setup_results</code></a>
- <a href="../internal/config__validate_metadata_table_registration/"><code>fabricops_kit.config._validate_metadata_table_registration</code></a>
- <a href="../internal/data_agreement__setup_data_agreement_tables/"><code>fabricops_kit.data_agreement._setup_data_agreement_tables</code></a>
- `fabricops_kit.data_agreement.get`
- <a href="../internal/governance_review__setup_governance_metadata_tables/"><code>fabricops_kit.governance_review._setup_governance_metadata_tables</code></a>
- <a href="../internal/metadata__setup_notebook_registry_table/"><code>fabricops_kit.metadata._setup_notebook_registry_table</code></a>

</details>
