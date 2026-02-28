"""Configuração centralizada de logging com suporte a arquivo e console."""

import logging
import logging.handlers
from pathlib import Path


def setup_logging(log_level: str = "INFO", log_file: Path | None = None) -> None:
    """Configura o sistema de logging da aplicação.

    Args:
        log_level: Nível de log (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        log_file: Caminho para o arquivo de log. Se None, apenas o console é usado.
    """
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    fmt = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    date_fmt = "%Y-%m-%d %H:%M:%S"
    formatter = logging.Formatter(fmt=fmt, datefmt=date_fmt)

    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)

    # Remove handlers previously attached to avoid duplicates on repeated calls.
    root_logger.handlers.clear()

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # File handler (rotativo para não crescer indefinidamente)
    if log_file is not None:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=5 * 1024 * 1024,  # 5 MB
            backupCount=3,
            encoding="utf-8",
        )
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)


def get_logger(name: str) -> logging.Logger:
    """Retorna um logger com o nome fornecido.

    Args:
        name: Nome do logger (normalmente ``__name__``).

    Returns:
        Instância de :class:`logging.Logger`.
    """
    return logging.getLogger(name)
