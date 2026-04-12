---
tags: [finance, fundamentals, inflation]
status: active
complexity: basic
context: br
updated: 2026-04-06
aliases: [Inflação, IPCA, IGP-M]
---

# Inflation (Inflação)

## Overview

Inflação é o aumento generalizado e sustentado dos preços de bens e serviços ao longo do tempo. Para investidores, inflação é o inimigo silencioso: ela corrói o poder de compra do dinheiro e transforma retornos nominais positivos em retornos reais negativos se não for adequadamente considerada.

No Brasil, a inflação tem uma história dramática — de hiperinflação nos anos 80-90 ao controle pós-Plano Real — e continua sendo um fator central em qualquer decisão financeira.

---

## Core Concepts

### Índices de Inflação no Brasil

| Índice | Medido por | Abrangência | Uso Principal |
|--------|-----------|-------------|--------------|
| **IPCA** | IBGE | Famílias 1-40 SM | Meta de inflação oficial |
| **INPC** | IBGE | Famílias 1-5 SM | Reajuste de salários |
| **IGP-M** | FGV | Atacado + varejo + construção | Reajuste de aluguéis |
| **IGP-DI** | FGV | Similar ao IGP-M | Contratos financeiros |

### Retorno Real vs Nominal

A equação de Fisher:

```
(1 + r_real) = (1 + r_nominal) / (1 + inflação)

# Aproximação:
r_real ≈ r_nominal - inflação
```

> [!example] Exemplo prático
> CDB rendendo 13% a.a. com IPCA de 5%:
> ```
> r_real = (1,13)/(1,05) - 1 = 7,62% a.a.
> ```

### Tipos de Inflação

- **De demanda**: excesso de consumo puxa preços
- **De custos**: aumento de insumos pressiona preços
- **Inercial**: expectativa futura gera inflação presente
- **Hiperinflação**: mensal > 50% (Brasil anos 80-90)

---

## How to Apply

### Protegendo-se da Inflação

1. **Invista em ativos reais**: [[tesouro-direto|Tesouro IPCA+]], ações com pricing power, [[fiis-real-estate|FIIs]]
2. **Evite manter caixa excessivo**: dinheiro parado perde valor
3. **Calcule sempre em termos reais**: retorno nominal não significa nada sem inflação
4. **Acompanhe expectativas**: Boletim Focus do BCB

---

## Examples

> [!example] O poder destrutivo da inflação
> R$ 100.000 com IPCA de 5% a.a.:
> | Ano | Poder de compra |
> |-----|-----------------|
> | 0 | R$ 100.000 |
> | 5 | R$ 78.353 |
> | 10 | R$ 61.391 |
> | 20 | R$ 37.689 |
> | 30 | R$ 23.138 |
>
> Em 30 anos, perde 77% do poder de compra!

---

## Gotchas

> [!warning] Armadilhas
> - **Ilusão monetária**: achar que ganhou porque o nominal subiu
> - **IGP-M ≠ IPCA**: aluguéis podem subir mais que salário
> - **Inflação pessoal**: sua cesta pode ter inflação diferente do IPCA
> - **Tesouro IPCA+ tem risco**: marcação a mercado se vender antes

---

## Brazilian Context

> [!info] História Brasileira
> - **Década de 80**: inflação anual > 200%
> - **1990**: Plano Collor — confisco da poupança
> - **1993**: inflação de 2.477% no ano
> - **1994**: Plano Real
> - **2015-16**: IPCA acima de 10%
> - **2022**: IPCA 5,79% (pressão global)
> - **Regime de metas** desde 1999, meta atual 3% (±1,5pp)

**Meta de inflação**: definida pelo CMN, perseguida pelo BCB via Selic.

---

## Formulas

```
# Equação de Fisher
(1 + r_real) = (1 + r_nominal) / (1 + π)

# Aproximação
r_real ≈ r_nominal - π

# Poder de compra futuro
PC_futuro = PC_hoje / (1 + π)^n
```

---

## References

- BCB — Relatório de Inflação
- IBGE — Séries históricas IPCA
- Boletim Focus — Expectativas de mercado
- Franco, G. — *O Plano Real e outros ensaios*

---

## Related

- [[tesouro-direto]] — Tesouro IPCA+ protege contra inflação
- [[compound-interest]] — Retorno real composto
- [[interest-rate-cycles]] — Selic e combate à inflação
- [[time-value-of-money]] — Taxas reais vs nominais
- [[yield-curve]] — Expectativas embutidas
- [[global-macro-indicators]] — IPCA como indicador
