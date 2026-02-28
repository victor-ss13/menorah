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

## OBS

- Google Drive:
    • Login: levemaislogistica@gmail.com
    • Senha: #@dm@leve-m@is#
- "G:\Outros computadores\Meu modelo Laptop (Samuel)\MAIS ATIVAS\Usuários\Check List e USUÁRIOS - Leve Mais.xlsx"
    •  Tabela de login e senha dos sistemas envolvidos
- Produto final do script existente:
    • Tabela de preços gerada pelo script Python
    • É necessário pegar todo conteúdo da tabela e converter em "número" dentro do Excel(manualmente)
    • Procurar forma de tratar essa conversão manual

## LAR

- Executa script Python (pasta "archives/lar")
- Converte conteúdo da tabela gerada para "Número"
- Cola tabela gerada dentro da "Tabela PADRÃO LAR" na aba "Nova Tabela Python"
- A tabela padrão faz o restante do serviço aplicando as fórmulas necessárias
- O intuito é fazer com que a tabela python seja inserida na aba correta de forma automatizada, após isso, os cálculos necessários estarão prontos
- Com cálculos prontos, pegamos o produto final nas abas "PROCV - LAR" e "PROCV - Calafate-LAR" e colamos o conteúdo da tabela dentro dos arquivos "modelo_importacao_produto_lar" e "modelo_importacao_produto_calafate_lar"
- Caminhos envolvidos:
    • Tabela Padrão: "G:\Outros computadores\Meu modelo Laptop (Samuel)\MAIS ATIVAS\Atualização de tabelas\Tabelas OFICIAIS em uso\Novas OFICIAIS em uso após atualização MERCOS\Tabela PADRÃO LAR - Sistema NOVO_ Preço Kg.xlsx"
    • Modelo LAR: "G:\Outros computadores\Meu modelo Laptop (Samuel)\MAIS ATIVAS\Atualização de tabelas\Tabelas OFICIAIS em uso\Novas OFICIAIS em uso após atualização MERCOS\modelo_importacao_produto_lar.xlsx"
    • Modelo Calafate LAR: "G:\Outros computadores\Meu modelo Laptop (Samuel)\MAIS ATIVAS\Atualização de tabelas\Tabelas OFICIAIS em uso\Novas OFICIAIS em uso após atualização MERCOS\modelo_importacao_produto_calafate_lar.xlsx"

## FRIMESA

- Executa cada um dos 4 scripts Python (pasta "archives/frimesa)
- Converte conteúdo das tabelas geradas para "Número"
- Cola cada uma das tabelas geradas nas respectivas abas da "Tabela PADRÃO Frimesa", abas: "Distribuidor", "Autosservico", "Varejo" e "Food Service"
- A tabela padrão faz o restante do serviço aplicando as fórmulas necessárias
- O intuito é fazer com que cada tabela python seja inserida nas respectivas abas corretas de forma automatizada, após isso, os cálculos necessários estarão prontos
- Com cálculos prontos, pegamos o produto final na aba "PROCV" e colamos seu conteúdo de tabela dentro do arquivo "modelo_importacao_produto_frimesa_4_tabelas"
- Caminhos envolvidos:
    • Tabela Padrão: "G:\Outros computadores\Meu modelo Laptop (Samuel)\MAIS ATIVAS\Atualização de tabelas\Tabelas OFICIAIS em uso\Novas OFICIAIS em uso após atualização MERCOS\Tabela PADRÃO Frimesa_4_tabelas.xlsx"
    • Modelo: "G:\Outros computadores\Meu modelo Laptop (Samuel)\MAIS ATIVAS\Atualização de tabelas\Tabelas OFICIAIS em uso\Novas OFICIAIS em uso após atualização MERCOS\modelo_importacao_produto_frimesa_4_tabelas.xlsx"