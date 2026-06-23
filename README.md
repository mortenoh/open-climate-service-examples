# Open Climate Service — Examples

Runnable, self-contained examples for working with an [Open Climate
Service](https://github.com/dhis2/open-climate-service) (OCS) instance, with a small
shared helper package so the scripts stay short and consistent.

- [What is Open Climate Service?](#what-is-open-climate-service)
- [Core concepts](#core-concepts)
- [Built-in data providers](#built-in-data-providers)
- [Requirements](#requirements)
- [Install](#install)
- [Configure](#configure)
- [Quick start](#quick-start)
- [The examples, step by step](#the-examples-step-by-step)
- [The shared helper package](#the-shared-helper-package)
- [End-to-end tests](#end-to-end-tests)
- [Data-source credentials](#data-source-credentials)
- [Develop](#develop)
- [Project layout](#project-layout)

---

## What is Open Climate Service?

Open Climate Service is an open-source platform that downloads, processes, and serves
climate and Earth Observation (EO) data so it can be used for decision-making — for
example, importing temperature and precipitation into [DHIS2](https://dhis2.org) or the
[CHAP](https://github.com/dhis2-chap) modelling platform for climate-and-health analysis.

Each **instance** is configured for one country or region. It scopes all data extraction,
processing, and storage to that spatial extent; pulls from sources such as CHIRPS,
ERA5-Land, and WorldPop; stores outputs as **GeoZarr**; and exposes them through open
standards (**STAC**, **Zarr over HTTP**, **openEO**). It runs independently of DHIS2 and
can be deployed on local, cloud, or sovereign national infrastructure. It is designed to
replace Google Earth Engine for DHIS2 Maps and Climate workflows.

There are two sides to it, and these examples mostly use the first:

- **The client** — a lightweight Python package (`open-climate-service`) and plain REST
  that talk to a running instance over HTTP: discover datasets, open them as xarray, run
  processing, trigger ingestion. This is what almost every example here uses.
- **The server** — the full instance that does the downloading and serving. You only need
  it to run your own instance (or, here, to run the end-to-end tests, which boot one).

---

## Core concepts

| Concept | What it means |
| --- | --- |
| **Instance** | One deployment, scoped to a single region. Serves a REST API (default `http://127.0.0.1:8000`). |
| **Extent** | The instance's single named bounding box (`GET /extent`). Everything is clipped to it. |
| **Dataset template** | A blueprint for a source (CHIRPS, ERA5-Land, WorldPop, ...) describing how to download and build it. Listed at `GET /dataset-templates`. Templates are not data yet. |
| **Managed dataset / artifact** | A template that has been *ingested* for the extent over a time range. Listed at `GET /datasets` and, once published, in the STAC catalog. |
| **Ingestion** | Downloading a template for the extent and time range and building its store (`POST /ingestions`). |
| **Sync** | Advancing an existing managed dataset forward in time as new upstream data appears (`POST /sync/{id}`). |
| **GeoZarr** | The storage format: chunked, cloud-optimised Zarr v3 with geospatial metadata, served chunk-by-chunk over HTTP — no special tile server. |
| **Publishing** | Making a managed dataset visible in the STAC catalog and openEO collections so clients can find it. |

Open standards the instance exposes:

- **STAC** — dataset discovery (`/stac/catalog.json`, `/stac/collections/{id}`).
- **Zarr / GeoZarr over HTTP** — read the raw arrays (`/zarr/{id}`), or the versioned
  **Icechunk** store (`/icechunk/{id}`).
- **openEO** — a processing API: a catalogue of processes (`/processes`), synchronous
  execution (`POST /result`), batch jobs (`/jobs`), and stored user-defined processes
  (`/process_graphs`).

---

## Built-in data providers

Every instance ships these templates. Credentials, where needed, are configured on the
**server** (see [Data-source credentials](#data-source-credentials)).

| Provider | Template id(s) | Variable / units | Period | Resolution | Credentials |
| --- | --- | --- | --- | --- | --- |
| **CHIRPS v3** (precipitation) | `chirps3_precipitation_daily` | `precip` / mm | daily | ~5 km, 50°S–50°N | none (public) |
| **ERA5-Land** (Copernicus, monthly) | `era5land_temperature_monthly`, `era5land_precipitation_monthly` | `t2m` / °C, `tp` / mm | monthly | ~9 km, global | Copernicus CDS |
| **ERA5-Land** (daily, pre-computed) | `era5land_temperature_daily`, `era5land_precipitation_daily` | `t2m` / °C, `tp` / mm | daily (UTC) | ~9 km, global | DestinE Earth Data Hub |
| **ERA5-Land** (daily, timezone-aware) | `era5land_temperature_daily_from_hourly`, `era5land_precipitation_daily_from_hourly` | `t2m` / °C, `tp` / mm | daily (local) | ~9 km, global | DestinE Earth Data Hub |
| **WorldPop Global2** (population) | `worldpop_population_yearly`, `worldpop_population_change` | `pop_total` / people | yearly | ~100 m, global | none, but needs `country_code` |

- **CHIRPS v3** merges satellite infrared with station data; widely used for drought and
  food-security monitoring. Keyless, so it is the default for the quick start and tests.
- **ERA5-Land** is ECMWF's land-surface reanalysis (1950–present). Monthly comes from the
  Copernicus CDS; daily/hourly come from the DestinE Earth Data Hub. Temperature is
  converted to °C and precipitation to mm by the server.
- **WorldPop Global2** is gridded population at 100 m (estimates through the present,
  projections to 2030). It needs the extent's ISO `country_code`.

Two built-in **workflows** (stored openEO processes) turn any of these into import-ready
output:

- `aggregate_to_dhis2_json` — spatially aggregate over org-unit polygons into a DHIS2
  `dataValueSet`.
- `aggregate_to_chap_csv` — aggregate into the wide CSV the CHAP platform expects.

---

## Requirements

- Python 3.13+ and [uv](https://docs.astral.sh/uv/)
- A running Open Climate Service instance. To start one locally, see the upstream [quick
  start](https://dhis2.github.io/open-climate-service/setup_guide/). Most examples also
  need at least one **published** dataset — run an ingestion example first (group 04), use
  the instance's `/manage` web page, or run the e2e suite, which ingests one for you.

---

## Install

```bash
make install        # uv sync --all-extras (client + xarray + openeo + dhis2)
```

The base install pulls `open-climate-service[xarray]`, so every data-access example can
open published datasets as xarray objects. The `openeo` and `dhis2` extras back the
examples in `examples/03_openeo` and `examples/05_dhis2`.

To also run the end-to-end suite (which boots a real instance), install the server stack:

```bash
make install-e2e    # uv sync --all-extras --group e2e
```

> This repo resolves `open-climate-service` from the sibling checkout at
> `../open-climate-service` and `dhis2-client` from git (see `[tool.uv.sources]` in
> `pyproject.toml`). Point these at a package index once the packages are published there.

---

## Configure

Every example reads its connection details from the environment (or a `.env` file) via
`ocs_examples.config.Settings`. Defaults target `http://127.0.0.1:8000`.

```bash
cp .env.example .env     # then edit if your instance or DHIS2 differ
```

| Variable | Default | Used by |
| --- | --- | --- |
| `OCS_BASE_URL` | `http://127.0.0.1:8000` | all examples |
| `OCS_TIMEOUT` | `30` | all examples |
| `OCS_DHIS2_BASE_URL` | DHIS2 climate demo | `examples/05_dhis2` |
| `OCS_DHIS2_USERNAME` / `OCS_DHIS2_PASSWORD` | `admin` / `district` | `examples/05_dhis2` |

Server-side data-source keys (CDS, Earth Data Hub) are separate — see
[Data-source credentials](#data-source-credentials).

---

## Quick start

```bash
# 1. Confirm the instance is up and see how it's configured
uv run python examples/01_discovery/server_info.py
uv run python examples/01_discovery/show_extent.py

# 2. If nothing is published yet, ingest a few days of CHIRPS (keyless)
uv run python examples/04_ingestion/ingest_dataset.py

# 3. Discover and open it
uv run python examples/01_discovery/list_datasets.py
uv run python examples/02_data_access/open_with_xarray.py
```

---

## The examples, step by step

27 scripts in six groups. Each is independently runnable, prints what it does, and guards
gracefully when nothing is published. Run any of them with `uv run python <path>`.

### 01_discovery — find out what an instance offers

| Script | What it does |
| --- | --- |
| `list_datasets.py` | `service.datasets()` — the published datasets, read from the STAC catalog. |
| `show_extent.py` | `GET /extent` — the instance's configured bounding box. |
| `list_dataset_templates.py` | `GET /dataset-templates` — the blueprints you can ingest. |
| `list_processes.py` | `service.processes()` — the openEO process catalogue. |
| `list_workflows.py` | `service.workflows()` — stored workflows / user-defined processes. |
| `server_info.py` | `/health`, `/info`, `/.well-known/openeo` — liveness, version, openEO versions. |

### 02_data_access — read the data

These open a published dataset as a lazy `xarray.Dataset`; only the chunks you touch are
fetched over HTTP. (Need the `[xarray]` extra, installed by default.)

| Script | What it does |
| --- | --- |
| `open_with_xarray.py` | Open the first published dataset and summarise dims, variables, and extent. |
| `zarr_subsetting.py` | Select a single time step and a spatial window without downloading everything. |
| `point_time_series.py` | Read the time series for the grid cell nearest a lon/lat (a point query). |
| `spatial_mean.py` | Compute a domain-wide area-average time series. |
| `export_netcdf.py` | Download a time-trimmed subset to a local NetCDF file (sanitising GeoZarr attributes NetCDF can't represent). |
| `icechunk_direct.py` | Open the native, versioned Icechunk store at `/icechunk/{id}`. |

### 03_openeo — process the data

| Script | What it does | Needs |
| --- | --- | --- |
| `openeo_connect.py` | Connect with the openEO Python client and list collections. | `openeo` extra |
| `openeo_batch_job.py` | `load_collection` -> `apply` -> `max_time`, submitted as a batch job; prints result assets. | `openeo` extra |
| `sync_result_raw_graph.py` | Build a typed `load -> save_result` graph and run it synchronously (`POST /result`) — no openEO client needed. | — |
| `save_result_formats.py` | Export the same subset as NetCDF, GeoTIFF, and Zarr. | — |
| `store_and_run_udp.py` | Store a parameterised user-defined process (`PUT /process_graphs/{id}`), then invoke it. | — |

### 04_ingestion — get data into an instance

| Script | What it does |
| --- | --- |
| `ingest_dataset.py` | `POST /ingestions` — download and publish a CHIRPS slice (synchronous). |
| `ingest_async_poll.py` | Same, with `Prefer: respond-async`, polling the job to completion. |
| `list_ingestions.py` | `GET /datasets` and `GET /ingestions` — what's held and the run history. |
| `sync_plan.py` | `GET /sync/{id}/plan` — preview the periods a sync would fetch (dry run). |
| `sync_forward.py` | `POST /sync/{id}` — advance a managed dataset forward with new upstream data. |

### 05_dhis2 — aggregate for DHIS2 and CHAP

| Script | What it does | Needs |
| --- | --- | --- |
| `aggregate_to_dhis2.py` | Fetch org-unit boundaries from DHIS2, run `aggregate_to_dhis2_json`, import the `dataValueSet` back. | `dhis2` extra + a DHIS2 instance |
| `aggregate_to_chap_csv.py` | Aggregate over the built-in sample polygons into CHAP CSV — no DHIS2 needed. | — |
| `preview_org_unit.py` | Aggregate over a single area and print the per-period values without importing (the "look before you import" workflow). | — |

### 06_http — no client, just HTTP

| Script | What it does |
| --- | --- |
| `raw_httpx_discovery.py` | Walk the STAC catalog and openEO collections with `httpx` alone. |
| `sync_result_curl_equivalent.py` | `POST /result` with the `{"process": {...}}` envelope — the Python form of the docs' curl example. |

---

## The shared helper package

`src/ocs_examples/` holds the building blocks the scripts reuse. Data types are
pydantic models and settings use pydantic-settings.

| Module | Provides |
| --- | --- |
| `config.py` | `Settings` (pydantic-settings) — `OCS_`-prefixed env + `.env`. |
| `connection.py` | Client factories: `climate_service()`, `http_client()`, `openeo_connection()`, `dhis2_client()`. |
| `models.py` | `ProcessGraph` / `ProcessNode` (validates exactly one result node), `SpatialExtent`, `TemporalExtent`, `AggregateToDhis2Args` / `AggregateToChapArgs`, and the `SaveFormat` / `AggregationMethod` enums. |
| `graphs.py` | Builders that assemble validated openEO process graphs from the models. |
| `discovery.py` | Pick the first published dataset and guard an empty catalog. |
| `geometry.py` | A small sample GeoJSON FeatureCollection (ids mimic DHIS2 UIDs) for the keyless aggregation examples. |
| `console.py` | Section headers and JSON pretty-printing. |

---

## End-to-end tests

The e2e suite boots a **real** instance in-process (uvicorn on an ephemeral port), ingests
a small dataset over the network, and then exercises the flow — including running a
curated set of the example scripts as real subprocesses against the live instance.

```bash
make install-e2e          # full server stack (uv sync --group e2e)
make test-e2e             # uv run pytest -m e2e
```

- `tests/e2e/test_flow.py` — health, discovery, open with xarray, aggregate to CHAP CSV.
- `tests/e2e/test_examples_run.py` — runs ~17 example scripts and asserts each exits 0.
- `tests/e2e/test_era5_cds.py` — ERA5-Land ingestion via the CDS; **skips** when no CDS
  credentials are configured.

The default keyless path ingests a 3-day CHIRPS slice over a small Rwanda extent (a few
hundred kB). The ERA5 test additionally needs Copernicus CDS credentials.

---

## Data-source credentials

Downloads happen **server-side** during ingestion, so credentials belong to the
environment that runs the instance (including the e2e tests, which boot one and load
`.env` on startup). Set them only for the datasets you ingest:

| Dataset | Credentials |
| --- | --- |
| CHIRPS (`chirps3_precipitation_daily`) | none — public HTTP |
| WorldPop (`worldpop_population_yearly`) | none, but the extent needs `country_code` |
| ERA5-Land monthly (Copernicus CDS) | `ECMWF_DATASTORES_URL` / `ECMWF_DATASTORES_KEY` (or `~/.ecmwfdatastoresrc` with `url:` / `key:`) |
| ERA5-Land daily / `*_from_hourly` (DestinE Earth Data Hub) | `EDH_API_KEY` (or `~/.netrc` for `api.earthdatahub.destine.eu`) |

The CDS URL/key are your [CDS personal access
token](https://cds.climate.copernicus.eu/). The Earth Data Hub key comes from
[earthdatahub.destine.eu](https://earthdatahub.destine.eu) (Account settings -> API keys).
See `.env.example` for the full list.

---

## Develop

```bash
make lint     # ruff format + ruff check + mypy + pyright
make test     # pytest, offline unit tests for the shared helpers (excludes e2e)
make clean    # remove caches and build artifacts
```

---

## Project layout

```
open-climate-service-examples/
├── examples/
│   ├── 01_discovery/        find out what an instance offers
│   ├── 02_data_access/      read data (xarray, zarr, icechunk)
│   ├── 03_openeo/           process data (openEO)
│   ├── 04_ingestion/        get data into an instance
│   ├── 05_dhis2/            aggregate for DHIS2 and CHAP
│   └── 06_http/             no client, just HTTP
├── src/ocs_examples/        shared helpers (pydantic models, settings, factories)
├── tests/
│   ├── test_models.py       offline unit tests
│   ├── test_settings.py
│   └── e2e/                 end-to-end suite (boots a real instance)
├── .env.example
├── Makefile
└── pyproject.toml
```

## License

BSD-3-Clause.
