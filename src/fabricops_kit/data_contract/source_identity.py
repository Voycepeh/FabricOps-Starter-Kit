"""Stable source identities shared by table and file Data Contracts."""
import hashlib
import json
from pathlib import PurePosixPath


def file_source_identity(*, workspace_id, item_id, relative_path, file_format, reader_options=None):
    """Identify a Lakehouse Files selector without manufacturing a Table ID.

    Identity includes physical workspace/item and a case-sensitive normalized
    relative selector. Folder/wildcard membership may change without changing
    the selector identity. Format and reader options are approved separately.
    """
    if any(not isinstance(value, str) or not value.strip() for value in (workspace_id, item_id, relative_path)):
        raise ValueError("File source requires workspace_id, item_id and relative_path.")
    if relative_path.startswith(("/", "\\")) or ":" in relative_path or "\\" in relative_path or ".." in relative_path.split("/"):
        raise ValueError("File selector must remain beneath the configured Lakehouse Files area.")
    path = str(PurePosixPath(relative_path))
    if path in {"", "."}:
        raise ValueError("Select a file, folder or wildcard beneath Files.")
    if file_format not in {"csv", "parquet", "json", "excel"}:
        raise ValueError("Unsupported file source format.")
    if reader_options is not None and not isinstance(reader_options, dict):
        raise ValueError("File reader_options must be an object.")
    physical = {"workspace_id": workspace_id.strip().lower(), "item_id": item_id.strip().lower(), "relative_path": path}
    digest = hashlib.sha256(json.dumps(physical, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    options = json.loads(json.dumps(reader_options or {}, allow_nan=False, sort_keys=True))
    return {"source_type": "file", "source_id": "file:" + digest, **physical,
            "file_format": file_format, "reader_options": options}


def validate_contract_source(payload):
    """Validate physical Table IDs or a distinct stable file selector identity."""
    source = payload.get("source")
    if source is None:
        return  # Physical table contracts retain their canonical Table ID.
    if not isinstance(source, dict):
        raise ValueError("Data Contract source must be an object.")
    if source.get("source_type") == "table":
        if not source.get("table_id") or source["table_id"] != payload.get("table", {}).get("table_id"):
            raise ValueError("Table source must preserve the canonical Table ID.")
    elif source.get("source_type") == "file":
        expected = file_source_identity(**{key: source.get(key) for key in
            ("workspace_id", "item_id", "relative_path", "file_format", "reader_options")})
        if expected != source or payload.get("table", {}).get("table_id"):
            raise ValueError("File source must use its stable file identity, without a Table ID.")
    else:
        raise ValueError("Data Contract source_type must be table or file.")
