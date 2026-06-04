# Compatibility

Compatibility review for FabricOps Starter Kit focuses on whether users can install the wheel, run the plug-and-play Microsoft Fabric notebook templates, and rely on documented metadata outputs without unexpected migration work.

## Supported Python versions

`pyproject.toml` declares `requires-python = ">=3.11"`. Exact Python versions validated for a release must be recorded in the release note and test evidence.

## Supported Fabric runtime assumptions

FabricOps is intended to run inside Microsoft Fabric notebooks with explicit lakehouse, warehouse, and metadata routing configured through `00_env_config` or equivalent setup. Exact Fabric runtime names and Spark versions are environment-specific and must be marked `Needs maintainer review` until validated in a Fabric workspace.

## Wheel version alignment

Before publishing a release, confirm that:

- `pyproject.toml` contains the intended release version
- `fabricops_kit.__version__` reports the same version
- the built wheel filename matches the release version
- Fabric Environments install the intended wheel artifact

## Dependency compatibility

Dependency compatibility should be validated against the project dependency bounds and the target Fabric runtime. If a Fabric runtime includes preinstalled versions of pandas, pyspark, or notebook dependencies, validate imports and smoke tests with the versions actually available in that runtime.

## Notebook template compatibility

Notebook template compatibility means existing users can understand whether template inputs, `%run 00_env_config` expectations, output writes, metadata writes, and human review steps changed. Review every template under `templates/notebooks/` before replacing existing Fabric notebook copies.

## Metadata output compatibility

Metadata compatibility means tables retain expected names, required columns, stable keys, and write behavior. Any metadata column rename, removal, table rename, table removal, or append/overwrite behavior change must be treated as a breaking-change candidate.

## Compatibility check process

Recommended release validation flow:

1. Install the wheel in a Fabric Environment.
2. Confirm package version with `import fabricops_kit; fabricops_kit.__version__`.
3. Run notebook smoke tests for the relevant templates.
4. Validate metadata writes through the configured metadata target.
5. Validate contract or governance outputs where applicable.

Record evidence in the release note before publishing the wheel or GitHub Release.
