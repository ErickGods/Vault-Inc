---
tags: [finance, fundamentals, time-value-of-money]
status: active
complexity: basic
context: global
updated: 2026-04-06
aliases: [TVM, Valor do Dinheiro no Tempo]
---

# Time Value of Money (Valor do Dinheiro no Tempo)

## Overview

O conceito de Time Value of Money (TVM) é o alicerce de todas as finanças. Afirma que um real hoje vale mais do que um real no futuro, porque o real de hoje pode ser investido e gerar rendimentos. Este princípio fundamenta desde a precificação de títulos de renda fixa até modelos complexos de [[valuation-dcf|valuation por DCF]].

Quando aplicar: toda vez que você precisa comparar valores em diferentes pontos no tempo — avaliar um investimento, calcular prestações, determinar o preço justo de um ativo, ou decidir entre receber agora ou depois.

> [!quote] Albert Einstein (atribuída)
> "Juros compostos são a oitava maravilha do mundo. Quem entende, ganha; quem não entende, paga."

---

## Core Concepts

### Valor Presente (Present Value — PV)

O valor presente é quanto vale hoje um fluxo de caixa futuro, descontado a uma taxa apropriada.

```
PV = FV / (1 + r)^n
```

Onde:
- `PV` = Valor Presente
- `FV` = Valor Futuro
- `r` = taxa de desconto por período
- `n` = número de períodos

> [!info] Intuição
> Descontar é o inverso de capitalizar. Se capitalizar é "avançar no tempo", descontar é "voltar no tempo".

### Valor Futuro (Future Value — FV)

```
FV = PV × (1 + r)^n
```

### Valor Presente Líquido (Net Present Value — NPV)

```
NPV = -Investimento_Inicial + Σ [FC_t / (1 + r)^t]
```

- NPV > 0 → projeto cria valor → aceitar
- NPV < 0 → projeto destrói valor → rejeitar
- NPV = 0 → projeto rende exatamente a taxa de desconto

### Taxa Interna de Retorno (IRR / TIR)

A TIR é a taxa de desconto que faz o NPV ser igual a zero.

> [!warning] Limitações da TIR
> - Assume reinvestimento dos fluxos à própria TIR (pode ser irrealista)
> - Pode haver múltiplas TIRs em projetos com fluxos não convencionais
> - Não funciona bem para comparar projetos de tamanhos diferentes
> - Prefira NPV quando houver conflito entre critérios

### Anuidades (Annuities)

**Anuidade Ordinária (pagamento no final do período):**

```
PV_anuidade = PMT × [(1 - (1 + r)^(-n)) / r]
FV_anuidade = PMT × [((1 + r)^n - 1) / r]
```

### Perpetuidade (Perpetuity)

```
PV_perpetuidade = PMT / r
```

**Perpetuidade Crescente (Growing Perpetuity):**

```
PV = PMT / (r - g)
```

Onde `g` = taxa de crescimento (g < r). Esta fórmula é a base do Gordon Growth Model em [[valuation-dcf]].

---

## How to Apply

### Passo a Passo para Calcular NPV

1. **Identifique todos os fluxos de caixa** do projeto
2. **Determine a taxa de desconto** apropriada (custo de oportunidade, WACC, ou CDI)
3. **Desconte cada fluxo** ao valor presente
4. **Some todos os valores presentes** e subtraia o investimento inicial
5. **Decida**: NPV > 0 → prossiga; NPV < 0 → recuse

### Quando Usar Cada Ferramenta

| Situação | Ferramenta |
|----------|-----------|
| Avaliar um projeto único | NPV |
| Comparar projetos de mesmo tamanho | TIR |
| Calcular prestação de financiamento | PMT (anuidade) |
| Avaliar dividendos perpétuos | Perpetuidade crescente |
| Precificar título de renda fixa | PV de fluxos + face value |

---

## Examples

> [!example] Valor Futuro de um Investimento
> Investimento: R$ 10.000 a 12% a.a. por 5 anos
> ```
> FV = 10.000 × (1,12)^5 = 10.000 × 1,7623 = R$ 17.623
> ```

> [!example] NPV de um Projeto
> Investimento de R$ 50.000 com fluxos anuais R$ 15.000, R$ 18.000, R$ 22.000, R$ 25.000, R$ 28.000. Taxa: 15% a.a.
> ```
> NPV = -50.000 + 15.000/1,15 + 18.000/1,3225 + 22.000/1,5209
>      + 25.000/1,7490 + 28.000/2,0114
> NPV = -50.000 + 69.341 = R$ 19.341
> ```
> Projeto viável!

> [!example] Prestação de Financiamento
> R$ 200.000, taxa 0,8% a.m., prazo 360 meses
> ```
> PMT = 200.000 × [0,008 / (1 - 1,008^(-360))]
> PMT = R$ 1.697,33/mês
> ```

> [!example] Gordon Growth Model
> Empresa paga R$ 2,50/ação, crescimento 5%, retorno exigido 12%:
> ```
> P = 2,50 × 1,05 / (0,12 - 0,05) = R$ 37,50
> ```

---

## Gotchas

> [!warning] Erros Comuns
> 1. **Misturar taxas e períodos**: usar taxa anual com períodos mensais
> 2. **Ignorar a inflação**: comparar valores nominais sem ajustar
> 3. **Usar taxa errada de desconto**: o desconto deve refletir o risco do fluxo
> 4. **Esquecer o reinvestimento**: a TIR assume reinvestimento à própria TIR
> 5. **Confundir juros simples e compostos**

---

## Brazilian Context

- **Taxas de juros altas**: Selic já chegou a 45% a.a.
- **Inflação relevante**: sempre trabalhe com taxas reais
- **CDI como benchmark**: taxa livre de risco de facto para cálculos de TVM
- **Conversão de taxas**:

```
Taxa mensal → anual: (1 + r_mensal)^12 - 1
Taxa anual → mensal: (1 + r_anual)^(1/12) - 1
Exemplo: 1% a.m. = 12,68% a.a. (não 12%!)
```

> [!info] Taxa Over vs Taxa a.a.
> Taxa DI é expressa em "over" (252 dias úteis): `Taxa a.a. = (1 + taxa_diária)^252 - 1`

---

## Formulas

```
# Valor Futuro / Presente
FV = PV × (1 + r)^n
PV = FV / (1 + r)^n

# NPV
NPV = Σ [FC_t / (1 + r)^t] - I₀

# Anuidades
PV = PMT × [(1 - (1 + r)^(-n)) / r]
FV = PMT × [((1 + r)^n - 1) / r]

# Perpetuidade
PV = PMT / r
PV_crescente = D₁ / (r - g)
```

---

## References

- Damodaran, A. — *Investment Valuation*
- Brealey, Myers & Allen — *Principles of Corporate Finance*
- Assaf Neto, A. — *Matemática Financeira e suas Aplicações*

---

## Related

- [[compound-interest]] — Juros compostos
- [[valuation-dcf]] — DCF usa TVM extensivamente
- [[risk-and-return]] — Taxa de desconto reflete risco
- [[tesouro-direto]] — Precificação de títulos públicos
- [[inflation]] — Taxas reais vs nominais
- [[dividends]] — Gordon Growth Model
- [[financial-statements]] — Fonte dos fluxos de caixa
- [[yield-curve]] — Estrutura a termo das taxas
