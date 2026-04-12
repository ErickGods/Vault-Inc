---
tags: [moc, investments, finance-vault]
status: active
complexity: basic
context: global
updated: 2026-04-06
aliases: [Investments MOC, Investimentos]
---

# 📈 Investments — Map of Content

## Visão Geral

Este MOC organiza todo o conhecimento sobre classes de ativos e estratégias de investimento do vault. Navegue por categoria para encontrar guias detalhados sobre cada tipo de investimento.

> [!tip] Como Usar
> Comece pela classe de ativo que mais interessa. Cada arquivo contém fundamentos, fórmulas, exemplos em BRL e adaptações para o mercado brasileiro.

---

## 📊 Visão por Classe de Ativo

| Classe | Risco | Liquidez | Retorno Típico (a.a.) | Complexidade |
|--------|-------|----------|----------------------|-------------|
| Renda Fixa (RF) | Baixo-Médio | Alta | CDI ± 2% | Básica |
| Ações | Alto | Alta | IPCA + 6-8% | Intermediária |
| FIIs | Médio | Média | IPCA + 4-6% | Intermediária |
| ETFs | Médio | Alta | Varia por índice | Básica |
| Cripto | Muito Alto | Alta | Indefinido | Avançada |
| Commodities | Alto | Média | Inflação + 2-4% | Avançada |
| Private Equity | Muito Alto | Baixa | 15-25% | Avançada |
| Opções/Futuros | Muito Alto | Média-Alta | Indefinido | Avançada |

---

## 🏢 Equities (Ações)

| Arquivo | Descrição | Complexidade |
|---------|-----------|-------------|
| [[stocks-fundamentals]] | O que são ações, tipos ON/PN, mercado primário e secundário | Básica |
| [[dividends]] | Dividend Yield, payout, JCP, estratégia de dividendos | Intermediária |
| [[growth-vs-value]] | Growth investing vs value investing, GARP | Intermediária |
| [[brazilian-market-b3]] | Mercado brasileiro, B3, Ibovespa, Novo Mercado | Intermediária |

---

## 🏦 Fixed Income (Renda Fixa)

| Arquivo | Descrição | Complexidade |
|---------|-----------|-------------|
| [[tesouro-direto]] | Títulos públicos brasileiros (Selic, IPCA+, Prefixado) | Básica |
| [[cdb-lci-lca]] | Renda fixa privada, FGC, comparação | Básica |
| [[bonds-international]] | Treasury bonds, corporate bonds, credit rating | Intermediária |
| [[yield-curve]] | Curva de juros, estrutura a termo, inversão | Avançada |

---

## 📦 Funds (Fundos)

| Arquivo | Descrição | Complexidade |
|---------|-----------|-------------|
| [[fundos-de-investimento]] | Tipos de fundos, taxas, come-cotas, regulação CVM | Básica |
| [[etfs]] | ETFs nacionais e internacionais, passive investing | Intermediária |
| [[fiis-real-estate]] | Fundos imobiliários, IFIX, tipos (tijolo/papel/FOF) | Intermediária |

---

## 🌐 Alternatives (Alternativos)

| Arquivo | Descrição | Complexidade |
|---------|-----------|-------------|
| [[crypto-assets]] | Bitcoin, Ethereum, DeFi, regulação BR | Intermediária |
| [[commodities]] | Agrícolas, energia, metais, Brasil exportador | Intermediária |
| [[private-equity]] | PE, VC, FIPs, J-curve | Avançada |

---

## ⚡ Derivatives (Derivativos)

| Arquivo | Descrição | Complexidade |
|---------|-----------|-------------|
| [[options-basics]] | Calls, puts, Greeks, Black-Scholes, estratégias | Avançada |
| [[futures]] | Contratos futuros, mini-índice, mini-dólar, hedge | Avançada |

---

## 📈 Trilha Recomendada para Iniciantes

> [!example] Por Onde Começar
> 1. [[stocks-fundamentals]] → Entender o que são ações
> 2. [[tesouro-direto]] → Primeiro investimento prático
> 3. [[cdb-lci-lca]] → Diversificar em renda fixa
> 4. [[etfs]] → Investir em índices com baixo custo
> 5. [[fiis-real-estate]] → Renda passiva imobiliária

> [!quote] Warren Buffett
> "Nunca invista em um negócio que você não entende."

---

## 📊 Dataview — Todos os Arquivos de Investimento

```dataview
TABLE status, complexity, context, updated
FROM "finance-vault/02-investments"
SORT file.folder ASC, complexity ASC
```

---

## Related

- [[🗺️ Home]] — Dashboard principal
- [[🗺️ Analysis-MOC]] — Frameworks de análise
- [[diversification]] — Princípios de diversificação
- [[capital-allocation]] — Alocação de capital
- [[risk-and-return]] — Relação risco-retorno
- [[portfolio-theory-mpt]] — Teoria moderna do portfólio
