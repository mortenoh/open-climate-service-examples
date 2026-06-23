"""Aggregate a climate dataset to DHIS2 org units and import it into DHIS2.

End-to-end pipeline:

  1. Fetch org-unit boundaries from DHIS2 as GeoJSON (each feature's ``id`` is its
     DHIS2 UID, which the workflow uses directly as the ``orgUnit``).
  2. Run the built-in ``aggregate_to_dhis2_json`` workflow on Open Climate Service to
     get a ready-to-import DHIS2 ``dataValueSet``.
  3. Import that ``dataValueSet`` back into DHIS2.

Configure the instances via environment variables (``OCS_DHIS2_BASE_URL``,
``OCS_DHIS2_USERNAME``, ``OCS_DHIS2_PASSWORD``) or a ``.env`` file; the constants below
choose the dataset and data element.

Needs both extras:
    uv sync --extra dhis2 --extra openeo   # openeo not required, dhis2 is

Run:
    uv run python examples/05_dhis2/aggregate_to_dhis2.py
"""

from __future__ import annotations

from geojson_pydantic import FeatureCollection

from ocs_examples import (
    AggregateToDhis2Args,
    AggregationMethod,
    TemporalExtent,
    climate_service,
    console,
    dhis2_client,
)
from ocs_examples.graphs import aggregate_to_dhis2_graph

DATASET_ID = "era5land_temperature_monthly"
TEMPORAL_EXTENT = TemporalExtent(start="2025-01-01", end="2025-12-31")
ORG_UNIT_LEVEL = 2
DATA_ELEMENT_ID = "BXgDHhPdFVU"
METHOD = AggregationMethod.MEAN
PERIOD_TYPE = "month"


def main() -> None:
    """Fetch org units, aggregate on Open Climate Service, import back into DHIS2."""
    dhis2 = dhis2_client()

    # 1. Org-unit boundaries as GeoJSON, validated into a typed FeatureCollection.
    raw = dhis2.get_org_units_geojson(level=ORG_UNIT_LEVEL)
    org_units: FeatureCollection = FeatureCollection.model_validate(raw)
    console.info(f"Fetched {len(org_units.features)} org units (level {ORG_UNIT_LEVEL})")

    # 2. Build and run the aggregation workflow -> DHIS2 dataValueSet.
    args = AggregateToDhis2Args(
        dataset_id=DATASET_ID,
        temporal_extent=TEMPORAL_EXTENT,
        geometries=org_units,
        data_element_id=DATA_ELEMENT_ID,
        method=METHOD,
        period_type=PERIOD_TYPE,
    )
    with climate_service() as service:
        data_value_set = service.execute(aggregate_to_dhis2_graph(args).to_payload())

    values = data_value_set.get("dataValues", [])
    console.info(f"Workflow produced {len(values)} data values for {DATA_ELEMENT_ID}")
    if not values:
        console.warn("No data values — check the dataset id, temporal extent, and org-unit geometries.")
        return
    console.info(f"  e.g. {values[0]}")

    # 3. Import the dataValueSet into DHIS2.
    report = dhis2.post_data_value_set(data_value_set)
    import_count = report.get("response", {}).get("importCount", report)
    console.section("DHIS2 import summary")
    console.dump(import_count)


if __name__ == "__main__":
    main()
