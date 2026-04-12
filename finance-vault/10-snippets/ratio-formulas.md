---
tags:
  - finance
  - snippets
  - ratios
aliases:
  - Fórmulas de Indicadores
  - Ratio Cheatsheet
complexity: intermediate
context: global
created: 2026-04-06
updated: 2026-04-06
---

# Fórmulas de Indicadores Financeiros

> [!info] Referência Rápida
> Compilação abrangente dos principais indicadores financeiros organizados por categoria. Cada fórmula inclui interpretação resumida para uso em análise fundamentalista.

---

## 1. Rentabilidade (Profitability)

### Return on Equity (ROE)

```
ROE = Lucro Líquido / Patrimônio Líquido
```

Mede a rentabilidade sobre o capital dos acionistas. ROE > 15% é geralmente considerado bom.

### Return on Assets (ROA)

```
ROA = Lucro Líquido / Ativos Totais
```

Mede a eficiência no uso de todos os ativos. Útil para comparar empresas capital-intensive.

### Return on Invested Capital (ROIC)

```
ROIC = NOPAT / Capital Investido
NOPAT = EBIT × (1 - Tax Rate)
Capital Investido = Equity + Dívida Líquida
```

Indicador superior ao ROE pois considera a estrutura de capital completa. ROIC > WACC indica criação de valor.

### Margem Bruta

```
Margem Bruta = (Receita - CPV) / Receita
```

Poder de precificação e eficiência na produção/prestação de serviço.

### Margem EBITDA

```
Margem EBITDA = EBITDA / Receita Líquida
```

Proxy para eficiência operacional antes de efeitos não-caixa e estrutura de capital.

### Margem Operacional

```
Margem Operacional = EBIT / Receita Líquida
```

Rentabilidade operacional após depreciação e amortização.

### Margem Líquida

```
Margem Líquida = Lucro Líquido / Receita Líquida
```

Rentabilidade final considerando todos os custos, despesas, juros e impostos.

---

## 2. Valuation

### Price-to-Earnings (P/E ou P/L)

```
P/E = Preço por Ação / Lucro por Ação (LPA)
```

Quantos anos de lucro atual o mercado paga. Comparar sempre com peers setoriais.

### Price-to-Book (P/B ou P/VPA)

```
P/B = Preço por Ação / Valor Patrimonial por Ação
```

P/B < 1 pode indicar desconto ou destruição de valor. Relevante para bancos e seguradoras.

### EV/EBITDA

```
EV/EBITDA = Enterprise Value / EBITDA
```

Múltiplo mais neutro em relação à estrutura de capital. Mediana do mercado brasileiro: 6-8x.

### Dividend Yield (DY)

```
DY = Dividendos por Ação (12 meses) / Preço por Ação
```

Retorno em dividendos. DY muito alto pode sinalizar corte futuro ou queda de preço.

### Price-to-Free Cash Flow (P/FCF)

```
P/FCF = Market Cap / Free Cash Flow
```

Similar ao P/E mas usa fluxo de caixa livre, menos sujeito a manipulação contábil.

---

## 3. Alavancagem (Leverage)

### Debt-to-Equity (D/E)

```
D/E = Dívida Total / Patrimônio Líquido
```

Grau de alavancagem financeira. D/E > 2 pode indicar risco elevado.

### Net Debt / EBITDA

```
Net Debt / EBITDA = (Dívida Total - Caixa) / EBITDA
```

Quantos anos de EBITDA seriam necessários para quitar a dívida líquida. Acima de 3x requer atenção.

### Interest Coverage Ratio (ICR)

```
ICR = EBIT / Despesas Financeiras
```

Capacidade de pagar juros com o resultado operacional. ICR < 1.5 indica risco de insolvência.

---

## 4. Liquidez (Liquidity)

### Current Ratio (Liquidez Corrente)

```
Current Ratio = Ativo Circulante / Passivo Circulante
```

Capacidade de pagar obrigações de curto prazo. Ideal > 1.0.

### Quick Ratio (Liquidez Seca)

```
Quick Ratio = (Ativo Circulante - Estoques) / Passivo Circulante
```

Liquidez excluindo estoques (menos líquidos). Mais conservador que o Current Ratio.

### Cash Ratio (Liquidez Imediata)

```
Cash Ratio = (Caixa + Equivalentes) / Passivo Circulante
```

Capacidade de pagamento imediato, sem depender de recebíveis ou estoques.

---

## 5. Eficiência (Efficiency)

### Asset Turnover (Giro do Ativo)

```
Asset Turnover = Receita Líquida / Ativos Totais Médios
```

Eficiência na utilização dos ativos para gerar receita.

### Inventory Turnover (Giro de Estoque)

```
Inventory Turnover = CPV / Estoque Médio
```

Quantas vezes o estoque é renovado no período.

### Receivables Turnover (Giro de Recebíveis)

```
Receivables Turnover = Receita Líquida / Contas a Receber Médias
```

Eficiência na cobrança de clientes.

### Days Sales Outstanding (DSO)

```
DSO = (Contas a Receber / Receita) × 365
```

Prazo médio de recebimento em dias.

### Days Payable Outstanding (DPO)

```
DPO = (Contas a Pagar / CPV) × 365
```

Prazo médio de pagamento a fornecedores em dias.

### Cash Conversion Cycle (CCC)

```
CCC = DSO + DIO - DPO
DIO = (Estoque / CPV) × 365
```

Ciclo de conversão de caixa — quantos dias o capital fica "preso". CCC negativo é excelente (ex.: varejo com pagamento antecipado).

---

## 6. Crescimento (Growth)

### CAGR — Compound Annual Growth Rate

```
CAGR = (Valor Final / Valor Inicial)^(1/n) - 1
```

- **n**: Número de anos
- Taxa de crescimento anual composta, suaviza volatilidade entre períodos

> Exemplo: Receita de R$100M para R$161M em 5 anos
> CAGR = (161/100)^(1/5) - 1 = 10%

---

## 7. Risco (Risk)

### Sharpe Ratio

```
Sharpe = (Rp - Rf) / σp
```

- **Rp**: Retorno do portfólio
- **Rf**: Taxa livre de risco (Selic ou CDI)
- **σp**: Desvio padrão dos retornos
- Retorno ajustado ao risco total. Sharpe > 1 é bom, > 2 é excelente.

### Sortino Ratio

```
Sortino = (Rp - Rf) / σ_downside
```

Similar ao Sharpe mas penaliza apenas volatilidade negativa (downside deviation).

### Treynor Ratio

```
Treynor = (Rp - Rf) / β
```

Retorno ajustado ao risco sistemático (beta). Útil para portfólios diversificados.

### Beta (β)

```
β = Cov(Ri, Rm) / Var(Rm)
```

Sensibilidade do ativo em relação ao mercado. β > 1 = mais volátil que o mercado.

### Value at Risk (VaR) — Paramétrico

```
VaR = Valor da Posição × z × σ × √t
```

- **z**: Z-score do nível de confiança (1.65 para 95%, 2.33 para 99%)
- **σ**: Volatilidade diária
- **t**: Horizonte temporal em dias

---

## 8. Análise DuPont

### DuPont 3 Fatores

```
ROE = Margem Líquida × Giro do Ativo × Multiplicador de Equity

ROE = (Lucro Líquido / Receita) × (Receita / Ativos) × (Ativos / PL)
```

Decompõe o ROE em: lucratividade, eficiência e alavancagem.

### DuPont 5 Fatores

```
ROE = Tax Burden × Interest Burden × Margem EBIT × Giro do Ativo × Multiplicador de Equity

ROE = (LL / EBT) × (EBT / EBIT) × (EBIT / Receita) × (Receita / Ativos) × (Ativos / PL)
```

Adiciona o impacto de impostos (Tax Burden) e juros (Interest Burden) à decomposição.

---

## Referências Cruzadas

- [[key-ratios]] — Guia detalhado de indicadores
- [[income-statement]] — Demonstração de Resultado
- [[balance-sheet]] — Balanço Patrimonial
- [[cash-flow-statement]] — Demonstração de Fluxo de Caixa

---

> [!tip] Dica Prática
> Indicadores isolados têm pouco valor. Analise sempre em séries temporais (evolução ao longo dos trimestres/anos) e em comparação relativa com peers do mesmo setor e porte. O contexto setorial muda completamente a interpretação de um mesmo número.

> [!warning] Atenção
> Cuidado com indicadores distorcidos por eventos não-recorrentes (write-offs, ganhos/perdas com câmbio, venda de ativos). Sempre normalize para obter uma visão mais fiel da operação recorrente.
