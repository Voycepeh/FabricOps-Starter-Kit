# Deployment and promotion appendix

For the complete workflow, read the [FabricOps Starter Kit Operating Model](fabricops-operating-model.md). Keep deployment simple:

- `00_env_config` is environment-specific and should not be blindly promoted.
- Promote production-ready `03_pc` notebooks from Engineering Dev to Engineering Prod.
- Promote or recreate approved metadata through a controlled process.
- Production pipelines must read production config and approved production metadata only.

Do not copy development paths, draft metadata, or unreviewed rules into production.
