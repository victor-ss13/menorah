"""Testes unitários para core/orchestrator.py."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from excel_automation.config.settings import Settings
from excel_automation.core.orchestrator import Orchestrator
from excel_automation.excel.transformer import STANDARD_COLUMNS


def _standard_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "id": [1],
            "nome": ["Test"],
            "valor": [99.0],
            "data": ["2024-01-01"],
            "status": ["ativo"],
        }
    )


def test_run_with_input_file(tmp_path):
    """run deve processar um arquivo de entrada e gerar o arquivo de saída."""
    from excel_automation.excel.writer import ExcelWriter

    # Cria planilha de entrada
    input_file = tmp_path / "input.xlsx"
    ExcelWriter().write(_standard_df(), input_file)

    output_file = tmp_path / "output.xlsx"
    settings = Settings()
    settings.input_dir = tmp_path
    settings.output_dir = tmp_path

    orch = Orchestrator(settings=settings)
    result = orch.run(input_file=input_file, output_file=output_file)

    assert result == output_file
    assert output_file.exists()


def test_run_raises_when_no_input(tmp_path):
    """run deve lançar FileNotFoundError se não houver dados disponíveis."""
    settings = Settings()
    settings.input_dir = tmp_path  # diretório vazio
    settings.output_dir = tmp_path

    orch = Orchestrator(settings=settings)
    with pytest.raises(FileNotFoundError):
        orch.run()


def test_run_uses_first_xlsx_in_input_dir(tmp_path):
    """run sem input_file explícito deve usar o primeiro .xlsx do input_dir."""
    from excel_automation.excel.writer import ExcelWriter

    first = tmp_path / "first.xlsx"
    ExcelWriter().write(_standard_df(), first)

    settings = Settings()
    settings.input_dir = tmp_path
    settings.output_dir = tmp_path

    orch = Orchestrator(settings=settings)
    result = orch.run()
    assert result.exists()
