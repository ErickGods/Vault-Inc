---
tags: [moc, analysis, finance-vault]
status: active
complexity: basic
context: global
updated: 2026-04-06
aliases: [Analysis MOC, Análise]
---

# 🔍 Analysis — Map of Content

## Visão Geral

Este MOC organiza os frameworks e métodos de análise disponíveis no vault. Cobre desde análise fundamentalista clássica (Graham, Buffett) até análise quantitativa moderna (factor investing, backtesting), passando por análise técnica e macroeconomia.

> [!info] Qual Análise Usar?
> - **Fundamentalista**: para decidir *o que* comprar (valor intrínseco)
> - **Técnica**: para decidir *quando* comprar (timing e tendências)
> - **Quantitativa**: para decidir *quanto* comprar (otimização e fatores)
> - **Macro**: para entender *o contexto* (ciclos e políticas)

---

## 📊 Análise Fundamentalista

| Arquivo | Descrição | Complexidade |
|---------|-----------|-------------|
| [[valuation-dcf]] | Fluxo de Caixa Descontado — o modelo core de valuation | Avançada |
| [[valuation-multiples]] | Valuation por múltiplos (P/L, EV/EBITDA) | Intermediária |
| [[warren-buffett-framework]] | Filosofia Buffett: moat, margem de segurança | Intermediária |
| [[graham-net-net]] | Ben Graham: Net-Net, Graham Number, investidor defensivo | Avançada |

> [!quote] Benjamin Graham
> "No curto prazo, o mercado é uma máquina de votar. No longo prazo, é uma balança."

---

## 📈 Análise Técnica

| Arquivo | Descrição | Complexidade |
|---------|-----------|-------------|
| [[price-action]] | Tendências, padrões gráficos, volume | Intermediária |
| [[indicators-overview]] | MA, RSI, MACD, Bollinger, VWAP | Intermediária |
| [[support-resistance]] | Suporte/resistência, Fibonacci, pivots | Básica |
| [[candlestick-patterns]] | Padrões de candle: doji, hammer, engulfing | Básica |

> [!warning] Atenção
> Análise técnica funciona melhor como complemento à análise fundamentalista, não como substituta.

---

## 🔢 Análise Quantitativa

| Arquivo | Descrição | Complexidade |
|---------|-----------|-------------|
| [[factor-investing]] | Fama-French, fatores: Value, Size, Momentum, Quality | Avançada |
| [[momentum-strategies]] | Momentum cross-sectional e time-series, Dual Momentum | Avançada |
| [[backtesting-basics]] | Walk-forward, vieses, ferramentas Python | Avançada |

---

## 🌍 Análise Macroeconômica

| Arquivo | Descrição | Complexidade |
|---------|-----------|-------------|
| [[ray-dalio-machine]] | A máquina econômica de Ray Dalio, debt cycles | Intermediária |
| [[interest-rate-cycles]] | Ciclos de juros, Copom, FOMC, Taylor Rule | Intermediária |
| [[global-macro-indicators]] | PIB, PMI, CPI, indicadores leading/lagging | Intermediária |

---

## 🔗 Combinando Métodos

> [!tip] Framework Integrado
> 1. **Macro** → entender o ciclo atual (expansão ou contração?)
> 2. **Fundamentalista** → selecionar ativos de qualidade a preço justo
> 3. **Quantitativa** → validar com dados e backtesting
> 4. **Técnica** → definir ponto de entrada e gestão de risco

---

## 📊 Dataview

```dataview
TABLE status, complexity, context, updated
FROM "finance-vault/03-analysis"
SORT file.folder ASC, complexity ASC
```

---

## Related

- [[🗺️ Home]] — Dashboard principal
- [[🗺️ Investments-MOC]] — Classes de ativos
- [[key-ratios]] — Indicadores financeiros
- [[investment-checklist]] — Checklist de decisão
- [[cognitive-biases]] — Vieses que afetam análise
- [[financial-statements]] — Base das demonstrações
