"""Orquestração do fluxo ETL principal (Extract → Transform → Load)."""

import logging
from pathlib import Path

import pandas as pd

from excel_automation.api.client import APIClient
from excel_automation.config.settings import Settings
from excel_automation.excel.reader import ExcelReader
from excel_automation.excel.transformer import DataTransformer
from excel_automation.excel.writer import ExcelWriter
from excel_automation.scraping.html_scraper import HTMLScraper

logger = logging.getLogger(__name__)


class Orchestrator:
    """Coordena o fluxo completo de ETL da aplicação.

    Fluxo:
    1. **Extract** – lê a planilha de entrada *e/ou* coleta dados externos.
    2. **Transform** – aplica as regras de padronização.
    3. **Load** – grava o Excel de saída formatado.
    """

    def __init__(
        self,
        settings: Settings,
        column_mapping: dict[str, str] | None = None,
    ) -> None:
        """Inicializa o orquestrador com as configurações da aplicação.

        Args:
            settings: Instância de :class:`~excel_automation.config.settings.Settings`.
            column_mapping: Mapeamento de colunas para o transformador.
        """
        self._settings = settings
        self._reader = ExcelReader()
        self._transformer = DataTransformer(column_mapping=column_mapping)
        self._writer = ExcelWriter()

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def run(
        self,
        input_file: Path | None = None,
        output_file: Path | None = None,
        api_path: str | None = None,
        scraping_url: str | None = None,
    ) -> Path:
        """Executa o pipeline ETL completo.

        Args:
            input_file: Caminho para a planilha de entrada. Se ``None``, o
                diretório de entrada configurado é varrido em busca do primeiro
                ``.xlsx``.
            output_file: Caminho de saída para o Excel gerado. Se ``None``,
                usa o diretório de saída configurado com o mesmo nome do arquivo
                de entrada.
            api_path: Caminho relativo na API para coleta de dados externos
                (ex.: ``"/v1/products"``). Opcional.
            scraping_url: URL para scraping como fallback. Usado somente se
                ``api_path`` for fornecido mas a API estiver indisponível.

        Returns:
            :class:`pathlib.Path` do arquivo Excel gerado.

        Raises:
            FileNotFoundError: Se não for encontrado nenhum arquivo de entrada.
        """
        frames: list[pd.DataFrame] = []

        # --- Extract: planilha local ---
        input_path = self._resolve_input(input_file)
        if input_path is not None:
            df_local = self._reader.read(input_path)
            frames.append(df_local)

        # --- Extract: dados externos ---
        if api_path:
            df_external = self._fetch_external(api_path, scraping_url)
            if df_external is not None:
                frames.append(df_external)

        if not frames:
            raise FileNotFoundError(
                "Nenhum dado disponível: verifique o arquivo de entrada "
                "e/ou a fonte de dados externos."
            )

        df_combined = pd.concat(frames, ignore_index=True) if len(frames) > 1 else frames[0]

        # --- Transform ---
        df_standard = self._transformer.transform(df_combined)

        # --- Load ---
        out_path = self._resolve_output(output_file, input_path)
        return self._writer.write(df_standard, out_path)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _resolve_input(self, input_file: Path | None) -> Path | None:
        if input_file is not None:
            return Path(input_file)
        candidates = list(self._settings.input_dir.glob("*.xlsx"))
        if candidates:
            return candidates[0]
        return None

    def _resolve_output(
        self,
        output_file: Path | None,
        input_path: Path | None,
    ) -> Path:
        if output_file is not None:
            return Path(output_file)
        stem = input_path.stem if input_path else "output"
        return self._settings.output_dir / f"{stem}_padronizado.xlsx"

    def _fetch_external(
        self, api_path: str, scraping_url: str | None
    ) -> pd.DataFrame | None:
        """Tenta buscar dados via API; usa scraping como fallback."""
        # Tentativa via API
        try:
            client = APIClient(
                self._settings.api_base_url, timeout=self._settings.api_timeout
            )
            with client:
                data = client.get(api_path)
            if isinstance(data, list):
                return pd.DataFrame(data)
            if isinstance(data, dict):
                return pd.DataFrame([data])
            logger.warning("Formato de resposta da API não reconhecido.")
        except Exception as exc:  # noqa: BLE001
            logger.warning("API indisponível (%s). Tentando scraping...", exc)

        # Fallback via scraping
        if scraping_url:
            try:
                scraper = HTMLScraper(timeout=self._settings.api_timeout)
                soup = scraper.fetch_page(scraping_url)
                rows = scraper.extract_table(soup)
                return pd.DataFrame(rows)
            except Exception as exc:  # noqa: BLE001
                logger.error("Falha no scraping de %s: %s", scraping_url, exc)

        return None
