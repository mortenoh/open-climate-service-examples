"""Runtime settings for the examples, sourced from the environment and an optional ``.env``.

All examples read their connection details from a single :class:`Settings` object so
that pointing them at a different instance is a one-line change (or an environment
variable) rather than an edit in every script.

Environment variables use the ``OCS_`` prefix, e.g. ``OCS_BASE_URL``. The Open Climate
Service client also honours ``CLIMATE_SERVICE_BASE_URL``; we mirror that default so the
two agree out of the box.
"""

from __future__ import annotations

from functools import lru_cache

from pydantic import Field, HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Connection settings shared by every example.

    Values are read from environment variables (prefixed ``OCS_``) and an optional
    ``.env`` file in the working directory. Defaults target a service running locally.
    """

    model_config = SettingsConfigDict(
        env_prefix="OCS_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    base_url: HttpUrl = Field(
        default=HttpUrl("http://127.0.0.1:8000"),
        description="Base URL of the running Open Climate Service instance.",
    )
    timeout: float = Field(
        default=30.0,
        gt=0,
        description="Default HTTP request timeout, in seconds.",
    )

    # --- DHIS2 (only needed by the examples under examples/05_dhis2) ---
    dhis2_base_url: HttpUrl = Field(
        default=HttpUrl("https://climate.im.dhis2.org/climate-tools-42"),
        description="Base URL of the target DHIS2 instance.",
    )
    dhis2_username: str = Field(default="admin", description="DHIS2 username.")
    dhis2_password: str = Field(default="district", description="DHIS2 password.")

    @property
    def base_url_str(self) -> str:
        """Return the service base URL as a plain string without a trailing slash."""
        return str(self.base_url).rstrip("/")

    @property
    def dhis2_base_url_str(self) -> str:
        """Return the DHIS2 base URL as a plain string without a trailing slash."""
        return str(self.dhis2_base_url).rstrip("/")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached :class:`Settings` instance."""
    return Settings()
