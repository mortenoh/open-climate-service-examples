"""Extract a value time series at a single location (a point query).

Mirrors the Google Earth Engine "value at a location" capability: pick the grid cell
nearest a coordinate and read its full time series. Defaults to the domain centre; edit
``LON``/``LAT`` for somewhere specific.

Run:
    uv run python examples/02_data_access/point_time_series.py
"""

from __future__ import annotations

from ocs_examples import climate_service, console, dataset_id_of, first_published_dataset

# Set to a (lon, lat) of interest, or leave as None to use the domain centre.
LON: float | None = None
LAT: float | None = None


def main() -> None:
    """Print a time series for the grid cell nearest the chosen location."""
    with climate_service() as service:
        dataset = first_published_dataset(service)
        if dataset is None:
            return

        ds = service.open_dataset(dataset_id_of(dataset))
        variable = list(ds.data_vars)[0]

        lon = LON if LON is not None else ds["x"].mean().item()
        lat = LAT if LAT is not None else ds["y"].mean().item()

        point = ds[variable].sel(x=lon, y=lat, method="nearest")
        console.section(f"{variable} at ({lat:.3f}, {lon:.3f})")
        frame = point.to_dataframe()[[variable]]
        console.info(frame.head(12).to_string())
        console.info(f"\n  {len(frame)} time steps,  mean = {float(point.mean())}")


if __name__ == "__main__":
    main()
