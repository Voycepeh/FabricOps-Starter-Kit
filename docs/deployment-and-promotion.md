# Deploy

This page explains: promotion controls, release strategy, and environment movement.
Use this when: you are planning how approved notebooks and metadata move to production.
Next read: [Install](install.md), [Workflow](lifecycle-operating-model.md), [Metadata](metadata-and-contracts/index.md).

## Promotion model

- Support both **Git-available** and **Git-restricted** Fabric environments.
- Use **Fabric deployment pipelines** for controlled environment movement.
- Keep `00_env_config` environment-local so paths/stores are correct per target.

## What gets promoted

1. Selected notebooks by stage ownership and release readiness.
2. Contract/evidence dependencies (approved metadata and related controls).
3. Production notebook versions with traceable release tags/checkpoints.

## Controls to enforce

- Promote only notebooks with completed human approvals.
- Validate metadata target routing before cutover.
- Keep version history of production notebooks and governance evidence.
