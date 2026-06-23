"""Shared helpers for the Open Climate Service examples.

Importable building blocks the example scripts reuse: configuration
(:mod:`ocs_examples.config`), client factories (:mod:`ocs_examples.connection`),
typed data models (:mod:`ocs_examples.models`), process-graph builders
(:mod:`ocs_examples.graphs`), dataset discovery (:mod:`ocs_examples.discovery`),
sample geometries (:mod:`ocs_examples.geometry`), and console formatting
(:mod:`ocs_examples.console`).
"""

from __future__ import annotations

from ocs_examples.config import Settings, get_settings
from ocs_examples.connection import (
    climate_service,
    dhis2_client,
    http_client,
    openeo_connection,
)
from ocs_examples.discovery import dataset_id_of, first_published_dataset
from ocs_examples.models import (
    AggregateToChapArgs,
    AggregateToDhis2Args,
    AggregationMethod,
    ProcessGraph,
    ProcessNode,
    SaveFormat,
    SpatialExtent,
    TemporalExtent,
)

__version__ = "0.1.0"

__all__ = [
    "AggregateToChapArgs",
    "AggregateToDhis2Args",
    "AggregationMethod",
    "ProcessGraph",
    "ProcessNode",
    "SaveFormat",
    "Settings",
    "SpatialExtent",
    "TemporalExtent",
    "__version__",
    "climate_service",
    "dataset_id_of",
    "dhis2_client",
    "first_published_dataset",
    "get_settings",
    "http_client",
    "openeo_connection",
]
