from pathlib import Path


def test_individual_reference_generator_does_not_own_function_call_graph_page() -> None:
    generator = Path("scripts/generate_individual_function_reference_pages.py").read_text(encoding="utf-8")

    assert "FUNCTION_CALL_GRAPH_PAGE_PATH.write_text" not in generator
