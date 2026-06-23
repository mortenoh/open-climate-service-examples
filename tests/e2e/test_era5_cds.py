"""End-to-end ERA5-Land ingestion via the Copernicus CDS, gated on credentials.

ERA5-Land downloads go through the ``ecmwf-datastores`` client, which needs a CDS
personal access token in ``ECMWF_DATASTORES_URL`` / ``ECMWF_DATASTORES_KEY`` (or a
``~/.ecmwfdatastoresrc`` file). When neither is present this test skips, so the rest of
the e2e suite still runs keyless on CHIRPS.
"""

from __future__ import annotations

import os
from pathlib import Path

import httpx
import pytest

from ocs_examples import Settings, climate_service

pytestmark = pytest.mark.e2e

ERA5_DATASET = "era5land_temperature_monthly"


def _cds_credentials_available() -> bool:
    """Return whether CDS credentials are reachable (env var or rc file)."""
    return bool(os.environ.get("ECMWF_DATASTORES_KEY")) or Path("~/.ecmwfdatastoresrc").expanduser().exists()


def test_ingest_era5_monthly_via_cds(base_url: str) -> None:
    if not _cds_credentials_available():
        pytest.skip("CDS credentials not configured (ECMWF_DATASTORES_KEY / ~/.ecmwfdatastoresrc)")

    payload = {
        "dataset_id": ERA5_DATASET,
        "start": "2024-01",
        "end": "2024-01",
        "overwrite": True,
        "publish": True,
    }
    response = httpx.post(f"{base_url}/ingestions", json=payload, timeout=900.0)
    response.raise_for_status()
    assert response.json().get("status") == "completed"

    # The ingested ERA5-Land temperature dataset should open with a `t2m` variable.
    settings = Settings(base_url=base_url)  # type: ignore[arg-type]
    with climate_service(settings) as service:
        ids = [str(d["id"]) for d in service.datasets()]
        assert ERA5_DATASET in ids
        ds = service.open_dataset(ERA5_DATASET)
    assert "t2m" in ds.data_vars
    assert ds.sizes["t"] >= 1
