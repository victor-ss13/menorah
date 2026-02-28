# menorah – Excel Automation

Aplicação Python para automação de tratamento e padronização de planilhas Excel,
com execução via linha de comando e possibilidade de agendamento pelo Agendador de
Tarefas do Windows.

## Funcionalidades

- Leitura de planilhas Excel heterogêneas (`.xlsx`).
- Validação e transformação de dados para um modelo padrão.
- Geração de planilhas formatadas com cabeçalhos coloridos, filtros automáticos e colunas ajustadas.
- Coleta de dados de APIs externas via `requests`.
- Fallback para scraping HTML com `BeautifulSoup` quando a API não está disponível.
- CLI construída com `Typer`.
- Configuração via arquivo `.env`.
- Logging estruturado em arquivo e console, com níveis configuráveis.

## Estrutura do Projeto

```
excel_automation/
│
├── src/
│   └── excel_automation/
│       ├── main.py              # Entrada da aplicação (CLI Typer)
│       ├── config/
│       │   └── settings.py      # Leitura do .env
│       ├── logging_config/
│       │   └── logger.py        # Configuração centralizada de logging
│       ├── api/
│       │   └── client.py        # Consumo das APIs (requests)
│       ├── scraping/
│       │   └── html_scraper.py  # Fallback para scraping HTML
│       ├── excel/
│       │   ├── reader.py        # Leitura de Excel
│       │   ├── transformer.py   # Transformação de dados
│       │   └── writer.py        # Geração de Excel formatado
│       └── core/
│           └── orchestrator.py  # Fluxo principal (ETL)
│
├── tests/
├── .env.example
├── requirements.txt
└── pyproject.toml
```

## Instalação

```bash
# Clone o repositório
git clone https://github.com/victor-ss13/menorah.git
cd menorah

# Crie e ative um ambiente virtual
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
.venv\Scripts\activate      # Windows

# Instale as dependências
pip install -e .

# Configure o ambiente
cp .env.example .env
# Edite .env conforme necessário
```

## Uso via CLI

```bash
# Processar planilha de entrada e gerar saída padronizada
excel-automation --input data/input/planilha.xlsx --output data/output/resultado.xlsx

# Com coleta de dados externos via API (e fallback por scraping)
excel-automation \
  --input data/input/planilha.xlsx \
  --api-path /v1/products \
  --scraping-url https://example.com/products \
  --log-level DEBUG

# Usando módulo diretamente
python -m excel_automation.main --help
```

## Executar os Testes

```bash
pip install -e ".[dev]"
pytest
```

## Variáveis de Ambiente (`.env`)

| Variável       | Padrão                       | Descrição                              |
|----------------|------------------------------|----------------------------------------|
| `API_BASE_URL` | `https://api.example.com`    | URL base da API externa                |
| `API_TIMEOUT`  | `30`                         | Timeout HTTP em segundos               |
| `INPUT_DIR`    | `data/input`                 | Diretório de entrada das planilhas     |
| `OUTPUT_DIR`   | `data/output`                | Diretório de saída das planilhas       |
| `LOG_LEVEL`    | `INFO`                       | Nível de log                           |
| `LOG_FILE`     | `logs/excel_automation.log`  | Caminho do arquivo de log              |