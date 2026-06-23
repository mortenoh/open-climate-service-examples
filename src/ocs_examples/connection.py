"""Factory helpers that build connected clients from the shared :class:`Settings`.

Centralising construction means every example opens its connections the same way and
honours the same environment configuration, and that swapping in a different instance
URL is a single environment variable.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import httpx
from open_climate_service import ClimateService

from ocs_examples.config import Settings, get_settings

if TYPE_CHECKING:
    import openeo
    from dhis2_client import DHIS2Client


def climate_service(settings: Settings | None = None) -> ClimateService:
    """Return an Open Climate Service client pointed at the configured instance."""
    settings = settings or get_settings()
    return ClimateService(settings.base_url_str, timeout=settings.timeout)


def http_client(settings: Settings | None = None) -> httpx.Client:
    """Return an ``httpx.Client`` with ``base_url`` set to the configured instance.

    Use this for the REST endpoints the typed client does not wrap (``/extent``,
    ``/datasets``, ``/ingestions``, ``/sync``, ...).
    """
    settings = settings or get_settings()
    # follow_redirects: several endpoints (e.g. /dataset-templates) 307-redirect to
    # their trailing-slash form, which httpx would otherwise not follow.
    return httpx.Client(base_url=settings.base_url_str, timeout=settings.timeout, follow_redirects=True)


def openeo_connection(settings: Settings | None = None) -> openeo.Connection:
    """Return an authenticated-free openEO connection to the configured instance.

    Requires the ``openeo`` extra: ``uv sync --extra openeo``.
    """
    import openeo

    settings = settings or get_settings()
    return openeo.connect(settings.base_url_str)


def dhis2_client(settings: Settings | None = None) -> DHIS2Client:
    """Return a DHIS2 Web API client built from the configured DHIS2 credentials.

    Requires the ``dhis2`` extra: ``uv sync --extra dhis2``.
    """
    from dhis2_client import DHIS2Client
    from dhis2_client.settings import ClientSettings

    settings = settings or get_settings()
    return DHIS2Client(
        settings=ClientSettings(
            base_url=settings.dhis2_base_url_str,
            username=settings.dhis2_username,
            password=settings.dhis2_password,
        )
    )
