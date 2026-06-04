# Release management

This page captures maintainer-facing release documentation practices for FabricOps Starter Kit.

## Versioned documentation deployment

After tagging a release, maintainers should publish the matching documentation snapshot with mike. Use the minor release version as the published documentation version and update aliases deliberately:

```bash
mike deploy --push --update-aliases 1.0 latest
mike set-default --push latest
```

Use `latest` for the newest release. Use `stable` for the recommended production baseline if that baseline is different from `latest`.

Do not manually copy documentation into versioned folders such as `docs/v1.0` or `docs/v1.1`; mike manages published version directories on the documentation publishing branch.
