"""Open a published dataset as an xarray.Dataset and summarise it.

``service.open_dataset(id)`` reads the remote GeoZarr store advertised in the dataset's
STAC collection and returns a lazy ``xarray.Dataset`` (needs the ``[xarray]`` extra,
which this repo installs by default).

Run:
    uv run python examples/02_data_access/open_with_xarray.py
"""

from __future__ import annotations

from ocs_examples import climate_service, console, dataset_id_of, first_published_dataset


def main() -> None:
    """Open the first published dataset and print its structure."""
    with climate_service() as service:
        dataset = first_published_dataset(service)
        if dataset is None:
            return

        dataset_id = dataset_id_of(dataset)
        console.section(f"Opening {dataset_id}")
        ds = service.open_dataset(dataset_id)

        console.info(repr(ds))
        console.section("Summary")
        console.info(f"  dimensions: {dict(ds.sizes)}")
        console.info(f"  variables:  {list(ds.data_vars)}")
        console.info(f"  time range: {ds['t'].values[0]}  ->  {ds['t'].values[-1]}")
        console.info(f"  latitude:   {ds['y'].min().item():.4f}  ->  {ds['y'].max().item():.4f}")
        console.info(f"  longitude:  {ds['x'].min().item():.4f}  ->  {ds['x'].max().item():.4f}")


if __name__ == "__main__":
    main()
