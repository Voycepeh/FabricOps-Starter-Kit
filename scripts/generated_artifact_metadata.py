"""Shared metadata helpers for generated FabricOps documentation artifacts."""

from __future__ import annotations

from datetime import UTC, datetime
import json
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
GENERATED_ARTIFACT_METADATA_PATH = ROOT / "docs" / "reference" / "_data" / "generated-artifacts.json"
SCHEMA = "fabricops_generated_artifact_timestamps_v1"
SINGAPORE_TZ = ZoneInfo("Asia/Singapore")


def format_sgt_timestamp(value: datetime) -> str:
    """Return a Singapore timestamp using day-month-year and AM/PM format."""
    sgt_value = value.astimezone(SINGAPORE_TZ)
    hour = sgt_value.strftime("%I").lstrip("0") or "12"
    return f"{sgt_value:%d %b %Y}, {hour}:{sgt_value:%M %p} SGT"


def read_generated_artifact_metadata(
    metadata_path: Path = GENERATED_ARTIFACT_METADATA_PATH,
) -> dict[str, object]:
    """Read generated artifact metadata, returning an empty schema when absent."""
    if not metadata_path.exists():
        return {"schema": SCHEMA, "artifacts": {}}
    try:
        payload = json.loads(metadata_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"schema": SCHEMA, "artifacts": {}}
    if not isinstance(payload, dict):
        return {"schema": SCHEMA, "artifacts": {}}
    payload.setdefault("schema", SCHEMA)
    artifacts = payload.get("artifacts")
    if not isinstance(artifacts, dict):
        payload["artifacts"] = {}
    return payload


def update_generated_artifact_metadata(
    artifact_key: str,
    label: str,
    generator: str,
    output_path: str,
    metadata_path: Path = GENERATED_ARTIFACT_METADATA_PATH,
) -> dict[str, object]:
    """Write timestamp metadata for one generated artifact while preserving others."""
    generated_at = datetime.now(UTC)
    generated_at_utc = generated_at.isoformat().replace("+00:00", "Z")
    generated_at_sgt = format_sgt_timestamp(generated_at)
    payload = read_generated_artifact_metadata(metadata_path)
    artifacts = payload.setdefault("artifacts", {})
    assert isinstance(artifacts, dict)
    artifacts[artifact_key] = {
        "label": label,
        "generator": generator,
        "output_path": output_path,
        "generated_at_utc": generated_at_utc,
        "generated_at_sgt": generated_at_sgt,
    }
    payload["schema"] = SCHEMA
    payload["last_generated_at_utc"] = generated_at_utc
    payload["last_generated_at_sgt"] = generated_at_sgt
    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    metadata_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload
