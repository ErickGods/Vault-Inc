---
tags: [template, docs, finance, equity-research]
status: active
type: template
updated: 2026-04-10
created: 2026-04-10
aliases: [Equity Research Template, Stock Analysis Template]
---

# Equity Research Template

> [!template] Como Usar
> Use este template para gerar relatórios de equity research na Vault Inc. O Equity Research Analyst agent usa este template para produzir análises padronizadas. Também pode ser usado manualmente para análises pessoais.

> [!info] Template Simples
> Para uma análise rápida sem o nível de detalhe de um research report, veja `finance-vault/11-templates/stock-analysis-template.md`.

---

## Template

```yaml
---
tags: [equity-research, {{setor}}, {{ticker}}]
status: {{draft | published | outdated}}
ticker: {{TICKER}}
company: {{Nome da Empresa}}
sector: {{setor}}
market: {{B3 | NYSE | NASDAQ}}
rating: {{Buy | Hold | Sell | Under Review}}
target_price: {{R$ XX,XX ou $XX.XX}}
current_price: {{preço no momento da análise}}
upside: {{+XX% ou -XX%}}
analyst: {{nome ou "AI-Generated"}}
created: {{YYYY-MM-DD}}
updated: {{YYYY-MM-DD}}
---
```

```markdown
# {{TICKER}} — {{Nome da Empresa}}

> **Rating:** {{Buy/Hold/Sell}} | **Target:** {{preço-alvo}} | **Upside:** {{%}} | **Data:** {{YYYY-MM-DD}}

---

## Executive Summary

{{Resumo executivo em 3-5 frases: o que a empresa faz, tese principal de investimento, e a recomendação com justificativa.}}

---

## 1. Company Overview

### Descrição do Negócio
{{O que a empresa faz, modelo de receita, mercado de atuação.}}

### Competitive Moat
{{Vantagens competitivas sustentáveis.}}

| Tipo de Moat | Presente? | Evidência |
|-------------|-----------|-----------|
| Brand | {{sim/não}} | {{evidência}} |
| Network Effects | {{sim/não}} | {{evidência}} |
| Switching Costs | {{sim/não}} | {{evidência}} |
| Cost Advantage | {{sim/não}} | {{evidência}} |
| Intangible Assets | {{sim/não}} | {{evidência}} |

### Management Quality
{{Qualidade da gestão, histórico, alinhamento com acionistas.}}

---

## 2. Financial Analysis

### Income Statement (últimos 5 anos)

| Métrica | {{Y-4}} | {{Y-3}} | {{Y-2}} | {{Y-1}} | {{Y0}} |
|---------|---------|---------|---------|---------|--------|
| Receita Líquida | | | | | |
| EBITDA | | | | | |
| Lucro Líquido | | | | | |
| Margem Bruta | | | | | |
| Margem EBITDA | | | | | |
| Margem Líquida | | | | | |

### Key Ratios

| Ratio | Valor | Setor Avg | Avaliação |
|-------|-------|-----------|-----------|
| P/L | | | {{barato/justo/caro}} |
| EV/EBITDA | | | |
| P/VP | | | |
| ROE | | | |
| ROIC | | | |
| Dividend Yield | | | |
| Dívida Líq./EBITDA | | | |

### Cash Flow

{{Análise do fluxo de caixa: geração operacional, capex, FCF.}}

### Balance Sheet Health

{{Endividamento, liquidez, qualidade dos ativos.}}

---

## 3. Valuation

### DCF — Discounted Cash Flow

| Premissa | Valor | Justificativa |
|----------|-------|---------------|
| WACC | {{%}} | {{base}} |
| Growth Rate (5y) | {{%}} | {{base}} |
| Terminal Growth | {{%}} | {{base}} |
| FCF Base | {{valor}} | {{último FCF normalizado}} |

**Fair Value (DCF):** {{R$ XX,XX}}

### Múltiplos — Análise Relativa

| Peer | P/L | EV/EBITDA | P/VP |
|------|-----|-----------|------|
| {{Peer 1}} | | | |
| {{Peer 2}} | | | |
| {{Peer 3}} | | | |
| **{{TICKER}}** | | | |

**Fair Value (Múltiplos):** {{R$ XX,XX}}

### Price Target Summary

| Método | Fair Value | Peso |
|--------|-----------|------|
| DCF | {{valor}} | {{%}} |
| Múltiplos | {{valor}} | {{%}} |
| **Weighted Target** | **{{valor}}** | **100%** |

---

## 4. Risks

| Risco | Probabilidade | Impacto | Mitigação |
|-------|--------------|---------|-----------|
| {{Risco 1}} | {{Alta/Média/Baixa}} | {{Alto/Médio/Baixo}} | {{como mitigar}} |
| {{Risco 2}} | | | |
| {{Risco 3}} | | | |

---

## 5. Investment Thesis

### Bull Case ({{target otimista}})
{{Cenário otimista — o que precisa dar certo.}}

### Base Case ({{target base}})
{{Cenário base — expectativa realista.}}

### Bear Case ({{target pessimista}})
{{Cenário pessimista — o que pode dar errado.}}

---

## 6. Catalysts & Timeline

| Catalyst | Expectativa | Horizonte |
|----------|-------------|-----------|
| {{Catalisador 1}} | {{impacto esperado}} | {{quando}} |
| {{Catalisador 2}} | | |

---

## Disclaimer

> [!warning] Aviso
> Este relatório é para fins educacionais e de pesquisa. Não constitui recomendação de investimento. Faça sua própria análise antes de investir.

## References

- {{Fonte de dados: RI da empresa, CVM, Bloomberg}}
- [[investment-checklist]] — checklist antes de investir

## Related

- [[🗺️ Investments-MOC]]
- [[growth-vs-value]]
- [[equity-research-workflow]] — workflow completo de pesquisa
```

## Related

- [[equity-research-workflow]] — workflow completo de pesquisa
- [[🗺️ Docs-Home]] — índice de templates
