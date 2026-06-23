"""Offline tests for the shared pydantic models and graph builders.

These need no running instance — they exercise validation and serialisation only.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from ocs_examples import (
    AggregateToDhis2Args,
    AggregationMethod,
    ProcessGraph,
    ProcessNode,
    SaveFormat,
    SpatialExtent,
    TemporalExtent,
)
from ocs_examples.geometry import sample_feature_collection, sample_spatial_extent
from ocs_examples.graphs import aggregate_to_dhis2_graph, load_and_save_graph


def test_spatial_extent_from_bbox_roundtrips() -> None:
    extent = SpatialExtent.from_bbox([28.8, -2.9, 30.9, -1.0])
    assert extent.west == 28.8
    assert extent.north == -1.0


def test_spatial_extent_rejects_inverted_bounds() -> None:
    with pytest.raises(ValidationError):
        SpatialExtent(west=30.0, south=0.0, east=10.0, north=1.0)


def test_temporal_extent_as_list() -> None:
    assert TemporalExtent(start="2025-01-01", end="2025-12-31").as_list() == ["2025-01-01", "2025-12-31"]


def test_process_graph_requires_exactly_one_result() -> None:
    with pytest.raises(ValidationError):
        ProcessGraph(nodes={"a": ProcessNode(process_id="load_collection")})


def test_process_graph_payload_shape() -> None:
    graph = load_and_save_graph(
        "chirps3_precipitation_daily",
        TemporalExtent(start="2024-01-01", end="2024-01-31"),
        save_format=SaveFormat.NETCDF,
    )
    payload = graph.to_payload()
    assert payload["save"]["result"] is True
    assert payload["save"]["arguments"]["format"] == "NetCDF"
    assert payload["load"]["arguments"]["id"] == "chirps3_precipitation_daily"


def test_aggregate_to_dhis2_graph_builds_arguments() -> None:
    args = AggregateToDhis2Args(
        dataset_id="era5land_temperature_monthly",
        temporal_extent=TemporalExtent(start="2025-01-01", end="2025-12-31"),
        geometries=sample_feature_collection(),
        data_element_id="BXgDHhPdFVU",
        method=AggregationMethod.MEAN,
    )
    payload = aggregate_to_dhis2_graph(args).to_payload()
    arguments = payload["agg"]["arguments"]
    assert payload["agg"]["process_id"] == "aggregate_to_dhis2_json"
    assert arguments["method"] == "mean"
    assert arguments["geometries"]["type"] == "FeatureCollection"
    assert len(arguments["geometries"]["features"]) == 2


def test_sample_geometry_covers_extent() -> None:
    extent = sample_spatial_extent()
    collection = sample_feature_collection()
    assert extent.west < extent.east
    assert all(feature.id for feature in collection.features)
