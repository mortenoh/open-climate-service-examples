"""Pydantic models for the data the examples build, pass around, and validate.

Open Climate Service speaks openEO, so the central type here is an openEO
:class:`ProcessGraph` — a mapping of node id to :class:`ProcessNode`, exactly one of
which is the result node. The helper classes (:class:`SpatialExtent`,
:class:`TemporalExtent`, :class:`AggregateToDhis2Args`, :class:`AggregateToChapArgs`)
give the common process arguments names and validation instead of raw dicts.

Building graphs from these models keeps the examples honest: an invalid extent or a
graph with no result node fails fast and locally, before any HTTP request is made.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Any

from geojson_pydantic import FeatureCollection
from pydantic import BaseModel, ConfigDict, Field, model_validator


class AggregationMethod(StrEnum):
    """Spatial aggregation method supported by the DHIS2/CHAP workflows."""

    MEAN = "mean"
    MIN = "min"
    MAX = "max"
    SUM = "sum"


class SaveFormat(StrEnum):
    """Output formats accepted by the openEO ``save_result`` process.

    Mirrors ``GET /file_formats`` on a running instance.
    """

    ZARR = "Zarr"
    NETCDF = "NetCDF"
    GTIFF = "GTiff"
    PNG = "PNG"
    GEOJSON = "GeoJSON"
    CSV = "CSV"
    PARQUET = "Parquet"
    DHIS2JSON = "DHIS2JSON"
    CHAPCSV = "CHAPCSV"


class SpatialExtent(BaseModel):
    """A WGS84 bounding box in the west/south/east/north form openEO expects."""

    west: float = Field(ge=-180, le=180)
    south: float = Field(ge=-90, le=90)
    east: float = Field(ge=-180, le=180)
    north: float = Field(ge=-90, le=90)

    @model_validator(mode="after")
    def _check_order(self) -> SpatialExtent:
        if self.west > self.east:
            raise ValueError("west must be <= east")
        if self.south > self.north:
            raise ValueError("south must be <= north")
        return self

    @classmethod
    def from_bbox(cls, bbox: tuple[float, float, float, float] | list[float]) -> SpatialExtent:
        """Build an extent from a ``[xmin, ymin, xmax, ymax]`` bounding box."""
        west, south, east, north = bbox
        return cls(west=west, south=south, east=east, north=north)


class TemporalExtent(BaseModel):
    """A closed time interval expressed as two ISO-8601 date strings."""

    start: str
    end: str

    def as_list(self) -> list[str]:
        """Return the interval as the two-element list openEO arguments expect."""
        return [self.start, self.end]


class ProcessNode(BaseModel):
    """A single node in an openEO process graph."""

    model_config = ConfigDict(populate_by_name=True)

    process_id: str
    arguments: dict[str, Any] = Field(default_factory=dict)
    result: bool = False


class ProcessGraph(BaseModel):
    """An openEO process graph: a mapping of node id to node, with one result node."""

    nodes: dict[str, ProcessNode]

    @model_validator(mode="after")
    def _exactly_one_result(self) -> ProcessGraph:
        result_nodes = [node_id for node_id, node in self.nodes.items() if node.result]
        if len(result_nodes) != 1:
            raise ValueError(f"a process graph needs exactly one result node, found {len(result_nodes)}")
        return self

    def to_payload(self) -> dict[str, dict[str, Any]]:
        """Serialise to the bare ``{node_id: {...}}`` mapping the client accepts."""
        return {node_id: node.model_dump(exclude_none=False) for node_id, node in self.nodes.items()}


class AggregateToDhis2Args(BaseModel):
    """Arguments for the built-in ``aggregate_to_dhis2_json`` workflow."""

    dataset_id: str
    temporal_extent: TemporalExtent
    geometries: FeatureCollection
    data_element_id: str
    method: AggregationMethod = AggregationMethod.MEAN
    period_type: str = "month"

    def to_arguments(self) -> dict[str, Any]:
        """Render the openEO process arguments dict."""
        return {
            "dataset_id": self.dataset_id,
            "temporal_extent": self.temporal_extent.as_list(),
            "geometries": self.geometries.model_dump(),
            "data_element_id": self.data_element_id,
            "method": self.method.value,
            "period_type": self.period_type,
        }


class AggregateToChapArgs(BaseModel):
    """Arguments for the built-in ``aggregate_to_chap_csv`` workflow."""

    dataset_id: str
    temporal_extent: TemporalExtent
    geometries: FeatureCollection
    method: AggregationMethod = AggregationMethod.MEAN
    period_type: str = "month"

    def to_arguments(self) -> dict[str, Any]:
        """Render the openEO process arguments dict."""
        return {
            "dataset_id": self.dataset_id,
            "temporal_extent": self.temporal_extent.as_list(),
            "geometries": self.geometries.model_dump(),
            "method": self.method.value,
            "period_type": self.period_type,
        }
