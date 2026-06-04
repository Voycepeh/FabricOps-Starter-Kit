# Changelog

All notable release changes for FabricOps Starter Kit should be documented here.

FabricOps release entries are organized around user impact areas instead of generic software feature categories. Future releases must document changed callable functions, changed plug-and-play notebook templates, changed metadata tables or outputs, breaking changes, deprecated functions or templates, required user migration steps, and tested compatibility evidence.

## [v1.0.0] - Needs maintainer review before publishing

### Release summary

v1.0.0 is the first stable release baseline for FabricOps Starter Kit: governed, quality-checked, AI-ready notebooks in Microsoft Fabric.

### Upgrade impact

| Area | Impact | User action required |
| --- | --- | --- |
| Callable functions | First stable callable package baseline. | Review the generated function reference and confirm changed exports before publishing. |
| Notebook templates | First stable plug-and-play template baseline. | Review template copies before replacing existing Fabric notebooks. |
| Metadata outputs | First stable metadata output documentation baseline. | Validate configured metadata writes in a non-production workspace. |
| Documentation | Release, compatibility, test, breaking-change, and feature-list pages added. | Review entries marked `Needs maintainer review`. |
| Compatibility | Exact Fabric runtime evidence needs maintainer review. | Run wheel, import, notebook smoke, metadata write, and governance-output checks before release. |

### Callable functions

The v1.0.0 release should document any changed public exports from `src/fabricops_kit/__init__.py::__all__`. Maintainers must reconcile this section with the release diff before publishing.

### Notebook templates

The v1.0.0 release should document any changed notebooks under `templates/notebooks/`. Maintainers must reconcile this section with the release diff before publishing.

### Metadata outputs

The v1.0.0 release should document any changed metadata tables or outputs listed in the metadata table documentation. Maintainers must reconcile this section with the release diff before publishing.

### Documentation

Added release management documentation for changelog structure, release notes, feature inventory, compatibility review, test evidence, and breaking-change review.

### Breaking changes

Needs maintainer review before publishing.

### Deprecated

None currently documented.

### Migration notes

Users should confirm the installed wheel version, review changed notebook templates before replacing existing copies, run compatibility checks where available, and validate metadata output changes before production use.

### Tested compatibility

Needs maintainer review before publishing. Release evidence should include Python version, Microsoft Fabric runtime, pandas, pyspark, notebook smoke tests, package import, and wheel build results.
