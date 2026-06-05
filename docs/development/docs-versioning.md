# Documentation versioning

FabricOps Starter Kit documentation is maintained from the same source tree as the package. The `main` branch represents documentation source for the next change, while released documentation is locked with Mike from Git tags.

## Version policy

Package versions use full semantic versions, for example `1.0.2`. Published Mike documentation versions use the major-minor series, for example `1.0`.

Patch releases normally reuse the same major-minor documentation site. Release notes and GitHub Releases remain patch-specific.

| Package version | Documentation version |
| --- | --- |
| `1.0.0` | `1.0` |
| `1.0.1` | `1.0` |
| `1.1.0` | `1.1` |

## Aliases

- `latest` points to the newest released documentation.
- `stable` points to the recommended production documentation. Initially it moves with `latest` unless maintainers document a different recommendation.
- `dev` may point to a preview built from `main`.

Do not automatically make `main` the `latest` documentation version. Only a validated release tag updates `latest`.

## Build-time traceability

The documentation build generates a release traceability page with the full package version, Mike documentation series, and Git commit SHA. Release builds pass those values from GitHub Actions environment variables; local builds derive the package version from `pyproject.toml` and the commit from Git when available.

## Release process

See [Release management](release-management.md) for the complete GitHub-only release flow, local validation commands, Mike deployment behavior, and retry guidance.
