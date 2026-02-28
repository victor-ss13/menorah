"""Leitura e validação de configurações a partir do arquivo .env."""

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


@dataclass
class Settings:
    """Configurações centralizadas da aplicação, lidas do arquivo .env."""

    api_base_url: str = field(
        default_factory=lambda: os.getenv("API_BASE_URL", "https://api.example.com")
    )
    api_timeout: int = field(
        default_factory=lambda: int(os.getenv("API_TIMEOUT", "30"))
    )
    input_dir: Path = field(
        default_factory=lambda: Path(os.getenv("INPUT_DIR", "data/input"))
    )
    output_dir: Path = field(
        default_factory=lambda: Path(os.getenv("OUTPUT_DIR", "data/output"))
    )
    log_level: str = field(
        default_factory=lambda: os.getenv("LOG_LEVEL", "INFO").upper()
    )
    log_file: Path = field(
        default_factory=lambda: Path(
            os.getenv("LOG_FILE", "logs/excel_automation.log")
        )
    )


def get_settings() -> Settings:
    """Retorna uma instância de Settings com os valores lidos do ambiente."""
    return Settings()
