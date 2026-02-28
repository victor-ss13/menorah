"""Testes unitários para api/client.py."""

from unittest.mock import MagicMock, patch

import pytest
import requests

from excel_automation.api.client import APIClient


def test_get_success():
    """GET bem-sucedido deve retornar o JSON desserializado."""
    mock_response = MagicMock()
    mock_response.json.return_value = [{"id": 1, "nome": "Test"}]
    mock_response.raise_for_status.return_value = None

    with patch("requests.Session.get", return_value=mock_response):
        client = APIClient("https://api.example.com")
        result = client.get("/v1/data")

    assert result == [{"id": 1, "nome": "Test"}]


def test_get_raises_on_http_error():
    """GET deve propagar HTTPError em caso de resposta de erro."""
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = requests.HTTPError("404")

    with patch("requests.Session.get", return_value=mock_response):
        client = APIClient("https://api.example.com")
        with pytest.raises(requests.HTTPError):
            client.get("/v1/data")


def test_post_success():
    """POST bem-sucedido deve retornar o JSON desserializado."""
    mock_response = MagicMock()
    mock_response.json.return_value = {"created": True}
    mock_response.raise_for_status.return_value = None

    with patch("requests.Session.post", return_value=mock_response):
        client = APIClient("https://api.example.com")
        result = client.post("/v1/data", payload={"nome": "Test"})

    assert result == {"created": True}


def test_context_manager():
    """APIClient deve funcionar como context manager."""
    with APIClient("https://api.example.com") as client:
        assert client is not None
