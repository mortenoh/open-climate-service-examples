"""Run a curated set of example scripts against the live instance, as real subprocesses.

This is the strongest guarantee the examples work: each script is executed exactly as a
user would run it (``python examples/.../foo.py``), with ``OCS_BASE_URL`` pointing at the
booted instance, and must exit 0. Scripts needing external services (DHIS2) or heavy
batch compute are covered elsewhere and excluded here.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.e2e

# Read-only / aggregation scripts that work with a single CHIRPS dataset and no
# external credentials. Paths are relative to the repo root.
CURATED = [
    "examples/01_discovery/list_datasets.py",
    "examples/01_discovery/show_extent.py",
    "examples/01_discovery/list_dataset_templates.py",
    "examples/01_discovery/list_processes.py",
    "examples/01_discovery/list_workflows.py",
    "examples/01_discovery/server_info.py",
    "examples/02_data_access/open_with_xarray.py",
    "examples/02_data_access/zarr_subsetting.py",
    "examples/02_data_access/point_time_series.py",
    "examples/02_data_access/spatial_mean.py",
    "examples/02_data_access/export_netcdf.py",
    "examples/03_openeo/openeo_connect.py",
    "examples/03_openeo/sync_result_raw_graph.py",
    "examples/05_dhis2/aggregate_to_chap_csv.py",
    "examples/05_dhis2/preview_org_unit.py",
    "examples/06_http/raw_httpx_discovery.py",
    "examples/06_http/sync_result_curl_equivalent.py",
]


@pytest.mark.parametrize("script", CURATED, ids=lambda s: Path(s).stem)
def test_example_script_runs(script: str, base_url: str, ingested_dataset: str, repo_root: Path) -> None:
    env = dict(os.environ, OCS_BASE_URL=base_url)
    result = subprocess.run(
        [sys.executable, str(repo_root / script)],
        cwd=repo_root,
        env=env,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert result.returncode == 0, f"{script} failed:\nSTDOUT\n{result.stdout}\nSTDERR\n{result.stderr}"
