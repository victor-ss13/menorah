"""Leitura de planilhas Excel heterogêneas com pandas."""

import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)


class ExcelReader:
    """Lê planilhas Excel e retorna um :class:`pandas.DataFrame`."""

    def read(
        self,
        file_path: Path | str,
        sheet_name: str | int = 0,
        header: int = 0,
        skiprows: int | None = None,
    ) -> pd.DataFrame:
        """Lê um arquivo Excel e retorna seu conteúdo como DataFrame.

        Args:
            file_path: Caminho para o arquivo ``.xlsx`` ou ``.xls``.
            sheet_name: Nome ou índice da aba a ler (padrão: primeira aba).
            header: Linha usada como cabeçalho (0-indexed).
            skiprows: Número de linhas a ignorar antes do cabeçalho.

        Returns:
            :class:`pandas.DataFrame` com os dados lidos.

        Raises:
            FileNotFoundError: Se ``file_path`` não existir.
            ValueError: Se o arquivo não for um Excel válido.
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")

        logger.info("Lendo planilha: %s (aba=%s)", file_path, sheet_name)
        try:
            df: pd.DataFrame = pd.read_excel(
                file_path,
                sheet_name=sheet_name,
                header=header,
                skiprows=skiprows,
                engine="openpyxl",
            )
        except Exception as exc:
            logger.error("Falha ao ler %s: %s", file_path, exc)
            raise ValueError(f"Não foi possível ler o arquivo Excel: {exc}") from exc

        logger.info("Lidas %d linhas e %d colunas", len(df), len(df.columns))
        return df
