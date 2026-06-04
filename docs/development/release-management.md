# Release Management

FabricOps Starter Kit releases are managed around the project surfaces users install, copy, run, and validate: callable package functions, plug-and-play Microsoft Fabric notebook templates, metadata outputs, documentation, compatibility evidence, and migration notes.

## Release process

1. Create the release branch from `main`.
2. Update the version in `pyproject.toml`.
3. Confirm `fabricops_kit.__version__` matches the release version.
4. Update `CHANGELOG.md`.
5. Add `docs/releases/vX.Y.Z.md`.
6. Update `docs/feature-list.md`.
7. Update `docs/compatibility.md`.
8. Update `docs/test-matrix.md`.
9. Document breaking changes in `docs/breaking-changes.md` and the release note.
10. Run tests.
11. Build the wheel.
12. Create the git tag after merge.
13. Create the GitHub Release.
14. Attach the wheel artifact.
15. Install and validate the wheel in Microsoft Fabric.

## Recommended release note structure

Each release note should use the same high-level structure:

- Release summary
- Upgrade impact
- Callable functions
- Notebook templates
- Metadata outputs
- Documentation
- Breaking changes
- Deprecated
- Migration notes
- Tested compatibility

## Release evidence expectations

Release evidence should include:

- package version alignment
- package import check
- wheel build output
- relevant pytest output
- MkDocs build output
- Fabric notebook smoke-test evidence where templates changed
- metadata write validation when metadata outputs changed
- maintainer review notes for entries marked `Needs maintainer review`

## Maintainer review remains required

Automation can prove that tests and builds run, but it does not replace maintainer review. Before publishing a release, maintainers must verify the release diff and update any uncertain release details.
