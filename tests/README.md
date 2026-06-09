# Test Suite Guide

This test suite validates the current **FabricOps Starter Kit** lifecycle implementation with local, public-safe tests.

## Test categories

FabricOps keeps a deliberately small pytest suite:

- `unit`: focused tests for public functions, validation, config resolution, agreement logic, metadata helpers, and core transformations.
- `integration`: mocked boundary tests for Lakehouse/Warehouse IO, file readers, metadata persistence, and Fabric-facing setup helpers.
- `spark`: a small number of tests that need a local Spark session for DQ and schema behaviour.
- `contract`: minimal public contract and notebook-template workflow checks.

Unit tests should remain fast and deterministic. Integration tests use local fakes and mocks; they must not require a live workspace. Spark tests should be limited to behaviour that cannot be trusted through mocks. Contract tests protect importability, essential schemas, and supported template workflows without checking exact wording or notebook presentation.

## Shared fixtures

`tests/conftest.py` provides reusable fixtures for:

- A session-scoped local Spark session using `local[2]`.
- Fake `notebookutils` and `mssparkutils` modules injected through `sys.modules`.
- Fake Fabric runtime context values.
- Fake filesystem, credential, and environment helpers.

Use these fixtures instead of repeated ad hoc notebook runtime mocks.

## What is covered

- Configuration and dataset-contract validation.
- Environment and path resolution.
- Data agreement and metadata-table persistence logic.
- Data quality, schema/profile stability, profiling, lineage, and governance review helpers.
- Lakehouse, Warehouse, Excel, CSV, and Parquet helper boundaries through mocks.
- Representative executable notebook-template workflows.
- Minimal public API, schema, and template availability contracts.

## What should not be tested locally

- Real Microsoft Fabric workspace access.
- Live Spark clusters/notebook runtime dependencies outside the local Spark fixture.
- Networked services, cloud credentials, or production resources.
- Exact documentation wording, Markdown headings, comments, or notebook cell ordering.
- Private helper details unless they are the only practical seam for a current public workflow.

## How to run

```bash
uv run pytest
uv run pytest -m unit
uv run pytest -m integration
uv run pytest -m spark
uv run pytest -m contract
uv run pytest --cov=fabricops_kit --cov-report=term-missing
```

## Naming convention

- Keep files grouped under `unit/`, `integration/`, `templates/`, or `contract/`.
- Prefer scenario tests that validate a meaningful workflow over one assertion per field or cell.
- Avoid adding regression-only folders while the starter kit is pre-live.
