# Test Matrix

FabricOps release testing focuses on package installation, callable functions, plug-and-play notebook templates, metadata outputs, compatibility evidence, and release validation.

## Package tests

| Test area | What is tested | Required before release | Evidence expected |
| --- | --- | --- | --- |
| Version alignment | `pyproject.toml`, wheel metadata, and `fabricops_kit.__version__` agree. | Yes | Automated test output and built wheel filename. |
| Package import | Package imports in a clean environment. | Yes | Command output from `python -c "import fabricops_kit"`. |

## Callable function tests

| Test area | What is tested | Required before release | Evidence expected |
| --- | --- | --- | --- |
| Public API smoke tests | Public exports import and core pure-Python helpers execute. | Yes | Pytest output and generated function reference review. |
| Callable behavior checks | Changed callables have focused tests or documented manual evidence. | Yes for changed callables | Test names, notebooks, or maintainer review notes. |

## Notebook template smoke tests

| Test area | What is tested | Required before release | Evidence expected |
| --- | --- | --- | --- |
| `00_env_config` smoke | Environment config initializes and metadata target is explicit. | Yes | Fabric notebook run evidence. |
| `01_da` smoke | Agreement intake widgets and metadata writes can initialize. | Yes when changed | Fabric notebook run evidence or maintainer review. |
| `02_ex` smoke | Exploration flow can load config, profile data, and prepare advisory evidence. | Yes when changed | Fabric notebook run evidence or maintainer review. |
| `03_pc` smoke | Pipeline template can run configured checks and output writes. | Yes when changed | Fabric notebook run evidence or maintainer review. |
| `04_gov` smoke | Governance review template can load and write approved metadata. | Yes when changed | Fabric notebook run evidence or maintainer review. |

## Metadata output tests

| Test area | What is tested | Required before release | Evidence expected |
| --- | --- | --- | --- |
| Metadata routing | Reads and writes use configured metadata target, not an attached/default lakehouse. | Yes | Code review, pytest, or Fabric run evidence. |
| Schema compatibility | Required metadata columns and table names remain compatible or are documented as breaking changes. | Yes | Schema diff or maintainer review notes. |
| Write behavior | Append versus overwrite behavior is unchanged or documented as breaking. | Yes | Test output or code review evidence. |

## Compatibility tests

| Test area | What is tested | Required before release | Evidence expected |
| --- | --- | --- | --- |
| Python compatibility | Release supports declared Python versions. | Yes | CI output by Python version. |
| Fabric runtime compatibility | Wheel and notebooks run in target Fabric runtime. | Yes | Fabric Environment and notebook run evidence. |
| Dependency compatibility | pandas, pyspark, notebook, and optional dependency versions are compatible. | Yes | Environment version output and smoke tests. |

## Release validation tests

| Test area | What is tested | Required before release | Evidence expected |
| --- | --- | --- | --- |
| Wheel build | `python -m build` creates releasable artifacts. | Yes | CI artifact and command output. |
| Docs build | MkDocs builds release documentation. | Yes | `mkdocs build` output. |
| Release notes review | Changelog, release note, feature list, compatibility, test matrix, and breaking changes pages are updated. | Yes | PR checklist and reviewer confirmation. |
