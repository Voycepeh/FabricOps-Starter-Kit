"""Shared foundations for Fabric access scanners."""

from __future__ import annotations

import json
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import HTTPRedirectHandler, Request, urlopen

from fabricops_kit.config.metadata_schemas import _require_catalogue_assets, metadata_table_physical_schema
from fabricops_kit.config.shared import build_table_id, get_store
from fabricops_kit.io.write_lakehouse_table import write_lakehouse_table


ACCESS_TABLE = "METADATA_DATA_ACCESS"
FABRIC_API_ROOT = "https://api.fabric.microsoft.com/v1"


def normalise_principal_type(principal_type: Any) -> str:
    """Normalize known source principal types without treating other identities as users."""
    source_type = str(principal_type or "UNKNOWN").strip().upper().replace(" ", "_").replace("-", "_")
    aliases = {
        "EXTERNAL_USER": "USER",
        "SQL_USER": "USER",
        "WINDOWS_USER": "USER",
        "EXTERNAL_GROUP": "GROUP",
        "EXTERNAL_GROUPS": "GROUP",
        "WINDOWS_GROUP": "GROUP",
        "SERVICEPRINCIPAL": "SERVICE_PRINCIPAL",
    }
    return aliases.get(source_type, source_type or "UNKNOWN")


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


def request_fabric_json(
    url: str,
    *,
    access_token: str,
    method: str = "GET",
    body: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Request one Fabric REST resource and return its JSON object."""
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.netloc.lower() != "api.fabric.microsoft.com":
        raise RuntimeError("Refusing to send a Fabric bearer token to an unexpected host.")
    encoded_body = json.dumps(body).encode("utf-8") if body is not None else None
    headers = {"Authorization": f"Bearer {access_token}", "Accept": "application/json"}
    if encoded_body is not None:
        headers["Content-Type"] = "application/json"
    request = Request(
        url,
        data=encoded_body,
        headers=headers,
        method=method.upper(),
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


def persist_access_rows(
    access_df,
    *,
    config,
    workspace_id: str,
    context: dict[str, Any],
    persist: bool,
    transaction_id: str,
) -> None:
    """Append immutable normalized OneLake observations to METADATA_DATA_ACCESS."""
    if not persist:
        return
    write_context = {**context, "config": config, "scope_workspace_id": workspace_id}
    _require_catalogue_assets(access_df, context=write_context, table_name=ACCESS_TABLE)
    write_lakehouse_table(
        access_df,
        ACCESS_TABLE,
        store="Metadata",
        schema=metadata_table_physical_schema(config, ACCESS_TABLE),
        context=write_context,
        mode="append",
        options={"txnAppId": transaction_id, "txnVersion": "0"},
    )


def catalogue_tables(catalogue_df, *, config, workspace_id: str, target_store_kinds: dict[str, str]):
    """Select active Catalogue tables belonging to configured scan targets."""
    from pyspark.sql import functions as F
    from pyspark.sql import types as T

    spark = catalogue_df.sparkSession
    targets = spark.createDataFrame(
        [(key, kind, store.workspace_id.lower(), store.item_id.lower())
         for key, kind in target_store_kinds.items()
         for store in [get_store(config, workspace_id, key)]],
        T.StructType(
            [
                T.StructField("_catalogue_target", T.StringType(), False),
                T.StructField("_target_store_type", T.StringType(), False),
                T.StructField("_catalogue_physical_workspace", T.StringType(), False),
                T.StructField("_catalogue_physical_item", T.StringType(), False),
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
            (F.col("asset_type") == "TABLE") & F.coalesce(F.col("is_active"), F.lit(True))
        )
        .crossJoin(targets)
        .filter(
            (F.lower(F.col("asset_workspace_id")) == F.col("_catalogue_physical_workspace"))
            & (F.lower(F.col("item_id")) == F.col("_catalogue_physical_item"))
            & (F.lower(F.col("store_type")) == F.col("_target_store_type"))
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
            F.col("asset_workspace_id").alias("_catalogue_workspace_id"),
            F.col("_catalogue_target"),
            F.col("schema_name").alias("_catalogue_schema_name"),
            F.col("table_name").alias("_catalogue_table_name"),
        )
        .dropDuplicates(["_catalogue_workspace_id", "_catalogue_table_id"])
    )


class PortalNoRedirect(HTTPRedirectHandler):
    """Refuse portal redirects to keep bearer tokens on the selected host."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        """Require the caller to select the current portal origin explicitly."""
        return None
