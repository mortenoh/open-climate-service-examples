"""Aggregate a dataset to CHAP-format CSV using built-in sample geometries.

The ``aggregate_to_chap_csv`` workflow produces the wide CSV the CHAP Modelling Platform
expects. Unlike the DHIS2 example, this one needs no DHIS2 instance — it uses the sample
FeatureCollection from ``ocs_examples.geometry``, so it runs against any published
dataset on its own.

Run:
    uv run python examples/05_dhis2/aggregate_to_chap_csv.py
"""

from __future__ import annotations

from pathlib import Path

from ocs_examples import (
    AggregateToChapArgs,
    AggregationMethod,
    TemporalExtent,
    climate_service,
    console,
    dataset_id_of,
    first_published_dataset,
)
from ocs_examples.geometry import sample_feature_collection
from ocs_examples.graphs import aggregate_to_chap_graph

OUTPUT_DIR = Path("output")


def main() -> None:
    """Aggregate the first published dataset over sample polygons to a CHAP CSV."""
    with climate_service() as service:
        dataset = first_published_dataset(service)
        if dataset is None:
            return
        dataset_id = dataset_id_of(dataset)

        ds = service.open_dataset(dataset_id)
        temporal = TemporalExtent(start=str(ds["t"].values[0])[:10], end=str(ds["t"].values[-1])[:10])

        args = AggregateToChapArgs(
            dataset_id=dataset_id,
            temporal_extent=temporal,
            geometries=sample_feature_collection(),
            method=AggregationMethod.MEAN,
            period_type="month",
        )
        OUTPUT_DIR.mkdir(exist_ok=True)
        target = OUTPUT_DIR / f"{dataset_id}_chap.csv"
        console.section(f"Aggregating {dataset_id} -> {target}")
        result = service.execute(aggregate_to_chap_graph(args).to_payload(), path=target)
        console.info(f"  wrote {result}")
        console.info(target.read_text()[:500])


if __name__ == "__main__":
    main()
