"""Tests for deterministic public API snapshots and comparisons."""

from __future__ import annotations

import json

from scripts import generate_public_api_compatibility as compatibility


def _sources(function_source: str, *, lifecycle: str = "SUPPORTED_PUBLIC_API") -> dict[str, str]:
    return {
        "src/fabricops_kit/public_api.py": (
            f'{lifecycle} = ("fabricops_kit.example.demo.demo",)\n'
            "PREVIEW_PUBLIC_API = ()\n"
            "DISCONTINUED_PUBLIC_API = ()\n"
        ),
        "src/fabricops_kit/example/demo.py": function_source,
    }


def _snapshot(function_source: str, *, version: str, lifecycle: str = "SUPPORTED_PUBLIC_API") -> dict:
    return compatibility.build_snapshot(
        version=version,
        revision=f"revision-{version}",
        source_kind="test",
        sources=_sources(function_source, lifecycle=lifecycle),
    )


def _change(before: str, after: str, *, before_lifecycle: str = "SUPPORTED_PUBLIC_API", after_lifecycle: str = "SUPPORTED_PUBLIC_API") -> dict:
    comparison = compatibility.compare_snapshots(
        _snapshot(before, version="before", lifecycle=before_lifecycle),
        _snapshot(after, version="after", lifecycle=after_lifecycle),
    )
    assert comparison["summary"]["total"] == 1
    return comparison["changes"][0]


def test_snapshot_generation_is_deterministic_and_captures_signature_contract() -> None:
    """The AST snapshot is stable and includes every binding detail."""
    sources = _sources(
        "def demo(first: int, /, second='x', *items: str, flag: bool, limit=None, **options) -> list[str]:\n"
        "    return []\n"
    )

    first = compatibility.build_snapshot(version="v1.0.0", revision="abc", source_kind="test", sources=sources)
    second = compatibility.build_snapshot(version="v1.0.0", revision="abc", source_kind="test", sources=sources)

    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)
    record = first["apis"][0]
    assert record["qualified_name"] == "fabricops_kit.example.demo.demo"
    assert record["lifecycle"] == "Live"
    assert record["return_annotation"] == "list[str]"
    assert [parameter["kind"] for parameter in record["parameters"]] == [
        "positional_only",
        "positional_or_keyword",
        "var_positional",
        "keyword_only",
        "keyword_only",
        "var_keyword",
    ]
    assert record["signature"] == (
        "demo(first: int, /, second = 'x', *items: str, flag: bool, limit = None, **options) -> list[str]"
    )


def test_required_parameter_addition_is_potentially_breaking() -> None:
    """Existing callers cannot omit a newly required parameter."""
    change = _change("def demo(value=1):\n    pass\n", "def demo(value=1, required=None):\n    pass\n")
    assert change["classification"] == "nonbreaking"

    change = _change("def demo(value=1):\n    pass\n", "def demo(value, required):\n    pass\n")
    assert change["classification"] == "potentially_breaking"
    assert "Required parameter added: required." in change["reasons"]
    assert "Parameter became required: value." in change["reasons"]


def test_parameter_removal_kind_and_order_changes_are_potentially_breaking() -> None:
    """Binding changes are classified conservatively."""
    removed = _change("def demo(first, second=2):\n    pass\n", "def demo(first):\n    pass\n")
    kind = _change("def demo(*, value=None):\n    pass\n", "def demo(value=None):\n    pass\n")
    reordered = _change("def demo(first, second):\n    pass\n", "def demo(second, first):\n    pass\n")
    inserted = _change("def demo(first, second=2):\n    pass\n", "def demo(first, inserted=1, second=2):\n    pass\n")

    assert removed["classification"] == "potentially_breaking"
    assert kind["classification"] == "potentially_breaking"
    assert reordered["classification"] == "potentially_breaking"
    assert inserted["classification"] == "potentially_breaking"


def test_default_and_annotation_changes_require_review() -> None:
    """Static evidence cannot prove semantic compatibility for these changes."""
    default = _change("def demo(value=1):\n    pass\n", "def demo(value=2):\n    pass\n")
    annotation = _change("def demo(value: int) -> int:\n    return value\n", "def demo(value: str) -> str:\n    return value\n")

    assert default["classification"] == "review_required"
    assert annotation["classification"] == "review_required"


def test_lifecycle_promotion_and_demotion_are_distinguished() -> None:
    """Live demotion breaks support while Preview promotion does not."""
    source = "def demo(value=None):\n    pass\n"
    promotion = _change(
        source,
        source,
        before_lifecycle="PREVIEW_PUBLIC_API",
        after_lifecycle="SUPPORTED_PUBLIC_API",
    )
    demotion = _change(
        source,
        source,
        before_lifecycle="SUPPORTED_PUBLIC_API",
        after_lifecycle="PREVIEW_PUBLIC_API",
    )
    discontinued = _change(
        source,
        source,
        before_lifecycle="SUPPORTED_PUBLIC_API",
        after_lifecycle="DISCONTINUED_PUBLIC_API",
    )

    assert promotion["classification"] == "nonbreaking"
    assert demotion["classification"] == "potentially_breaking"
    assert discontinued["classification"] == "potentially_breaking"


def test_legacy_export_fallback_is_explicitly_uncertain() -> None:
    """Pre-registry package exports are useful evidence but never declared compatible."""
    legacy = compatibility.build_snapshot(
        version="v0.0.1",
        revision="old",
        source_kind="git_tag",
        sources={
            "src/fabricops_kit/__init__.py": (
                'FUNCTION_EXPORTS = ("demo",)\nOTHER_EXPORTS = ()\n'
                "__all__ = FUNCTION_EXPORTS + OTHER_EXPORTS\n"
            ),
            "src/fabricops_kit/example.py": "def demo(value=None):\n    pass\n",
        },
    )
    current = _snapshot("def demo(value=None):\n    pass\n", version="main")

    assert legacy["lifecycle_source"] == "legacy_package_exports"
    assert legacy["certainty"] == "uncertain"
    assert legacy["apis"][0]["lifecycle"] == "Unknown"
    comparison = compatibility.compare_snapshots(legacy, current)
    assert comparison["changes"]
    assert all(change["classification"] != "nonbreaking" for change in comparison["changes"])
    assert any("uncertain" in reason.lower() for reason in comparison["changes"][0]["reasons"])


def test_unresolved_registry_entry_requires_review_instead_of_disappearing() -> None:
    """Missing source evidence remains visible in the snapshot and comparison."""
    missing = compatibility.build_snapshot(
        version="v1.0.0",
        revision="old",
        source_kind="git_tag",
        sources={
            "src/fabricops_kit/public_api.py": (
                'SUPPORTED_PUBLIC_API = ("fabricops_kit.missing.demo",)\nPREVIEW_PUBLIC_API = ()\n'
            )
        },
    )
    current = _snapshot("def demo():\n    pass\n", version="main")

    assert missing["apis"][0]["extraction_error"]
    comparison = compatibility.compare_snapshots(missing, current)
    assert comparison["changes"][0]["classification"] == "review_required"


def test_same_named_function_elsewhere_does_not_resolve_registry_identity() -> None:
    """A same-named function outside the registered path is not identity evidence."""
    snapshot = compatibility.build_snapshot(
        version="v1.0.0",
        revision="old",
        source_kind="git_tag",
        sources={
            "src/fabricops_kit/public_api.py": (
                'SUPPORTED_PUBLIC_API = ("fabricops_kit.expected.demo",)\nPREVIEW_PUBLIC_API = ()\n'
            ),
            "src/fabricops_kit/unrelated.py": "def demo(value=None):\n    pass\n",
        },
    )

    assert snapshot["certainty"] == "uncertain"
    assert snapshot["apis"][0]["source_qualified_name"] is None
    assert snapshot["apis"][0]["extraction_error"]


def test_package_shorthand_resolves_only_through_verified_re_export() -> None:
    """A registry package attribute may resolve through its actual static import."""
    snapshot = compatibility.build_snapshot(
        version="v1.0.0",
        revision="old",
        source_kind="git_tag",
        sources={
            "src/fabricops_kit/public_api.py": (
                'SUPPORTED_PUBLIC_API = ("fabricops_kit.pipeline.demo",)\nPREVIEW_PUBLIC_API = ()\n'
            ),
            "src/fabricops_kit/pipeline/__init__.py": "from .owner import demo\n",
            "src/fabricops_kit/pipeline/owner.py": "def demo(value=None):\n    pass\n",
        },
    )

    assert snapshot["certainty"] == "certain"
    assert snapshot["apis"][0]["source_qualified_name"] == "fabricops_kit.pipeline.owner.demo"


def test_explicit_parameters_that_consume_variadic_inputs_are_potentially_breaking() -> None:
    """New explicit bindings must not be treated as harmless optional additions."""
    positional = _change("def demo(*items):\n    pass\n", "def demo(value=None, *items):\n    pass\n")
    keyword = _change("def demo(**options):\n    pass\n", "def demo(*, flag=None, **options):\n    pass\n")

    assert positional["classification"] == "potentially_breaking"
    assert "consume an existing *args value" in " ".join(positional["reasons"])
    assert keyword["classification"] == "potentially_breaking"
    assert "consume an existing **kwargs key" in " ".join(keyword["reasons"])


def test_published_release_snapshots_use_each_tags_actual_source() -> None:
    """Release snapshots are extracted from tags and do not clone current definitions."""
    payload = compatibility.build_payload(tags=("v0.1.0", "v0.2.0"))
    snapshots = {snapshot["version"]: snapshot for snapshot in payload["snapshots"]}

    assert payload["versions"] == ["v0.1.0", "v0.2.0", "main", "working-tree"]
    assert snapshots["v0.1.0"]["source_kind"] == "git_tag"
    assert snapshots["v0.2.0"]["source_kind"] == "git_tag"
    assert snapshots["v0.1.0"]["revision"] != snapshots["v0.2.0"]["revision"]
    assert len(snapshots["v0.1.0"]["apis"]) == 26
    assert len(snapshots["v0.2.0"]["apis"]) == 28
    assert snapshots["v0.1.0"]["apis"] != snapshots["v0.2.0"]["apis"]
    assert all(record["extraction_error"] is None for record in snapshots["v0.1.0"]["apis"])
    assert all(record["extraction_error"] is None for record in snapshots["v0.2.0"]["apis"])
    assert snapshots["working-tree"]["revision"] is None
    assert snapshots["main"]["revision"]
    assert snapshots["main"]["source_kind"] == "git_branch"
    assert snapshots["working-tree"]["source_digest"].startswith("sha256:")
    assert "does not assert a Git branch identity" in snapshots["working-tree"]["notes"][-1]
    comparison = next(
        comparison
        for comparison in payload["comparisons"]
        if comparison["baseline"] == "v0.1.0" and comparison["target"] == "v0.2.0"
    )
    assert comparison["summary"]["total"] > 0
    assert comparison["summary"]["potentially_breaking"] > 0


def test_payload_generation_is_byte_deterministic(tmp_path) -> None:
    """Repeated generation produces identical committed JSON bytes."""
    first = tmp_path / "first.json"
    second = tmp_path / "second.json"

    compatibility.write_payload(first, tags=("v0.1.0", "v0.2.0"))
    compatibility.write_payload(second, tags=("v0.1.0", "v0.2.0"))

    assert first.read_bytes() == second.read_bytes()
