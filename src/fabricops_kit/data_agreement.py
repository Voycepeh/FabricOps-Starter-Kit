"""Versioned data-agreement intake helpers for Fabric notebook workflows.

The ``01_da`` notebook owns agreement intake and usage boundaries. Later
notebooks select the latest committed agreement version and bind their evidence
to both ``agreement_id`` and ``contract_version``.
"""

from __future__ import annotations

from datetime import date, datetime, timezone
from html import escape
from typing import Any

from .fabric_input_output import read_lakehouse_table, write_lakehouse_table
from .metadata import _runtime_context

DATA_AGREEMENT_TABLE = "METADATA_DATA_AGREEMENT"
DATA_STEWARD_TABLE = "METADATA_DATA_STEWARD"
_SELECTED_AGREEMENT: dict[str, Any] | None = None

YES_NO_OPTIONS = ["Yes", "No"]
DATA_AGREEMENT_FIELDS = [
    "agreement_id", "contract_version", "agreement_name", "steward_id",
    "business_purpose", "approved_usage", "restricted_usage", "allowed_consumer_type",
    "expected_output", "source_system", "refresh_frequency", "retention_expectation",
    "start_date", "expiry_date", "renewal_required", "_committed_by", "_committed_at",
    "_workspace_name", "_notebook_name", "_metadata_lakehouse_name", "_activity_id",
]
DATA_STEWARD_FIELDS = [
    "steward_id", "data_steward_name", "data_steward_email", "domain", "department",
    "faculty", "effective_from", "effective_to", "is_active", "created_at", "updated_at",
]
_REQUIRED_FIELDS = [
    "agreement_id", "contract_version", "agreement_name", "steward_id", "business_purpose",
    "approved_usage", "allowed_consumer_type", "expected_output", "source_system",
    "refresh_frequency", "retention_expectation", "expiry_date", "renewal_required",
    "_committed_by", "_committed_at",
]


def _coerce_row_dicts(rows: Any) -> list[dict[str, Any]]:
    if rows is None:
        return []
    if hasattr(rows, "collect"):
        rows = rows.collect()
    return [row.asDict(recursive=True) if hasattr(row, "asDict") else dict(row) for row in rows]


def _context_get(context: Any, *keys: str) -> Any:
    for key in keys:
        try:
            value = context.get(key) if isinstance(context, dict) else context.get(key)
        except Exception:
            value = None
        if value is not None and str(value).strip():
            return value
    return None


def metadata_lakehouse_root(config: Any, env: str) -> str:
    """Return the configured metadata lakehouse OneLake root.

    Parameters
    ----------
    config : FrameworkConfig | dict
        Framework config containing ``path_config.paths[env]["metadata"]``.
    env : str
        Environment key configured by ``00_env_config``.

    Returns
    -------
    str
        ABFSS OneLake root for the metadata lakehouse.

    Raises
    ------
    ValueError
        If the metadata target is absent or is not a lakehouse.
    """
    paths = config.path_config.paths if hasattr(config, "path_config") else config.paths
    try:
        store = paths[env]["metadata"]
    except (KeyError, TypeError) as exc:
        raise ValueError(f"Metadata target not found for environment '{env}'.") from exc
    if store.kind != "lakehouse":
        raise ValueError(f"Target '{env}/metadata' is not a lakehouse store.")
    return store.root.rstrip("/")


def _table_path(config: Any, env: str, table_name: str) -> str:
    return f"{metadata_lakehouse_root(config, env)}/Tables/{table_name}"


def _ensure_delta_table(spark: Any, config: Any, env: str, table_name: str, fields: list[str]) -> None:
    path = _table_path(config, env, table_name)
    try:
        spark.read.format("delta").load(path).limit(0).collect()
    except Exception:
        spark.createDataFrame([{field: "" for field in fields}]).limit(0).write.format("delta").mode("overwrite").save(path)


def setup_data_agreement_tables(*, spark: Any, config: Any, env: str) -> list[str]:
    """Create empty agreement and steward Delta tables when they do not exist.

    Parameters
    ----------
    spark : pyspark.sql.SparkSession
        Active Fabric Spark session.
    config : FrameworkConfig | dict
        Framework config with the metadata lakehouse target.
    env : str
        Environment key configured by ``00_env_config``.

    Returns
    -------
    list[str]
        Metadata table names checked or created.

    Notes
    -----
    The steward table is intentionally created empty. Populate it with real,
    public-safe organization data before using the intake form; this helper
    never seeds fake people.
    """
    _ensure_delta_table(spark, config, env, DATA_AGREEMENT_TABLE, DATA_AGREEMENT_FIELDS)
    _ensure_delta_table(spark, config, env, DATA_STEWARD_TABLE, DATA_STEWARD_FIELDS)
    return [DATA_AGREEMENT_TABLE, DATA_STEWARD_TABLE]


def parse_contract_version(version: Any) -> tuple[int, int, int]:
    """Parse a semantic contract version into a comparable tuple."""
    try:
        parts = str(version or "").strip().split(".")
        return tuple(int(parts[index]) if index < len(parts) else 0 for index in range(3))  # type: ignore[return-value]
    except (TypeError, ValueError):
        return (0, 0, 0)


def next_minor_version(version: Any) -> str:
    """Return the next minor contract version, defaulting invalid input to ``1.0.0``."""
    major, minor, _ = parse_contract_version(version)
    return "1.0.0" if major == 0 else f"{major}.{minor + 1}.0"


def latest_agreement_versions(rows: Any) -> list[dict[str, Any]]:
    """Return only the latest contract version for each stable agreement ID.

    Parameters
    ----------
    rows : iterable | pyspark.sql.DataFrame
        Agreement rows or a Spark DataFrame containing agreement rows.

    Returns
    -------
    list[dict[str, Any]]
        Latest row per ``agreement_id``, sorted for deterministic dropdowns.
    """
    latest: dict[str, dict[str, Any]] = {}
    for row in _coerce_row_dicts(rows):
        agreement_id = str(row.get("agreement_id") or "").strip()
        if agreement_id and (
            agreement_id not in latest
            or parse_contract_version(row.get("contract_version"))
            > parse_contract_version(latest[agreement_id].get("contract_version"))
        ):
            latest[agreement_id] = row
    return sorted(latest.values(), key=lambda row: (
        str(row.get("agreement_name") or "").lower(),
        str(row.get("source_system") or "").lower(),
        str(row.get("allowed_consumer_type") or "").lower(),
    ))


def load_agreements(config: Any, env: str, *, spark_session: Any = None, missing_ok: bool = False) -> list[dict[str, Any]]:
    """Load latest versioned agreements from the configured metadata lakehouse.

    Parameters
    ----------
    config : FrameworkConfig | dict
        Framework config with the metadata lakehouse route.
    env : str
        Environment key configured by ``00_env_config``.
    spark_session : pyspark.sql.SparkSession, optional
        Explicit Spark session. Fabric notebooks may omit it.
    missing_ok : bool, default=False
        Return an empty list instead of raising when the table is absent.

    Returns
    -------
    list[dict[str, Any]]
        Latest row for each ``agreement_id``.
    """
    try:
        rows = read_lakehouse_table(config, env, "metadata", DATA_AGREEMENT_TABLE, spark_session=spark_session)
    except Exception as exc:
        if missing_ok:
            return []
        raise RuntimeError("No agreements found. Run 01_da first.") from exc
    return latest_agreement_versions(rows)


def agreement_dropdown_options(rows: Any, *, include_prompt: bool = False) -> list[tuple[str, Any]]:
    """Build selector options that preserve stable and version keys.

    Parameters
    ----------
    rows : iterable | pyspark.sql.DataFrame
        Agreement rows. Only the latest version per ``agreement_id`` is shown.
    include_prompt : bool, default=False
        Add an initial empty selection prompt for update-mode forms.

    Returns
    -------
    list[tuple[str, Any]]
        Display-label and agreement-row pairs suitable for ``ipywidgets``.
    """
    options: list[tuple[str, Any]] = []
    if include_prompt:
        options.append(("Select an agreement to update...", None))
    for row in latest_agreement_versions(rows):
        label = (
            f"{row.get('agreement_name', '')} (Latest v{row.get('contract_version', '')}) - "
            f"{row.get('source_system', '')} / {row.get('allowed_consumer_type', '')} - "
            f"Steward ID: {row.get('steward_id', '')}"
        )
        options.append((label, row))
    return options


def select_agreement(agreement_rows_or_df: Any) -> Any:
    """Render an ``ipywidgets`` selector and retain the selected agreement version.

    Parameters
    ----------
    agreement_rows_or_df : iterable | pyspark.sql.DataFrame
        Agreement rows, normally returned by :func:`load_agreements`.

    Returns
    -------
    ipywidgets.Dropdown
        Rendered selector. The selected row is also retained for
        :func:`get_selected_agreement`.
    """
    import ipywidgets as widgets
    import IPython.display as ip_display

    global _SELECTED_AGREEMENT
    options = agreement_dropdown_options(agreement_rows_or_df)
    if not options:
        raise ValueError("No agreements found. Save a data agreement in notebook 01_da first.")
    dropdown = widgets.Dropdown(options=options, description="Agreement", layout=widgets.Layout(width="1000px"))

    def _on_change(change: dict[str, Any]) -> None:
        global _SELECTED_AGREEMENT
        if change.get("name") == "value" and change.get("new") is not None:
            _SELECTED_AGREEMENT = dict(change["new"])

    dropdown.observe(_on_change, names="value")
    _SELECTED_AGREEMENT = dict(options[0][1])
    ip_display.display(dropdown)
    return dropdown


def get_selected_agreement() -> dict[str, Any]:
    """Return the selected agreement row, including its stable and version keys.

    Returns
    -------
    dict[str, Any]
        Selected latest-version agreement row.

    Raises
    ------
    RuntimeError
        If :func:`select_agreement` has not established a selection.
    """
    if not _SELECTED_AGREEMENT:
        raise RuntimeError("No agreement selected. Run select_agreement(...) and pick an agreement first.")
    return dict(_SELECTED_AGREEMENT)


def load_active_data_steward_profiles(*, spark: Any, config: Any, env: str) -> list[dict[str, Any]]:
    """Load active steward profiles from the configured metadata lakehouse.

    Parameters
    ----------
    spark : pyspark.sql.SparkSession
        Active Fabric Spark session.
    config : FrameworkConfig | dict
        Framework config with a metadata lakehouse target.
    env : str
        Environment key configured by ``00_env_config``.

    Returns
    -------
    list[dict[str, Any]]
        Active steward rows prepared for dropdown rendering.

    Raises
    ------
    ValueError
        If the steward table contains no active rows or an effective-date value
        is invalid.

    Notes
    -----
    A steward is selectable only when ``is_active`` is true, ``effective_from``
    is blank or not in the future, and ``effective_to`` is blank or not in the
    past.
    """
    _ensure_delta_table(spark, config, env, DATA_STEWARD_TABLE, DATA_STEWARD_FIELDS)
    rows = _coerce_row_dicts(read_lakehouse_table(config, env, "metadata", DATA_STEWARD_TABLE, spark_session=spark))
    profiles = []
    today = datetime.now(timezone.utc).date()
    for row in rows:
        if str(row.get("is_active") or "").strip().lower() != "true":
            continue
        effective_from = str(row.get("effective_from") or "").strip()
        effective_to = str(row.get("effective_to") or "").strip()
        try:
            if effective_from and date.fromisoformat(effective_from[:10]) > today:
                continue
            if effective_to and date.fromisoformat(effective_to[:10]) < today:
                continue
        except ValueError as exc:
            raise ValueError(
                f"{DATA_STEWARD_TABLE} row '{row.get('steward_id', '')}' has an invalid effective date. "
                "Use ISO dates for effective_from and effective_to."
            ) from exc
        profile = {field: row.get(field, "") for field in DATA_STEWARD_FIELDS if field not in {"is_active", "created_at", "updated_at"}}
        profile["label"] = " | ".join(str(profile.get(field) or "") for field in ("data_steward_name", "domain", "department", "faculty"))
        profiles.append(profile)
    if not profiles:
        raise ValueError(
            f"{DATA_STEWARD_TABLE} has no active steward rows. Populate real steward profiles in the metadata lakehouse before creating a data agreement."
        )
    return profiles


def _parse_required_date(value: Any, field_name: str) -> date:
    text = str(value or "").strip()
    if not text:
        raise ValueError(f"{field_name} is required.")
    try:
        return date.fromisoformat(text[:10])
    except ValueError as exc:
        raise ValueError(f"{field_name} must be a valid date.") from exc


def _generate_agreement_id() -> str:
    return "DA-" + datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S-%f")


def _to_iso_date(value: Any) -> str:
    if value is None:
        return ""
    return value.date().isoformat() if isinstance(value, datetime) else value.isoformat() if isinstance(value, date) else str(value)


def resolve_agreement_identity(rows: Any, *, agreement_name: str, source_system: str, allowed_consumer_type: str, mode: str = "create", selected_agreement: dict[str, Any] | None = None) -> dict[str, Any]:
    """Resolve a create-mode or update-mode append-only agreement identity.

    Parameters
    ----------
    rows : iterable | pyspark.sql.DataFrame
        Existing agreement rows. Retained for caller compatibility and future
        validation, but create mode intentionally does not reuse matching rows.
    agreement_name, source_system, allowed_consumer_type : str
        Human-entered identity fields retained on each agreement version.
    mode : {"create", "update"}, default="create"
        Intake operation. Create mode always generates a new stable ID and
        ``1.0.0`` version. Update mode requires ``selected_agreement``.
    selected_agreement : dict[str, Any], optional
        Latest agreement row selected by update mode.

    Returns
    -------
    dict[str, Any]
        Stable ID, next version, and whether the agreement is new.

    Raises
    ------
    ValueError
        If ``mode`` is invalid or update mode has no selected agreement.
    """
    del rows, agreement_name, source_system, allowed_consumer_type
    normalized_mode = str(mode or "").strip().lower()
    if normalized_mode == "create":
        return {"agreement_id": _generate_agreement_id(), "contract_version": "1.0.0", "is_new_agreement": True}
    if normalized_mode != "update":
        raise ValueError("mode must be either 'create' or 'update'.")
    if not selected_agreement:
        raise ValueError("Update mode requires selected_agreement.")
    return {"agreement_id": selected_agreement["agreement_id"], "contract_version": next_minor_version(selected_agreement.get("contract_version")), "is_new_agreement": False}


def collect_agreement_metadata(*, widget_values: dict[str, Any], mode: str = "create", existing_rows: Any = None, selected_agreement: dict[str, Any] | None = None, committed_by: str | None = None, committed_at: str | None = None, runtime_context: dict[str, Any] | None = None, config: Any = None, env: str | None = None) -> dict[str, Any]:
    """Build one validated append-only agreement-version row from intake values.

    Parameters
    ----------
    widget_values : dict[str, Any]
        Human-entered values returned by :func:`read_agreement_form`.
    mode : {"create", "update"}, default="create"
        Intake operation. Create mode always creates a fresh agreement ID.
    existing_rows : iterable | pyspark.sql.DataFrame, optional
        Existing agreement versions available to the intake workflow.
    selected_agreement : dict[str, Any], optional
        Explicit latest row selected in update mode.
    committed_by, committed_at : str, optional
        Audit overrides, primarily for deterministic tests.
    runtime_context : dict[str, Any], optional
        Runtime context overrides merged over Fabric notebook context.
    config : FrameworkConfig | dict, optional
        Framework config used to record the configured metadata lakehouse name.
    env : str, optional
        Environment key paired with ``config``.

    Returns
    -------
    dict[str, Any]
        Validated ``agreement_row``, identity flag, and commit summary.
    """
    steward = dict(widget_values.get("data_steward_profile") or {})
    values = {key: (_to_iso_date(value) if key in {"start_date", "expiry_date"} else str(value or "").strip()) for key, value in widget_values.items() if key != "data_steward_profile"}
    agreement_rows = [] if existing_rows is None else existing_rows
    identity = resolve_agreement_identity(agreement_rows, agreement_name=values.get("agreement_name", ""), source_system=values.get("source_system", ""), allowed_consumer_type=values.get("allowed_consumer_type", ""), mode=mode, selected_agreement=selected_agreement)
    context = {**_runtime_context(), **(runtime_context or {})}
    configured_lakehouse_name = ""
    if config is not None and env is not None:
        paths = config.path_config.paths if hasattr(config, "path_config") else config.paths
        configured_lakehouse_name = str(paths[env]["metadata"].name)
    row = {
        **values, **identity,
        "steward_id": str(steward.get("steward_id") or "").strip(),
        "_committed_by": str(committed_by).strip() if committed_by and str(committed_by).strip() else str(_context_get(context, "userName", "userId") or "unknown"),
        "_committed_at": committed_at or datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "_workspace_name": str(_context_get(context, "currentWorkspaceName", "workspaceName") or ""),
        "_notebook_name": str(_context_get(context, "currentNotebookName", "notebookName") or "01_da_agreement_template"),
        "_metadata_lakehouse_name": configured_lakehouse_name or str(_context_get(context, "lakehouseName") or ""),
        "_activity_id": str(_context_get(context, "activityId") or ""),
    }
    missing = [field for field in _REQUIRED_FIELDS if row.get(field) is None or (isinstance(row.get(field), str) and not row[field].strip())]
    if missing:
        raise ValueError("Missing required agreement field(s): " + ", ".join(missing))
    _parse_required_date(row["expiry_date"], "expiry_date")
    if row["renewal_required"] not in YES_NO_OPTIONS:
        raise ValueError("renewal_required must be Yes or No.")
    agreement_row = {field: row.get(field, "") for field in DATA_AGREEMENT_FIELDS}
    return {"agreement_row": agreement_row, "is_new_agreement": identity["is_new_agreement"], "summary": {**{key: agreement_row[key] for key in ("agreement_id", "contract_version", "expiry_date", "_committed_by", "_committed_at")}, "table_updated": DATA_AGREEMENT_TABLE}}


def commit_agreement_metadata(*, spark: Any, config: Any, env: str, agreement_metadata: dict[str, Any], mode: str = "append") -> dict[str, Any]:
    """Append one agreement-version row by configured OneLake path.

    Parameters
    ----------
    spark : pyspark.sql.SparkSession
        Active Fabric Spark session.
    config : FrameworkConfig | dict
        Framework config with the metadata lakehouse target.
    env : str
        Environment key configured by ``00_env_config``.
    agreement_metadata : dict[str, Any]
        Validated result from :func:`collect_agreement_metadata`.
    mode : str, default="append"
        Write mode. Agreement versions intentionally support append only.

    Returns
    -------
    dict[str, Any]
        Commit summary for the appended ``METADATA_DATA_AGREEMENT`` row.
    """
    if mode != "append":
        raise ValueError("Agreement versions are append-only; mode must be 'append'.")
    _ensure_delta_table(spark, config, env, DATA_AGREEMENT_TABLE, DATA_AGREEMENT_FIELDS)
    row = {field: agreement_metadata["agreement_row"].get(field, "") for field in DATA_AGREEMENT_FIELDS}
    write_lakehouse_table(spark.createDataFrame([row]), config, env, "metadata", DATA_AGREEMENT_TABLE, mode="append")
    return dict(agreement_metadata["summary"])


def create_agreement_form(*, spark: Any, config: Any, env: str, default_values: dict[str, Any] | None = None) -> dict[str, Any]:
    """Render the standalone ``01_da`` intake form with ``ipywidgets``.

    Parameters
    ----------
    spark : pyspark.sql.SparkSession
        Active Fabric Spark session.
    config : FrameworkConfig
        Framework config containing ``DataAgreementConfig`` widget defaults.
    env : str
        Environment key configured by ``00_env_config``.
    default_values : dict[str, Any], optional
        Per-form overrides merged over the ``01_da`` config defaults.

    Returns
    -------
    dict[str, Any]
        Named widgets, including mode, latest-version selector, and commit button.
    """
    import ipywidgets as widgets
    import IPython.display as ip_display

    intake = getattr(config, "data_agreement_config", None)
    defaults = {**dict(getattr(intake, "default_values", {}) or {}), **(default_values or {})}
    get_options = lambda name: list(getattr(intake, name, ()) or ())
    profiles = load_active_data_steward_profiles(spark=spark, config=config, env=env)
    latest = load_agreements(config, env, spark_session=spark, missing_ok=True)
    steward_options = [(profile["label"], profile) for profile in profiles]
    form: dict[str, Any] = {
        "mode": widgets.Dropdown(options=["Create New Agreement", "Update Existing Agreement"], description="Mode"),
        "existing_agreement": widgets.Dropdown(options=agreement_dropdown_options(latest, include_prompt=True), description="Existing"),
        "agreement_identity": widgets.HTML(),
        "agreement_name": widgets.Text(value=str(defaults.get("agreement_name", "")), description="Agreement Name"),
        "data_steward_profile": widgets.Dropdown(options=steward_options, description="Data Steward"),
    }
    for name in ("business_purpose", "approved_usage", "restricted_usage", "retention_expectation"):
        form[name] = widgets.Textarea(value=str(defaults.get(name, "")), description=name.replace("_", " ").title())
    option_fields = {"allowed_consumer_type": "allowed_consumer_types", "expected_output": "expected_outputs", "source_system": "source_systems", "refresh_frequency": "refresh_frequencies", "renewal_required": "renewal_options"}
    for name, option_name in option_fields.items():
        options = get_options(option_name)
        form[name] = widgets.Dropdown(options=options, value=defaults.get(name) if defaults.get(name) in options else options[0], description=name.replace("_", " ").title())
    form["start_date"] = widgets.DatePicker(value=defaults.get("start_date"), description="Start Date")
    form["expiry_date"] = widgets.DatePicker(value=defaults.get("expiry_date"), description="Expiry Date")
    form["commit_button"] = widgets.Button(description="Commit Agreement", button_style="success", icon="check")
    form["output"] = widgets.Output()

    def refresh(*_: Any) -> None:
        selected = form["existing_agreement"].value
        is_update = form["mode"].value == "Update Existing Agreement"
        form["existing_agreement"].layout.display = "" if is_update else "none"
        if not is_update:
            form["agreement_identity"].value = "<b>Agreement Identity</b><br>New agreement: ID generated on commit; version 1.0.0"
        elif not selected:
            form["agreement_identity"].value = "<b>Agreement Identity</b><br>Select an existing agreement to continue."
        else:
            form["agreement_identity"].value = (
                f"<b>Agreement Identity</b><br>"
                f"ID: {escape(str(selected.get('agreement_id', '')))}<br>"
                f"Latest version: {escape(str(selected.get('contract_version', '')))}<br>"
                f"Next version: {escape(next_minor_version(selected.get('contract_version')))}<br>"
                f"Latest expiry date: {escape(str(selected.get('expiry_date', '')))}"
            )
    def prefill(*_: Any) -> None:
        refresh()
        selected = form["existing_agreement"].value
        if form["mode"].value != "Update Existing Agreement" or not selected:
            return
        for name in ("agreement_name", "business_purpose", "approved_usage", "restricted_usage", "retention_expectation"):
            form[name].value = selected.get(name) or ""
        for name in ("allowed_consumer_type", "expected_output", "source_system", "refresh_frequency", "renewal_required"):
            if selected.get(name) in list(form[name].options):
                form[name].value = selected[name]
        matching = [profile for _, profile in steward_options if str(profile.get("steward_id") or "") == str(selected.get("steward_id") or "")]
        if matching:
            form["data_steward_profile"].value = matching[0]
        for name in ("start_date", "expiry_date"):
            if selected.get(name):
                form[name].value = date.fromisoformat(str(selected[name])[:10])
    form["mode"].observe(prefill, names="value")
    form["existing_agreement"].observe(prefill, names="value")
    refresh()
    ip_display.display(widgets.HTML("<h3>Data Agreement Intake / Usage Boundary</h3>"), widgets.VBox(list(form.values())))
    return form


def render_agreement_intake_app(
    *,
    spark: Any,
    config: Any,
    env: str,
    default_values: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Render and wire the standalone ``01_da`` agreement-intake application.

    Parameters
    ----------
    spark : pyspark.sql.SparkSession
        Active Fabric Spark session.
    config : FrameworkConfig
        Framework config containing metadata routing and ``DataAgreementConfig``
        widget defaults.
    env : str
        Environment key configured by ``00_env_config``.
    default_values : dict[str, Any], optional
        Per-form overrides merged over the configured ``01_da`` defaults.

    Returns
    -------
    dict[str, Any]
        Named widgets returned by :func:`create_agreement_form`. Advanced users
        may inspect or customize these widgets after the default callback is
        registered.

    Notes
    -----
    This is the default notebook-friendly entrypoint for agreement intake. It
    keeps create/update branching, widget reads, metadata collection, and
    commit-summary rendering inside the framework while preserving lower-level
    helpers for customized workflows.
    """
    from IPython.display import clear_output

    form = create_agreement_form(spark=spark, config=config, env=env, default_values=default_values)

    def on_commit_clicked(_: Any) -> None:
        with form["output"]:
            clear_output()
            try:
                latest = load_agreements(config, env, spark_session=spark, missing_ok=True)
                intake_mode = "update" if form["mode"].value == "Update Existing Agreement" else "create"
                selected = form["existing_agreement"].value if intake_mode == "update" else None
                if intake_mode == "update" and not selected:
                    raise ValueError("Update mode selected, but no existing agreement was chosen.")
                metadata = collect_agreement_metadata(
                    widget_values=read_agreement_form(form),
                    mode=intake_mode,
                    existing_rows=latest,
                    selected_agreement=selected,
                    config=config,
                    env=env,
                )
                summary = commit_agreement_metadata(
                    spark=spark,
                    config=config,
                    env=env,
                    agreement_metadata=metadata,
                )
                print("Data agreement committed successfully.")
                print(f"- Agreement ID: {summary['agreement_id']}")
                print(f"- Contract Version: {summary['contract_version']}")
                print(f"- Expiry Date: {summary['expiry_date']}")
                print(f"- Committed By: {summary['_committed_by']}")
                print(f"- Committed At: {summary['_committed_at']}")
                print(f"- Table Updated: {summary['table_updated']}")
            except Exception as exc:
                print(f"Commit failed: {exc}")

    form["commit_button"].on_click(on_commit_clicked)
    return form


def read_agreement_form(form: dict[str, Any]) -> dict[str, Any]:
    """Return human-entered values from an ``01_da`` intake form.

    Parameters
    ----------
    form : dict[str, Any]
        Form returned by :func:`create_agreement_form`.

    Returns
    -------
    dict[str, Any]
        Human-entered agreement values ready for collection and validation.
    """
    names = ["agreement_name", "data_steward_profile", "business_purpose", "approved_usage", "restricted_usage", "allowed_consumer_type", "expected_output", "source_system", "refresh_frequency", "retention_expectation", "start_date", "expiry_date", "renewal_required"]
    return {name: form[name].value for name in names}
