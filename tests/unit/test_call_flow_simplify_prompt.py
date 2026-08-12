"""Tests for the Call Flow Dashboard Codex simplify prompt export."""

from scripts import generate_public_function_call_flows_dashboard as dashboard


def test_dashboard_exposes_codex_simplify_prompt_pack() -> None:
    """Keep the simplify export wired to deterministic call-flow evidence."""
    html = dashboard.render_dashboard()

    assert "Export Codex prompt pack" in html
    assert "Download Codex simplify packet" in html
    assert "function buildSimplifyPrompt(evidence)" in html
    assert "function simplifyPacket()" in html
    assert "function exportSimplifyPacket()" in html
    assert "prompt_task='simplify_preserve_behaviour'" in html
    assert "cleanup_mode='preserve_compatibility'" in html
    assert "Use AGENTS.md, existing repository patterns, deterministic call-flow evidence, and tests as the source of truth." in html
    assert "Remove unnecessary branching, duplication, wrappers, indirection, and dead implementation" in html
    assert "Keep public behaviour, accepted inputs, outputs, schemas, side effects, persisted contracts, audit behaviour, and documented errors unchanged." in html
    assert "Respect Type 1 to Type 5 architecture rules; do not introduce new architecture violations." in html
    assert "Downloaded Codex/GPT-ready simplify packet." in html
    assert "$('downloadSimplifyPacket').onclick=()=>exportSimplifyPacket()" in html
