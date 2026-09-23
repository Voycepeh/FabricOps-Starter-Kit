"""Shared foundations for Fabric access scanners."""

from __future__ import annotations

import json
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from fabricops_kit.config.metadata_schemas import metadata_table_physical_schema
from fabricops_kit.config.shared import build_table_id, get_store
from fabricops_kit.io.write_lakehouse_table import write_lakehouse_table


ACCESS_TABLE = "METADATA_DATA_ACCESS"
FABRIC_API_ROOT = "https://api.fabric.microsoft.com/v1"


def normalise_targets(targets: str | list[str] | tuple[str, ...]) -> list[str]:
    """Return unique, validated configured target keys in input order."""
    values = [targets] if isinstance(targets, str) else list(targets)
    normalised = []
    for value in values:
        store = str(value or "").strip()
        if not store:
            raise ValueError("Access scan targets must be non-empty strings.")
        if store not in normalised:
            normalised.append(store)
    if not normalised:
        raise ValueError("At least one configured physical data item target is required for access scanning.")
    return normalised


def target_store_kinds(config, environment_name: str, targets: list[str]) -> dict[str, str]:
    """Resolve configured physical data item targets to normalized store kinds."""
    return {store: str(get_store(config, environment_name, store).kind).strip().lower() for store in targets}


def fabric_access_token(access_token: str | None = None) -> str:
    """Return an explicit token or acquire the current Fabric notebook token."""
    if access_token:
        return str(access_token).strip()
    try:
        import notebookutils  # type: ignore

        token = notebookutils.credentials.getToken("pbi")
    except Exception as exc:
        raise RuntimeError(
            "Access scanning requires a Fabric REST token. Run inside a Fabric notebook "
            "or pass access_token explicitly."
        ) from exc
    if not token:
        raise RuntimeError("NotebookUtils did not return a Fabric REST token.")
    return str(token)


def request_fabric_json(url: str, *, access_token: str) -> dict[str, Any]:
    """GET one Fabric REST resource and return its JSON object."""
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.netloc.lower() != "api.fabric.microsoft.com":
        raise RuntimeError("Refusing to send a Fabric bearer token to an unexpected host.")
    request = Request(
        url,
        headers={"Authorization": f"Bearer {access_token}", "Accept": "application/json"},
        method="GET",
    )
    try:
        with urlopen(request, timeout=60) as response:
            payload = response.read().decode("utf-8")
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Fabric REST request failed with HTTP {exc.code}: {detail or exc.reason}") from exc
    except URLError as exc:
        raise RuntimeError(f"Fabric REST request failed: {exc.reason}") from exc
    data = json.loads(payload or "{}")
    if not isinstance(data, dict):
        raise RuntimeError("Fabric REST response was not a JSON object.")
    return data


def list_fabric_pages(url: str, *, access_token: str) -> list[dict[str, Any]]:
    """Return every object from a paginated Fabric REST value response."""
    rows: list[dict[str, Any]] = []
    seen_urls: set[str] = set()
    while url:
        if url in seen_urls:
            raise RuntimeError("Fabric REST pagination returned a repeated continuation URI.")
        seen_urls.add(url)
        payload = request_fabric_json(url, access_token=access_token)
        values = payload.get("value") or []
        if not isinstance(values, list):
            raise RuntimeError("Fabric REST response contains a non-list value.")
        rows.extend(value for value in values if isinstance(value, dict))
        next_url = payload.get("continuationUri")
        url = str(next_url).strip() if next_url else ""
    return rows


def persist_access_rows(
    access_df,
    *,
    config,
    environment_name: str,
    context: dict[str, Any],
    persist: bool,
) -> None:
    """Append one scanner's normalized observations to METADATA_DATA_ACCESS."""
    if not persist:
        return
    write_lakehouse_table(
        access_df,
        ACCESS_TABLE,
        store="Metadata",
        schema=metadata_table_physical_schema(config, ACCESS_TABLE),
        context={**context, "config": config, "env": environment_name},
        mode="append",
    )


def catalogue_tables(catalogue_df, *, environment_name: str, target_store_kinds: dict[str, str]):
    """Select active Catalogue tables belonging to configured scan targets."""
    from pyspark.sql import functions as F
    from pyspark.sql import types as T

    spark = catalogue_df.sparkSession
    targets = spark.createDataFrame(
        list(target_store_kinds.items()),
        T.StructType(
            [
                T.StructField("_catalogue_target", T.StringType(), False),
                T.StructField("_target_store_type", T.StringType(), False),
            ]
        ),
    )
    canonical_table_id = F.udf(
        lambda store_type, target, schema_name, table_name: build_table_id(
            store_type,
            target,
            None if schema_name is None or not str(schema_name).strip() else schema_name,
            table_name,
        ),
        T.StringType(),
    )

    return (
        catalogue_df.filter(
            (F.lower(F.col("metadata_level")) == F.lit("table"))
            & (F.col("environment_name") == F.lit(environment_name))
            & F.col("is_active")
        )
        .crossJoin(targets)
        .filter(
            (F.lower(F.col("store_type")) == F.col("_target_store_type"))
            & (
                F.col("table_id")
                == canonical_table_id(
                    F.col("store_type"),
                    F.col("_catalogue_target"),
                    F.col("schema_name"),
                    F.col("table_name"),
                )
            )
        )
        .select(
            F.col("table_id").alias("_catalogue_table_id"),
            F.col("_catalogue_target"),
            F.col("schema_name").alias("_catalogue_schema_name"),
            F.col("table_name").alias("_catalogue_table_name"),
        )
        .dropDuplicates(["_catalogue_table_id"])
    )
