"""Sample GeoJSON geometries for the aggregation examples that don't talk to DHIS2.

The DHIS2 examples fetch real org-unit boundaries from a DHIS2 instance. To let the
aggregation workflows run without one, :func:`sample_feature_collection` returns a small
hand-built FeatureCollection whose feature ``id`` values stand in for DHIS2 org-unit
UIDs — the same shape the workflows consume.
"""

from __future__ import annotations

from geojson_pydantic import Feature, FeatureCollection, Polygon

from ocs_examples.models import SpatialExtent


def _square(min_x: float, min_y: float, size: float) -> Polygon:
    """Return a square polygon with its lower-left corner at ``(min_x, min_y)``."""
    max_x, max_y = min_x + size, min_y + size
    ring = [
        [min_x, min_y],
        [max_x, min_y],
        [max_x, max_y],
        [min_x, max_y],
        [min_x, min_y],
    ]
    return Polygon.model_validate({"type": "Polygon", "coordinates": [ring]})


def sample_feature_collection() -> FeatureCollection:
    """Return a 2-feature FeatureCollection over Rwanda, ids mimicking DHIS2 UIDs.

    The geometries are intentionally coarse; their purpose is to give the aggregation
    workflows valid polygons with stable ``id`` values to key results on.
    """
    features = [
        Feature(
            type="Feature",
            id="OrgUnitAAAA1",
            geometry=_square(29.2, -2.2, 0.4),
            properties={"name": "Sample area A"},
        ),
        Feature(
            type="Feature",
            id="OrgUnitBBBB2",
            geometry=_square(29.8, -1.6, 0.4),
            properties={"name": "Sample area B"},
        ),
    ]
    return FeatureCollection(type="FeatureCollection", features=features)


def sample_spatial_extent() -> SpatialExtent:
    """Return a WGS84 extent covering the sample features (roughly Rwanda)."""
    return SpatialExtent(west=28.8, south=-2.9, east=30.9, north=-1.0)
