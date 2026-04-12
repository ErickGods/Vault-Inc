---
tags: [finance, investments, fixed-income, bonds, treasuries, international]
status: active
complexity: intermediate
context: global
updated: 2026-04-07
aliases: [Bonds, Treasuries, Renda Fixa Internacional]
---

# International Bonds

## Overview

Bonds são títulos de dívida emitidos por governos ou empresas. Globalmente, o mercado de bonds é **maior** que o de ações (~US$ 130 tri vs ~US$ 100 tri). Para investidores brasileiros, bonds internacionais — especialmente Treasuries americanas — oferecem **diversificação cambial**, exposição a juros em USD e proteção em crises globais (flight to quality).

Como diz Howard Marks: *"You can't predict, but you can prepare."* — bonds são parte central de qualquer portfólio preparado.

---

## Core Concepts

### Tipos de Treasuries (US)

| Título | Prazo |
|--------|-------|
| **T-Bills** | < 1 ano (zero coupon) |
| **T-Notes** | 2-10 anos (cupom semestral) |
| **T-Bonds** | 20-30 anos (cupom semestral) |
| **TIPS** | Indexados à inflação (CPI) |
| **FRN** | Pós-fixados (taxa flutuante) |

### Corporate Bonds

- **Investment Grade (IG)**: rating BBB- ou superior
- **High Yield (HY) / Junk**: rating abaixo de BBB-
- **Convertibles**: conversíveis em ações
- **Preferred Stock**: híbrido entre dívida e equity

### Conceitos-Chave

**Yield to Maturity (YTM)**: taxa que iguala o valor presente dos fluxos ao preço de mercado.

**Duration**: sensibilidade do preço a mudanças na taxa.
```
ΔP/P ≈ -Duration × Δyield
```

**Convexity**: refinamento da relação preço-yield (curvatura).

**Credit Spread**: diferença entre yield do bond corporativo e treasury equivalente. Mede risco de crédito.

> [!tip] Regra de Bolso
> Cada 1% de aumento na taxa de juros reduz o preço de um bond em ~Duration%. Bond de Duration 10 cai ~10% se yields sobem 1pp.

### Rating de Crédito

| Agência | Investment Grade | High Yield |
|---------|-----------------|------------|
| **S&P** | AAA → BBB- | BB+ → D |
| **Moody's** | Aaa → Baa3 | Ba1 → C |
| **Fitch** | AAA → BBB- | BB+ → D |

---

## How to Apply

### Como Investir como Brasileiro

1. **BDRs de ETFs de Bonds**: BIVB39 (Treasury), USDB11 (longa)
2. **Corretora internacional**: Avenue, Inter Internacional, Nomad → comprar TLT, IEF, AGG, BND
3. **Fundos brasileiros de RF Internacional**: oferecem exposição com hedge ou sem
4. **Direta**: brokers como Interactive Brokers (mais sofisticado)

### Por Objetivo

| Objetivo | Instrumento |
|----------|------------|
| Hedge cambial USD | T-Bills curto |
| Renda em USD | T-Notes 5-10y |
| Especular queda de juros | TLT (T-Bonds 20+) |
| Hedge inflação USD | TIPS / VTIP |
| Renda alta (com risco) | HY corporate (HYG, JNK) |

### ETFs de Bonds Mais Usados

| Ticker | Exposição |
|--------|-----------|
| **TLT** | Treasuries 20+ anos |
| **IEF** | Treasuries 7-10 anos |
| **SHY** | Treasuries 1-3 anos |
| **AGG** | Aggregate US bonds |
| **BND** | Total bond market |
| **LQD** | Investment grade corporate |
| **HYG** | High yield corporate |
| **TIP** | TIPS (inflação) |
| **EMB** | Emerging markets bonds |

---

## Examples

> [!example] Hedge Cambial
> Brasileiro com R$ 100k temendo desvalorização do real.
> Compra US$ 18k em T-Bills 6 meses via Avenue.
> Se real desvaloriza 20%, posição em BRL valoriza ~20% sem precisar acertar timing.

> [!example] Duration em ação
> TLT (Duration ~17): yields sobem 1pp → preço cai ~17%
> Em 2022, TLT caiu **-31%** quando yields longas dispararam.

---

## Gotchas

> [!warning] Riscos
> - **Risco de juros**: bonds longos sofrem em ciclos de alta
> - **Risco cambial** (para brasileiro sem hedge)
> - **Risco de crédito** em corporates HY
> - **Liquidez baixa** em corporates pequenos
> - **Tributação**: ganhos em bonds via corretora estrangeira são tributados como exterior (15%, com possibilidade de compensar prejuízos)

---

## Brazilian Context

### Tributação para PF

- **BDR de bonds (B3)**: tabela regressiva como RF
- **Bonds via corretora exterior**: 15% sobre ganhos cambiais + cupons; isenção R$ 35k/mês
- **Fundos brasileiros internacionais**: come-cotas + IR

> [!info] Avenue, Nomad, Inter Global
> Plataformas que facilitam acesso a bonds e ETFs americanos com ordem em USD direto. Útil para começar.

### Vantagens da Diversificação

- **Hedge cambial natural**
- **Correlação baixa com ativos brasileiros** (em crises locais)
- **Diversificação de risco soberano**
- **Exposição a juros em USD** (diferente de Selic)

---

## Formulas

```
# Yield to Maturity (aprox)
YTM ≈ [Cupom + (Face - Preço)/n] / [(Face + Preço)/2]

# Duration de Macaulay
D = Σ [t × CF_t / (1+y)^t] / Σ [CF_t / (1+y)^t]

# Sensibilidade do preço
ΔP/P ≈ -D × Δy / (1+y)

# Credit spread
Spread = Yield_corp - Yield_treasury (mesmo prazo)

# Real yield (TIPS)
Real Yield = Nominal Yield - Inflação esperada
```

---

## References

- Fabozzi, F. — *Bond Markets, Analysis, and Strategies*
- Tuckman, B. — *Fixed Income Securities*
- US Treasury — *TreasuryDirect.gov*
- Bridgewater — *All Weather*

---

## Related

- [[tesouro-direto]] — Equivalente brasileiro
- [[yield-curve]] — Estrutura a termo
- [[interest-rate-cycles]] — Drivers de yield
- [[ray-dalio-machine]] — Bonds em risk parity
- [[capital-allocation]] — Bonds no portfólio
- [[etfs]] — Acesso via ETF
