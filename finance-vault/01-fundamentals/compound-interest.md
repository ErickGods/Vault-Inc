---
tags: [finance, fundamentals, compound-interest]
status: active
complexity: basic
context: global
updated: 2026-04-06
aliases: [Juros Compostos, Compound Interest]
---

# Compound Interest (Juros Compostos)

## Overview

Juros compostos são juros calculados sobre o principal original e sobre os juros acumulados de períodos anteriores. É o mecanismo fundamental que torna possível a construção de riqueza a longo prazo e é a razão pela qual o [[time-value-of-money|valor do dinheiro no tempo]] é tão importante.

A diferença entre juros simples e compostos parece pequena no curto prazo, mas se torna astronômica em horizontes longos — é por isso que Einstein supostamente os chamou de "a oitava maravilha do mundo".

---

## Core Concepts

### Juros Simples vs Compostos

**Juros Simples:**
```
FV = PV × (1 + r × n)
```

**Juros Compostos:**
```
FV = PV × (1 + r)^n
```

| Ano | Simples (10%) | Compostos (10%) | Diferença |
|-----|-------------|----------------|-----------|
| 1 | R$ 11.000 | R$ 11.000 | R$ 0 |
| 5 | R$ 15.000 | R$ 16.105 | R$ 1.105 |
| 10 | R$ 20.000 | R$ 25.937 | R$ 5.937 |
| 20 | R$ 30.000 | R$ 67.275 | R$ 37.275 |
| 30 | R$ 40.000 | R$ 174.494 | R$ 134.494 |

> [!warning] A Armadilha do Curto Prazo
> Nos primeiros anos a diferença parece insignificante. É por isso que muitos subestimam o poder dos compostos — e também o custo de dívidas.

### Regra dos 72

```
Tempo para dobrar ≈ 72 / taxa de juros (%)
```

| Taxa | Tempo para dobrar |
|------|------------------|
| 6% | 12 anos |
| 8% | 9 anos |
| 10% | 7,2 anos |
| 12% | 6 anos |
| 15% | 4,8 anos |

### Capitalização Contínua

```
FV = PV × e^(r × n)
```

Onde `e ≈ 2,71828`.

### O Efeito do Tempo

O fator mais importante nos juros compostos é o **tempo**, não a taxa:

> [!example] O custo de esperar 10 anos
> Investidor A: começa com 25 anos, R$ 500/mês a 10% até os 65 (40 anos)
> Investidor B: começa com 35 anos, R$ 500/mês a 10% até os 65 (30 anos)
>
> Investidor A: **R$ 3.162.040**
> Investidor B: **R$ 1.130.244**
>
> Diferença: R$ 2.031.796 — quase 3x menos!

---

## How to Apply

### Como usar juros compostos a seu favor

1. **Comece o mais cedo possível** — o tempo é seu maior aliado
2. **Reinvista os rendimentos** — não gaste juros/dividendos
3. **Minimize taxas e impostos** — eles reduzem a base de capitalização
4. **Aportes regulares** — combine compostos com aportes mensais
5. **Evite resgates** — cada resgate "reinicia" parte do efeito composto

### Fórmula com Aportes Regulares

```
FV = PV × (1 + r)^n + PMT × [((1 + r)^n - 1) / r]
```

---

## Examples

> [!example] Tesouro Selic composto
> R$ 30.000 a CDI 13,25% a.a. por 3 anos:
> ```
> FV = 30.000 × (1,1325)^3 = R$ 43.569 (bruto)
> IR 15%: R$ 2.035
> Líquido: R$ 41.534
> ```

> [!example] Aportes mensais em fundo de ações
> R$ 1.000/mês por 20 anos a 1% a.m.:
> ```
> FV = 1.000 × [((1,01)^240 - 1) / 0,01] = R$ 989.255
> ```
> Investiu R$ 240.000, patrimônio de R$ 989.255.

---

## Gotchas

> [!warning] Armadilhas
> 1. **Inflação come os compostos**: 12% nominal com 5% inflação = 6,7% real
> 2. **Taxas destroem patrimônio**: 2% a.a. em 30 anos consome ~45% do patrimônio
> 3. **Juros compostos nas dívidas**: cartão a 15% a.m. = 435% a.a.!
> 4. **Come-cotas**: fundos brasileiros cobram IR semestral

---

## Brazilian Context

- **CDI** é a taxa de referência para renda fixa
- **Tesouro IPCA+** capitaliza juros reais + [[inflation|inflação]]
- **Come-cotas** (maio e novembro): antecipa IR em fundos
- **Isenção de IR em LCI/LCA** maximiza efeito composto
- **Calculadora do cidadão do BCB** para simulações

---

## Formulas

```
# Juros Compostos
FV = PV × (1 + r)^n

# Com Aportes Regulares
FV = PV × (1 + r)^n + PMT × [((1 + r)^n - 1) / r]

# Capitalização Contínua
FV = PV × e^(r×n)

# Regra dos 72
n_dobrar ≈ 72 / r(%)

# Taxa Real (Fisher)
(1 + r_real) = (1 + r_nominal) / (1 + inflação)
```

---

## References

- Mankiw, N.G. — *Principles of Economics*
- Assaf Neto, A. — *Matemática Financeira*
- Calculadora do Cidadão — BCB

---

## Related

- [[time-value-of-money]] — Fundamento do TVM
- [[tesouro-direto]] — Compostos em títulos públicos
- [[cdb-lci-lca]] — Renda fixa com compostos
- [[inflation]] — Retorno real vs nominal
- [[fire-movement]] — Compostos e independência
- [[wealth-building-stages]] — Construção de patrimônio
- [[dividends]] — Reinvestimento de dividendos
