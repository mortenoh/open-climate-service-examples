"""End-to-end flow against a live instance, driven through the shared helpers.

Ingest -> discover -> open with xarray -> aggregate to CHAP CSV, using the same
``ocs_examples`` building blocks the example scripts use.
"""

from __future__ import annotations

import httpx
import pytest

from ocs_examples import (
    AggregateToChapArgs,
    Settings,
    TemporalExtent,
    climate_service,
)
from ocs_examples.geometry import sample_feature_collection
from ocs_examples.graphs import aggregate_to_chap_graph

pytestmark = pytest.mark.e2e


def test_health_and_extent(base_url: str) -> None:
    assert httpx.get(f"{base_url}/health", timeout=10.0).is_success
    extent = httpx.get(f"{base_url}/extent", timeout=10.0).json()
    assert extent  # configured extent is non-empty


def test_discovery_lists_ingested_dataset(base_url: str, ingested_dataset: str) -> None:
    settings = Settings(base_url=base_url)  # type: ignore[arg-type]
    with climate_service(settings) as service:
        ids = [str(d["id"]) for d in service.datasets()]
    assert ingested_dataset in ids


def test_open_dataset_with_xarray(base_url: str, ingested_dataset: str) -> None:
    settings = Settings(base_url=base_url)  # type: ignore[arg-type]
    with climate_service(settings) as service:
        ds = service.open_dataset(ingested_dataset)
    assert ds.sizes["t"] >= 1
    assert "precip" in ds.data_vars or len(ds.data_vars) >= 1


def test_aggregate_to_chap_csv(base_url: str, ingested_dataset: str) -> None:
    settings = Settings(base_url=base_url)  # type: ignore[arg-type]
    with climate_service(settings) as service:
        ds = service.open_dataset(ingested_dataset)
        temporal = TemporalExtent(start=str(ds["t"].values[0])[:10], end=str(ds["t"].values[-1])[:10])
        args = AggregateToChapArgs(
            dataset_id=ingested_dataset,
            temporal_extent=temporal,
            geometries=sample_feature_collection(),
            period_type="day",
        )
        result = service.execute(aggregate_to_chap_graph(args).to_payload())
    # CHAP CSV comes back as bytes; it should at least carry a header row.
    text = result.decode() if isinstance(result, bytes) else str(result)
    assert "," in text
