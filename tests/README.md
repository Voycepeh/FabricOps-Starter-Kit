# Test Suite Guide

This test suite validates the current **FabricOps Starter Kit** lifecycle implementation with local, public-safe tests.

## Test categories

FabricOps keeps a deliberately small pytest suite:

- `unit`: focused tests for public functions, validation, config resolution, agreement logic, metadata helpers, and core transformations.
- `integration`: mocked boundary tests for Lakehouse/Warehouse IO, file readers, metadata persistence, and Fabric-facing setup helpers.
- `spark`: a small number of tests that need a local Spark session for DQ and schema behaviour.
- `contract`: minimal public contract and notebook-template workflow checks.

Unit tests should remain fast and deterministic. Integration tests use local fakes and mocks; they must not require a live workspace. Spark tests should be limited to behaviour that cannot be trusted through mocks. Contract tests protect importability, essential schemas, and supported template workflows without checking exact wording or notebook presentation.

Every test must identify the meaningful behavioural or public-contract regression it prevents. Prefer structural parsing for notebooks and generated artifacts; do not freeze equivalent SQL formatting, serialized source text, or documentation prose.

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

## Fabric widget smoke test

Local tests do not prove Microsoft Fabric rendering. Before a widget UI release, run every live widget in a Fabric notebook at normal landscape width and confirm:

- controls are not clipped and the page does not scroll horizontally;
- long table, column, schema, and DQ selections scroll inside their panes;
- table and column navigation does not resize the whole cell excessively;
- switching DQ rule types does not cause major layout jumps;
- status messages do not substantially move the primary action;
- save controls remain visible and predictably placed;
- DataFrame output still uses Fabric-native `display()` outside the widget; and
- rerunning or reopening the notebook recreates each widget normally.

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
