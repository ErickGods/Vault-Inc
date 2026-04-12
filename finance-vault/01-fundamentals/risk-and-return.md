---
tags: [finance, fundamentals, risk-return]
status: active
complexity: intermediate
context: global
updated: 2026-04-06
aliases: [Risco e Retorno, Risk-Return Tradeoff]
---

# Risk and Return (Risco e Retorno)

## Overview

A relação risco-retorno é um dos princípios mais fundamentais em finanças: para obter retornos maiores, é necessário aceitar riscos maiores. Este tradeoff governa toda a teoria de investimentos e é a base para modelos como o CAPM, a [[portfolio-theory-mpt|Teoria Moderna do Portfólio]] e o [[factor-investing|Factor Investing]].

Entender risco não é apenas sobre volatilidade — é sobre a probabilidade de perda permanente de capital e sobre ser adequadamente compensado pelos riscos assumidos.

---

## Core Concepts

### Medidas de Risco

**Variância e Desvio Padrão (Volatilidade):**
```
Variância (σ²) = Σ(r_i - r̄)² / (n - 1)
Desvio Padrão (σ) = √Variância
```

**Beta — Risco Sistemático:**
```
β = Cov(r_ativo, r_mercado) / Var(r_mercado)
```

- β = 1,0 → se move com o mercado
- β > 1,0 → mais volátil que o mercado
- β < 1,0 → menos volátil que o mercado

### Risco Sistemático vs Não-Sistemático

- **Sistemático (não diversificável)**: risco de mercado, juros, inflação → compensado pelo retorno
- **Não-sistemático (diversificável)**: risco específico da empresa → eliminável via [[diversification|diversificação]]

> [!info] Princípio-Chave
> O mercado só remunera o risco sistemático. Risco específico pode ser eliminado pela diversificação, então o mercado não paga prêmio por ele.

### CAPM (Capital Asset Pricing Model)

```
E(r) = r_f + β × (r_m - r_f)
```

Onde:
- `E(r)` = retorno esperado do ativo
- `r_f` = taxa livre de risco (Selic/CDI no Brasil)
- `β` = beta do ativo
- `r_m - r_f` = prêmio de risco do mercado (ERP)

### Indicadores de Retorno Ajustado ao Risco

**Sharpe Ratio:**
```
Sharpe = (r_p - r_f) / σ_p
```

**Sortino Ratio:**
```
Sortino = (r_p - r_f) / σ_downside
```

**Treynor Ratio:**
```
Treynor = (r_p - r_f) / β_p
```

| Indicador | Usa como risco | Melhor para |
|-----------|---------------|-------------|
| Sharpe | Desvio padrão total | Portfolios completos |
| Sortino | Desvio downside | Avaliar proteção em quedas |
| Treynor | Beta | Ativos dentro de portfolio |

---

## How to Apply

1. **Calcule o retorno esperado** via CAPM ou dados históricos
2. **Meça o risco** via desvio padrão e beta
3. **Compare o Sharpe Ratio** entre alternativas
4. **Verifique se o retorno compensa o risco** — ROIC > WACC
5. **Considere seu perfil**: [[risk-tolerance|tolerância ao risco]] pessoal

---

## Examples

> [!example] Retorno esperado via CAPM
> "EnerBR S.A." com β = 1,3, Selic 13,25%, ERP 6%:
> ```
> E(r) = 13,25% + 1,3 × 6% = 21,05%
> ```

> [!example] Sharpe Ratio de dois fundos
> Fundo A: retorno 18%, vol 12%
> Fundo B: retorno 22%, vol 20%
> CDI: 13%
> ```
> Sharpe A = (18% - 13%) / 12% = 0,42
> Sharpe B = (22% - 13%) / 20% = 0,45
> ```
> Fundo B tem melhor retorno ajustado ao risco.

---

## Gotchas

> [!warning] Cuidados
> - **Volatilidade ≠ risco**: Buffett diz que "risco é perda permanente de capital"
> - **Beta histórico muda**: passado pode não prever o futuro
> - **CAPM tem limitações**: assume mercados eficientes e distribuições normais
> - **Sharpe negativo é enganoso**: não compare Sharpes negativos
> - **Risco de cauda**: eventos extremos são subestimados

---

## Brazilian Context

- **Taxa livre de risco**: use Selic ou CDI (entre as mais altas do mundo)
- **Prêmio de risco (ERP) Brasil**: historicamente 4-7% acima da Selic
- **Risco-país (CDS)**: prêmio extra para estrangeiros
- **Alta correlação Ibovespa-commodities**: componente commodity no beta
- **Câmbio como risco**: para investimentos internacionais

---

## Formulas

```
# Variância e Desvio Padrão
σ² = Σ(r_i - r̄)² / (n-1)
σ = √σ²

# Beta
β = Cov(r_i, r_m) / Var(r_m)

# CAPM
E(r) = r_f + β × (r_m - r_f)

# Retorno Ajustado ao Risco
Sharpe = (r_p - r_f) / σ_p
Sortino = (r_p - r_f) / σ_downside
Treynor = (r_p - r_f) / β_p
```

---

## References

- Markowitz, H. — *Portfolio Selection* (1952)
- Sharpe, W. — *Capital Asset Prices* (1964)
- Damodaran, A. — *Investment Valuation*
- Taleb, N.N. — *The Black Swan*

---

## Related

- [[diversification]] — Reduzir risco não-sistemático
- [[portfolio-theory-mpt]] — Teoria moderna do portfólio
- [[factor-investing]] — Fatores de risco precificados
- [[risk-tolerance]] — Perfil de risco pessoal
- [[compound-interest]] — Retorno composto
- [[valuation-dcf]] — Taxa de desconto reflete risco
- [[behavioral-finance]] — Vieses na percepção de risco
