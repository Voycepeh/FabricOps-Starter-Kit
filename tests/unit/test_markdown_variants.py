"""Smoke tests for documentation build artifacts."""

from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
HOOK_PATH = ROOT / "docs" / "copy_markdown_variants.py"


def _load_hook_module():
    spec = importlib.util.spec_from_file_location("copy_markdown_variants", HOOK_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_markdown_variant_hook_publishes_agent_friendly_entrypoints(tmp_path: Path) -> None:
    """Verify markdown variant hook publishes agent friendly entrypoints."""
    hook = _load_hook_module()
    site_dir = tmp_path / "site"

    hook.on_post_build({"docs_dir": str(ROOT / "docs"), "site_dir": str(site_dir)})

    expected_paths = [
        site_dir / "llms.txt",
        site_dir / "guided-demo.md",
        site_dir / "how-fabricops-works.md",
        site_dir / "reference.md",
        site_dir / "reference" / "dq-rules.md",
    ]
    missing_paths = [str(path.relative_to(site_dir)) for path in expected_paths if not path.exists()]

    assert missing_paths == []


def test_markdown_variant_hook_preserves_grouped_source_paths(tmp_path: Path) -> None:
    """Verify grouped docs publish Markdown variants at grouped paths only."""
    hook = _load_hook_module()
    site_dir = tmp_path / "site"

    hook.on_post_build({"docs_dir": str(ROOT / "docs"), "site_dir": str(site_dir)})

    expected_grouped_paths = [
        site_dir / "how-fabricops-works" / "notebook-templates" / "index.md",
        site_dir / "how-fabricops-works" / "notebook-templates" / "environment-config.md",
        site_dir / "how-fabricops-works" / "notebook-templates" / "agreement-setup.md",
        site_dir / "how-fabricops-works" / "notebook-templates" / "pipeline-execution.md",
        site_dir / "how-fabricops-works" / "notebook-templates" / "governance-review.md",
        site_dir / "how-fabricops-works" / "notebook-templates" / "metadata-dashboard.md",
        site_dir / "how-fabricops-works" / "guardrails" / "pipeline-guardrails.md",
        site_dir / "how-fabricops-works" / "guardrails" / "guardrail-authoring.md",
        site_dir / "how-fabricops-works" / "api" / "template-driven-api.md",
    ]
    stale_flat_paths = [
        site_dir / "how-fabricops-works" / "notebook-templates.md",
        site_dir / "how-fabricops-works" / "environment-config.md",
        site_dir / "how-fabricops-works" / "agreement-setup.md",
        site_dir / "how-fabricops-works" / "pipeline-execution.md",
        site_dir / "how-fabricops-works" / "governance-review.md",
        site_dir / "how-fabricops-works" / "metadata-dashboard.md",
        site_dir / "how-fabricops-works" / "pipeline-guardrails.md",
        site_dir / "how-fabricops-works" / "guardrail-authoring.md",
        site_dir / "how-fabricops-works" / "template-driven-api.md",
    ]

    missing_grouped_paths = [str(path.relative_to(site_dir)) for path in expected_grouped_paths if not path.exists()]
    stale_paths = [str(path.relative_to(site_dir)) for path in stale_flat_paths if path.exists()]

    assert missing_grouped_paths == []
    assert stale_paths == []


def test_markdown_variant_hook_publishes_versioned_agent_friendly_entrypoints(tmp_path: Path) -> None:
    """Verify markdown variant hook publishes versioned agent friendly entrypoints."""
    hook = _load_hook_module()
    versioned_site_dir = tmp_path / "site" / "1.2.3"

    hook.on_post_build({"docs_dir": str(ROOT / "docs"), "site_dir": str(versioned_site_dir)})

    expected_paths = [
        versioned_site_dir / "llms.txt",
        versioned_site_dir / "guided-demo.md",
        versioned_site_dir / "reference.md",
    ]
    missing_paths = [str(path.relative_to(versioned_site_dir)) for path in expected_paths if not path.exists()]

    assert missing_paths == []


def test_llms_txt_uses_relative_documentation_links_for_versioned_snapshots() -> None:
    """Verify llms txt uses relative documentation links for versioned snapshots."""
    llms_text = (ROOT / "docs" / "llms.txt").read_text(encoding="utf-8")

    assert "https://voycepeh.github.io/FabricOps-Starter-Kit/" not in llms_text
    assert "(how-fabricops-works.md)" in llms_text
    assert "(reference.md)" in llms_text
    assert "(reference/dq-rules.md)" in llms_text
