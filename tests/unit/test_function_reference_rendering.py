"""Regression coverage for callable reference signatures and mixed examples."""

import ast

import pytest

from scripts.generate_individual_function_reference_pages import (
    _format_api_signature,
    _format_docstring_examples,
    _parameter_rows_from_node,
    _validate_preferred_example,
    parse_docs_metadata,
    parse_module,
    parse_public_exports,
    source_module_paths,
)


def test_signature_defaults_and_variadic_parameters() -> None:
    """Keep absent defaults distinct from explicit None and preserve expressions."""
    node = ast.parse(
        "def sample(required, /, nothing=None, flag=True, disabled=False, text='a|b', "
        "count=0, ratio=1.25, items=(1, 2), factory=make_default, *args, keyword, optional=None, **options): pass"
    ).body[0]
    rows = {row["name"]: row for row in _parameter_rows_from_node(node, "**options\n    Reader options.")}
    assert rows["required"]["required"] == rows["keyword"]["required"] == "Yes"
    assert rows["required"]["default"] == "—"
    expected = {"nothing": "None", "flag": "True", "disabled": "False", "text": "'a|b'", "count": "0", "ratio": "1.25", "items": "(1, 2)", "factory": "make_default", "optional": "None"}
    for name, value in expected.items():
        assert rows[name]["default"] == value
        assert rows[name]["required"] == "No"
    assert rows["*args"]["required"] == rows["**options"]["required"] == "No"
    assert rows["**options"]["description"] == "Reader options."


def test_mixed_repl_prose_output_and_existing_fences() -> None:
    """Preserve narrative and output while making multiline REPL input copyable."""
    rendered = _format_docstring_examples('''Read one table:

>>> result = read_table(
...     "orders",
... )
>>> result["count"]
3

Use the result for a subsequent transformation.

```python
other = read_table("customers")
```

>>> print("ready")
ready
''')
    assert "Read one table:" in rendered
    assert "Use the result for a subsequent transformation." in rendered
    assert '```python\nresult = read_table(\n    "orders",\n)\nresult["count"]\n```' in rendered
    assert "```text\n3\n```" in rendered
    assert "```text\nready\n```" in rendered
    assert '```python\nother = read_table("customers")\n```' in rendered
    assert ">>>" not in rendered and "... " not in rendered
    for code in rendered.split("```python\n")[1:]:
        ast.parse(code.split("```", 1)[0])


def test_example_signature_validation_rejects_removed_arguments() -> None:
    """Reject positional calls to keyword-only APIs and missing required values."""
    signature = "def profile_table(*, dataframe=None, table_id=None)"
    with pytest.raises(RuntimeError, match="conflicts with its signature"):
        _validate_preferred_example("profile_table", signature, "profile_table(df, profile_role='source')")
    with pytest.raises(RuntimeError, match="conflicts with its signature"):
        _validate_preferred_example("sample", "def sample(*, required, optional=None)", "sample()")
    _validate_preferred_example("profile_table", signature, "profile_table(dataframe=df)")


def test_formatted_signature_preserves_keyword_only_separator() -> None:
    """A displayed signature must retain its calling convention."""
    formatted = _format_api_signature("def example(*, required: str, optional: str | None=None)", max_inline_length=10)
    assert "    *," in formatted
    ast.parse(formatted + "\n    pass")


def test_all_public_function_parameters_and_curated_examples() -> None:
    """Audit every exported function against its source and curated example."""
    exports = set(parse_public_exports())
    metadata = parse_docs_metadata()
    found = set()
    for path in source_module_paths():
        module = parse_module(path)
        for name in exports & module["functions"].keys():
            found.add(name)
            for row in module["parameters"][name]:
                assert row["description"] != "Not documented yet.", (name, row["name"])
            example = metadata[name].get("preferred_example")
            if example:
                _validate_preferred_example(name, module["signatures"][name], example)
    assert found == {name for name in exports if metadata[name]["kind"] == "function"}
