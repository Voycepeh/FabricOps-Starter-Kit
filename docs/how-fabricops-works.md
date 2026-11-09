<meta http-equiv="refresh" content="0; url=../architecture/">
<link rel="canonical" href="../architecture/">

# This page moved

The FabricOps operating model now lives in [Architecture](architecture.md). Engineering capabilities and Governance capabilities have their own dedicated pages.

- [Open Architecture](architecture.md)
- [Explore Engineering](engineering.md)
- [Explore Governance](governance.md)
- [Run the Guided Demo](guided-demo.md)

## Optional Source Drift observation

**Setup → Read → Observe Source Drift (optional) → Transform → Write → Finalize**. `observe_source_drift()` checks every source already read against accepted historical content, independently of Data Contracts and target Write Modes. New rows are allowed. [Engineering](engineering.md#how-does-fabricops-detect-source-drift) explains the controls, costs and baseline lifecycle.
