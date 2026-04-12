---
tags: [finance, analysis, fundamental, valuation, dcf]
status: active
complexity: advanced
context: global
updated: 2026-04-07
aliases: [DCF, Discounted Cash Flow, Valuation por DCF]
---

# Valuation by DCF

## Overview

Discounted Cash Flow (DCF) é o método de valuation mais rigoroso teoricamente: o valor de uma empresa é o **valor presente de todos os fluxos de caixa que ela gerará no futuro**, descontados pelo custo de capital. É a aplicação direta do [[time-value-of-money|valor do dinheiro no tempo]] aos negócios.

Aswath Damodaran chama DCF de "first principles valuation" — todo outro método (múltiplos, relativo) é atalho que assume implicitamente premissas de DCF.

---

## Core Concepts

### Equação Central

```
Valor da Empresa = Σ [FCFF_t / (1+WACC)^t] + Valor Terminal / (1+WACC)^n
```

Onde:
- FCFF_t = Free Cash Flow to Firm no ano t
- WACC = custo médio ponderado de capital
- Valor Terminal = valor após o horizonte explícito

### FCFF vs FCFE

- **FCFF (Firm)**: caixa antes de pagar credores. Desconta por [[wacc|WACC]]. Resultado: Enterprise Value.
- **FCFE (Equity)**: caixa após credores. Desconta pelo Custo do Equity. Resultado: Equity Value direto.

### Valor Terminal (TV)

Captura o valor após o horizonte explícito (5-10 anos). Dois métodos:

**Gordon Growth (perpetuidade)**:
```
TV = FCFF_n+1 / (WACC - g)
```

**Múltiplo de Saída**:
```
TV = EBITDA_n × Múltiplo de saída
```

> [!warning] TV é Tudo
> Em DCF típico, 60-80% do valor está no Terminal Value. Pequenas mudanças em g ou WACC alteram dramaticamente o resultado. **Seja conservador**.

### WACC

```
WACC = (E/V) × Ke + (D/V) × Kd × (1-t)
```

Custo do Equity via [[capm|CAPM]]:
```
Ke = rf + β × (Rm - rf)
```

### Premissas Críticas

1. **Crescimento de receita** (próximos 5-10 anos)
2. **Margens operacionais** (convergência ou estabilidade)
3. **Capex e working capital** (% da receita)
4. **g perpétuo** (≤ crescimento do PIB de longo prazo)
5. **WACC** (custo de capital atual)

---

## How to Apply

### Processo de 7 Passos

1. **Projetar receita** com base em crescimento histórico, mercado, share
2. **Projetar margens** (EBIT) considerando ciclo e competição
3. **Calcular FCFF** = EBIT(1-t) + D&A - Capex - ΔWC
4. **Determinar WACC** consistente com a estrutura de capital-alvo
5. **Calcular Valor Terminal** com Gordon ou múltiplo
6. **Descontar tudo** ao presente
7. **Ajustar para Equity**: subtrair dívida líquida, somar caixa

```
Equity Value = Enterprise Value - Dívida Líquida + Caixa Excedente
Preço Justo por Ação = Equity Value / Nº de ações
```

### Sensibilidade

Sempre rode tabela de sensibilidade variando WACC (±1pp) e g (±0,5pp). Mostra a fragilidade das estimativas.

---

## Examples

> [!example] DCF Simplificado
> Empresa com FCFF projetado:
> | Ano | FCFF | Fator (WACC=10%) | VP |
> |-----|------|------------------|-----|
> | 1 | 100 | 0,909 | 90,9 |
> | 2 | 110 | 0,826 | 90,9 |
> | 3 | 121 | 0,751 | 90,9 |
> | 4 | 133 | 0,683 | 90,9 |
> | 5 | 146 | 0,621 | 90,7 |
>
> TV (g=3%): 146×1,03 / (0,10-0,03) = 2.149
> VP do TV: 2.149 × 0,621 = 1.334
>
> **Enterprise Value** = 90,9×4 + 90,7 + 1.334 = **1.788**
>
> Se dívida líquida = 300 e nº ações = 100:
> Equity Value = 1.488
> **Preço Justo** = R$ 14,88

---

## Gotchas

> [!warning] Erros Mortais
> - **Hockey stick projections**: receita "decola" no ano 5 sem justificativa
> - **g > crescimento da economia**: matemática implica empresa virar o mundo
> - **WACC inconsistente**: usar D/V atual numa empresa que vai desalavancar
> - **Capex muito baixo**: ignora reinvestimento real
> - **Working capital ignorado**: subestima necessidade de caixa em crescimento
> - **Não fazer sensibilidade**: vender uma única estimativa como "o valor"
> - **Falsa precisão**: planilha com 3 casas decimais e premissas chutadas

> [!tip] Munger
> *"I've never seen Warren do a DCF on paper. He does them in his head."* — DCF mental força a focar no essencial: durabilidade do FCF e custo de capital.

---

## Brazilian Context

Desafios específicos no Brasil:

- **Taxa livre de risco**: usar NTN-B longa (10y) ao invés de Selic
- **Prêmio de risco país**: adicionar 200-400 bps ao Ke (Damodaran publica anualmente)
- **Inflação**: projetar em **termos reais** (deflacionar pelo IPCA) ou nominais com consistência
- **Juros altos** elevam WACC, reduzindo valuations
- **Volatilidade cambial**: para empresas exportadoras, modelar cenários de FX
- **Histórico curto**: regimes monetários quebrados dificultam estimar β

> [!info] Damodaran Brasil
> Aswath Damodaran publica anualmente em [pages.stern.nyu.edu/~adamodar](http://pages.stern.nyu.edu/~adamodar) prêmios de risco país, β setoriais e tax rates por país. Recurso obrigatório.

---

## Formulas

```
# DCF base
EV = Σ [FCFF_t / (1+WACC)^t] + TV/(1+WACC)^n

# FCFF
FCFF = EBIT × (1-t) + D&A - Capex - ΔWC

# Terminal Value (Gordon)
TV = FCFF_{n+1} / (WACC - g)

# WACC
WACC = (E/V)×Ke + (D/V)×Kd×(1-t)

# Custo do Equity (CAPM)
Ke = rf + β×(Rm - rf) + Risco País

# Equity Value
Equity Value = EV - Dívida Líquida + Caixa não-operacional
```

---

## References

- Damodaran, A. — *Investment Valuation* (3rd ed.)
- Koller, Goedhart, Wessels — *Valuation: Measuring and Managing*
- McKinsey — *Valuation Workbook*
- Rappaport, A. — *Creating Shareholder Value*

---

## Related

- [[valuation-multiples]] — Método relativo
- [[warren-buffett-framework]] — Owner earnings (DCF mental)
- [[graham-net-net]] — Abordagem alternativa
- [[financial-statements]] — Inputs do DCF
- [[cash-flow-statement]] — FCFF
- [[time-value-of-money]] — Base teórica
- [[investment-checklist]] — Validação
- [[stock-analysis-template]] — Template prático
