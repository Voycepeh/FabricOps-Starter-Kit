# Release management

This page captures maintainer-facing release documentation practices for FabricOps Starter Kit.

## Versioned documentation deployment

After tagging a release, maintainers should publish the matching documentation snapshot with mike. Use the minor release version as the published documentation version and update aliases deliberately:

```bash
mike deploy --push --update-aliases 1.0 latest stable
mike set-default --push latest
```

Use `latest` for the newest release. Use `stable` for the recommended production baseline; this can point to a different version when the newest release should not yet be the production recommendation.

Do not manually copy documentation into versioned folders such as `docs/v1.0` or `docs/v1.1`; mike manages published version directories on the documentation publishing branch. Do not publish documentation, create GitHub releases, or publish to PyPI until the release process is intentionally started by maintainers.
