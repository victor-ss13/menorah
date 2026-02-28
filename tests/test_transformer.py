"""Testes unitários para excel/transformer.py."""

import pandas as pd
import pytest

from excel_automation.excel.transformer import STANDARD_COLUMNS, DataTransformer


def _make_df(**kwargs) -> pd.DataFrame:
    defaults = {
        "id": [1, 2],
        "nome": ["Alice", "Bob"],
        "valor": [10.0, 20.0],
        "data": ["2024-01-01", "2024-01-02"],
        "status": ["ativo", "inativo"],
    }
    defaults.update(kwargs)
    return pd.DataFrame(defaults)


def test_transform_returns_standard_columns():
    """O resultado deve conter exatamente as colunas do modelo padrão."""
    df = _make_df()
    result = DataTransformer().transform(df)
    assert list(result.columns) == STANDARD_COLUMNS


def test_transform_drops_duplicates():
    """Linhas duplicadas devem ser removidas."""
    df = _make_df(
        id=[1, 1],
        nome=["Alice", "Alice"],
        valor=[10.0, 10.0],
        data=["2024-01-01", "2024-01-01"],
        status=["ativo", "ativo"],
    )
    result = DataTransformer().transform(df)
    assert len(result) == 1


def test_transform_fills_nulls():
    """Valores nulos devem ser substituídos por 0 (numérico) ou '' (texto)."""
    df = _make_df(nome=[None, "Bob"], valor=[None, 20.0])
    result = DataTransformer().transform(df)
    assert result["nome"].iloc[0] == ""
    assert result["valor"].iloc[0] == 0


def test_transform_adds_missing_columns():
    """Colunas ausentes devem ser criadas com valor padrão."""
    df = pd.DataFrame({"id": [1], "nome": ["Alice"]})
    result = DataTransformer().transform(df)
    assert "valor" in result.columns
    assert "status" in result.columns


def test_column_mapping():
    """column_mapping deve renomear colunas antes da transformação."""
    df = pd.DataFrame(
        {
            "codigo": [1],
            "descricao": ["Item A"],
            "preco": [9.99],
            "criado_em": ["2024-01-01"],
            "situacao": ["ok"],
        }
    )
    mapping = {
        "codigo": "id",
        "descricao": "nome",
        "preco": "valor",
        "criado_em": "data",
        "situacao": "status",
    }
    result = DataTransformer(column_mapping=mapping).transform(df)
    assert list(result.columns) == STANDARD_COLUMNS
