# Implementation Module Catalogue

Implementation Modules document only current major source boundaries for package maintainers and internal helper traceability, not every `.py` file in `src/fabricops_kit`.

Zero-callable modules are hidden unless explicitly allowlisted as major internal plumbing. `metadata` is allowlisted as shared internal plumbing because it owns metadata keys, audit fields, and persistence helpers used by multiple workflows. The public v1 callable API is controlled by `src/fabricops_kit/__init__.py::__all__` and is surfaced through the Function Reference catalogue.

- [`config`](config.md)
- [`data_agreement`](data_agreement.md)
- [`governance_review`](governance_review.md)
- [`data_profiling`](data_profiling.md)
- [`fabric_input_output`](fabric_input_output.md)
- [`io_core`](io_core.md)
- [`data_lineage`](data_lineage.md)
- [`guardrails`](guardrails.md)
- [`metadata`](metadata.md)
- [`pipeline`](pipeline.md)
