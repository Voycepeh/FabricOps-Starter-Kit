# Documentation versioning

FabricOps Starter Kit documentation is maintained from the same source tree as the package. The `main` branch represents the latest documentation source and should stay ready for the next release.

## Release notes and source snapshots

Release notes are kept as individual files under `docs/releases/` using the `vX.Y.Z.md` naming pattern. For example, release notes for version `1.0.0` should live in `docs/releases/v1.0.0.md`.

Git tags represent release documentation snapshots. When maintainers tag a release, the tag captures the package source, generated reference documentation, and release notes for that exact version.

## Published documentation versions

Full documentation versions should be published with [mike](https://github.com/jimporter/mike), rather than by manually duplicating the documentation tree into folders such as `docs/v1.0` or `docs/v1.1`.

Published documentation should expose version labels such as:

- `1.0` for the 1.0 release line.
- `1.1` for the 1.1 release line.
- `latest` for the newest published release.
- `stable` for the recommended production baseline when it differs from `latest`.

Users should read the documentation version that matches their installed wheel version. For example, users running a `1.0.x` wheel should use the `1.0` documentation unless the release notes direct them to a more specific patch-level note.
