---
tags: [finance, investments, equities, brazil, b3, ibovespa]
status: active
complexity: intermediate
context: br
updated: 2026-04-07
aliases: [Mercado Brasileiro, B3, Bovespa]
---

# Brazilian Market (B3)

## Overview

A B3 (Brasil, Bolsa, Balcão) é a única bolsa de valores do Brasil, formada em 2017 pela fusão da BM&FBovespa com a Cetip. É a 5ª maior bolsa do mundo em market cap (~US$ 1 tri) e concentra negociação de ações, futuros, opções, FIIs, ETFs e renda fixa privada.

Entender a estrutura, os índices e os segmentos de governança da B3 é pré-requisito para investir em ações brasileiras.

---

## Core Concepts

### Estrutura da B3

- **Bovespa Segment**: ações, FIIs, ETFs, BDRs
- **BM&F Segment**: futuros, opções, swaps
- **Cetip Segment**: balcão organizado, renda fixa privada
- **Liquidação**: B3 Clearing centraliza todas as operações

### Segmentos de Governança

| Segmento | Free float | Tipo de ação | Tag along |
|----------|-----------|--------------|-----------|
| **Novo Mercado** | ≥ 25% | Apenas ON | 100% |
| **Nível 2** | ≥ 25% | ON + PN | 100% |
| **Nível 1** | ≥ 25% | ON + PN | 80% (ON) |
| **Tradicional** | sem mín. | ON + PN | 80% (ON) |
| **Bovespa Mais** | sem mín. | Apenas ON | 100% |

### Principais Índices

| Índice | Composição |
|--------|-----------|
| **IBOV** | ~85 ações mais líquidas |
| **IBrX-100** | Top 100 por liquidez |
| **IBrX-50** | Top 50 |
| **SMLL** | Small Caps |
| **IDIV** | Dividendos |
| **IFIX** | FIIs |
| **IMAT** | Materiais básicos |
| **ICON** | Consumo |
| **IFNC** | Financeiro |
| **IEE** | Energia elétrica |

### Pregão

- **Pre-opening**: 9h45-10h
- **Pregão regular**: 10h-17h
- **After-market**: 17h30-18h (apenas IBOV)
- **Liquidação ações**: D+2

---

## How to Apply

### Setores Dominantes

1. **Financeiro** (30%): bancos (ITUB, BBDC, SANB, BBAS), seguros (BBSE, PSSA)
2. **Materiais** (20%): VALE3 sozinho domina; siderúrgicas (CSNA, GGBR)
3. **Energia** (15%): PETR4, eletricas (ELET, CMIG, TAEE)
4. **Consumo** (10%): ABEV3, varejo (LREN, MGLU)
5. **Utilities/Saneamento** (8%): SBSP, SAPR
6. **Outros** (17%)

### Concentração

> [!warning] Risco de concentração
> IBOV é altamente concentrado: top 10 ações respondem por ~55% do índice. PETR4 + VALE3 + ITUB4 ~25%.

### Tributação Brasil

- **Swing trade**: 15% sobre ganho líquido; isenção até R$ 20k vendidos/mês
- **Day trade**: 20% sobre ganho líquido; sem isenção; 1% de IR retido na fonte
- **Dividendos**: isentos para PF
- **JCP**: 15% retido na fonte
- **DARF**: até último dia útil do mês seguinte; código 6015

---

## Examples

> [!example] Composição IBOV (top 5, 2025)
> | Ticker | Setor | Peso |
> |--------|-------|------|
> | VALE3 | Mineração | ~12% |
> | PETR4 | Petróleo | ~9% |
> | ITUB4 | Bancos | ~8% |
> | BBDC4 | Bancos | ~5% |
> | ABEV3 | Bebidas | ~4% |

---

## Gotchas

> [!warning] Particularidades BR
> - **Liquidez baixa fora do IBOV**: small caps com spread alto
> - **Concentração setorial**: bancos + commodities dominam
> - **Risco político**: estatais sofrem com ciclo eleitoral
> - **Free float baixo**: muitas empresas controladas por famílias
> - **Câmbio impacta exportadoras**: VALE, PETR, SUZB seguem USD
> - **JCP** distorce comparações de P/L com mercados sem JCP

---

## Brazilian Context

### Regulação

- **CVM**: regula emissores e mercado de capitais
- **B3**: autorregulação operacional
- **ANBIMA**: distribuição e fundos
- **CMN**: define diretrizes do SFN

### Lei das S.A. (6.404/76)

- 25% mínimo de dividendos do lucro ajustado
- Direitos de minoritários
- Tag along
- Conselho fiscal

> [!info] Onde Achar Informação
> - **CVM**: gov.br/cvm — formulários de referência, fatos relevantes
> - **B3**: b3.com.br — cotações, índices, calendários
> - **RI das empresas**: releases, transcrições de calls
> - **Status Invest, Fundamentus**: screening gratuito

---

## Formulas

```
# Free Float
Free Float = Ações em circulação / Total de ações

# Liquidez (volume médio diário)
ADTV = Σ(Volume diário) / Nº pregões

# Tag along payout
Pagamento = Preço pago pelo controlador × % tag along
```

---

## References

- B3 — *Manual de Procedimentos Operacionais*
- CVM — *Lei das S.A. (6.404)*
- Lopes, A.; Martins, E. — *Teoria da Contabilidade*
- ANBIMA — *Códigos de Autorregulação*

---

## Related

- [[stocks-fundamentals]] — Base
- [[dividends]] — Proventos
- [[b3-structure]] — Estrutura detalhada
- [[market-participants]] — Players
- [[acronyms-br]] — Siglas BR
- [[tax-optimization-br]] — Tributação
- [[fiis-real-estate]] — Outro produto B3
