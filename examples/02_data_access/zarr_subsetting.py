"""Open a GeoZarr dataset and demonstrate spatial and temporal subsetting.

Because ``open_dataset`` returns a lazy xarray object backed by the remote Zarr store,
only the chunks you actually touch are fetched. This selects a single time step and a
spatial window without downloading the whole archive.

Run:
    uv run python examples/02_data_access/zarr_subsetting.py
"""

from __future__ import annotations

from ocs_examples import climate_service, console, dataset_id_of, first_published_dataset


def main() -> None:
    """Subset the first published dataset in time and space."""
    with climate_service() as service:
        dataset = first_published_dataset(service)
        if dataset is None:
            return

        ds = service.open_dataset(dataset_id_of(dataset))
        variable = list(ds.data_vars)[0]

        # One time step, fully realised into memory.
        t0 = ds["t"].values[0]
        snapshot = ds[variable].isel(t=0).compute()
        console.section(f"{variable} snapshot at {t0}")
        console.info(f"  shape: {snapshot.shape}")
        console.info(f"  min:   {float(snapshot.min())}")
        console.info(f"  max:   {float(snapshot.max())}")

        # A spatial window: the southern half of the domain at the first time step.
        y_mid = ds["y"].mean().item()
        window = ds[variable].isel(t=0).sel(y=slice(ds["y"].min().item(), y_mid)).compute()
        console.section("Southern-half window")
        console.info(f"  shape: {window.shape}")
        console.info(f"  mean:  {float(window.mean())}")


if __name__ == "__main__":
    main()
