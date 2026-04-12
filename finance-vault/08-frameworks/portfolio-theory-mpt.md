---
tags: [finance, frameworks, mpt, portfolio-theory]
status: active
complexity: advanced
context: global
updated: 2026-04-07
aliases: [Modern Portfolio Theory, MPT, Teoria Moderna de Portfólio]
---

# Modern Portfolio Theory (MPT)

## Overview

Modern Portfolio Theory, formulada por Harry Markowitz em 1952, é o framework matemático que fundamenta a alocação racional de ativos. A tese central: investidores avessos a risco podem construir portfólios que **maximizam retorno esperado para um dado nível de risco** combinando ativos cujos retornos não são perfeitamente correlacionados.

A MPT transformou o investimento de uma análise de ativos individuais em uma análise de portfólios — o que importa não é o risco isolado de um ativo, mas sua contribuição marginal ao risco do portfólio.

---

## Core Concepts

### Hipóteses da MPT

1. Investidores são racionais e avessos a risco
2. Decisões baseadas em **média** (retorno esperado) e **variância** (risco)
3. Mercados eficientes — preços refletem toda informação disponível
4. Sem custos de transação ou impostos
5. Possibilidade de tomar/emprestar à taxa livre de risco
6. Distribuição normal dos retornos

### Retorno Esperado do Portfólio

```
E(r_p) = Σ(w_i × E(r_i))
```

### Variância do Portfólio (n ativos)

```
σ²_p = ΣΣ(w_i × w_j × σ_i × σ_j × ρ_ij)
```

### Fronteira Eficiente

Conjunto de portfólios que oferecem **maior retorno esperado** para cada nível de risco. Portfólios abaixo da fronteira são dominados (subótimos).

> [!tip] Insight-Chave
> A diversificação reduz o risco específico (não-sistemático) sem reduzir retorno esperado proporcionalmente — é "o único almoço grátis em finanças".

### Capital Market Line (CML)

Quando se inclui o ativo livre de risco, a fronteira eficiente vira uma reta tangente ao **portfólio de mercado**:

```
E(r_p) = r_f + ((E(r_m) - r_f) / σ_m) × σ_p
```

A inclinação da CML é o [[sharpe-ratio|Sharpe Ratio]] do portfólio de mercado.

---

## How to Apply

### Construção Prática

1. **Estimar inputs**: retornos esperados, volatilidades e matriz de correlações
2. **Otimizar**: resolver para pesos que minimizam variância sujeita a retorno-alvo
3. **Combinar com ativo livre de risco** conforme tolerância a risco do investidor
4. **Rebalancear periodicamente** para manter alocação-alvo

### Black-Litterman (Refinamento)

Modelo que incorpora views subjetivas do investidor aos retornos de equilíbrio do mercado, evitando portfólios extremos típicos da otimização ingênua.

---

## Examples

> [!example] Portfólio de 2 Ativos
> Ações (E[r]=12%, σ=20%) e Bonds (E[r]=5%, σ=8%), ρ=0,2
>
> Pesos 60/40:
> ```
> E(r_p) = 0,6×12% + 0,4×5% = 9,2%
> σ²_p = 0,36×0,04 + 0,16×0,0064 + 2×0,6×0,4×0,2×0,20×0,08
> σ_p ≈ 12,9%
> ```
> Sharpe (rf=3%) = (9,2 - 3) / 12,9 = 0,48

---

## Gotchas

> [!warning] Limitações Reais
> - **Inputs instáveis**: pequenas mudanças nas estimativas geram pesos muito diferentes
> - **Correlações não são estáticas**: aumentam em crises, justamente quando diversificação é mais necessária
> - **Distribuição normal é falsa**: retornos têm fat tails e skewness
> - **Variância ≠ risco**: não captura risco de ruína, drawdown ou risco de cauda
> - **Mean-variance optimization** tende a concentrar em ativos com erros de estimativa para cima

---

## Brazilian Context

Para investidor brasileiro, MPT enfrenta desafios extras:

- Histórico curto e estruturalmente quebrado (vários regimes monetários)
- Correlações Bovespa-S&P sobem em crises globais (2008, 2020)
- Renda fixa atrelada à Selic distorce a fronteira em períodos de juros altos
- Hedge cambial encarece exposição internacional

> [!info] Aplicação Prática
> Roboadvisors brasileiros (Warren, Magnetis, Vitreo) usam variantes simplificadas de MPT com Black-Litterman para construir portfólios-modelo por perfil.

---

## Formulas

```
# Retorno do portfólio
E(r_p) = Σ(w_i × E(r_i))

# Variância (matriz)
σ²_p = w' Σ w

# Sharpe Ratio
Sharpe = (E(r_p) - r_f) / σ_p

# Portfólio de variância mínima (2 ativos)
w_A* = (σ²_B - ρ × σ_A × σ_B) / (σ²_A + σ²_B - 2 × ρ × σ_A × σ_B)
```

---

## References

- Markowitz, H. — *Portfolio Selection* (1952), *Journal of Finance*
- Sharpe, W. — *Capital Asset Prices* (1964)
- Black, F.; Litterman, R. — *Global Portfolio Optimization* (1992)
- Bodie, Kane, Marcus — *Investments*

---

## Related

- [[diversification]] — Princípio intuitivo por trás da MPT
- [[capital-allocation]] — Aplicação prática de pesos
- [[risk-and-return]] — Trade-off central da teoria
- [[sharpe-ratio]] — Métrica derivada da CML
- [[capm]] — Extensão para precificação de ativos individuais
- [[factor-investing]] — Crítica e evolução da MPT
