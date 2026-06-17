# Documentation versioning

FabricOps Starter Kit documentation is maintained from the same source tree as the package. The `main` branch represents documentation source for the next change, while released documentation is locked with Mike from Git tags.

## Version policy

Package versions and published Mike documentation snapshots use full semantic versions, for example `1.0.2`. This preserves an exact documentation URL for each released wheel. Release aliases can still point users to the newest or recommended production snapshot.

| Package version | Documentation version |
| --- | --- |
| `1.0.0` | `1.0.0` |
| `1.0.1` | `1.0.1` |
| `1.1.0` | `1.1.0` |

## Aliases

- `latest` points to the newest released documentation.
- `stable` points to the recommended production documentation. Initially it moves with `latest` unless maintainers document a different recommendation.
- `dev` may point to a preview built from `main`.

Do not automatically make `main` the `latest` documentation version. Only a validated release tag updates `latest`.

## Build-time traceability

The documentation build generates a release traceability page with the full package version, Mike documentation version, and Git commit SHA. Release builds pass those values from GitHub Actions environment variables; local builds derive the package version from `pyproject.toml` and the commit from Git when available.

## Template and wheel alignment

Released documentation, released wheel files, and released notebook templates must be frozen together. Dev documentation may point to `main` branch templates, but released documentation should point to the matching Git tag or release assets.

Mike release snapshots freeze all static documentation artifacts together, including rendered HTML pages, `/llms.txt`, sibling `.md` page variants, and generated reference manifests. Keep `llms.txt` as a static build artifact with relative documentation links so each versioned snapshot serves its own frozen copies, such as `/<version>/llms.txt`, `/<version>/guided-demo.md`, and `/<version>/reference.md`.

Template downloads should use the same release as the wheel, ideally as a `templates.zip` release asset. This avoids users reading released documentation while opening a newer notebook that expects a newer wheel or metadata schema.

## Release process

See [Release management](release-management.md) for the complete GitHub-only release flow, local validation commands, Mike deployment behavior, and retry guidance.
