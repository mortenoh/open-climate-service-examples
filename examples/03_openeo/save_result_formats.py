"""Export the same dataset subset in several output formats.

``save_result`` accepts a range of formats (see ``GET /file_formats``). This runs the
same ``load_collection`` -> ``save_result`` graph once per format and writes each result
to ``output/``, so you can compare NetCDF, GeoTIFF, and Zarr side by side.

Run:
    uv run python examples/03_openeo/save_result_formats.py
"""

from __future__ import annotations

from pathlib import Path

from ocs_examples import (
    SaveFormat,
    TemporalExtent,
    climate_service,
    console,
    dataset_id_of,
    first_published_dataset,
)
from ocs_examples.graphs import load_and_save_graph

OUTPUT_DIR = Path("output")

# Map each format to the file extension we'll save it under.
FORMATS: dict[SaveFormat, str] = {
    SaveFormat.NETCDF: "nc",
    SaveFormat.GTIFF: "tif",
    SaveFormat.ZARR: "zarr",
}


def main() -> None:
    """Export the first published dataset in each configured format."""
    with climate_service() as service:
        dataset = first_published_dataset(service)
        if dataset is None:
            return
        dataset_id = dataset_id_of(dataset)

        ds = service.open_dataset(dataset_id)
        temporal = TemporalExtent(start=str(ds["t"].values[0])[:10], end=str(ds["t"].values[0])[:10])

        OUTPUT_DIR.mkdir(exist_ok=True)
        for save_format, extension in FORMATS.items():
            graph = load_and_save_graph(dataset_id, temporal, save_format=save_format)
            target = OUTPUT_DIR / f"{dataset_id}.{extension}"
            console.section(f"{save_format.value} -> {target}")
            try:
                result = service.execute(graph.to_payload(), path=target)
                console.info(f"  wrote {result}")
            except Exception as error:  # noqa: BLE001 - examples surface, don't crash
                console.warn(f"  {save_format.value} failed: {error}")


if __name__ == "__main__":
    main()
