---
tags: [finance, accounting, income-statement, dre]
status: active
complexity: intermediate
context: global
updated: 2026-04-07
aliases: [DRE, Demonstração do Resultado, P&L]
---

# Income Statement (DRE)

## Overview

A Demonstração do Resultado do Exercício (DRE) ou *Income Statement* mostra a performance econômica de uma empresa em um período (trimestre ou ano). Vai da **Receita Bruta** ao **Lucro Líquido**, descontando custos, despesas, juros e impostos. É a primeira demonstração que analistas leem porque revela rentabilidade, escalabilidade e poder de precificação.

Diferente do balanço (foto em uma data), a DRE é um **filme** do período.

---

## Core Concepts

### Estrutura Padrão (IFRS/Brasil)

```
Receita Bruta
(-) Deduções (impostos sobre vendas, devoluções)
= Receita Líquida
(-) Custo dos Produtos/Serviços Vendidos (CMV/CSP)
= Lucro Bruto
(-) Despesas Operacionais (vendas, G&A, P&D)
= EBIT (Lucro Operacional)
(+/-) Resultado Financeiro
(+/-) Outras receitas/despesas
= LAIR (Lucro Antes do IR)
(-) IR e CSLL
= Lucro Líquido
```

### EBITDA

EBIT + Depreciação + Amortização. Proxy popular de geração de caixa operacional, mas **não é fluxo de caixa real** — ignora capex, working capital e juros.

> [!warning] EBITDA Mente
> Charlie Munger: *"I think every time you see the word EBITDA, you should substitute the words 'bullshit earnings'."* Use com cuidado para empresas capital-intensivas.

### Margens

- **Margem Bruta** = Lucro Bruto / Receita Líquida → mede pricing power
- **Margem EBITDA** = EBITDA / Receita Líquida → eficiência operacional
- **Margem Operacional** = EBIT / Receita Líquida
- **Margem Líquida** = Lucro Líquido / Receita Líquida

### Receita Recorrente vs Não-Recorrente

Itens não-recorrentes (ganhos com venda de ativos, baixas, reestruturações) distorcem a comparação. Sempre olhe lucro **ajustado** e **recorrente**.

---

## How to Apply

### Roteiro de Análise

1. **Crescimento de receita**: orgânico × inorgânico, YoY e CAGR 3-5 anos
2. **Estabilidade das margens**: expandindo, estáveis ou contraindo?
3. **Mix de receitas**: produtos vs serviços, recorrente vs one-time
4. **Alavancagem operacional**: mudança em EBIT / mudança em receita
5. **Resultado financeiro**: dependência de juros do caixa ou peso da dívida
6. **Carga tributária efetiva**: anormalidades indicam benefícios temporários

---

## Examples

> [!example] DRE Simplificada (R$ milhões)
> | Item | 2024 | 2025 |
> |------|------|------|
> | Receita Líquida | 1.000 | 1.200 |
> | (-) CMV | (600) | (720) |
> | Lucro Bruto | 400 | 480 |
> | Margem Bruta | 40% | 40% |
> | (-) Despesas Op. | (200) | (240) |
> | EBIT | 200 | 240 |
> | (+) D&A | 50 | 60 |
> | EBITDA | 250 | 300 |
> | Margem EBITDA | 25% | 25% |
> | (-) Resultado Financeiro | (40) | (45) |
> | (-) IR/CSLL | (54) | (66) |
> | **Lucro Líquido** | **106** | **129** |
> | Margem Líquida | 10,6% | 10,75% |

---

## Gotchas

> [!warning] Sinais de Alerta
> - **Receita cresce, margens encolhem**: crescimento via desconto, perda de pricing power
> - **EBIT cresce muito mais que caixa operacional**: provisões, accruals agressivos
> - **Itens "não recorrentes" recorrentes**: empresas que sempre têm "extraordinários"
> - **Mudança de critério contábil**: investigar nas notas explicativas
> - **Receita reconhecida antecipadamente**: comum em SaaS, construção, software
> - **Capitalização de despesas**: P&D ou marketing virando ativo

---

## Brazilian Context

Particularidades da DRE no Brasil:

- **Tributos sobre vendas** (PIS, COFINS, ICMS, ISS) são deduzidos da receita bruta para chegar à líquida
- **JCP** ([[acronyms-br|Juros sobre Capital Próprio]]) é despesa financeira contábil mas remunera acionistas
- **IR/CSLL** combinados = ~34% (alíquota cheia para empresas no lucro real)
- **Subvenções e incentivos fiscais** (Lei do Bem, ICMS subvencionado) inflam lucro líquido

> [!info] Padrão CVM
> Companhias abertas seguem CPC/IFRS. ITR (trimestral) e DFP (anual) auditados disponíveis no site da CVM e RI da empresa.

---

## Formulas

```
# Margens
Margem Bruta = Lucro Bruto / Receita Líquida
Margem EBITDA = EBITDA / Receita Líquida
Margem Líquida = Lucro Líquido / Receita Líquida

# Crescimento
Crescimento YoY = (Receita_t / Receita_t-1) - 1
CAGR = (Receita_final / Receita_inicial)^(1/n) - 1

# Alavancagem operacional
Operating Leverage = Δ% EBIT / Δ% Receita

# LPA / EPS
LPA = Lucro Líquido / Nº de ações
```

---

## References

- Iudícibus, S. — *Análise de Balanços*
- Penman, S. — *Financial Statement Analysis and Security Valuation*
- CPC 26 — Apresentação das Demonstrações Contábeis

---

## Related

- [[financial-statements]] — Visão geral das demonstrações
- [[balance-sheet]] — Foto patrimonial
- [[cash-flow-statement]] — Caixa real
- [[key-ratios]] — Indicadores derivados
- [[red-flags-accounting]] — Manipulações comuns
- [[valuation-multiples]] — Múltiplos baseados em DRE
- [[earnings-call-notes]] — Template para acompanhar resultados
