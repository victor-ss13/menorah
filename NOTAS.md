# Notas de Análise — excel-automation (menorah)

Anotações coletadas durante a revisão do build inicial do projeto.

---

## Visão Geral

- O projeto é uma **CLI** que recebe planilhas Excel heterogêneas e devolve uma planilha padronizada.
- O usuário final interage exclusivamente pelo terminal (`excel-automation --input ... --output ...`).
- O arquivo original **nunca é modificado** — a saída é sempre um arquivo novo.
- Configurações de diretório padrão, URL de API e nível de log ficam no `.env`, tornando o uso ainda mais simples (basta rodar `excel-automation` sem argumentos se o `.env` estiver configurado).

---

## Colunas Padrão (`STANDARD_COLUMNS`)

- Atualmente as colunas da planilha de saída são **fixas e hardcoded** em `src/excel_automation/excel/transformer.py`:

```python
STANDARD_COLUMNS: list[str] = [
    "id",
    "nome",
    "valor",
    "data",
    "status",
]
```

- Qualquer coluna fora dessa lista é **descartada** no final da transformação.
- Colunas ausentes na entrada são **criadas automaticamente** com valor padrão vazio/zero.

### Decisão pendente

| Opção | Quando usar |
|-------|-------------|
| **A — Editar a constante diretamente** | Modelo de saída sempre igual para todos os usos |
| **B — Tornar configurável** (via `.env` ou argumento `--columns` na CLI) | Diferentes execuções exigem modelos de colunas distintos |

> Ainda não decidido. Avaliar conforme os requisitos do sistema terceiro que consumirá a planilha.

---

## Pontos de Melhoria / Observações Futuras

- [ ] Definir quais colunas realmente compõem o modelo padrão de saída.
- [ ] Avaliar se `STANDARD_COLUMNS` deve ser configurável externamente (Opção B acima).
- [ ] Verificar se o `column_mapping` (renomeação de colunas) será suficiente para absorver a variação entre fontes, ou se será necessário mapeamento por cliente/fonte.

---

*Atualizado em: 27/02/2026*
