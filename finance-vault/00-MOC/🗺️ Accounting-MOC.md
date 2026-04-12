---
tags: [moc, accounting, finance-vault]
status: active
complexity: basic
context: global
updated: 2026-04-06
aliases: [Accounting MOC, Contabilidade]
---

# 📊 Accounting — Map of Content

## Visão Geral

Este MOC organiza o conhecimento contábil essencial para análise de investimentos. Entender demonstrações financeiras é pré-requisito para qualquer análise fundamentalista séria.

> [!quote] Warren Buffett
> "Contabilidade é a linguagem dos negócios. Você tem que ser fluente nela para ser um bom investidor."

---

## 📋 Conteúdo

| Arquivo | Descrição | Complexidade |
|---------|-----------|-------------|
| [[income-statement]] | DRE: da Receita Bruta ao Lucro Líquido | Intermediária |
| [[balance-sheet]] | Balanço Patrimonial: Ativo = Passivo + PL | Intermediária |
| [[cash-flow-statement]] | DFC: fluxos operacional, investimento, financiamento | Intermediária |
| [[key-ratios]] | Indicadores financeiros: rentabilidade, valuation, alavancagem | Intermediária |
| [[red-flags-accounting]] | Red flags contábeis e sinais de manipulação | Avançada |

---

## 🔗 Relação entre as Demonstrações

```
                    ┌──────────────────┐
                    │  INCOME STATEMENT │
                    │       (DRE)       │
                    │  Receita → Lucro  │
                    └────────┬─────────┘
                             │
                    Lucro Líquido alimenta
                             │
         ┌───────────────────┼───────────────────┐
         ▼                                       ▼
┌─────────────────┐                    ┌──────────────────┐
│  BALANCE SHEET   │                    │  CASH FLOW STMT  │
│    (BALANÇO)     │◄──── Variações ───►│      (DFC)        │
│ Ativo = P + PL   │    do Balanço      │ Op + Inv + Fin    │
└─────────────────┘                    └──────────────────┘
```

> [!tip] Dica de Análise
> Sempre analise as três demonstrações em conjunto. Uma empresa pode ter lucro (DRE) mas queimar caixa (DFC).

---

## 📐 Indicadores-Chave Derivados

Os [[key-ratios|indicadores financeiros]] são calculados a partir das demonstrações:

- **Da DRE**: margens (bruta, EBITDA, líquida), LPA
- **Do Balanço**: ROE, ROA, liquidez corrente, D/E
- **Da DFC**: FCF, conversão de caixa, Capex/Revenue
- **Combinados**: ROIC, EV/EBITDA, P/FCF

---

## 🚩 Red Flags

> [!warning] Sinais de Alerta
> - Lucro crescente com caixa operacional decrescente
> - Crescimento de receita muito acima do setor
> - Mudanças frequentes de critérios contábeis
> - Transações com partes relacionadas relevantes
> - Goodwill desproporcional ao ativo total

---

## 📊 Dataview

```dataview
TABLE status, complexity, updated
FROM "finance-vault/05-accounting"
SORT complexity ASC
```

---

## Related

- [[🗺️ Home]] — Dashboard principal
- [[🗺️ Analysis-MOC]] — Frameworks de análise
- [[financial-statements]] — Visão geral das demonstrações
- [[valuation-dcf]] — DCF usa dados contábeis
- [[valuation-multiples]] — Múltiplos derivam das demonstrações
- [[investment-checklist]] — Checklist quantitativo
