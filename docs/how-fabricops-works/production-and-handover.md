# Production and Handover

Keep production promotion lightweight. Promote the repeatable notebook, use production-specific configuration, and generate handover material from the implementation that actually runs in production.

## Promote the production notebook

- `00_env_config` is environment-specific and should not be blindly promoted.
- Promote production-ready `03_pc` notebooks from Engineering Dev to Engineering Prod.
- Do not promote development outputs. Production notebooks create production outputs when they run.
- Promote or recreate approved metadata through a controlled process.
- Production pipelines must read production config and approved production metadata only.

Do not copy development paths, draft metadata, or unreviewed rules into production.

## Store notebook evidence for handover

Once a production `03_pc` pipeline is stable, store a copy of the production notebook as a `.py` or `.ipynb` file in the Governance workspace lakehouse file area. This keeps the handover grounded in the production implementation.

Use the exported notebook plus a reusable AI prompt to generate:

- a human-readable handover summary;
- an AI manifest;
- production support notes; and
- a data product explanation.

Review the generated material before publishing it. AI speeds up explanation and support preparation, while people remain accountable for the approved metadata and production notebook.

## Return to the overview

Return to [How FabricOps Works](index.md) or follow the [Quick Start](../quick-start.md) to begin configuring Fabric.
