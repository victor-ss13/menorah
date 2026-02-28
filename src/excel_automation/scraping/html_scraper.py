"""Scraping HTML como fallback quando a API não está disponível."""

import logging
from typing import Any

import requests
from bs4 import BeautifulSoup
from requests.exceptions import RequestException

logger = logging.getLogger(__name__)


class HTMLScraper:
    """Extrai dados de páginas HTML quando a API não está disponível.

    Deve ser utilizado **somente** como fallback para :class:`~excel_automation.api.client.APIClient`.
    """

    def __init__(self, timeout: int = 30) -> None:
        """Inicializa o scraper.

        Args:
            timeout: Timeout em segundos para cada requisição HTTP.
        """
        self.timeout = timeout

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def fetch_page(self, url: str) -> BeautifulSoup:
        """Baixa uma página HTML e retorna um objeto :class:`BeautifulSoup`.

        Args:
            url: URL completa da página a ser baixada.

        Returns:
            Objeto :class:`BeautifulSoup` pronto para navegação.

        Raises:
            requests.RequestException: Em caso de erro de rede ou timeout.
        """
        logger.warning("Usando scraping como fallback para %s", url)
        try:
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            return BeautifulSoup(response.text, "html.parser")
        except RequestException as exc:
            logger.error("Erro ao acessar %s: %s", url, exc)
            raise

    def extract_table(
        self,
        soup: BeautifulSoup,
        table_index: int = 0,
    ) -> list[dict[str, Any]]:
        """Extrai a tabela HTML na posição ``table_index`` como lista de dicionários.

        Args:
            soup: Objeto :class:`BeautifulSoup` da página.
            table_index: Índice (0-based) da tabela a extrair.

        Returns:
            Lista de dicionários onde cada item representa uma linha da tabela.

        Raises:
            IndexError: Se não existir tabela no índice fornecido.
            ValueError: Se a tabela não possuir cabeçalho (``<th>``).
        """
        tables = soup.find_all("table")
        if table_index >= len(tables):
            raise IndexError(
                f"Tabela de índice {table_index} não encontrada. "
                f"Total de tabelas: {len(tables)}"
            )

        table = tables[table_index]
        headers = [th.get_text(strip=True) for th in table.find_all("th")]
        if not headers:
            raise ValueError("A tabela não possui cabeçalho (<th>).")

        rows: list[dict[str, Any]] = []
        for tr in table.find_all("tr"):
            cells = tr.find_all("td")
            if not cells:
                continue
            row = {
                headers[i]: cell.get_text(strip=True)
                for i, cell in enumerate(cells)
                if i < len(headers)
            }
            rows.append(row)

        logger.info("Extraídas %d linhas da tabela %d", len(rows), table_index)
        return rows
