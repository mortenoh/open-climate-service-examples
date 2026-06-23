"""Tests for environment-driven settings."""

from __future__ import annotations

import pytest

from ocs_examples.config import Settings


def test_defaults_target_localhost() -> None:
    settings = Settings()
    assert settings.base_url_str == "http://127.0.0.1:8000"
    assert settings.timeout == 30.0


def test_env_prefix_overrides(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OCS_BASE_URL", "https://climate.example.org/")
    monkeypatch.setenv("OCS_TIMEOUT", "5")
    settings = Settings()
    assert settings.base_url_str == "https://climate.example.org"
    assert settings.timeout == 5.0


def test_timeout_must_be_positive(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OCS_TIMEOUT", "0")
    with pytest.raises(ValueError):
        Settings()
