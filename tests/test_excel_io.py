"""Testes unitários para excel/reader.py e excel/writer.py."""

import pandas as pd
import pytest

from excel_automation.excel.reader import ExcelReader
from excel_automation.excel.transformer import STANDARD_COLUMNS
from excel_automation.excel.writer import ExcelWriter


def _make_standard_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "id": [1, 2, 3],
            "nome": ["Alpha", "Beta", "Gamma"],
            "valor": [100.0, 200.0, 300.0],
            "data": ["2024-01-01", "2024-01-02", "2024-01-03"],
            "status": ["ativo", "inativo", "ativo"],
        }
    )


class TestExcelWriter:
    def test_write_creates_file(self, tmp_path):
        df = _make_standard_df()
        out = tmp_path / "output.xlsx"
        writer = ExcelWriter()
        result = writer.write(df, out)
        assert result == out
        assert out.exists()

    def test_write_creates_parent_dirs(self, tmp_path):
        df = _make_standard_df()
        out = tmp_path / "nested" / "dir" / "output.xlsx"
        ExcelWriter().write(df, out)
        assert out.exists()

    def test_write_empty_dataframe(self, tmp_path):
        df = pd.DataFrame(columns=STANDARD_COLUMNS)
        out = tmp_path / "empty.xlsx"
        ExcelWriter().write(df, out)
        assert out.exists()


class TestExcelReader:
    def test_read_raises_if_file_missing(self, tmp_path):
        reader = ExcelReader()
        with pytest.raises(FileNotFoundError):
            reader.read(tmp_path / "nonexistent.xlsx")

    def test_round_trip(self, tmp_path):
        """Escreve e relê um arquivo Excel verificando os dados."""
        df_original = _make_standard_df()
        out = tmp_path / "round_trip.xlsx"
        ExcelWriter().write(df_original, out)

        df_read = ExcelReader().read(out)
        assert list(df_read.columns) == STANDARD_COLUMNS
        assert len(df_read) == len(df_original)
