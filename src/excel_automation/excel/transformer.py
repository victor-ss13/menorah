"""Transformação e validação de DataFrames para o modelo padrão."""

import logging
from typing import Any

import pandas as pd

logger = logging.getLogger(__name__)

# Colunas obrigatórias do modelo padrão exigido pelo sistema terceiro.
STANDARD_COLUMNS: list[str] = [
    "id",
    "nome",
    "valor",
    "data",
    "status",
]


class DataTransformer:
    """Transforma um :class:`pandas.DataFrame` heterogêneo para o modelo padrão."""

    def __init__(self, column_mapping: dict[str, str] | None = None) -> None:
        """Inicializa o transformador.

        Args:
            column_mapping: Mapeamento ``{coluna_origem: coluna_destino}`` para
                renomear colunas do DataFrame de entrada.
        """
        self.column_mapping: dict[str, str] = column_mapping or {}

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Aplica todas as transformações e retorna o DataFrame padronizado.

        Passos executados:
        1. Renomear colunas conforme ``column_mapping``.
        2. Remover duplicatas.
        3. Preencher valores nulos com strings vazias / 0.
        4. Garantir que as colunas do modelo padrão estejam presentes.
        5. Retornar apenas as colunas do modelo padrão.

        Args:
            df: DataFrame de entrada (possivelmente heterogêneo).

        Returns:
            DataFrame padronizado com exatamente as colunas de :data:`STANDARD_COLUMNS`.
        """
        logger.info("Iniciando transformação de %d linhas", len(df))
        df = df.copy()
        df = self._rename_columns(df)
        df = self._drop_duplicates(df)
        df = self._fill_nulls(df)
        df = self._ensure_standard_columns(df)
        df = df[STANDARD_COLUMNS]
        logger.info("Transformação concluída: %d linhas resultantes", len(df))
        return df

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _rename_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        if self.column_mapping:
            df = df.rename(columns=self.column_mapping)
            logger.debug("Colunas renomeadas: %s", self.column_mapping)
        return df

    def _drop_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        before = len(df)
        df = df.drop_duplicates()
        removed = before - len(df)
        if removed:
            logger.warning("Removidas %d linhas duplicadas", removed)
        return df

    def _fill_nulls(self, df: pd.DataFrame) -> pd.DataFrame:
        fill_values: dict[str, Any] = {}
        for col in df.columns:
            if pd.api.types.is_numeric_dtype(df[col]):
                fill_values[col] = 0
            else:
                fill_values[col] = ""
        return df.fillna(fill_values)

    def _ensure_standard_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        for col in STANDARD_COLUMNS:
            if col not in df.columns:
                logger.warning("Coluna ausente '%s' criada com valor padrão", col)
                df[col] = 0 if pd.api.types.is_numeric_dtype(
                    df.get(col, pd.Series(dtype="object"))
                ) else ""
        return df
