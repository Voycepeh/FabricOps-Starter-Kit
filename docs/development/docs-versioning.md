# Documentation versioning

FabricOps Starter Kit documentation is maintained from the same source tree as the package. The `main` branch represents the latest documentation source and should stay ready for the next release.

This page prepares documentation versioning infrastructure. It does **not** declare FabricOps Starter Kit as officially `v1.0.0` stable.

## Version policy

Package versions use full semantic versions, for example `1.0.2`. Published documentation versions use major/minor versions, for example `1.0`.

Patch releases normally reuse the same major/minor documentation site. Release notes may still be patch-specific, using files such as `docs/releases/v1.0.2.md`.

Use this mapping when publishing documentation:

| Package version | Documentation version |
| --- | --- |
| `1.0.0` | `1.0` |
| `1.0.1` | `1.0` |
| `1.1.0` | `1.1` |

## Source snapshots and release notes

Release notes are kept as individual files under `docs/releases/` using the `vX.Y.Z.md` naming pattern. For example, release notes for package version `1.0.2` should live in `docs/releases/v1.0.2.md`.

Git tags represent release source snapshots. When maintainers tag a release, the tag captures the package source, generated reference documentation, and release notes for that exact version.

## Published documentation versions

Full documentation versions should be published with [mike](https://github.com/jimporter/mike), rather than by manually duplicating the documentation tree into folders such as `docs/v1.0` or `docs/v1.1`.

Published documentation should expose version labels such as:

- `1.0` for the 1.0 release line.
- `1.1` for the 1.1 release line.
- `latest` for the newest published release.
- `stable` for the recommended production baseline when it differs from `latest`.

Users should read the documentation version that matches their installed wheel version. For example, users running a `1.0.x` wheel should use the `1.0` documentation unless the release notes direct them to a more specific patch-level note.
