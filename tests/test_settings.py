"""Testes unitários para config/settings.py."""

import os

import pytest

from excel_automation.config.settings import Settings, get_settings


def test_settings_defaults():
    """Settings deve ter valores padrão razoáveis sem variáveis de ambiente."""
    s = Settings()
    assert s.api_timeout > 0
    assert s.log_level in ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")


def test_settings_from_env(monkeypatch: pytest.MonkeyPatch):
    """Settings deve ler valores das variáveis de ambiente."""
    monkeypatch.setenv("API_BASE_URL", "https://test.example.com")
    monkeypatch.setenv("API_TIMEOUT", "60")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")

    s = Settings()
    assert s.api_base_url == "https://test.example.com"
    assert s.api_timeout == 60
    assert s.log_level == "DEBUG"


def test_get_settings_returns_settings():
    """get_settings() deve retornar uma instância de Settings."""
    s = get_settings()
    assert isinstance(s, Settings)
