from pathlib import Path


def write(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def require_replace(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise SystemExit(f"Expected text not found for {label}: {old[:120]!r}")
    return text.replace(old, new, 1)


# Shared config identity helpers are architecture-visible internal functions.
config_shared = Path("src/fabricops_kit/config/shared.py")
text = config_shared.read_text(encoding="utf-8")
if "import hashlib\n" not in text:
    text = require_replace(text, "from datetime import datetime\n", "from datetime import datetime\nimport hashlib\nimport json\n", "config shared imports")
identity_block = '''\n\n# ---------------------------------------------------------------------------\n# Stable metadata identity\n# ---------------------------------------------------------------------------\n\n\ndef _stable_metadata_id(*parts: Any) -> str:\n    \"\"\"Return a deterministic SHA-256 identity from normalized logical parts.\"\"\"\n    payload = [\n        {\"is_null\": part is None, \"value\": None if part is None else str(part).strip().lower()}\n        for part in parts\n    ]\n    return hashlib.sha256(\n        json.dumps(payload, separators=(\",\", \":\"), sort_keys=True).encode(\"utf-8\")\n    ).hexdigest()\n\n\ndef build_table_id(store_type: Any, layer: Any, schema_name: Any, table_name: Any) -> str:\n    \"\"\"Return the environment-independent logical identity for a table asset.\"\"\"\n    return _stable_metadata_id(store_type, layer, schema_name, table_name)\n\n\ndef build_column_id(table_id: Any, column_name: Any) -> str:\n    \"\"\"Return the environment-independent logical identity for a column asset.\"\"\"\n    return _stable_metadata_id(table_id, column_name)\n'''
if "def build_table_id(" not in text:
    text = text.rstrip() + identity_block + "\n"
write(config_shared, text)

# Shared pipeline observation helpers belong in the existing package shared.py.
pipeline_shared = Path("src/fabricops_kit/pipeline/shared.py")
text = pipeline_shared.read_text(encoding="utf-8")
text = require_replace(
    text,
    "from ..io.shared import configured_lakehouse_schema, write_lakehouse_table_core\n",
    "from ..io.shared import configured_lakehouse_schema, read_lakehouse_table_core, write_lakehouse_table_core\n",
    "pipeline shared IO imports",
)
observation_block = '''\n\n# ---------------------------------------------------------------------------\n# Source observation helpers\n# ---------------------------------------------------------------------------\n\nSOURCE_OBSERVATION_COLUMNS = frozenset(\n    {\n        \"observation_id\",\n        \"table_id\",\n        \"environment_name\",\n        \"partition_value\",\n        \"row_count\",\n        \"min_change_value\",\n        \"max_change_value\",\n        \"is_present\",\n        \"observed_at\",\n    }\n)\n\n\ndef observation_rows(dataframe: Any) -> list[dict[str, Any]]:\n    \"\"\"Return canonical observation rows as dictionaries.\"\"\"\n    values = dataframe.collect() if hasattr(dataframe, \"collect\") else dataframe\n    return [row.asDict(recursive=True) if hasattr(row, \"asDict\") else dict(row) for row in values or []]\n\n\ndef is_source_observation(dataframe: Any) -> bool:\n    \"\"\"Return whether a value exposes the normalized observation contract.\"\"\"\n    columns = set(getattr(dataframe, \"columns\", ()))\n    if not columns and isinstance(dataframe, (list, tuple)) and dataframe:\n        columns = set(dict(dataframe[0]))\n    return SOURCE_OBSERVATION_COLUMNS <= columns\n\n\ndef catalogue_table_identity(\n    *, config: Any, env: str, table_id: str, spark_session: Any\n) -> dict[str, Any] | None:\n    \"\"\"Resolve physical table attributes from the environment-specific Catalogue row.\"\"\"\n    catalogue = read_lakehouse_table_core(\n        \"METADATA_DATA_CATALOGUE\",\n        target=\"metadata\",\n        schema=configured_lakehouse_schema(config, env, \"metadata\"),\n        spark_session=spark_session,\n        context={\"config\": config, \"env\": env},\n    )\n    if hasattr(catalogue, \"where\"):\n        from pyspark.sql import functions as F\n\n        matches = catalogue.where(\n            (F.col(\"environment_name\") == env)\n            & (F.col(\"table_id\") == table_id)\n            & (F.col(\"metadata_level\") == \"table\")\n        )\n        if \"is_active\" in getattr(matches, \"columns\", ()):\n            matches = matches.where(F.col(\"is_active\") == F.lit(True))\n        rows = matches.orderBy(F.col(\"last_profiled_at\").desc_nulls_last()).limit(1).collect()\n        return rows[0].asDict(recursive=True) if rows else None\n\n    rows = observation_rows(catalogue)\n    candidates = [\n        row\n        for row in rows\n        if str(row.get(\"environment_name\") or \"\") == env\n        and str(row.get(\"table_id\") or \"\") == table_id\n        and str(row.get(\"metadata_level\") or \"\") == \"table\"\n        and row.get(\"is_active\", True) is not False\n    ]\n    if not candidates:\n        return None\n    candidates.sort(key=lambda row: str(row.get(\"last_profiled_at\") or \"\"), reverse=True)\n    return candidates[0]\n\n\ndef guardrail_compatibility_observation(\n    observation: Any, *, table_id: str, change_column: str\n) -> Any:\n    \"\"\"Add temporary in-memory aliases required by the not-yet-migrated Guardrail core.\n\n    These aliases are never persisted. They isolate the staged Stage 2\n    observation schema from the Stage 4 Guardrail migration.\n    \"\"\"\n    if hasattr(observation, \"withColumn\"):\n        from pyspark.sql import functions as F\n\n        return observation.withColumn(\"metadata_table_key\", F.lit(table_id)).withColumn(\n            \"change_column\", F.lit(change_column)\n        )\n    return [\n        {**row, \"metadata_table_key\": table_id, \"change_column\": change_column}\n        for row in observation_rows(observation)\n    ]\n'''
if "def observation_rows(" not in text:
    text = text.rstrip() + observation_block + "\n"
write(pipeline_shared, text)

# Replace imports and helper names across authoritative Python sources and tests.
for root in (Path("src"), Path("tests"), Path("scripts")):
    for path in root.rglob("*.py"):
        if path in {config_shared, pipeline_shared}:
            continue
        source = path.read_text(encoding="utf-8")
        updated = source.replace("from fabricops_kit.config.metadata_identity import _build_column_id, _build_table_id", "from fabricops_kit.config.shared import build_column_id, build_table_id")
        updated = updated.replace("from fabricops_kit.config.metadata_identity import _build_table_id", "from fabricops_kit.config.shared import build_table_id")
        updated = updated.replace("from fabricops_kit.config.metadata_identity import _build_column_id", "from fabricops_kit.config.shared import build_column_id")
        updated = updated.replace("fabricops_kit.config.metadata_identity._build_column_id", "fabricops_kit.config.shared.build_column_id")
        updated = updated.replace("fabricops_kit.config.metadata_identity._build_table_id", "fabricops_kit.config.shared.build_table_id")
        updated = updated.replace("_build_column_id", "build_column_id").replace("_build_table_id", "build_table_id")
        updated = updated.replace("from fabricops_kit.pipeline.observation_shared import (", "from fabricops_kit.pipeline.shared import (")
        updated = updated.replace("from fabricops_kit.pipeline.observation_shared import _is_source_observation, _observation_rows", "from fabricops_kit.pipeline.shared import is_source_observation, observation_rows")
        updated = updated.replace("fabricops_kit.pipeline.observation_shared._guardrail_compatibility_observation", "fabricops_kit.pipeline.shared.guardrail_compatibility_observation")
        updated = updated.replace("fabricops_kit.pipeline.observation_shared._is_source_observation", "fabricops_kit.pipeline.shared.is_source_observation")
        updated = updated.replace("fabricops_kit.pipeline.observation_shared._observation_rows", "fabricops_kit.pipeline.shared.observation_rows")
        updated = updated.replace("fabricops_kit.pipeline.observation_shared._catalogue_table_identity", "fabricops_kit.pipeline.shared.catalogue_table_identity")
        updated = updated.replace("_guardrail_compatibility_observation", "guardrail_compatibility_observation")
        updated = updated.replace("_is_source_observation", "is_source_observation")
        updated = updated.replace("_observation_rows", "observation_rows")
        updated = updated.replace("_catalogue_table_identity", "catalogue_table_identity")
        if updated != source:
            write(path, updated)

# Tests should import the internal architecture-visible helpers from shared.py.
identity_test = Path("tests/unit/test_metadata_identity.py")
text = identity_test.read_text(encoding="utf-8")
text = text.replace("from fabricops_kit.config.metadata_identity import build_column_id, build_table_id", "from fabricops_kit.config.shared import build_column_id, build_table_id")
write(identity_test, text)
