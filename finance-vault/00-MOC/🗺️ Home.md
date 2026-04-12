---
tags: [moc, home, finance-vault]
status: active
complexity: basic
context: global
updated: 2026-04-06
aliases: [Finance Vault, Home]
---

# 🗺️ Finance Knowledge Vault

## Visão Geral

Este vault é o repositório central de conhecimento financeiro estruturado para uso no Obsidian. Funciona como um segundo cérebro para finanças pessoais, investimentos, análise de mercado, valuation, contabilidade e educação financeira. O vault serve tanto para estudo quanto para consulta rápida durante tomadas de decisão reais de investimento.

> [!info] Como Navegar
> Use os MOCs (Maps of Content) abaixo como ponto de entrada para cada domínio. O Graph View do Obsidian revela a rede de conhecimento financeiro conectada por centenas de wikilinks.

---

## 🧭 Maps of Content

| MOC | Domínio | Descrição |
|-----|---------|-----------|
| [[🗺️ Investments-MOC\|📈 Investments]] | Classes de ativos e estratégias | Ações, renda fixa, fundos, cripto, derivativos |
| [[🗺️ Analysis-MOC\|🔍 Analysis]] | Frameworks de análise | Fundamentalista, técnica, quantitativa, macro |
| [[🗺️ Personal-Finance-MOC\|💰 Personal Finance]] | Finanças pessoais | Orçamento, reserva, FIRE, impostos |
| [[🗺️ Macroeconomics-MOC\|🌍 Macroeconomics]] | Macroeconomia | Ciclos, juros, indicadores globais |
| [[🗺️ Accounting-MOC\|📊 Accounting]] | Contabilidade | DRE, balanço, fluxo de caixa, indicadores |

---

## ⚡ Quick Formulas — As 10 Mais Usadas

### 1. P/L (Price-to-Earnings)
```
P/L = Preço da Ação / Lucro por Ação (LPA)
```

### 2. EV/EBITDA
```
EV/EBITDA = (Market Cap + Dívida Líquida) / EBITDA
```

### 3. ROE (Return on Equity)
```
ROE = Lucro Líquido / Patrimônio Líquido
```

### 4. ROA (Return on Assets)
```
ROA = Lucro Líquido / Ativo Total
```

### 5. ROIC (Return on Invested Capital)
```
ROIC = NOPAT / Capital Investido
NOPAT = EBIT × (1 - Taxa de IR)
```

### 6. Dividend Yield
```
DY = Dividendos por Ação (12m) / Preço da Ação × 100
```

### 7. Margem Líquida
```
Margem Líquida = Lucro Líquido / Receita Líquida × 100
```

### 8. CAGR (Compound Annual Growth Rate)
```
CAGR = (Valor Final / Valor Inicial)^(1/n) - 1
```

### 9. Sharpe Ratio
```
Sharpe = (Retorno do Portfolio - Taxa Livre de Risco) / Desvio Padrão
```

### 10. DCF Simplificado
```
Valor = Σ [FCF_t / (1 + WACC)^t] + [Terminal Value / (1 + WACC)^n]
```

> [!tip] Dica Prática
> Mantenha estas fórmulas acessíveis. Com o tempo, você as calcula mentalmente ao ler relatórios de resultados.

---

## ✅ Decision Framework — Checklist Antes de Investir

- [ ] **Entendo o negócio?** Consigo explicar em 3 frases o que a empresa faz e como ganha dinheiro?
- [ ] **Moat identificável?** A empresa tem [[warren-buffett-framework|vantagem competitiva]] sustentável?
- [ ] **Números saudáveis?** [[key-ratios|Indicadores]] de rentabilidade, endividamento e crescimento adequados?
- [ ] **Valuation atrativo?** O preço atual oferece [[valuation-dcf|margem de segurança]]?
- [ ] **Riscos mapeados?** Identifiquei os principais riscos (regulatório, concorrência, macro)?
- [ ] **Tamanho da posição?** O [[position-sizing|dimensionamento]] está de acordo com meu perfil?
- [ ] **Sem vieses?** Revisei [[cognitive-biases|vieses cognitivos]] — não estou comprando por FOMO?
- [ ] **Tese documentada?** Registrei a tese de investimento por escrito?

> [!warning] Regra de Ouro
> Se você não consegue explicar por que está comprando sem olhar para o gráfico de preço, você não deveria comprar.

---

## 🇧🇷 Market Context BR — Indicadores a Monitorar

| Indicador | O que é | Onde acompanhar |
|-----------|---------|-----------------|
| **Selic** | Taxa básica de juros (Copom) | bcb.gov.br |
| **IPCA** | Inflação oficial (IBGE) | ibge.gov.br |
| **Ibovespa** | Índice da bolsa brasileira | b3.com.br |
| **USD/BRL** | Câmbio dólar/real | bcb.gov.br |
| **CDI** | Taxa interbancária (benchmark RF) | b3.com.br |
| **DI Futuro** | Expectativa de juros futuros | b3.com.br |
| **IGP-M** | Inflação do aluguel (FGV) | fgv.br |
| **PIB** | Crescimento econômico (IBGE) | ibge.gov.br |

> [!info] Calendário Econômico
> - **Copom**: reuniões a cada 45 dias (define Selic)
> - **IPCA**: divulgação mensal pelo IBGE (~dia 10)
> - **PIB**: divulgação trimestral pelo IBGE
> - **Payroll (US)**: primeira sexta-feira do mês

---

## 📊 Dashboard — Notas Recentes

```dataview
TABLE status, complexity, context, updated
FROM "finance-vault"
WHERE updated >= date(today) - dur(30 days)
SORT updated DESC
LIMIT 15
```

---

## 🔍 Quick Access por Complexidade

### Básico — Comece Aqui
- [[time-value-of-money]] — Fundamento de tudo em finanças
- [[compound-interest]] — A oitava maravilha do mundo
- [[emergency-fund]] — Primeiro passo prático
- [[budgeting-methods]] — Controle financeiro
- [[stocks-fundamentals]] — O que são ações

### Intermediário — Aprofundando
- [[key-ratios]] — Indicadores essenciais
- [[valuation-multiples]] — Análise relativa
- [[behavioral-finance]] — Entendendo seus vieses
- [[capital-allocation]] — Alocação estratégica
- [[fiis-real-estate]] — Fundos imobiliários

### Avançado — Nível Profissional
- [[valuation-dcf]] — Valuation intrínseco
- [[portfolio-theory-mpt]] — Teoria moderna do portfólio
- [[options-basics]] — Derivativos
- [[factor-investing]] — Smart beta e fatores
- [[backtesting-basics]] — Teste de estratégias

---

## 📁 Recursos Rápidos

- [[valuation-formulas]] — Cheatsheet de fórmulas de valuation
- [[ratio-formulas]] — Cheatsheet de indicadores financeiros
- [[python-finance-snippets]] — Código Python para finanças
- [[stock-analysis-template]] — Template para análise de ações
- [[investment-checklist]] — Checklist completo de investimento
- [[trade-journal-template]] — Diário de trades

---

*Vault criado em 2026-04-06. Mantenha os arquivos atualizados e adicione novas notas conforme seu conhecimento evolui.*
