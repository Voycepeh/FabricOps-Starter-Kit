from __future__ import annotations

import sys
import types
from dataclasses import dataclass, field
from typing import Any

import pytest


@dataclass
class FakeFabricFs:
    """Configurable notebookutils.mssparkutils.fs test double."""

    existing_paths: set[str] = field(default_factory=set)
    listings: dict[str, list[Any]] = field(default_factory=dict)
    made_dirs: list[str] = field(default_factory=list)

    def exists(self, path: str) -> bool:
        return path in self.existing_paths

    def ls(self, path: str) -> list[Any]:
        return list(self.listings.get(path, []))

    def mkdirs(self, path: str) -> bool:
        self.made_dirs.append(path)
        self.existing_paths.add(path)
        return True


@dataclass
class FakeFabricCredentials:
    """Configurable notebookutils.mssparkutils.credentials test double."""

    tokens: dict[str, str] = field(default_factory=dict)
    secrets: dict[tuple[str, str], str] = field(default_factory=dict)

    def getToken(self, audience: str) -> str:  # noqa: N802 - mirrors Fabric API
        return self.tokens.get(audience, f"fake-token-for-{audience}")

    def getSecret(self, vault: str, name: str) -> str:  # noqa: N802 - mirrors Fabric API
        try:
            return self.secrets[(vault, name)]
        except KeyError as exc:
            raise KeyError(f"No fake secret configured for {vault}/{name}") from exc


@dataclass
class FakeFabricEnv:
    """Configurable notebookutils.mssparkutils.env test double."""

    values: dict[str, str] = field(default_factory=dict)

    def get(self, key: str, default: Any = None) -> Any:
        return self.values.get(key, default)


class FakeRuntimeContext(dict):
    """Dict-backed Fabric runtime context with attribute access."""

    def __getattr__(self, name: str) -> Any:
        try:
            return self[name]
        except KeyError as exc:
            raise AttributeError(name) from exc


@pytest.fixture
def fake_fabric_runtime_context() -> FakeRuntimeContext:
    """Return a reusable Fabric runtime context for local tests."""

    return FakeRuntimeContext(
        currentWorkspaceId="workspace-id",
        currentWorkspaceName="FabricOps Test Workspace",
        currentNotebookId="notebook-id",
        currentNotebookName="02_ex_orders_customers",
        currentRunId="run-id",
        workspaceId="workspace-id",
        workspaceName="FabricOps Test Workspace",
        notebookId="notebook-id",
        notebookName="02_ex_orders_customers",
        userId="user-id",
        userName="fabricops.test@example.com",
        activityId="activity-id",
    )


@pytest.fixture
def fake_notebookutils(monkeypatch: pytest.MonkeyPatch, fake_fabric_runtime_context: FakeRuntimeContext):
    """Inject configurable notebookutils and mssparkutils modules through sys.modules."""

    fs = FakeFabricFs()
    credentials = FakeFabricCredentials()
    env = FakeFabricEnv()
    runtime_module = types.ModuleType("notebookutils.runtime")
    runtime_module.context = fake_fabric_runtime_context

    mssparkutils_module = types.ModuleType("notebookutils.mssparkutils")
    mssparkutils_module.fs = fs
    mssparkutils_module.credentials = credentials
    mssparkutils_module.runtime = runtime_module
    mssparkutils_module.env = env

    notebookutils_module = types.ModuleType("notebookutils")
    notebookutils_module.fs = fs
    notebookutils_module.credentials = credentials
    notebookutils_module.runtime = runtime_module
    notebookutils_module.mssparkutils = mssparkutils_module
    notebookutils_module.env = env

    bare_mssparkutils_module = types.ModuleType("mssparkutils")
    bare_mssparkutils_module.fs = fs
    bare_mssparkutils_module.credentials = credentials
    bare_mssparkutils_module.runtime = runtime_module
    bare_mssparkutils_module.env = env

    monkeypatch.setitem(sys.modules, "notebookutils", notebookutils_module)
    monkeypatch.setitem(sys.modules, "notebookutils.runtime", runtime_module)
    monkeypatch.setitem(sys.modules, "notebookutils.mssparkutils", mssparkutils_module)
    monkeypatch.setitem(sys.modules, "mssparkutils", bare_mssparkutils_module)

    return types.SimpleNamespace(
        notebookutils=notebookutils_module,
        mssparkutils=mssparkutils_module,
        fs=fs,
        credentials=credentials,
        runtime=runtime_module,
        context=fake_fabric_runtime_context,
        env=env,
    )


@pytest.fixture(scope="session")
def spark_session():
    """Return a local Spark session or skip when Spark prerequisites are unavailable."""

    try:
        from pyspark.sql import SparkSession
    except Exception as exc:  # pragma: no cover - environment dependent
        pytest.skip(f"PySpark is unavailable: {exc}")

    try:
        spark = (
            SparkSession.builder.master("local[2]")
            .appName("fabricops-local-tests")
            .config("spark.ui.enabled", "false")
            .config("spark.sql.shuffle.partitions", "2")
            .config("spark.driver.bindAddress", "127.0.0.1")
            .getOrCreate()
        )
    except Exception as exc:  # pragma: no cover - environment dependent
        pytest.skip(f"Local Spark prerequisites are unavailable: {exc}")

    spark.sparkContext.setLogLevel("ERROR")
    yield spark
    spark.stop()
