"""Preview aggregated values for one area before committing an import.

The "look before you import" workflow (PRD user story D): run ``aggregate_to_dhis2_json``
over a single polygon and print the resulting per-period values instead of pushing them
to DHIS2. Uses the first sample feature, so no DHIS2 instance is required.

Run:
    uv run python examples/05_dhis2/preview_org_unit.py
"""

from __future__ import annotations

from geojson_pydantic import FeatureCollection

from ocs_examples import (
    AggregateToDhis2Args,
    TemporalExtent,
    climate_service,
    console,
    dataset_id_of,
    first_published_dataset,
)
from ocs_examples.geometry import sample_feature_collection
from ocs_examples.graphs import aggregate_to_dhis2_graph

# Placeholder data element — irrelevant for a preview, since we never import.
PREVIEW_DATA_ELEMENT = "previewDE001"


def main() -> None:
    """Aggregate the first published dataset over one area and print the values."""
    sample = sample_feature_collection()
    single = FeatureCollection(type="FeatureCollection", features=sample.features[:1])
    area_name = single.features[0].properties.get("name") if single.features[0].properties else "area"

    with climate_service() as service:
        dataset = first_published_dataset(service)
        if dataset is None:
            return
        dataset_id = dataset_id_of(dataset)

        ds = service.open_dataset(dataset_id)
        temporal = TemporalExtent(start=str(ds["t"].values[0])[:10], end=str(ds["t"].values[-1])[:10])

        args = AggregateToDhis2Args(
            dataset_id=dataset_id,
            temporal_extent=temporal,
            geometries=single,
            data_element_id=PREVIEW_DATA_ELEMENT,
        )
        result = service.execute(aggregate_to_dhis2_graph(args).to_payload())

    values = result.get("dataValues", [])
    console.section(f"Preview: {dataset_id} over '{area_name}' ({len(values)} periods)")
    for value in values[:24]:
        print(f"  {value.get('period', '?'):<10} {value.get('value', '')}")


if __name__ == "__main__":
    main()
