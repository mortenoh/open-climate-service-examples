"""Compute a domain-wide spatial mean time series (an area average).

Averages each time step over all grid cells to produce a single value per step — the
"how is the whole region trending?" view. xarray streams only the chunks it needs.

Run:
    uv run python examples/02_data_access/spatial_mean.py
"""

from __future__ import annotations

from ocs_examples import climate_service, console, dataset_id_of, first_published_dataset

# Cap the number of time steps so the example stays quick on large archives.
MAX_STEPS = 24


def main() -> None:
    """Print a spatial-mean time series over the first published dataset."""
    with climate_service() as service:
        dataset = first_published_dataset(service)
        if dataset is None:
            return

        ds = service.open_dataset(dataset_id_of(dataset))
        variable = list(ds.data_vars)[0]

        steps = min(MAX_STEPS, ds.sizes["t"])
        spatial_mean = ds[variable].isel(t=slice(steps)).mean(dim=["y", "x"])
        console.section(f"Spatial mean {variable} (first {steps} steps)")
        console.info(spatial_mean.to_dataframe()[[variable]].to_string())


if __name__ == "__main__":
    main()
