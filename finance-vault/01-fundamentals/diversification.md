---
tags: [finance, fundamentals, diversification]
status: active
complexity: basic
context: global
updated: 2026-04-06
aliases: [Diversificação]
---

# Diversification (Diversificação)

## Overview

Diversificação é a estratégia de distribuir investimentos entre diferentes ativos, classes, setores e geografias para reduzir o risco total do portfólio sem necessariamente sacrificar retorno. É frequentemente chamada de "o único almoço grátis em finanças", frase atribuída a Harry Markowitz.

O princípio é simples: ativos que não se movem perfeitamente juntos (correlação < 1) reduzem a volatilidade do portfólio quando combinados.

---

## Core Concepts

### Correlação e Covariância

```
Correlação (ρ) = Cov(A, B) / (σ_A × σ_B)
```

- ρ = +1,0 → se movem perfeitamente juntos (zero diversificação)
- ρ = 0,0 → não há relação (boa diversificação)
- ρ = -1,0 → se movem em direções opostas (diversificação máxima)

### Variância do Portfólio (2 ativos)

```
σ²_p = w²_A × σ²_A + w²_B × σ²_B + 2 × w_A × w_B × Cov(A,B)
```

> [!tip] Insight-Chave
> Quando a correlação é menor que 1, a variância do portfólio é MENOR que a média ponderada das variâncias individuais. Isso é a magia da diversificação.

### Fronteira Eficiente

A [[portfolio-theory-mpt|fronteira eficiente]] de Markowitz mostra as combinações de ativos que maximizam retorno para cada nível de risco. Portfólios abaixo da fronteira são ineficientes.

### Quantos Ativos São Suficientes?

- 10-15 ações eliminam ~80% do risco não-sistemático
- 25-30 ações eliminam ~95%
- Além de 40 ações, o benefício marginal é mínimo

> [!warning] Diversificação Excessiva
> "Diworsification" (Peter Lynch): ter tantos ativos que o portfólio se torna um índice caro. Se você quer 50+ ações, compre um [[etfs|ETF]].

---

## How to Apply

### Dimensões de Diversificação

1. **Por classe de ativo**: ações, renda fixa, FIIs, ouro, cripto
2. **Por setor**: bancos, varejo, energia, tecnologia, saúde
3. **Por geografia**: Brasil, EUA, Europa, emergentes
4. **Por moeda**: BRL, USD, EUR
5. **Por prazo**: curto, médio e longo prazo
6. **Por estilo**: growth, value, dividendos

---

## Examples

> [!example] Efeito da diversificação em 2 ativos
> Ativo A: retorno 15%, vol 25%
> Ativo B: retorno 10%, vol 15%
> Correlação: 0,3
> Portfólio 50/50:
> ```
> Retorno = 0,5 × 15% + 0,5 × 10% = 12,5%
> σ²_p = 0,25 × 0,0625 + 0,25 × 0,0225 + 2 × 0,25 × 0,3 × 0,25 × 0,15
> σ_p = 16,4%
> ```
> Média ponderada das vols seria 20%, mas o portfólio tem 16,4% — ganho de 3,6pp.

---

## Gotchas

> [!warning] Armadilhas
> - **Correlações mudam em crises**: ativos "descorrelacionados" tendem a se correlacionar em pânico
> - **Home bias**: brasileiros concentram em ativos locais — Brasil é ~2% do mercado global
> - **Diversificação falsa**: ter 10 ações de bancos não é diversificar
> - **Custo de complexidade**: muitos ativos = mais taxas e impostos

---

## Brazilian Context

Modelo de alocação típico brasileiro:

| Perfil | Renda Fixa | Ações | FIIs | Internacional | Alternativo |
|--------|-----------|-------|------|--------------|-------------|
| Conservador | 70% | 10% | 10% | 5% | 5% |
| Moderado | 40% | 25% | 15% | 15% | 5% |
| Agressivo | 15% | 35% | 15% | 25% | 10% |

> [!info] Regulação
> Fundos de previdência (PGBL/VGBL) têm limites de alocação definidos pela PREVIC e CMN.

---

## Formulas

```
# Correlação
ρ(A,B) = Cov(A,B) / (σ_A × σ_B)

# Variância do Portfólio (2 ativos)
σ²_p = w²_A × σ²_A + w²_B × σ²_B + 2 × w_A × w_B × ρ × σ_A × σ_B

# Retorno do Portfólio
r_p = Σ(w_i × r_i)
```

---

## References

- Markowitz, H. — *Portfolio Selection* (1952)
- Bernstein, W. — *The Intelligent Asset Allocator*
- Swedroe, L. — *The Only Guide to a Winning Investment Strategy*

---

## Related

- [[portfolio-theory-mpt]] — Teoria formal da diversificação
- [[risk-and-return]] — Risco sistemático vs não-sistemático
- [[capital-allocation]] — Como alocar entre classes
- [[etfs]] — Diversificação instantânea via ETF
- [[fiis-real-estate]] — Diversificação imobiliária
- [[factor-investing]] — Diversificação entre fatores
