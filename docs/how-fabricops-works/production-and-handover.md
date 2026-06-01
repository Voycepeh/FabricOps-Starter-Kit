# Production and Handover

The kit is designed to stay self-contained within Fabric, so production promotion should remain lightweight.

Promote the production-ready `03_pc` notebook, run it with the production `00_env_config`, and store a copy of the final production notebook in the Governance workspace metadata lakehouse. This copy can later be used to generate AI-assisted handover material.

## Promote the production notebook

* `00_env_config` is environment-specific and should not be blindly promoted.
* Promote production-ready `03_pc` notebooks from Engineering Dev to Engineering Prod.
* Do not promote development outputs. Production outputs should be created by production notebooks running in production.
* Promote or recreate approved metadata through a controlled process.
* Production pipelines must read only production config and approved production metadata.

Do not copy development paths, draft metadata, or unreviewed rules into production.

## Store notebook evidence for handover

Once a production `03_pc` pipeline is stable, store a copy of the production notebook as a `.py` or `.ipynb` file in the Governance workspace lakehouse file area.

This keeps the handover grounded in the actual production implementation.

The exported notebook can then be used with a reusable AI prompt to generate:

* a handover summary;
* an AI manifest;
* production support notes; and
* a data product explanation.

Review the generated material before publishing it. AI can speed up documentation and support preparation, but people remain accountable for the approved metadata and production notebook.

## Return to the overview

Return to [How FabricOps Works](index.md) or follow the [Quick Start](../quick-start.md) to begin configuring Fabric.
