"""Tests for true-unused classification in the public call-flow generator."""

from __future__ import annotations

from pathlib import Path

from scripts import generate_public_function_call_flows_json as flows


def _write_project(tmp_path: Path) -> tuple[Path, Path, Path]:
    root = tmp_path
    pkg = root / "src" / "fabricops_kit"
    pkg.mkdir(parents=True)
    init_path = pkg / "__init__.py"
    init_path.write_text(
        "from .entry import public_entry\n"
        "__all__ = ['public_entry']\n",
        encoding="utf-8",
    )
    (pkg / "entry.py").write_text(
        "from .internal import reached_helper\n\n"
        "def public_entry():\n"
        "    return reached_helper()\n",
        encoding="utf-8",
    )
    (pkg / "internal.py").write_text(
        "def reached_helper():\n"
        "    return None\n\n"
        "def detached_root():\n"
        "    detached_helper()\n"
        "    return callback_consumer()\n\n"
        "def detached_helper():\n"
        "    return None\n\n"
        "def callback_only():\n"
        "    return None\n\n"
        "CALLBACKS = {'callback': callback_only}\n\n"
        "def body_callback_only():\n"
        "    return None\n\n"
        "def callback_consumer():\n"
        "    return {'label_fn': body_callback_only}\n\n"
        "def orphan():\n"
        "    return None\n\n"
        "def __getattr__(name):\n"
        "    raise AttributeError(name)\n",
        encoding="utf-8",
    )
    manifests = root / "docs" / "releases" / "manifests"
    manifests.mkdir(parents=True)
    return root, pkg, init_path


def test_unused_cleanup_only_keeps_unreferenced_roots(tmp_path: Path) -> None:
    """Internal references and Python hooks must not be reported as unused cleanup rows."""
    root, pkg, init_path = _write_project(tmp_path)

    payload = flows.build_payload(root=root, pkg_dir=pkg, init_path=init_path)

    unused_names = {row["function_name"] for row in payload["defined_but_not_used"]}
    assert unused_names == {"detached_root", "orphan"}

    detached_names = {
        payload_name.split(".")[-1]
        for payload_name in payload["detached_functions"]
    }
    assert {"detached_helper", "callback_only", "callback_consumer", "body_callback_only", "__getattr__"} <= detached_names

    source_referenced_names = {
        payload_name.split(".")[-1]
        for payload_name in payload["source_referenced_functions"]
    }
    assert {"detached_helper", "callback_only", "callback_consumer", "body_callback_only"} <= source_referenced_names
    assert "__getattr__" not in source_referenced_names

    runtime_hook_names = {
        payload_name.split(".")[-1]
        for payload_name in payload["implicit_runtime_hook_functions"]
    }
    assert runtime_hook_names == {"__getattr__"}

    assert payload["summary"]["defined_but_not_used_count"] == 2
    assert payload["summary"]["detached_function_count"] == 5
    assert all(row["inbound_source_references"] == [] for row in payload["defined_but_not_used"])


def test_global_source_references_capture_internal_calls_and_module_registries(tmp_path: Path) -> None:
    """Global inbound references should include detached calls and module-level callback wiring."""
    root, pkg, _ = _write_project(tmp_path)
    modules = flows.discover_modules(pkg)
    functions = flows.discover_functions(modules, root)

    inbound = flows.build_global_source_references(modules, functions)

    detached_helper = "fabricops_kit.internal.detached_helper"
    callback_only = "fabricops_kit.internal.callback_only"
    callback_consumer = "fabricops_kit.internal.callback_consumer"
    body_callback_only = "fabricops_kit.internal.body_callback_only"
    assert inbound[detached_helper] == {"fabricops_kit.internal.detached_root"}
    assert inbound[callback_only] == {"fabricops_kit.internal::<module>"}
    assert inbound[callback_consumer] == {"fabricops_kit.internal.detached_root"}
    assert inbound[body_callback_only] == {"fabricops_kit.internal.callback_consumer"}
