"""Entrada da aplicação – CLI construída com Typer."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

import typer

from excel_automation.config.settings import get_settings
from excel_automation.core.orchestrator import Orchestrator
from excel_automation.logging_config.logger import setup_logging

app = typer.Typer(
    name="excel-automation",
    help="Automação de tratamento e padronização de planilhas Excel.",
    add_completion=False,
)


@app.command()
def process(
    input_file: Optional[Path] = typer.Option(
        None,
        "--input",
        "-i",
        help="Caminho para a planilha de entrada (.xlsx). "
        "Se omitido, usa o diretório INPUT_DIR configurado no .env.",
        exists=False,
        dir_okay=False,
    ),
    output_file: Optional[Path] = typer.Option(
        None,
        "--output",
        "-o",
        help="Caminho para o arquivo de saída (.xlsx). "
        "Se omitido, usa o diretório OUTPUT_DIR configurado no .env.",
        dir_okay=False,
    ),
    api_path: Optional[str] = typer.Option(
        None,
        "--api-path",
        help="Caminho relativo na API externa para coleta de dados "
        "(ex.: /v1/products). Opcional.",
    ),
    scraping_url: Optional[str] = typer.Option(
        None,
        "--scraping-url",
        help="URL para scraping HTML como fallback da API. "
        "Usado somente se --api-path for fornecido.",
    ),
    log_level: Optional[str] = typer.Option(
        None,
        "--log-level",
        help="Nível de log (DEBUG, INFO, WARNING, ERROR). "
        "Sobrepõe o valor do .env.",
    ),
) -> None:
    """Processa planilhas Excel: lê, transforma e gera o arquivo padronizado."""
    settings = get_settings()

    effective_log_level = log_level.upper() if log_level else settings.log_level
    setup_logging(log_level=effective_log_level, log_file=settings.log_file)

    logger = logging.getLogger(__name__)
    logger.info("Iniciando excel-automation")

    try:
        orchestrator = Orchestrator(settings=settings)
        result = orchestrator.run(
            input_file=input_file,
            output_file=output_file,
            api_path=api_path,
            scraping_url=scraping_url,
        )
        typer.echo(f"✅ Arquivo gerado com sucesso: {result}")
    except FileNotFoundError as exc:
        logger.error("Arquivo não encontrado: %s", exc)
        typer.echo(f"❌ Erro: {exc}", err=True)
        raise typer.Exit(code=1) from exc
    except Exception as exc:
        logger.error("Erro inesperado: %s", exc, exc_info=True)
        typer.echo(f"❌ Erro inesperado: {exc}", err=True)
        raise typer.Exit(code=1) from exc


def main() -> None:
    """Ponto de entrada para empacotamento como executável."""
    app()


if __name__ == "__main__":
    main()
