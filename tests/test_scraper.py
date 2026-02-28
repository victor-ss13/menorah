"""Testes unitários para scraping/html_scraper.py."""

from unittest.mock import MagicMock, patch

import pytest
import requests
from bs4 import BeautifulSoup

from excel_automation.scraping.html_scraper import HTMLScraper

SIMPLE_HTML = """
<html><body>
<table>
  <tr><th>id</th><th>nome</th></tr>
  <tr><td>1</td><td>Alpha</td></tr>
  <tr><td>2</td><td>Beta</td></tr>
</table>
</body></html>
"""


def test_fetch_page_returns_soup():
    """fetch_page deve retornar um objeto BeautifulSoup."""
    mock_response = MagicMock()
    mock_response.text = SIMPLE_HTML
    mock_response.raise_for_status.return_value = None

    with patch("requests.get", return_value=mock_response):
        scraper = HTMLScraper()
        soup = scraper.fetch_page("https://example.com")

    assert isinstance(soup, BeautifulSoup)


def test_extract_table_returns_rows():
    """extract_table deve retornar lista de dicionários com as linhas da tabela."""
    soup = BeautifulSoup(SIMPLE_HTML, "html.parser")
    scraper = HTMLScraper()
    rows = scraper.extract_table(soup)

    assert len(rows) == 2
    assert rows[0] == {"id": "1", "nome": "Alpha"}
    assert rows[1] == {"id": "2", "nome": "Beta"}


def test_extract_table_raises_on_missing_table():
    """extract_table deve lançar IndexError se não houver tabela no índice."""
    soup = BeautifulSoup("<html><body></body></html>", "html.parser")
    scraper = HTMLScraper()
    with pytest.raises(IndexError):
        scraper.extract_table(soup)


def test_extract_table_raises_on_missing_header():
    """extract_table deve lançar ValueError se não houver <th>."""
    html = "<html><body><table><tr><td>1</td></tr></table></body></html>"
    soup = BeautifulSoup(html, "html.parser")
    scraper = HTMLScraper()
    with pytest.raises(ValueError):
        scraper.extract_table(soup)


def test_fetch_page_raises_on_network_error():
    """fetch_page deve propagar RequestException em caso de falha de rede."""
    with patch("requests.get", side_effect=requests.ConnectionError("offline")):
        scraper = HTMLScraper()
        with pytest.raises(requests.ConnectionError):
            scraper.fetch_page("https://offline.example.com")
