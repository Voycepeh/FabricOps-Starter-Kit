# Implementation Module Catalogue

Implementation modules are curated source-level reference pages for package maintainers and internal helper traceability.

They are useful for debugging major implementation boundaries, but they are not the public v1 callable API and are not generated for every `.py` file. The public v1 callable API is controlled by `src/fabricops_kit/__init__.py::__all__` and is surfaced through the Function Reference catalogue.

Zero-callable modules are hidden unless explicitly allowlisted as major internal plumbing, such as `metadata`.

- [`config`](config.md)
- [`data_agreement`](data_agreement.md)
- [`data_lineage`](data_lineage.md)
- [`data_profiling`](data_profiling.md)
- [`drift`](drift.md)
- [`fabric_input_output`](fabric_input_output.md)
- [`governance_review`](governance_review.md)
- [`handover`](handover.md)
- [`metadata`](metadata.md)
