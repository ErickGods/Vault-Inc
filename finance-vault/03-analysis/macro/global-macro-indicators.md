---
tags: [finance, analysis, macro, indicators, leading-indicators]
status: active
complexity: intermediate
context: global
updated: 2026-04-07
aliases: [Indicadores Macro, Macro Indicators, Leading Indicators]
---

# Global Macro Indicators

## Overview

Indicadores macroeconômicos são as **séries de dados** que sinalizam a saúde da economia, antecipam ciclos e guiam decisões de bancos centrais e investidores. Eles se dividem em **leading** (antecipam), **coincident** (acompanham) e **lagging** (confirmam) — e cada classe tem usos distintos para análise de investimentos.

Como diz Stanley Druckenmiller: *"Never ever invest in the present. It doesn't matter what a company is earning today; what matters is what people think it'll earn 18 months from now."* — daí a importância dos leading indicators.

---

## Core Concepts

### Leading vs Coincident vs Lagging

| Tipo | Característica | Exemplos |
|------|----------------|----------|
| **Leading** | Antecipam o ciclo | PMI, yield curve, building permits, ISM new orders, confidence |
| **Coincident** | Movem com o ciclo | PIB, payroll, vendas no varejo, produção industrial |
| **Lagging** | Confirmam após | Desemprego, CPI core, custo unitário do trabalho |

### Indicadores de Atividade (PIB)

**GDP (Gross Domestic Product)** = soma de bens e serviços produzidos em um período.

```
PIB = C + I + G + (X - M)
```

- C = Consumo das famílias
- I = Investimento privado
- G = Gastos do governo
- X-M = Exportações líquidas

Variações importantes:
- **PIB Real** (deflacionado pela inflação)
- **PIB Nominal**
- **PIB per capita** (mede padrão de vida)

### Indicadores de Inflação

- **CPI (Consumer Price Index)**: cesta de bens e serviços ao consumidor
- **PPI (Producer Price Index)**: preços ao produtor (leading do CPI)
- **Core CPI**: exclui alimentos e energia (volátil)
- **PCE**: preferido pelo Fed; menos peso a habitação
- **IPCA**: índice oficial brasileiro (IBGE)

### Indicadores de Mercado de Trabalho (US)

- **Nonfarm Payroll**: emprego criado (mensal, primeira sexta)
- **Unemployment Rate**: taxa de desemprego
- **Initial Jobless Claims**: pedidos de seguro-desemprego (semanal, leading)
- **Wage Growth**: pressão inflacionária via salários
- **Labor Force Participation**: % da população que trabalha ou busca emprego

### Indicadores de Sentimento e Atividade

- **PMI (Purchasing Managers Index)**: pesquisa de gerentes de compra. >50 = expansão, <50 = contração
  - **ISM Manufacturing** (US) / **PMI Caixin** (China) / **HCOB PMI** (Europa)
- **Consumer Confidence Index**: confiança das famílias
- **CEO Confidence**: planos de investimento
- **Building Permits** / **Housing Starts**: leading do setor de construção

### Yield Curve

A inversão da curva 10y-2y é o **leading indicator de recessão mais confiável** historicamente nos EUA. Ver [[interest-rate-cycles]].

---

## How to Apply

### Calendário Macro (Principais Releases)

| Frequência | Indicador | Por que importa |
|------------|-----------|-----------------|
| Diária | Yield curve, oil, USD index | Pulso do mercado |
| Semanal | Initial claims (US) | Mercado de trabalho leading |
| Mensal | NFP, CPI, PMI, Retail Sales | Inflação e atividade |
| Trimestral | PIB | Output total |
| Anual | Orçamento federal | Política fiscal |

### Como Interpretar Surpresas

```
Surpresa = Realizado - Esperado (consenso)
```

Mercado reage a **surpresas**, não a níveis. PIB de 2% pode ser bullish (esperado 1%) ou bearish (esperado 3%).

### Hierarquia de Importância

1. **Decisões do Fed/BCB** (semanal alta)
2. **CPI / PCE** (drives the Fed)
3. **NFP** (drives expectativas)
4. **PMI/ISM** (drives crescimento)
5. **PIB** (lagging, mas confirma)

---

## Examples

> [!example] PMI como Sinal
> ISM Manufacturing cai de 52 para 48 em 2 meses → cruzou abaixo de 50 → contração da indústria.
> Historicamente, ISM < 45 está associado a recessão nos próximos 6-12 meses.
> Reação típica: ações cíclicas vendem, treasuries longas se valorizam.

> [!example] CPI Surpresa
> Consenso: CPI core +0,3% MoM
> Realizado: +0,5%
> Reação: yields sobem, USD se fortalece, ações caem (Fed mais hawkish).

---

## Gotchas

> [!warning] Erros Comuns
> - **Confiar em um único indicador**: macroeconomia exige triangulação
> - **Confundir nominal com real**: PIB nominal de 8% pode ser 2% real se inflação 6%
> - **Ignorar revisões**: dados são revisados (NFP especialmente)
> - **Sobre-reagir a um mês**: tendência > ponto único
> - **Esquecer sazonalidade**: muitos dados são ajustados (SA), checar se SA ou NSA
> - **Comparar países sem ajuste**: metodologias diferem (IPCA ≠ CPI)
> - **Lagging como leading**: desemprego é lagging, não antecipa ciclo

---

## Brazilian Context

### Indicadores Brasileiros Essenciais

| Indicador | Fonte | Frequência |
|-----------|-------|------------|
| IPCA | IBGE | Mensal |
| IGP-M | FGV | Mensal |
| PIB | IBGE | Trimestral |
| IBC-Br | BCB | Mensal (proxy do PIB) |
| PMC (varejo) | IBGE | Mensal |
| PIM (indústria) | IBGE | Mensal |
| PMS (serviços) | IBGE | Mensal |
| PNAD Contínua | IBGE | Mensal |
| Caged | MTE | Mensal (criação de emprego formal) |
| Focus | BCB | Semanal (expectativas) |
| Boletim Regional | BCB | Trimestral |

### Particularidades

- **IBC-Br** é o melhor proxy mensal do PIB brasileiro
- **Caged** vs **PNAD**: Caged é formal, PNAD inclui informal
- **IGP-M** tem peso de atacado (volatil), IPCA é varejo
- **Focus** é o termômetro do consenso de economistas

> [!info] Recursos
> - **BCB**: [bcb.gov.br](https://www.bcb.gov.br) — Focus, atas, séries históricas (SGS)
> - **IBGE**: [ibge.gov.br](https://www.ibge.gov.br) — PIB, IPCA, Pnad
> - **FGV/IBRE**: confiança, IGP-M
> - **FRED** (St. Louis Fed): séries internacionais, gratuito

---

## Formulas

```
# PIB pela ótica da despesa
PIB = C + I + G + (X - M)

# Crescimento real
Crescimento Real = (PIB_t / PIB_t-1) - 1 (em termos reais)

# Inflação acumulada
π_acum = Π(1 + π_i) - 1

# PMI direção
PMI > 50 → expansão
PMI < 50 → contração
PMI = 50 → estável

# Surpresa econômica
Surprise = Actual - Consensus
Z-Score = Surprise / σ_histórica
```

---

## References

- Achuthan, L. — *Beating the Business Cycle*
- Mishkin, F. — *Macroeconomics: Policy and Practice*
- BCB — *Boletim Focus* (semanal)
- IBGE — *PIB Trimestral*
- FRED — *Federal Reserve Economic Data*
- Bloomberg Economic Calendar

---

## Related

- [[ray-dalio-machine]] — Indicadores no contexto de ciclos
- [[interest-rate-cycles]] — BC reage a indicadores
- [[market-cycles]] — Mercados respondem a macro
- [[inflation]] — IPCA e CPI
- [[yield-curve]] — Indicador leading
- [[us-markets-overview]] — Calendário US
