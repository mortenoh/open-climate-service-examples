"""Helpers for discovering published datasets and failing gracefully when there are none.

Every data-access example needs a published dataset to work with. Rather than repeat
the same "did anything come back?" guard in each script, they call
:func:`first_published_dataset`, which returns ``None`` and prints a friendly hint when
the instance has nothing published yet.
"""

from __future__ import annotations

from open_climate_service import ClimateService

from ocs_examples import console


def first_published_dataset(service: ClimateService) -> dict[str, object] | None:
    """Return the first published dataset (a STAC child-link dict), or ``None``.

    Prints a hint pointing at the ingestion examples when the catalog is empty.
    """
    datasets = service.datasets()
    if not datasets:
        console.warn(
            "No published datasets found. Ingest one first — see "
            "examples/04_ingestion/ingest_dataset.py or POST to /ingestions."
        )
        return None
    first: dict[str, object] = datasets[0]
    return first


def dataset_id_of(dataset: dict[str, object]) -> str:
    """Extract the dataset id from a STAC child-link dict."""
    return str(dataset["id"])
