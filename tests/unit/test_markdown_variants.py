"""Smoke tests for AI-friendly documentation build artifacts."""

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
    hook = _load_hook_module()
    site_dir = tmp_path / "site"

    hook.on_post_build({"docs_dir": str(ROOT / "docs"), "site_dir": str(site_dir)})

    expected_paths = [
        site_dir / "llms.txt",
        site_dir / "quick-start.md",
        site_dir / "how-fabricops-works.md",
        site_dir / "reference.md",
        site_dir / "reference" / "dq-rules.md",
    ]
    missing_paths = [str(path.relative_to(site_dir)) for path in expected_paths if not path.exists()]

    assert missing_paths == []
