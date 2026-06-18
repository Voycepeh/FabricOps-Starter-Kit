# Environment configuration

`00_env_config` is the shared bootstrap notebook for FabricOps Starter Kit runs. It defines the active environment, points each logical target at a Fabric Lakehouse or Warehouse, builds the framework configuration object, runs startup validation, and prepares or validates metadata tables in the configured metadata Lakehouse.

Use this page when you adapt the starter notebook for your own workspace. The values with workspace, item, schema, environment, and organization-specific labels are user-owned. The config object shape, metadata table registry, required FabricStore fields, and metadata setup behavior are framework-owned and should stay aligned with the current implementation.

## Runtime Config

The Runtime Config section creates the notebook runtime policy and shared runtime defaults.

```python
NOTEBOOK_PREFIXES = ("00_env_config", "01_agreement", "02_pipeline", "03_governance", "99_explore")
RUNTIME_CONFIG = NotebookRuntimeConfig(NOTEBOOK_PREFIXES)
```

The starter defines `NOTEBOOK_PREFIXES` and passes them into `NotebookRuntimeConfig` so the intended notebook families stay visible in one place. In the current implementation, however, `setup_notebook` naming validation still uses the built-in FabricOps notebook name patterns (`00_env_config`, `01_agreement`, `02_pipeline`, `03_governance`, and `99_explore`) rather than reading custom prefixes from `NotebookRuntimeConfig`. Treat `NOTEBOOK_PREFIXES` as configuration documentation for now unless the implementation is changed to make custom prefixes enforceable.

The same section also defines:

- `FABRICOPS_AUDIT_TIMEZONE`
- `LAKEHOUSE_SCHEMAS_ENABLED`
- `DEFAULT_LAKEHOUSE_SCHEMA`
- `SOURCE_SCHEMA`, `UNIFIED_SCHEMA`, `PRODUCT_SCHEMA`, and `METADATA_SCHEMA`
- `VALIDATION_MODE`

## Audit timezone

`FABRICOPS_AUDIT_TIMEZONE` controls FabricOps-generated audit and technical timestamps.

```python
FABRICOPS_AUDIT_TIMEZONE = "Asia/Singapore"
_validate_audit_timezone(FABRICOPS_AUDIT_TIMEZONE)
```

Edit this value only if your team wants local audit timestamps. Use a valid IANA timezone such as `"UTC"`, `"Asia/Singapore"`, `"Australia/Sydney"`, or `"America/New_York"`. Blank values default to `"UTC"`; invalid names fail validation. `UTC` is the most portable default for public examples and cross-region operations.

## Lakehouse schema settings

The starter notebook separates schema routing from table names:

```python
LAKEHOUSE_SCHEMAS_ENABLED = True
DEFAULT_LAKEHOUSE_SCHEMA = "dbo"
SOURCE_SCHEMA = DEFAULT_LAKEHOUSE_SCHEMA
UNIFIED_SCHEMA = DEFAULT_LAKEHOUSE_SCHEMA
PRODUCT_SCHEMA = DEFAULT_LAKEHOUSE_SCHEMA
METADATA_SCHEMA = "METADATA"
```

Set `LAKEHOUSE_SCHEMAS_ENABLED = False` for classic/non-schema Lakehouses and set schema variables to `None` when you do not want schema-qualified Lakehouse paths. Set it to `True` only when the target Lakehouses are schema-enabled.

For schema-enabled Lakehouses, each Lakehouse `FabricStore` must have a simple schema name. The implementation rejects schema values with paths, dots, invalid characters, or names that start with a number. Schema routing should be configured through the `schema` field on each `FabricStore` or through the `metadata_schema` argument to metadata setup, not by embedding the schema in table names.

Lakehouse helpers use the `FabricStore` schema for schema-enabled Lakehouses. Warehouse read/write helpers still receive the warehouse schema as an explicit function argument, even if the starter `product` target also carries a `schema` value for configuration readability.

## Metadata schema

`METADATA_SCHEMA` controls where metadata tables are created and validated when the metadata Lakehouse is schema-enabled.

```python
METADATA_SCHEMA = "METADATA"
```

With a metadata schema, setup and validation use fully qualified metadata visibility such as `METADATA.METADATA_DATA_AGREEMENT`, while physical schema-aware Lakehouse paths are handled by the FabricOps IO helpers. Without a metadata schema, metadata tables stay under classic `Tables/<table_name>` paths.

Keep metadata table names themselves simple, for example `METADATA_DATA_AGREEMENT`, not `METADATA.METADATA_DATA_AGREEMENT`. The framework resolves schema separately.

## Validation mode

The starter notebook defines:

```python
VALIDATION_MODE = "warn"
```

Use `"warn"` during initial setup so the notebook can print missing steward or metadata-table readiness information without stopping immediately. Use `"strict"` when you want missing prerequisites to fail the bootstrap.

Current strict checks in `00_env_config` raise when:

- agreement metadata setup is not ready, for example no active steward rows exist and strict mode is enabled;
- metadata table registration validation is not `ready` or `skipped`.

`setup_notebook` also returns `RUN_CONTEXT.readiness_status` after startup completes. Missing required environments or targets can raise during `setup_notebook` before `RUN_CONTEXT` is returned, so do not expect every path-resolution problem to produce a context object. When setup does return a context, completed smoke checks can produce readiness values such as `ready` or `not_ready`; for example, notebook naming failures are reflected in the returned readiness status.

## Path Config

The Path Config section selects the active environment and maps logical target names to Fabric items.

```python
ENV = "dev"
ENV_NAME = ENV

REQUIRED_TARGETS = ["source", "unified", "product", "metadata"]

ENV_PATHS = {
    ENV: {
        "source": FabricStore(...),
        "unified": FabricStore(...),
        "product": FabricStore(...),
        "metadata": FabricStore(...),
    }
}

PATH_CONFIG = PathConfig(paths=ENV_PATHS)
```

### `ENV` and `ENV_NAME`

`ENV` is the environment key passed to `setup_notebook`, `setup_metadata_tables`, and later read/write helpers. `ENV_NAME` is an alias set to the same value for notebook readability.

Edit `ENV` to match your environment naming convention, for example `dev`, `test`, or `prod`. Keep `ENV_NAME = ENV` unless you have a clear reason to expose another display variable. The key used in `ENV_PATHS` must match the `env` argument supplied to setup and IO helpers.

### `REQUIRED_TARGETS`

`REQUIRED_TARGETS` lists the logical targets that must resolve before the notebook is considered ready.

The starter expects:

- `source` for source Lakehouse reads;
- `unified` for governed or transformed Lakehouse writes;
- `product` for product-serving Warehouse writes;
- `metadata` for all FabricOps metadata tables.

Edit this list only when your workflow intentionally has a different set of targets. Every required target must exist under `ENV_PATHS[ENV]`, and each target must provide the required `FabricStore` fields.

### `ENV_PATHS`

`ENV_PATHS` is the source of truth for environment-to-target routing. It is passed into `PathConfig`, then into `FrameworkConfig`, and then used by FabricOps IO helpers.

Users should edit the workspace IDs, item IDs, item names, target kinds, and schema settings to match their Fabric workspace. Keep the nested shape:

```python
{
    ENV: {
        "target_name": FabricStore(...),
    }
}
```

Do not assume an attached or default Lakehouse for metadata. Metadata reads and writes route through `CONFIG.path_config.paths[ENV]["metadata"]`.

## `FabricStore` fields

Each configured target is a `FabricStore`:

```python
FabricStore(
    env=ENV,
    workspace_id="<workspace-id>",
    item_id="<lakehouse-or-warehouse-item-id>",
    name="<fabric-item-name>",
    kind="lakehouse",
    schema_enabled=LAKEHOUSE_SCHEMAS_ENABLED,
    schema=SOURCE_SCHEMA,
)
```

User-owned fields:

| Field | What to set |
| --- | --- |
| `env` | Usually `ENV`; it should match the environment key. |
| `workspace_id` | Fabric workspace ID containing the item. |
| `item_id` | Lakehouse or Warehouse item ID. |
| `name` | Lakehouse or Warehouse display/name used by helpers and diagnostics. |
| `kind` | `"lakehouse"` or `"warehouse"`. |
| `schema_enabled` | `True` for schema-enabled Lakehouses, otherwise `False`. |
| `schema` | Simple schema name for schema-enabled Lakehouses; otherwise `None`. |

Framework-owned behavior:

- required field names are `env`, `workspace_id`, `item_id`, `name`, and `kind`;
- `kind` is normalized and must be `lakehouse` or `warehouse`;
- Lakehouse `root` is derived from `workspace_id` and `item_id`;
- schema names are validated as simple identifiers;
- metadata target routing uses the `metadata` target rather than a default attached Lakehouse.

## Framework config assembly

After runtime and path values are declared, `00_env_config` compiles them into one framework object:

```python
CONFIG = FrameworkConfig(
    path_config=PATH_CONFIG,
    notebook_runtime_config=RUNTIME_CONFIG,
    governance_config=GovernanceConfig(...),
    data_agreement_config=DATA_AGREEMENT_CONFIG,
    audit_timezone=FABRICOPS_AUDIT_TIMEZONE,
)

RUN_CONTEXT = setup_notebook(
    config=CONFIG,
    env=ENV,
    required_targets=REQUIRED_TARGETS,
)
```

Users may edit the governance dropdown options, agreement custom fields, audit timezone, and path mappings. Keep `FrameworkConfig`, `PathConfig`, and `setup_notebook` wiring in place so downstream notebooks receive a validated config object.

## First-run metadata table setup

`00_env_config` calls `setup_metadata_tables` to create missing metadata tables and validate existing ones:

```python
METADATA_TABLE_SETUP = setup_metadata_tables(
    spark=spark,
    config=CONFIG,
    env=ENV,
    metadata_schema=METADATA_SCHEMA,
    require_active_steward=False,
)
AGREEMENT_METADATA_SETUP = METADATA_TABLE_SETUP["data_agreement"]
```

On first run, this creates the active FabricOps metadata tables in the configured metadata Lakehouse target. The registry is framework-owned and combines agreement tables, notebook registry metadata, and governance/guardrail metadata schemas. Setup creates empty tables with the expected schemas; it does not populate business rows.

Keep `require_active_steward=False` for initial bootstrapping. After setup, use `01_agreement` to create active steward rows and agreements.

## Later-run validation behavior

On later runs, the same setup call reads each expected metadata table from the configured metadata target and validates that required columns exist. Missing tables are created. Existing tables with missing required columns are not automatically migrated; recreate or manually migrate them before continuing.

The setup summary includes:

- `status`
- `created_tables`
- `active_metadata_tables`
- `active_metadata_table_count`
- `metadata_schema`
- `fully_qualified_tables`
- `registration_validation`
- `warnings`

The notebook prints registered tables, missing tables, warnings, steward readiness, and active table counts. FabricOps may warn about legacy nested or unidentified Delta folders, but it does not delete or migrate user data automatically.

## What users should edit vs keep framework-owned

| Area | Users should edit | Keep framework-owned |
| --- | --- | --- |
| Runtime Config | Audit timezone, optional notebook prefixes, validation mode. | `NotebookRuntimeConfig` construction and startup validation flow. |
| Schema settings | Whether schemas are enabled and the simple schema names for each target. | Separate schema routing; do not bake schema into table names. |
| Path Config | `ENV`, target IDs, target names, target kinds, and target schemas. | `ENV_PATHS -> PathConfig -> FrameworkConfig` shape. |
| Required targets | Target list only when the workflow genuinely differs. | Required targets must match configured target keys. |
| Metadata | Metadata Lakehouse target and optional metadata schema. | Active metadata table registry and table schemas. |
| FabricStore | Fabric workspace/item values and target type. | Required field names, validation rules, and derived `root`. |
| First-run setup | Run once during environment bootstrap, then keep available for validation. | `setup_metadata_tables` implementation and metadata routing through `metadata` target. |
| Later runs | Review printed warnings and migrate broken tables manually when required. | No automatic deletion or migration of existing user data. |

## Default Fabric context for downstream notebooks

`00_env_config` is the single source of truth for environment settings in a notebook run. It initializes `FABRIC_CONTEXT`, an active context dictionary that includes the selected environment name, the validated `CONFIG`, the active workspace/lakehouse identifiers, and the setup context returned by `setup_notebook`.

Subsequent template notebooks run `00_env_config` first and use helper defaults that resolve framework plumbing from `FABRIC_CONTEXT`. Common users should edit only business inputs such as source tables, target tables, file paths, primary keys, validation rules, and output names. They should not need to pass `CONFIG`, `ENV`, workspace IDs, or lakehouse IDs in normal helper calls.

For example, prefer:

```python
source_table = "your_source_table"  # Change this to your input table
source_df = read_data(source_table)
```

Advanced users can still override the active context explicitly when a notebook needs to read from another configured environment or target:

```python
custom_context = get_fabric_context(env_name="DEV")
source_df = read_data("table_name", context=custom_context)
```

If a downstream notebook is run without first running `00_env_config`, context-aware helpers raise a clear error asking the user to run `00_env_config` before continuing.
