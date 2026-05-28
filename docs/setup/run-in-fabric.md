# Run in Fabric

## Purpose

After building the wheel, upload it to a Microsoft Fabric Environment,
publish that Environment, attach it to notebooks, and validate imports
before running the FabricOps workflow.

## Upload wheel to Fabric Environment

1. Open your Fabric workspace.
2. Go to **Environment**.
3. Open **Custom libraries**.
4. Upload the `.whl` file from `dist/`.

## Publish and attach Environment

1. Save and publish the Environment.
2. Attach the published Environment to your notebook.
3. Restart the notebook session after library changes.

## Verify import

Use current package paths.

- Use `fabricops_kit.data_profiling`.
- Do not use stale `fabricops_kit.profiling`.

Verification cells:

```python
import fabricops_kit

print(fabricops_kit.__file__)
print(getattr(fabricops_kit, "__version__", "unknown"))
```

## Run the FabricOps notebook workflow

Run notebooks in this order:

1. `00_env_config` configures paths and runtime settings.
2. `01_da_<agreement>` captures approved usage,
   restrictions, ownership, business context, and governance metadata.
3. `02_ex_<agreement>_<topic>` profiles source data and prepares AI-assisted
   DQ and classification suggestions.
4. Human approval is required before DQ/classification enforcement.
5. `03_pc_<agreement>_<pipeline>` enforces approved metadata, DQ rules,
   checks, lineage, and outputs in a run-all-safe pipeline.

## Troubleshooting

- Old wheel still active: republish Environment and restart session.
- Import fails after upload: confirm publish finished and Environment attached.
- Wrong Environment attached: verify notebook is bound to the target Environment.
- Wrong module path: use current `fabricops_kit` module names.
- Missing dependencies: add dependency to package config, rebuild, and re-upload.
- Fabric runtime dependency conflict: pin or simplify dependency versions.
- Version mismatch: bump wheel version, rebuild, and re-upload.
- Local tests pass but Fabric runtime fails: validate behavior in Fabric runtime.

## Release checklist

1. Pull latest `main`.
2. Run local validation.
3. Bump version.
4. Run `uv build`.
5. Upload wheel.
6. Publish Environment.
7. Restart notebook session.
8. Smoke test import.
9. Smoke test one notebook.
10. Record tested version.

## Related pages

- [Quick Start](../quick-start.md)
- [Deployment](../deployment-and-promotion.md)


## Fabric smoke validation (merged)

- Attach expected lakehouse/warehouse resources for the selected environment.
- Run `00_env_config` and confirm configuration checks pass.
- Execute a minimal metadata read/write dry run against the configured `metadata` target.
- Run a lightweight `02_ex` and `03_pc` flow to confirm approved-rule loading and enforcement wiring.
- Capture outcome in release evidence before scheduling production runs.
