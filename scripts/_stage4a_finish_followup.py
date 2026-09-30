"""Follow-up normalization for the temporary Stage 4A completion workflow."""

from pathlib import Path


def _replace_once(text: str, old: str, new: str, *, label: str) -> str:
    if old not in text:
        raise RuntimeError(f"Expected Stage 4A text not found for {label}: {old}")
    return text.replace(old, new, 1)


def _fix_shared_result_writer() -> None:
    path = Path("src/fabricops_kit/pipeline/guardrails_shared.py")
    text = path.read_text()
    text = _replace_once(
        text,
        'results_table: str = GUARDRAIL_RESULTS_TABLE,',
        'results_table: str = "METADATA_GUARDRAIL_RESULTS",',
        label="shared result table default",
    )
    text = _replace_once(
        text,
        '"result_payload_json": _stable_json(payload),',
        '"result_payload_json": json.dumps(payload, default=str, sort_keys=True, separators=(",", ":")),',
        label="shared result payload serialization",
    )
    path.write_text(text)


if __name__ == "__main__":
    _fix_shared_result_writer()
