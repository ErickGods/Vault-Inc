---
tags: [finance, analysis, macro, interest-rates, monetary-policy]
status: active
complexity: intermediate
context: global
updated: 2026-04-07
aliases: [Ciclos de Juros, Política Monetária, Selic, FOMC]
---

# Interest Rate Cycles

## Overview

Os ciclos de juros são o **mecanismo central** pelo qual bancos centrais conduzem política monetária para controlar inflação, atividade econômica e estabilidade financeira. Entender esses ciclos é essencial porque a taxa básica afeta **todos os ativos**: ações, bonds, imóveis, câmbio, commodities — via custo de capital, valor presente e fluxos de capital.

Como diz Stanley Druckenmiller: *"Earnings don't move the overall market; it's the Federal Reserve."*

---

## Core Concepts

### Por Que BCs Mexem Juros

Mandatos típicos:
- **Inflação sob controle** (FOMC: 2% PCE; BCB: 3% IPCA)
- **Pleno emprego** (FOMC dual mandate; BCB foca apenas inflação)
- **Estabilidade financeira**

### Mecanismos de Transmissão

```
Juros sobem
   ↓
↑ Custo de crédito → ↓ consumo e investimento
↑ Custo de capital → ↓ valuations
↑ Atratividade da renda fixa → ↓ ações
↑ Câmbio (carry trade) → ↓ exportações, ↓ inflação importada
   ↓
↓ Atividade econômica → ↓ inflação
```

Lag típico: 12-18 meses do choque até efeito pleno na inflação.

### Curva de Juros (Yield Curve)

- **Normal**: longas > curtas (expectativa de crescimento)
- **Plana**: curtas ≈ longas (incerteza)
- **Invertida**: curtas > longas (sinal de recessão)

> [!warning] Yield Curve Inversion
> Inversão da treasury 10y-2y precedeu **todas** as recessões americanas dos últimos 60 anos. Lag típico: 12-24 meses entre inversão e recessão.

### Taylor Rule

Regra prescritiva para juros do BC:

```
i = r* + π + 0,5×(π - π*) + 0,5×(y - y*)
```

Onde π é inflação corrente, π* é meta, y é PIB, y* é PIB potencial.

### Ciclo Típico do BC

1. **Cutting**: estímulo durante recessão
2. **Holding low**: aguardando recuperação
3. **Hiking**: combatendo inflação no aquecimento
4. **Holding high**: até inflação ceder
5. **Cutting**: recomeça ciclo

---

## How to Apply

### Reading the Cycle

Indicadores para mapear posição no ciclo:
- **Inflação atual vs meta**
- **Desemprego atual vs NAIRU**
- **Hiato do produto** (PIB real vs potencial)
- **Inflação esperada** (breakevens, Focus)
- **Comunicação do BC** (atas, dot plot)

### Implicações por Classe de Ativo

| Fase | Ações | Bonds | USD | Ouro |
|------|-------|-------|-----|------|
| Cortando juros | Bullish | Bullish | Bearish | Bullish |
| Mantendo baixo | Bullish | Neutro | Neutro | Bullish |
| Subindo juros | Bearish | Bearish | Bullish | Bearish |
| Mantendo alto | Misto | Neutro | Bullish | Misto |
| Pivot (corte iminente) | Muito Bullish | Bullish | Bearish | Bullish |

### Calendário de Decisões

- **FOMC**: 8 reuniões/ano (a cada ~6 semanas)
- **Copom**: 8 reuniões/ano (a cada ~45 dias)
- **ECB**: 8 reuniões/ano
- **BoE, BoJ**: ~8 reuniões/ano

---

## Examples

> [!example] Ciclo Fed 2022-2024
> - Mar/22: Fed começa a subir (de 0% para 0,25%)
> - Jun/22-Mai/23: 11 altas, atinge 5,25-5,50%
> - Jul/23-Set/24: hold prolongado
> - Set/24: primeiro corte (-50 bps)
>
> S&P caiu -19% em 2022 (ano de hiking), subiu +24% em 2023 (sinais de pivot).

> [!example] Ciclo Copom 2021-2024
> - Mar/21: Selic em 2,00% (mínima histórica)
> - Mar/21-Ago/22: 12 altas, atinge 13,75%
> - Ago/22-Jul/23: hold
> - Ago/23-Mai/24: cortes graduais
> - Set/24+: novo ciclo de alta por inflação persistente

---

## Gotchas

> [!warning] Erros Comuns
> - **Lutar contra o BC**: "don't fight the Fed" — política monetária é mais forte que tese individual
> - **Ler dot plots como certeza**: são projeções, não compromissos
> - **Ignorar lags**: efeitos de juros aparecem com 12-18 meses de atraso
> - **Sobre-reagir a uma reunião**: tendência importa mais que decisão única
> - **Confundir nominal com real**: juro real = nominal - inflação esperada
> - **Esquecer balanço do BC**: QE/QT também impactam liquidez

> [!tip] Real vs Nominal
> O que importa para investimentos é o **juro real**. Selic 13,75% com inflação 11% é frouxa; Selic 5% com inflação 2% é restritiva.

---

## Brazilian Context

### Particularidades do Brasil

- **Selic alta estrutural**: histórico de juros reais entre os mais altos do mundo
- **Sensibilidade fiscal**: prêmio de risco fiscal afeta curva longa mesmo sem mudança Selic
- **Câmbio volátil**: BCB não tem dual mandate, foca só em inflação
- **Carry trade**: Selic alta atrai capital, fortalece real
- **Tesouro IPCA+** oferece juro real puro garantido — única no mundo nesse nível

### Estrutura Copom

- 9 membros (presidente + 8 diretores)
- Decisão por consenso
- Comunicado + ata semanal seguinte
- **Relatório de Inflação** trimestral

> [!info] Focus Survey
> Toda segunda-feira, BCB publica o **Relatório Focus**: mediana de projeções de mercado para Selic, IPCA, PIB, câmbio. Termômetro do consenso.

---

## Formulas

```
# Juro real (Fisher)
(1 + i_real) = (1 + i_nominal) / (1 + π)
i_real ≈ i_nominal - π

# Taylor Rule
i = r* + π + 0,5(π - π*) + 0,5(y - y*)

# Term spread (sinal recessão)
Spread = Yield_10y - Yield_2y
Inversão se Spread < 0

# Duration approx
ΔP/P ≈ -Duration × Δy
```

---

## References

- Bernanke, B. — *21st Century Monetary Policy*
- Mishkin, F. — *The Economics of Money, Banking, and Financial Markets*
- BCB — *Relatório de Inflação* (trimestral)
- Fed — *FOMC Statements & Minutes*
- Estrella, A.; Mishkin, F. — *The Yield Curve as a Predictor of Recession*

---

## Related

- [[ray-dalio-machine]] — Juros como motor do ciclo
- [[global-macro-indicators]] — Indicadores que BC observa
- [[inflation]] — Alvo da política monetária
- [[yield-curve]] — Estrutura a termo
- [[market-cycles]] — Mercados respondem a juros
- [[selic-and-monetary-policy]] — Política BR
- [[acronyms-br]] — Selic, CDI, COPOM
