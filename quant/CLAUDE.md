# Casa Quant — Vault Inc

## Mandato

A casa quant traduz em duas direções, e é a única que faz isso:

- **← finance:** tese discricionária → hipótese testável (universo, período, fator, critério de rejeição)
- **→ tech:** hipótese validada → código que roda (engine de backtest, pipeline, execução)

Toda entrega desta casa é uma dessas duas traduções, ou a evidência que sustenta uma delas.

## Como alcançar o conhecimento

Carregue `quant/00-index/_house.md` primeiro. Ele lista os domínios e o que cada um
cobre. Escolha o domínio, carregue o `_index.md` dele, e leia apenas as notas que a
tarefa exige. Nunca varra o vault com Glob às cegas.

## Padrões obrigatórios

- **Nenhum resultado sem período, universo e critério de rejeição declarados.** Backtest
  sem isso não é evidência, é anedota.
- **Custos de transação sempre.** Estratégia bruta de custo não é resultado.
- **Viés de sobrevivência tratado e declarado.** Se o dado não é point-in-time, diga.
- **Sharpe reportado com o número de tentativas.** Ver [[sharpe-ratio]] — Sharpe de uma
  estratégia escolhida entre 200 testadas não é o mesmo de uma testada uma vez.
- **Cenário de falha explícito:** em que regime esta estratégia perde dinheiro?

## Fronteira com a casa tech

`market-data-quant` cuida da **correção financeira** do dado — point-in-time, ajuste de
proventos, sobrevivência, splits, corporate actions. **Especifica.**

`data-engineer` (tech) cuida do **transporte** — ingestão, orquestração, storage, SLA,
custo. **Constrói.**

Quando a fronteira ficar ambígua, abra um Cross-Desk Request em vez de decidir sozinho.

## Entregáveis

Vão para o repositório privado, nunca para este:

- Backtests: `reports/quant/<estrategia>-<YYYY-MM-DD>.md`
- Risk reports: `reports/risk/<portfolio>-<YYYY-MM-DD>.md`
- Cross-Desk Requests: `cross-desk/<YYYY-MM-DD>-<from>-<to>.md`

Conhecimento durável que sair de um estudo **sobe para este vault** como nota nova, e o
índice do domínio ganha uma linha.
