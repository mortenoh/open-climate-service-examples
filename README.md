# Open Climate Service — Examples

Runnable, self-contained examples for working with an [Open Climate
Service](https://github.com/dhis2/open-climate-service) instance: discovering and opening
published datasets, processing them with openEO, ingesting and syncing managed datasets,
and aggregating climate data into DHIS2 and CHAP.

Each script under [`examples/`](examples/) is independently runnable and prints what it
does. Shared building blocks (settings, client factories, typed models, process-graph
builders) live in [`src/ocs_examples/`](src/ocs_examples/) so the examples stay short and
consistent.

## Requirements

- Python 3.13+ and [uv](https://docs.astral.sh/uv/)
- A running Open Climate Service instance. To start one locally, see the
  [quick start](https://dhis2.github.io/open-climate-service/setup_guide/). Most examples
  also need at least one **published** dataset — run an ingestion example first, or use
  the instance's `/manage` web interface.

## Install

```bash
make install        # uv sync --all-extras (client + xarray + openeo + dhis2)
```

The base install pulls `open-climate-service[xarray]`, so every data-access example can
open published datasets as xarray objects. The `openeo` and `dhis2` extras back the
examples in `examples/03_openeo` and `examples/05_dhis2` respectively.

> This repo resolves `open-climate-service` from the sibling checkout at
> `../open-climate-service` and `dhis2-client` from git (see `[tool.uv.sources]` in
> `pyproject.toml`). Point these at a package index once the packages are published there.

## Configure

Every example reads its connection details from the environment (or a `.env` file) via
`ocs_examples.config.Settings`. Defaults target `http://127.0.0.1:8000`.

```bash
cp .env.example .env     # then edit if your instance or DHIS2 differ
```

| Variable | Default | Used by |
| --- | --- | --- |
| `OCS_BASE_URL` | `http://127.0.0.1:8000` | all |
| `OCS_TIMEOUT` | `30` | all |
| `OCS_DHIS2_BASE_URL` | DHIS2 climate demo | `examples/05_dhis2` |
| `OCS_DHIS2_USERNAME` / `OCS_DHIS2_PASSWORD` | `admin` / `district` | `examples/05_dhis2` |

## Run an example

```bash
uv run python examples/01_discovery/list_datasets.py
uv run python examples/02_data_access/open_with_xarray.py
uv run python examples/03_openeo/openeo_batch_job.py
```

## What's here

| Group | Examples |
| --- | --- |
| **01_discovery** | list datasets, show extent, list dataset templates, list processes, list workflows, server info/health |
| **02_data_access** | open with xarray, Zarr subsetting, point time series, spatial mean, export to NetCDF, native Icechunk access |
| **03_openeo** | connect + list collections, batch job, synchronous `/result` from a typed graph, multi-format export, store + run a UDP |
| **04_ingestion** | ingest a dataset, async ingest with polling, list ingestions, sync plan (dry run), sync forward |
| **05_dhis2** | aggregate + import to DHIS2, aggregate to CHAP CSV, preview an org unit before import |
| **06_http** | discovery with raw httpx, `POST /result` (the curl example in Python) |

## Develop

```bash
make lint     # ruff format + ruff check + mypy + pyright
make test     # pytest, offline unit tests for the shared helpers (excludes e2e)
make clean    # remove caches and build artifacts
```

## End-to-end tests

The e2e suite boots a **real** Open Climate Service instance in-process (uvicorn on an
ephemeral port), ingests a small dataset over the network, and then exercises the flow —
including running a curated set of the example scripts as real subprocesses against the
live instance.

```bash
make install-e2e          # adds the full server stack (uv sync --group e2e)
make test-e2e             # uv run pytest -m e2e
```

- `tests/e2e/test_flow.py` — health, discovery, open with xarray, aggregate to CHAP CSV
- `tests/e2e/test_examples_run.py` — runs ~17 example scripts and asserts each exits 0
- `tests/e2e/test_era5_cds.py` — ERA5-Land ingestion via the CDS; **skips** when no CDS
  credentials are configured

The default keyless path ingests a 3-day CHIRPS slice over a small Rwanda extent (a few
hundred kB). The ERA5 test additionally needs Copernicus CDS credentials — see below.

### Data-source credentials

Downloads happen **server-side** during ingestion, so credentials belong to the
environment that runs the instance (including the e2e tests, which boot one and load
`.env` on startup). Set them only for the datasets you ingest:

| Dataset | Credentials |
| --- | --- |
| CHIRPS (`chirps3_precipitation_daily`) | none — public HTTP |
| WorldPop (`worldpop_population_yearly`) | none, but needs `extent.country_code` |
| ERA5-Land monthly/daily (Copernicus CDS) | `ECMWF_DATASTORES_URL` / `ECMWF_DATASTORES_KEY` (or `~/.ecmwfdatastoresrc`) |
| ERA5-Land `*_from_hourly` (DestinE Earth Data Hub) | `EDH_API_KEY` |

The CDS URL/key are your [CDS personal access token](https://cds.climate.copernicus.eu/).
See `.env.example` for the full list.
