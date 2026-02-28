"""Testes unitários para logging_config/logger.py."""

import logging

from excel_automation.logging_config.logger import get_logger, setup_logging


def test_setup_logging_no_file(tmp_path):
    """setup_logging sem arquivo deve configurar apenas o handler de console."""
    setup_logging(log_level="DEBUG")
    root = logging.getLogger()
    assert root.level == logging.DEBUG
    assert any(
        isinstance(h, logging.StreamHandler) for h in root.handlers
    )


def test_setup_logging_with_file(tmp_path):
    """setup_logging com arquivo deve criar o arquivo de log."""
    log_file = tmp_path / "logs" / "test.log"
    setup_logging(log_level="INFO", log_file=log_file)
    assert log_file.exists()


def test_get_logger_returns_logger():
    """get_logger deve retornar um Logger com o nome correto."""
    logger = get_logger("test.module")
    assert isinstance(logger, logging.Logger)
    assert logger.name == "test.module"
