"""Fixtures that boot a real Open Climate Service instance for end-to-end tests.

The instance is the genuine FastAPI app served over a real TCP socket by uvicorn in a
background thread, so the typed client and the example scripts exercise it exactly as
they would a deployed instance. A small Sierra Leone extent keeps downloads tiny.

These tests need the server stack and download real data over the network:

    uv sync --group e2e
    uv run pytest -m e2e

Marked ``e2e`` and deselected by the default ``make test`` run.
"""

from __future__ import annotations

import os
import socket
import threading
import time
from collections.abc import Iterator
from pathlib import Path

import httpx
import pytest
import uvicorn

# A small extent over Rwanda — CHIRPS is global, so clipping here keeps each ingested
# day to a few hundred kilobytes. Matches the sample geometry in ocs_examples.geometry,
# so the aggregation examples produce real (non-empty) values.
EXTENT_NAME = "Rwanda (test)"
EXTENT_BBOX = [28.8, -2.9, 30.9, -1.0]
COUNTRY_CODE = "RWA"


def _free_port() -> int:
    """Return an unused localhost TCP port."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


class _ThreadedServer(uvicorn.Server):
    """A uvicorn server that runs in a thread without installing signal handlers."""

    def install_signal_handlers(self) -> None:  # noqa: D102 - override to no-op
        return


@pytest.fixture(scope="session")
def base_url(tmp_path_factory: pytest.TempPathFactory) -> Iterator[str]:
    """Boot an instance configured for a small extent and yield its base URL."""
    config_dir = tmp_path_factory.mktemp("instance")
    (config_dir / "data").mkdir()
    config_file = config_dir / "climate-service.yaml"
    config_file.write_text(
        "\n".join(
            [
                "id: e2e-test",
                f"name: {EXTENT_NAME}",
                "extent:",
                f"  name: {EXTENT_NAME}",
                f"  bbox: [{', '.join(str(v) for v in EXTENT_BBOX)}]",
                f"  country_code: {COUNTRY_CODE}",
                "data_dir: ./data",
                "",
            ]
        ),
        encoding="utf-8",
    )
    os.environ["CLIMATE_SERVICE_CONFIG"] = str(config_file)

    # Reset the cached config, then build the app now that the env points at our YAML.
    from open_climate_service import config as api_config

    api_config._cache = None
    from open_climate_service.main import create_app

    app = create_app()

    port = _free_port()
    server = _ThreadedServer(uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning"))
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()

    url = f"http://127.0.0.1:{port}"
    deadline = time.monotonic() + 30
    while time.monotonic() < deadline:
        try:
            if httpx.get(f"{url}/health", timeout=1.0).is_success:
                break
        except httpx.HTTPError:
            time.sleep(0.2)
    else:
        server.should_exit = True
        raise RuntimeError("server did not become healthy within 30s")

    # Point the example helpers (ocs_examples.Settings) at this instance.
    os.environ["OCS_BASE_URL"] = url
    try:
        yield url
    finally:
        server.should_exit = True
        thread.join(timeout=10)


@pytest.fixture(scope="session")
def ingested_dataset(base_url: str) -> str:
    """Ingest a tiny multi-day CHIRPS slice and return its dataset id.

    Session-scoped so the (network) download happens once for the whole e2e run.
    """
    payload = {
        "dataset_id": "chirps3_precipitation_daily",
        "start": "2024-11-01",
        "end": "2024-11-03",
        "overwrite": True,
        "publish": True,
    }
    response = httpx.post(f"{base_url}/ingestions", json=payload, timeout=600.0)
    response.raise_for_status()

    # The catalog should now list at least one published dataset.
    deadline = time.monotonic() + 30
    while time.monotonic() < deadline:
        catalog = httpx.get(f"{base_url}/stac/catalog.json", timeout=10.0).json()
        children = [link for link in catalog.get("links", []) if link.get("rel") == "child"]
        if children:
            href = str(children[0]["href"])
            return children[0].get("id") or href.rstrip("/").split("/")[-1].removesuffix(".json")
        time.sleep(0.5)
    raise RuntimeError("ingestion did not publish a dataset")


@pytest.fixture
def repo_root() -> Path:
    """Return the repository root (two levels up from this file)."""
    return Path(__file__).resolve().parents[2]
