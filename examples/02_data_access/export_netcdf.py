"""Download a published dataset (or a subset) to a local NetCDF file.

Opens the dataset with xarray, optionally trims it to the first ``MAX_STEPS`` time
steps to keep the file small, and writes it to disk with ``to_netcdf``. From there it
is a plain local file you can open in any NetCDF-aware tool.

Run:
    uv run python examples/02_data_access/export_netcdf.py
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING

from ocs_examples import climate_service, console, dataset_id_of, first_published_dataset

if TYPE_CHECKING:
    import xarray as xr

OUTPUT_DIR = Path("output")
MAX_STEPS = 12


def netcdf_safe(ds: xr.Dataset) -> xr.Dataset:
    """Return a copy whose attributes NetCDF can represent.

    GeoZarr stores carry structured attributes (e.g. ``zarr_conventions``) whose types
    the NetCDF classic model rejects. Serialise any non-scalar attribute to a JSON
    string so the export round-trips cleanly.
    """
    ds = ds.copy()
    containers = [ds, *(ds[name] for name in list(ds.variables))]
    for container in containers:
        for key, value in list(container.attrs.items()):
            if not isinstance(value, (str, int, float)):
                container.attrs[key] = json.dumps(value, default=str)
    return ds


def main() -> None:
    """Write the first published dataset (trimmed in time) to a NetCDF file."""
    with climate_service() as service:
        dataset = first_published_dataset(service)
        if dataset is None:
            return

        dataset_id = dataset_id_of(dataset)
        ds = service.open_dataset(dataset_id)

        steps = min(MAX_STEPS, ds.sizes["t"])
        subset = netcdf_safe(ds.isel(t=slice(steps)))

        OUTPUT_DIR.mkdir(exist_ok=True)
        target = OUTPUT_DIR / f"{dataset_id}.nc"
        console.section(f"Writing {steps} time steps to {target}")
        subset.to_netcdf(target)
        console.info(f"  wrote {target.stat().st_size / 1_000:.1f} kB")


if __name__ == "__main__":
    main()
