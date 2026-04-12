---
tags: [finance, fundamentals, financial-statements]
status: active
complexity: intermediate
context: global
updated: 2026-04-06
aliases: [Demonstrações Financeiras, DRE, Balanço, Financial Statements]
---

# Financial Statements (Demonstrações Financeiras)

## Overview

As demonstrações financeiras são os documentos contábeis que revelam a saúde financeira de uma empresa. São a matéria-prima de toda [[valuation-dcf|análise fundamentalista]] e a base para calcular os [[key-ratios|indicadores financeiros]] que guiam decisões de investimento.

Existem três demonstrações principais, cada uma respondendo uma pergunta diferente:

| Demonstração | Pergunta | Analogia |
|-------------|----------|---------|
| [[income-statement\|DRE]] | A empresa é lucrativa? | O "filme" do resultado |
| [[balance-sheet\|Balanço]] | O que a empresa tem e deve? | A "foto" patrimonial |
| [[cash-flow-statement\|DFC]] | A empresa gera caixa? | O "extrato" bancário |

---

## Core Concepts

### DRE — Income Statement

Mostra receitas, custos e despesas em um período:

```
  Receita Bruta
- Deduções (impostos sobre vendas)
= Receita Líquida
- CPV/CMV (Custo dos Produtos/Mercadorias)
= Lucro Bruto
- Despesas Operacionais (SG&A)
= EBIT (Lucro Operacional)
+ Depreciação e Amortização
= EBITDA
- Resultado Financeiro
- IR/CSLL
= Lucro Líquido
```

### Balanço Patrimonial

Equação fundamental: **Ativo = Passivo + Patrimônio Líquido**

- **Ativo**: o que a empresa possui
- **Passivo**: o que a empresa deve
- **PL**: o que pertence aos acionistas

### DFC — Cash Flow Statement

Três atividades:
1. **Operacional (FCO)**: caixa gerado pelo negócio principal
2. **Investimento (FCI)**: capex, aquisições
3. **Financiamento (FCF)**: empréstimos, emissão de ações, dividendos

```
Caixa Final = Caixa Inicial + FCO + FCI + FCF
```

> [!tip] Regra de Ouro
> "Revenue is vanity, profit is sanity, cash is king." Receita é vaidade, lucro é sanidade, caixa é rei.

---

## How to Apply

### Sequência de Análise Recomendada

1. **DRE**: verifique tendência de receita e margens
2. **Balanço**: analise endividamento e liquidez
3. **DFC**: confirme que lucro se traduz em caixa
4. **Indicadores**: calcule [[key-ratios|ratios]] para comparação
5. **Red flags**: busque [[red-flags-accounting|sinais de alerta]]

---

## Examples

> [!example] Análise rápida — "VareBR S.A."
>
> **DRE (12 meses):**
> - Receita Líquida: R$ 1,2 bilhão
> - Margem Bruta: 35%
> - Margem EBITDA: 12%
> - Margem Líquida: 5%
>
> **Balanço:**
> - Ativo Total: R$ 800M
> - Dívida Líquida: R$ 200M
> - PL: R$ 350M
>
> **Indicadores:**
> - ROE = 60M/350M = 17,1% ✅
> - Dívida Líquida/EBITDA = 200M/144M = 1,4x ✅

---

## Gotchas

> [!warning] Cuidados
> - **Lucro não é caixa**: empresa pode ter lucro e queimar caixa
> - **EBITDA não é tudo**: exclui capex, que é vital em indústrias capital-intensive
> - **Balanço é uma foto**: pode ser "maquiado" no fechamento (window dressing)
> - **Notas explicativas importam**: detalhes cruciais ficam nas notas

---

## Brazilian Context

- **CPC/IFRS**: Brasil adota padrões internacionais desde 2010
- **CVM**: empresas listadas publicam trimestralmente (ITR) e anualmente (DFP)
- **Onde encontrar**: site de RI da empresa, CVM (rad.cvm.gov.br), B3
- **Periodicidade**: resultados trimestrais ~45 dias após fim do trimestre

---

## Formulas

```
# Equação do Balanço
Ativo = Passivo + Patrimônio Líquido

# EBITDA
EBITDA = EBIT + Depreciação + Amortização

# Free Cash Flow
FCF = FCO - Capex

# Capital de Giro
WC = Ativo Circulante - Passivo Circulante
```

---

## References

- Assaf Neto, A. — *Estrutura e Análise de Balanços*
- Palepu, Healy & Peek — *Business Analysis and Valuation*
- CVM — rad.cvm.gov.br

---

## Related

- [[income-statement]] — DRE detalhada
- [[balance-sheet]] — Balanço detalhado
- [[cash-flow-statement]] — DFC detalhada
- [[key-ratios]] — Indicadores derivados
- [[red-flags-accounting]] — Sinais de manipulação
- [[valuation-dcf]] — DCF usa dados das demonstrações
- [[valuation-multiples]] — Múltiplos derivam das demonstrações
