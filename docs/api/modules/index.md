# Implementation Module Catalogue

Module pages document source modules and internal helpers for package maintainers.

They are useful for debugging and implementation traceability, but they are not the public v1 callable surface. The public v1 callable surface is controlled by `src/fabricops_kit/__init__.py::__all__` and is surfaced through the Function Reference catalogue.

Short-form modules remain import-compatible aliases but are intentionally hidden from this user-facing catalogue.

- [`business_context`](business_context.md)
- [`config`](config.md)
- [`data_agreement`](data_agreement.md)
- [`data_governance`](data_governance.md)
- [`data_lineage`](data_lineage.md)
- [`data_profiling`](data_profiling.md)
- [`data_quality`](data_quality.md)
- [`drift`](drift.md)
- [`fabric_input_output`](fabric_input_output.md)
- [`governance_review`](governance_review.md)
- [`handover`](handover.md)
- [`metadata`](metadata.md)
- [`versioning`](versioning.md)
