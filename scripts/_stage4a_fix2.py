"""One-shot corrections for the Stage 4A completion pass."""

from pathlib import Path


def _replace_once(text: str, old: str, new: str, *, label: str) -> str:
    if old not in text:
        raise RuntimeError(f"Expected Stage 4A text not found for {label}: {old}")
    return text.replace(old, new, 1)


def _restore_rule_audit_fields() -> None:
    path = Path("src/fabricops_kit/pipeline/guardrail_metadata.py")
    text = path.read_text()
    text = _replace_once(
        text,
        "    parameters = _parse_parameters(record)\n    return {\n",
        "    audit = build_runtime_audit_fields(config=config, env=env)\n    parameters = _parse_parameters(record)\n    return {\n",
        label="canonical rule audit resolution",
    )
    text = _replace_once(
        text,
        '        "is_active": bool(record.get("is_active", True)),\n    }\n',
        '        "is_active": bool(record.get("is_active", True)),\n        **audit,\n    }\n',
        label="canonical rule audit fields",
    )
    path.write_text(text)


def _align_writer_test_with_authoritative_module() -> None:
    path = Path("tests/unit/test_guardrail_metadata_contract.py")
    text = path.read_text()
    text = _replace_once(
        text,
        "from fabricops_kit.pipeline import guardrail_metadata\n",
        "from fabricops_kit.pipeline import guardrail_metadata, guardrails_shared\n",
        label="shared writer test import",
    )
    text = _replace_once(
        text,
        '    monkeypatch.setattr(guardrail_metadata, "build_runtime_audit_fields", lambda **_kwargs: _audit())\n    monkeypatch.setattr(guardrail_metadata, "configured_lakehouse_schema", lambda *_args, **_kwargs: None)\n    monkeypatch.setattr(\n        guardrail_metadata,\n        "write_lakehouse_table_core",\n',
        '    monkeypatch.setattr(guardrails_shared, "build_runtime_audit_fields", lambda **_kwargs: _audit())\n    monkeypatch.setattr(guardrails_shared, "configured_lakehouse_schema", lambda *_args, **_kwargs: None)\n    monkeypatch.setattr(\n        guardrails_shared,\n        "write_lakehouse_table_core",\n',
        label="shared writer monkeypatches",
    )
    path.write_text(text)


if __name__ == "__main__":
    _restore_rule_audit_fields()
    _align_writer_test_with_authoritative_module()
    Path(__file__).unlink()
