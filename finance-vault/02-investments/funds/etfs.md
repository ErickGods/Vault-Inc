---
tags: [finance, investments, funds, etfs, passive-investing]
status: active
complexity: intermediate
context: global
updated: 2026-04-07
aliases: [ETFs, Exchange-Traded Funds, Passive Investing]
---

# ETFs (Exchange-Traded Funds)

## Overview

ETFs são **fundos de investimento negociados em bolsa como ações**, geralmente passivos, replicando um índice (S&P 500, IBOV, MSCI World). Inventados em 1993 (SPY), revolucionaram a indústria de gestão ao oferecer **diversificação instantânea, baixo custo, alta liquidez e transparência**. O mercado global de ETFs ultrapassa US$ 12 trilhões.

John Bogle (Vanguard) é o pai do investimento passivo e provou empiricamente que **a maioria dos gestores ativos não bate o índice** após custos.

---

## Core Concepts

### Como Funcionam

ETFs replicam um índice mantendo as mesmas ações nas mesmas proporções. Compradores e vendedores negociam cotas em bolsa enquanto **Authorized Participants (APs)** criam/resgatam blocos de cotas via mecanismo de arbitragem que mantém o preço próximo do NAV.

### Vantagens vs Fundos Tradicionais

| Critério | ETF | Fundo Ativo |
|----------|-----|-------------|
| Custo (expense ratio) | 0,03-0,5% | 1-3% |
| Liquidez | Intradiária | D+1+ |
| Transparência | Diária | Mensal/trimestral |
| Tributação | Simples | Come-cotas |
| Acesso | Bolsa (qualquer corretora) | Distribuidor específico |
| Diversificação | Instantânea | Variável |

### Tipos de ETFs

- **Equity ETFs**: replicam índices de ações (SPY, IVV, VOO, BOVA11)
- **Bond ETFs**: replicam índices de bonds (AGG, TLT, BND)
- **Sector ETFs**: focam em setores (XLK tech, XLE energia)
- **Factor ETFs**: smart beta (value, momentum, quality)
- **International**: EFA (developed), EEM (emerging)
- **Commodity ETFs**: GLD (ouro), USO (petróleo)
- **Inverse / Leveraged**: amplificam ou invertem retornos (cuidado!)
- **Active ETFs**: cresceram nos últimos anos (ARKK)

### ETFs no Brasil

| Ticker | Índice |
|--------|--------|
| **BOVA11** | Ibovespa |
| **SMAL11** | Small Caps |
| **DIVO11** | Dividendos |
| **IVVB11** | S&P 500 (BR) |
| **NASD11** | Nasdaq 100 |
| **BBSD11** | Setor financeiro |
| **HASH11** | Cripto |

---

## How to Apply

### Estratégia Bogle (Three-Fund Portfolio)

```
60% US Total Market (VTI)
20% International (VXUS)
20% Bonds (BND)
```

Simples, baixo custo, supera ~85% dos gestores ativos no longo prazo.

### Estratégia Brasileira

```
40% IVVB11 (S&P 500)
30% BOVA11 (IBOV)
20% Tesouro IPCA+
10% IFIX/HGLG11 (FIIs)
```

### DCA (Dollar-Cost Averaging)

Aportar valores fixos mensalmente independente do preço. Reduz risco de timing e força disciplina.

---

## Examples

> [!example] Custo Composto
> US$ 100k investidos por 30 anos a 8% a.a.:
> - **ETF (0,03%)**: US$ 1.000.626
> - **Fundo (1,5%)**: US$ 660.872
>
> Diferença: ~US$ 340.000 só em taxas.

> [!example] BOVA11 vs Fundo Ativo
> Backtest 2010-2024: ~80% dos fundos de ações brasileiros NÃO bateram BOVA11 após taxas. SPIVA Brazil report confirma.

---

## Gotchas

> [!warning] Atenção
> - **ETFs alavancados**: SQQQ, TQQQ destrutivos no longo prazo (path dependency)
> - **ETFs sintéticos**: usam swaps, não detêm os ativos (risco de contraparte)
> - **Tracking error**: nem todo ETF replica perfeitamente
> - **Liquidez do underlying**: ETF pode ser líquido mas o índice não (raros casos)
> - **Tributação ETF Brasil**: 15% sobre ganhos, **sem isenção** dos R$ 20k de ações
> - **ETFs nicho** podem ter spread alto e baixo AUM

---

## Brazilian Context

### Tributação ETFs no Brasil

- **IR**: 15% sobre ganho de capital (sem isenção R$ 20k)
- **DARF mensal**: investidor recolhe
- **Day trade ETF**: 20%
- **Sem come-cotas** (vantagem vs fundos tradicionais)
- **Dividendos**: ETFs brasileiros reinvestem (não distribuem)

### ETFs Internacionais via Brasil

- **BDRs de ETFs**: BIVO39 (S&P), NASD11, IVVB11
- **Corretoras estrangeiras**: Avenue, Inter Internacional, Nomad
- **Preferência por BDRs**: simplificam tributação para PF

> [!info] Cobertura Crescente
> A B3 lançou dezenas de ETFs nos últimos anos. Acompanhar página oficial: b3.com.br/etf

---

## Formulas

```
# Tracking error
TE = σ(Retorno_ETF - Retorno_Index)

# Expense ratio impact (30 anos)
Drag = (1 - ER)^30

# Bid-ask spread cost
Custo = (Ask - Bid) / Mid × Volume

# DCA cost average
P_médio = Σ(Aporte_i) / Σ(Cotas_i)
```

---

## References

- Bogle, J. — *The Little Book of Common Sense Investing*
- Ferri, R. — *All About Asset Allocation*
- Malkiel, B. — *A Random Walk Down Wall Street*
- SPIVA — *S&P Index vs Active Reports*

---

## Related

- [[fundos-de-investimento]] — Alternativa ativa
- [[fiis-real-estate]] — Outro tipo de fundo em bolsa
- [[diversification]] — ETFs como vehículo de diversificação
- [[capital-allocation]] — Bogle three-fund
- [[factor-investing]] — Smart beta ETFs
- [[bonds-international]] — Bond ETFs
- [[tax-optimization-br]] — Tributação ETF
