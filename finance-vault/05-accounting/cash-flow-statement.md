---
tags: [finance, accounting, cash-flow, dfc]
status: active
complexity: intermediate
context: global
updated: 2026-04-07
aliases: [DFC, Demonstração de Fluxo de Caixa, Cash Flow Statement]
---

# Cash Flow Statement (DFC)

## Overview

A Demonstração de Fluxo de Caixa (DFC) mostra **de onde vem e para onde vai o dinheiro** da empresa em um período. É a única demonstração baseada em **regime de caixa** (não competência), o que a torna a mais difícil de manipular contabilmente.

Uma máxima de analistas: *"Cash is a fact, profit is an opinion."* — Alfred Rappaport. Empresas podem mostrar lucro contábil enquanto queimam caixa; a DFC expõe isso.

---

## Core Concepts

### Estrutura (3 atividades)

```
1. FLUXO DE CAIXA OPERACIONAL (FCO)
   Lucro Líquido
   (+) D&A
   (+/-) Variação de working capital
   (+/-) Outros ajustes
   = FCO

2. FLUXO DE CAIXA DE INVESTIMENTO (FCI)
   (-) Capex (compra de imobilizado)
   (+) Venda de ativos
   (-) Aquisições / participações
   = FCI

3. FLUXO DE CAIXA DE FINANCIAMENTO (FCF_in)
   (+) Captação de dívida
   (-) Amortização de dívida
   (+) Emissão de ações
   (-) Recompra de ações
   (-) Dividendos pagos
   = FCFin

VARIAÇÃO DE CAIXA = FCO + FCI + FCFin
```

### Métodos: Direto vs Indireto

- **Direto**: lista entradas e saídas operacionais (recebimentos de clientes, pagamentos a fornecedores). Mais informativo, raro no Brasil.
- **Indireto**: parte do lucro líquido e ajusta. Padrão no Brasil (CPC 03).

### Free Cash Flow (FCF)

```
FCF = FCO - Capex de Manutenção
```

O **caixa real disponível** para acionistas e credores após reinvestir o necessário para manter o negócio rodando. Mais conservador que FCFF (que usa capex total).

> [!tip] FCF é Rei
> Para Buffett, o que importa é o "owner earnings" — semelhante ao FCF. Lucro contábil pode crescer sem que o acionista veja um centavo.

### FCFF vs FCFE

- **FCFF (Free Cash Flow to Firm)**: caixa antes de pagar credores. Usado em [[valuation-dcf|DCF]] de empresa.
- **FCFE (Free Cash Flow to Equity)**: caixa após pagar credores. Usado em DCF de equity.

```
FCFF = EBIT × (1-t) + D&A - Capex - ΔWC
FCFE = FCFF - Juros×(1-t) + Variação de Dívida
```

---

## How to Apply

### Roteiro de Análise

1. **FCO consistentemente positivo?** Empresas saudáveis geram caixa
2. **FCO ≥ Lucro Líquido?** Sinal de qualidade dos lucros
3. **Capex × Depreciação**: capex muito > depreciação = empresa em expansão
4. **Conversão de caixa** = FCO / EBITDA: ideal > 70%
5. **FCF positivo após dividendos?** Sustentabilidade da política de proventos
6. **Dependência de captação?** FCO + FCI negativos cobertos só por FCFin = sinal de alerta

### Quality of Earnings

```
Quality Ratio = FCO / Lucro Líquido
```

Idealmente próximo ou maior que 1. Muito menor sugere lucros "de papel".

---

## Examples

> [!example] DFC Simplificada (R$ milhões)
> | Item | Valor |
> |------|-------|
> | Lucro Líquido | 200 |
> | (+) D&A | 80 |
> | (-) ΔRecebíveis | (30) |
> | (+) ΔFornecedores | 20 |
> | (-) ΔEstoques | (10) |
> | **FCO** | **260** |
> | (-) Capex | (120) |
> | (-) Aquisição | (50) |
> | **FCI** | **(170)** |
> | (+) Captação dívida | 100 |
> | (-) Amortização | (60) |
> | (-) Dividendos | (80) |
> | **FCFin** | **(40)** |
> | **Variação Caixa** | **50** |
>
> **FCF** = 260 - 120 = 140 → empresa gera caixa após capex
> **Conversão** = 260 / 320 (EBITDA) = 81% → saudável
> **Quality** = 260 / 200 = 1,3 → lucros de qualidade

---

## Gotchas

> [!warning] Sinais de Alerta
> - **FCO < Lucro Líquido sistematicamente**: lucros não viram caixa (red flag clássico)
> - **Capex < Depreciação por anos**: empresa em decadência (consumindo ativos)
> - **Working capital crescendo mais que receita**: clientes não pagando, estoques empilhando
> - **Crescimento financiado só por dívida**: insustentável
> - **Dividendos > FCF**: distribuindo o que não tem
> - **One-time gains em FCO**: vendas de ativos contadas como operacional
> - **Capitalização agressiva**: capex que deveria ser despesa

---

## Brazilian Context

- **CPC 03 / IAS 7** rege a DFC no Brasil
- **JCP pago** aparece em FCFin (como dividendos)
- **IR pago em caixa** divulgado obrigatoriamente
- **Operações descontinuadas** segregadas
- **Variação cambial** sobre caixa em moeda estrangeira segregada

> [!info] Onde Encontrar
> Site da CVM, RI da empresa, ITR (trimestral) e DFP (anual). Sempre cruze com o release de resultados, que costuma trazer FCO, capex e FCF de forma destacada.

---

## Formulas

```
# Free Cash Flow (varia por convenção)
FCF = FCO - Capex
FCFF = EBIT(1-t) + D&A - Capex - ΔWC
FCFE = FCFF - Juros(1-t) + ΔDívida

# Conversão de caixa
Conversão = FCO / EBITDA

# Qualidade dos lucros
Quality = FCO / Lucro Líquido

# Capex como % da receita
Capex Intensity = Capex / Receita

# Cobertura de dividendos
Cobertura = FCF / Dividendos pagos
```

---

## References

- Mulford, C.; Comiskey, E. — *Creative Cash Flow Reporting*
- Penman, S. — *Financial Statement Analysis and Security Valuation*
- CPC 03 — Demonstração dos Fluxos de Caixa

---

## Related

- [[financial-statements]] — Visão geral
- [[income-statement]] — DRE
- [[balance-sheet]] — Balanço
- [[key-ratios]] — Indicadores
- [[red-flags-accounting]] — Manipulações
- [[valuation-dcf]] — Usa FCFF/FCFE
- [[warren-buffett-framework]] — Owner earnings
