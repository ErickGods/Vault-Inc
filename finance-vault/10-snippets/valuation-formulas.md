---
tags:
  - finance
  - snippets
  - valuation
aliases:
  - Fórmulas de Valuation
  - Valuation Cheatsheet
complexity: intermediate
context: global
created: 2026-04-06
updated: 2026-04-06
---

# Fórmulas de Valuation

> [!info] Referência Rápida
> Compilação das principais fórmulas de valuation utilizadas em análise fundamentalista. Para aprofundamento, consulte as notas específicas de cada método.

---

## Discounted Cash Flow (DCF)

### Free Cash Flow to Firm (FCFF)

```
FCFF = EBIT × (1 - Tax Rate) + D&A - CapEx - ΔWorking Capital
```

- **EBIT**: Lucro antes de juros e impostos
- **Tax Rate**: Alíquota efetiva de impostos
- **D&A**: Depreciação e amortização
- **CapEx**: Investimentos em capital fixo
- **ΔWorking Capital**: Variação do capital de giro

> Exemplo: EBIT = R$100M, Tax = 34%, D&A = R$20M, CapEx = R$25M, ΔWC = R$5M
> FCFF = 100 × 0.66 + 20 - 25 - 5 = R$56M

### Free Cash Flow to Equity (FCFE)

```
FCFE = Net Income + D&A - CapEx - ΔWorking Capital + Net Borrowing
```

- **Net Income**: Lucro líquido
- **Net Borrowing**: Emissão líquida de dívida (captações - amortizações)

### Weighted Average Cost of Capital (WACC)

```
WACC = (E / V) × Ke + (D / V) × Kd × (1 - Tax Rate)
```

- **E**: Valor de mercado do equity
- **D**: Valor de mercado da dívida
- **V**: E + D (valor total da firma)
- **Ke**: Custo do equity (via CAPM: Rf + β × (Rm - Rf))
- **Kd**: Custo da dívida antes de impostos

> Exemplo: E/V = 60%, Ke = 14%, D/V = 40%, Kd = 10%, Tax = 34%
> WACC = 0.60 × 14% + 0.40 × 10% × 0.66 = 8.4% + 2.64% = 11.04%

### Terminal Value (Perpetuidade com Crescimento)

```
TV = FCFF_n × (1 + g) / (WACC - g)
```

- **FCFF_n**: Fluxo de caixa livre no último ano projetado
- **g**: Taxa de crescimento na perpetuidade (geralmente PIB nominal ou inflação)

> Exemplo: FCFF_5 = R$80M, g = 4%, WACC = 11%
> TV = 80 × 1.04 / (0.11 - 0.04) = R$1.188,6M

### Valor Intrínseco (DCF Completo)

```
Valor Intrínseco = Σ [FCFFt / (1 + WACC)^t] + TV / (1 + WACC)^n
```

Detalhes completos em [[valuation-dcf]].

---

## Valuation por Múltiplos

### Price-to-Earnings (P/E)

```
P/E = Preço por Ação / Lucro por Ação (LPA)
```

- P/E alto pode indicar expectativa de crescimento ou sobrevalorização
- Comparar com peers do mesmo setor

### Price-to-Book (P/B)

```
P/B = Preço por Ação / Valor Patrimonial por Ação (VPA)
```

- P/B < 1 pode indicar subvalorização (ou destruição de valor)

### EV/EBITDA

```
EV/EBITDA = Enterprise Value / EBITDA
```

- Múltiplo mais usado para comparações entre empresas com estruturas de capital diferentes

### EV/Revenue

```
EV/Revenue = Enterprise Value / Receita Líquida
```

- Útil para empresas pré-lucro ou em crescimento acelerado

### PEG Ratio

```
PEG = (P/E) / Taxa de Crescimento do LPA (%)
```

- PEG < 1 sugere subvalorização relativa ao crescimento
- PEG > 1 sugere sobrevalorização relativa ao crescimento

> Exemplo: P/E = 15, Crescimento LPA = 20% → PEG = 15/20 = 0.75

Detalhes em [[valuation-multiples]] e [[key-ratios]].

---

## Modelos de Dividendos

### Gordon Growth Model (GGM)

```
P0 = D1 / (Ke - g)
```

- **D1**: Dividendo esperado no próximo período (D0 × (1 + g))
- **Ke**: Taxa de retorno exigida pelo acionista
- **g**: Taxa de crescimento sustentável dos dividendos

> Exemplo: D0 = R$3.00, g = 5%, Ke = 12%
> P0 = 3.00 × 1.05 / (0.12 - 0.05) = R$45.00

### Dividend Discount Model (DDM) — Multi-estágio

```
P0 = Σ [Dt / (1 + Ke)^t] + Pn / (1 + Ke)^n
```

- Projetar dividendos individuais nos primeiros anos (crescimento alto)
- Usar GGM para calcular Pn no estágio de maturidade

---

## Fórmulas Complementares

### Graham Number

```
Graham Number = √(22.5 × LPA × VPA)
```

- **LPA**: Lucro por ação
- **VPA**: Valor patrimonial por ação
- Preço justo segundo Benjamin Graham (P/E ≤ 15 e P/B ≤ 1.5)

> Exemplo: LPA = R$5.00, VPA = R$30.00
> Graham = √(22.5 × 5 × 30) = √3.375 = R$58.09

Veja também [[graham-net-net]] para a estratégia Net-Net.

### Enterprise Value (EV)

```
EV = Market Cap + Dívida Total - Caixa e Equivalentes
```

- Representa o valor total da empresa para todos os stakeholders (equity + debt holders)
- Algumas variações incluem participações minoritárias e preferred shares

---

## Referências Cruzadas

- [[valuation-dcf]] — Guia detalhado de DCF
- [[valuation-multiples]] — Análise por múltiplos
- [[key-ratios]] — Indicadores fundamentalistas
- [[graham-net-net]] — Estratégia Net-Net de Graham

---

> [!tip] Dica Prática
> Nunca dependa de um único método de valuation. Combine DCF, múltiplos e modelos de dividendos para triangular o valor justo e construir uma faixa de preço-alvo com margem de segurança.
