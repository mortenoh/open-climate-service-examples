"""List the datasets published by an Open Climate Service instance.

Uses the typed client's ``datasets()`` method, which reads the STAC catalog
(``GET /stac/catalog.json``) and returns one child-link dict per published collection.

Run:
    uv run python examples/01_discovery/list_datasets.py
"""

from __future__ import annotations

from ocs_examples import climate_service, console


def main() -> None:
    """Print the id and title of every published dataset."""
    with climate_service() as service:
        datasets = service.datasets()

    console.section(f"Published datasets ({len(datasets)})")
    if not datasets:
        console.warn("Nothing published yet — see examples/04_ingestion/ingest_dataset.py")
        return

    for link in datasets:
        print(f"  {link['id']:<45} {link.get('title', '')}")


if __name__ == "__main__":
    main()
