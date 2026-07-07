"""Public widget entrypoint for ``widget_render_agreement_evidence``."""

from __future__ import annotations

from datetime import datetime
import re
import sys
from typing import Any

from fabricops_kit.config.shared import get_current_audit_timestamp, resolve_fabric_context
from fabricops_kit.config.audit import build_runtime_audit_fields
from fabricops_kit.widgets.shared import (
    AGREEMENT_EVIDENCE_ALLOWED_EXTENSIONS,
    AGREEMENT_EVIDENCE_MIME_TYPES,
    AGREEMENT_EVIDENCE_TYPES,
    DATA_AGREEMENT_EVIDENCE_TABLE,
    config_value,
    list_all_data_agreement_rows,
    render_searchable_selector,
    require_ipywidgets,
    widget_common,
    write_widget_metadata_row,
)


def widget_render_agreement_evidence(*, spark: Any, context: dict[str, Any] | None = None) -> dict[str, Any]:
    """Render standalone agreement evidence upload controls.

    Parameters
    ----------
    spark : pyspark.sql.SparkSession
        Fabric Spark session used for metadata reads, file writes, and
        append-only evidence metadata writes.
    context : dict[str, Any], optional
        Advanced override for the active Fabric context. When omitted, the
        helper uses ``FABRIC_CONTEXT`` initialized by ``00_env_config``.

    Returns
    -------
    dict[str, Any]
        Rendered controls for selecting an agreement version, pasting
        metadata lakehouse evidence file paths, refreshing agreement options,
        and saving evidence metadata rows.

    """
    config, env, _context = resolve_fabric_context(context=context)
    return _render_agreement_evidence_widget_workflow(spark=spark, config=config, env=env)


def _get_notebookutils() -> Any:
    """Return a notebookutils-like object when the Fabric runtime exposes one."""
    candidate = globals().get("notebookutils")
    if candidate is not None:
        return candidate
    for module_name in ("notebookutils", "mssparkutils"):
        candidate = sys.modules.get(module_name)
        if candidate is not None:
            return candidate
    return None


def _prepare_evidence_file_references(paths_value: Any) -> list[dict[str, str]]:
    """Parse and validate manually supplied evidence file paths before writes."""
    utils = _get_notebookutils()
    fs = getattr(utils, "fs", None) if utils is not None else None
    exists = getattr(fs, "exists", None) if fs is not None else None
    list_dir = getattr(fs, "ls", None) if fs is not None else None

    references: list[dict[str, str]] = []
    for raw_line in str(paths_value or "").splitlines():
        path = re.sub(r"^(?:[-*]\s*|\d+\.\s*)", "", raw_line.strip()).strip()
        if not path:
            continue
        if not path.startswith("Files/"):
            raise ValueError(f"Evidence file path must start with Files/: {path}")

        file_name = path.replace("\\", "/").rsplit("/", 1)[-1].strip()
        if not file_name:
            raise ValueError(f"Evidence file path must include a file name: {path}")
        suffix = "." + file_name.rsplit(".", 1)[-1].lower() if "." in file_name else ""
        if suffix not in AGREEMENT_EVIDENCE_ALLOWED_EXTENSIONS:
            allowed = ", ".join(AGREEMENT_EVIDENCE_ALLOWED_EXTENSIONS)
            raise ValueError(f"Unsupported evidence file type for {path}. Allowed types: {allowed}.")
        if callable(exists) and not bool(exists(path)):
            raise ValueError(f"Evidence file path does not exist: {path}")

        file_size = ""
        if callable(list_dir):
            normalized = path.rstrip("/")
            parent = normalized.rsplit("/", 1)[0] if "/" in normalized else ""
            try:
                items = list_dir(parent)
            except Exception:
                items = []
            for item in items:
                item_path = str(getattr(item, "path", "") or getattr(item, "name", "") or "")
                item_name = item_path.rstrip("/").rsplit("/", 1)[-1]
                if item_path.rstrip("/") == normalized or item_name == file_name:
                    size = getattr(item, "size", "")
                    file_size = "" if size is None else str(size)
                    break

        references.append(
            {
                "file_name": file_name,
                "file_path": path,
                "mime_type": AGREEMENT_EVIDENCE_MIME_TYPES.get(suffix, ""),
                "file_size": file_size,
            }
        )

    if not references:
        raise ValueError("Paste at least one evidence file path before saving.")
    return references


def _save_agreement_evidence_records(
    *,
    spark: Any,
    config: Any,
    env: str,
    agreement_id: str,
    agreement_version: str,
    evidence_type: str,
    evidence_file_paths: Any,
    committed_by: str | None = None,
    committed_at: str | None = None,
    runtime_context: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Append manually uploaded evidence file-reference metadata rows."""
    agreement_id = str(agreement_id or "").strip()
    agreement_version = str(agreement_version or "").strip()
    if not agreement_id:
        raise ValueError("agreement_id is required before saving agreement evidence.")
    if not agreement_version:
        raise ValueError("agreement_version is required before saving agreement evidence.")
    evidence_type = str(evidence_type or "Other").strip() or "Other"
    file_references = _prepare_evidence_file_references(evidence_file_paths)
    audit = build_runtime_audit_fields(
        config=config, env=env, committed_by=committed_by, committed_at=committed_at, runtime_context=runtime_context
    )
    metadata_tables = config_value(config, "metadata_tables", {}) or {}
    rows: list[dict[str, Any]] = []
    for reference in file_references:
        row = {
            "agreement_id": agreement_id,
            "agreement_version": agreement_version,
            "evidence_type": evidence_type,
            "file_name": reference["file_name"],
            "file_path": reference["file_path"],
            "mime_type": reference["mime_type"],
            "file_size": reference["file_size"],
            **audit,
        }
        write_widget_metadata_row(
            spark=spark,
            config=config,
            env=env,
            table=str(metadata_tables.get("data_agreement_evidence", DATA_AGREEMENT_EVIDENCE_TABLE)),
            row=row,
        )
        rows.append(row)
    return rows


def _render_agreement_evidence_widget_workflow(
    *, spark: Any, config: Any, env: str, display_widget: bool = True
) -> dict[str, Any]:
    """Render optional agreement evidence upload controls."""
    widgets = require_ipywidgets()
    from IPython import display as ip

    row_lookup: dict[str, dict[str, Any]] = {}

    def _agreement_rows() -> list[dict[str, Any]]:
        return list_all_data_agreement_rows(config, env, spark_session=spark, missing_ok=True)

    def _version_key(row: dict[str, Any]) -> str:
        agreement_id = str(row.get("agreement_id") or "").strip()
        agreement_version = str(row.get("agreement_version") or "").strip()
        return f"{agreement_id}||{agreement_version}" if agreement_id and agreement_version else ""

    def _version_label(row: dict[str, Any]) -> str:
        key = _version_key(row)
        return (
            f"{row.get('agreement_name', '') or row.get('agreement_id', '')} ({row.get('agreement_id', '')} / v{row.get('agreement_version', '')})"
            if key
            else ""
        )

    def _selector_rows() -> list[dict[str, Any]]:
        row_lookup.clear()
        rows = [row for row in _agreement_rows() if _version_key(row)]
        row_lookup.update({_version_key(row): row for row in rows})
        return rows

    message = widgets.HTML(value="")
    version_selector = render_searchable_selector(
        widgets=widgets,
        label="Agreement Version",
        rows=_selector_rows(),
        label_fn=_version_label,
        value_fn=_version_key,
        placeholder="Search agreement versions...",
        search_fields=["agreement_name", "agreement_id", "agreement_version", "domain", "recipient"],
        context_fields=[
            ("agreement_name", "Agreement name"),
            ("agreement_id", "Agreement ID"),
            ("agreement_version", "Contract version"),
            ("recipient", "Recipient"),
        ],
        empty_label="Select an agreement version...",
    )
    selected = version_selector["selector"]
    evidence_type = widgets.Dropdown(
        options=[(item, item) for item in AGREEMENT_EVIDENCE_TYPES], **widget_common(widgets, "Evidence Type")
    )
    evidence_file_paths = widgets.Textarea(
        placeholder=(
            "Files/fabricops/agreement_evidence/<agreement_id>/<agreement_version>/signed_agreement.pdf\n"
            "Files/fabricops/agreement_evidence/<agreement_id>/<agreement_version>/email_approval.pdf"
        ),
        **widget_common(widgets, "Evidence File Paths"),
    )
    instructions = widgets.HTML(
        value=(
            "Upload evidence files manually to the metadata lakehouse Files area, "
            "then paste one Files/... path per line."
        )
    )
    refresh = widgets.Button(description="Refresh agreements")
    save = widgets.Button(description="Save evidence")
    output = widgets.Output()

    def _set_empty_state() -> None:
        has_agreement = any(value for _, value in selected.options)
        message.value = (
            ""
            if has_agreement
            else "<b>No data agreements found.</b> Save a Data Agreement first, then return here to upload optional evidence."
        )
        evidence_file_paths.disabled = not has_agreement
        save.disabled = not has_agreement

    def _refresh(_: Any = None) -> None:
        current = str(selected.value or "")
        rows = _selector_rows()
        selected.refresh_rows(rows, current if current in row_lookup else "")
        _set_empty_state()

    def _clear_output() -> None:
        clear = getattr(output, "clear_output", None)
        if clear is not None:
            clear(wait=True)

    def _save(_: Any) -> None:
        save.disabled = True
        _clear_output()
        with output:
            try:
                selected_row = row_lookup.get(selected.value or "")
                if not selected_row:
                    raise ValueError("Select an agreement version before saving evidence.")
                rows = _save_agreement_evidence_records(
                    spark=spark,
                    config=config,
                    env=env,
                    agreement_id=str(selected_row.get("agreement_id") or ""),
                    agreement_version=str(selected_row.get("agreement_version") or ""),
                    evidence_type=str(evidence_type.value or "Other"),
                    evidence_file_paths=evidence_file_paths.value,
                )
                print(f"Saved {len(rows)} agreement evidence file reference row(s).")
            except Exception as exc:
                print(f"Error: {exc}")
            finally:
                _set_empty_state()
                if any(value for _, value in selected.options):
                    save.disabled = False

    refresh.on_click(_refresh)
    save.on_click(_save)
    _set_empty_state()
    container = widgets.VBox(
        [
            message,
            version_selector["container"],
            evidence_type,
            instructions,
            evidence_file_paths,
            refresh,
            save,
            output,
        ]
    )
    if display_widget:
        ip.display(container)
    return {
        "container": container,
        "message": message,
        "agreement_version": selected,
        "agreement_version_search": version_selector["search"],
        "agreement_version_context": version_selector["context"],
        "agreement_versions_by_key": row_lookup,
        "evidence_type": evidence_type,
        "evidence_file_paths": evidence_file_paths,
        "instructions": instructions,
        "refresh_agreements_button": refresh,
        "refresh_agreements": _refresh,
        "save_button": save,
        "output": output,
    }
