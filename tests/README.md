# Test Suite Guide

This test suite validates the current **FabricOps Starter Kit** lifecycle implementation with local, fast tests.

## What is covered

- Configuration and contract loading/validation.
- Data contract normalization and rule execution behavior.
- Data quality workflows, rule compilation, and quarantine record behavior.
- Drift checks (schema/partition/profile) and orchestration summaries.
- Metadata, profiling, runtime audit columns, lineage, governance classification, and handover summary helpers.
- Docs/reference generation and consistency checks.

## What should not be tested locally

- Real Microsoft Fabric workspace access.
- Live Spark clusters/notebook runtime dependencies.
- Networked services, cloud credentials, or production resources.

Use mocks/stubs for Fabric runtime helpers and Spark-like interfaces.

## How to run

```bash
uv run pytest
uv run ruff check .
```

## Naming convention

- Name tests by current product concepts and module behavior (for example: `test_config.py`, `test_data_contract.py`, `test_dq_workflow.py`, `test_drift.py`).
- Avoid legacy MVP/template-era naming for new files.
- Prefer consolidating closely related coverage into a single clear module-focused file.
