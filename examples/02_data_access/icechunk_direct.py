"""Open a dataset's native Icechunk store directly, bypassing the typed client.

Instances back their datasets with Icechunk and expose the raw store at
``/icechunk/{dataset_id}``. Opening it directly gives you the versioned store (with its
snapshot history) rather than a flattened xarray view.

Needs Icechunk, which is not a default dependency of this repo:
    uv pip install icechunk

Run:
    uv run python examples/02_data_access/icechunk_direct.py
"""

from __future__ import annotations

from ocs_examples import (
    climate_service,
    console,
    dataset_id_of,
    first_published_dataset,
    get_settings,
)


def main() -> None:
    """Open the first published dataset through its Icechunk HTTP store."""
    try:
        import icechunk
    except ModuleNotFoundError:
        console.warn("Icechunk is not installed. Install it with: uv pip install icechunk")
        return

    import xarray as xr

    settings = get_settings()
    with climate_service(settings) as service:
        dataset = first_published_dataset(service)
        if dataset is None:
            return
        dataset_id = dataset_id_of(dataset)

    store_url = f"{settings.base_url_str}/icechunk/{dataset_id}"
    console.section(f"Opening Icechunk store {store_url}")

    repo = icechunk.Repository.open(icechunk.http_storage(store_url))
    session = repo.readonly_session("main")
    ds = xr.open_zarr(session.store, zarr_format=3, consolidated=False)

    console.info(repr(ds))
    console.info(f"\n  dimensions: {dict(ds.sizes)}")
    console.info(f"  variables:  {list(ds.data_vars)}")


if __name__ == "__main__":
    main()
