# Test Suite Guide

This test suite validates the current **FabricOps Starter Kit** lifecycle implementation with local, public-safe tests.

## Test categories

FabricOps uses four pytest marker categories:

- `unit`: fast tests that do not require Spark or Fabric runtime behaviour.
- `spark`: focused tests that require a local Spark session.
- `fabric`: tests that simulate Microsoft Fabric runtime interfaces with local fakes.
- `contract`: package, schema, documentation, release, and public API consistency tests.

Unit tests should remain fast and deterministic. Spark tests should be limited to behaviour that cannot be trusted through mocks, such as schema preservation, data types, null handling, column ordering, quarantine output, and Spark window ordering. Fabric tests simulate runtime interfaces through shared fixtures; they must not require a live workspace. Live Microsoft Fabric workspace integration is outside the local test suite.

## Shared fixtures

`tests/conftest.py` provides reusable fixtures for:

- A session-scoped local Spark session using `local[2]`.
- Fake `notebookutils` and `mssparkutils` modules injected through `sys.modules`.
- Fake Fabric runtime context values.
- Fake filesystem, credential, and environment helpers.

Use these fixtures instead of repeated ad hoc notebook runtime mocks.

## What is covered

- Configuration and contract loading/validation.
- Data contract normalization and rule execution behavior.
- Data quality workflows, rule compilation, deterministic rule history resolution, and quarantine record behavior.
- Drift checks, metadata, profiling, runtime audit columns, lineage, governance classification, and handover summary helpers.
- Optional dependency boundaries and package importability outside Fabric.
- Distribution build validation and packaged schema assets.
- Docs/reference generation and consistency checks.

## What should not be tested locally

- Real Microsoft Fabric workspace access.
- Live Spark clusters/notebook runtime dependencies outside the local Spark fixture.
- Networked services, cloud credentials, or production resources.
- Key Vault or live Fabric integration unless those are covered by a separate integration suite.

## How to run

```bash
uv run pytest
uv run pytest -m unit
uv run pytest -m spark
uv run pytest -m fabric
uv run pytest -m contract
uv run pytest --cov=fabricops_kit --cov-report=term-missing
uv run ruff check .
python -m build
twine check dist/*
```

## Naming convention

- Name tests by current product concepts and module behavior (for example: `test_config.py`, `test_data_contract.py`, `test_dq_workflow.py`, `test_drift.py`).
- Avoid legacy MVP/template-era naming for new files.
- Prefer consolidating closely related coverage into a single clear module-focused file.
