# Releases

FabricOps Starter Kit releases are organized around the surfaces users actually install, copy, run, and validate in Microsoft Fabric.

Each release note should focus on:

- callable package functions exported by `fabricops_kit`
- plug-and-play notebook templates under `templates/notebooks/`
- metadata outputs written by workflow notebooks and helper functions
- documentation and example changes
- compatibility checks for Python, package dependencies, and Microsoft Fabric runtime assumptions
- test coverage and release validation evidence
- breaking changes that can affect existing notebooks, metadata tables, or package calls
- migration notes users must complete before replacing an existing version

## Release notes

- [FabricOps Starter Kit v1.0.0](v1.0.0.md)

## Maintainer checklist for future release notes

Before publishing a release, maintainers should update the release page from the release diff and replace any `Needs maintainer review` entries with verified evidence.
