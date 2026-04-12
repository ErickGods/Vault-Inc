---
tags: [finance, accounting, balance-sheet, balanco]
status: active
complexity: intermediate
context: global
updated: 2026-04-07
aliases: [Balanço Patrimonial, BP]
---

# Balance Sheet (Balanço Patrimonial)

## Overview

O Balanço Patrimonial é a fotografia da situação patrimonial da empresa em uma data específica. Ele obedece à equação fundamental:

```
Ativo = Passivo + Patrimônio Líquido
```

Tudo que a empresa **possui** (ativo) é financiado por capital de **terceiros** (passivo) ou capital **próprio** (PL). Diferente da DRE, não cobre um período — é um instantâneo.

---

## Core Concepts

### Estrutura

**ATIVO** (ordenado por liquidez decrescente):
```
Ativo Circulante (curto prazo, <12 meses)
  ├─ Caixa e equivalentes
  ├─ Aplicações financeiras
  ├─ Contas a receber
  ├─ Estoques
  └─ Outros

Ativo Não Circulante
  ├─ Realizável a longo prazo
  ├─ Investimentos (participações)
  ├─ Imobilizado (PP&E)
  └─ Intangível (goodwill, marcas, software)
```

**PASSIVO** (ordenado por exigibilidade decrescente):
```
Passivo Circulante (<12 meses)
  ├─ Fornecedores
  ├─ Empréstimos curto prazo
  ├─ Salários, impostos, dividendos a pagar

Passivo Não Circulante
  ├─ Empréstimos e debêntures longo prazo
  ├─ Provisões
  └─ Imposto diferido

Patrimônio Líquido
  ├─ Capital social
  ├─ Reservas
  ├─ Lucros acumulados
  └─ AOCI (ajustes acumulados)
```

### Conceitos-Chave

**Working Capital** = Ativo Circulante - Passivo Circulante
Mede capital de giro disponível para operação.

**Dívida Líquida** = (Empréstimos CP + LP) - Caixa e Equivalentes
Mede endividamento real após considerar caixa.

**Goodwill** = Ágio pago em aquisições. Não amortizado, mas testado para impairment anualmente.

**Tangible Book Value** = PL - Goodwill - Intangíveis
Valor "duro" do patrimônio.

---

## How to Apply

### Roteiro de Análise

1. **Liquidez**: a empresa consegue pagar contas de curto prazo?
2. **Alavancagem**: quanto deve em relação ao PL e EBITDA?
3. **Qualidade dos ativos**: muito goodwill? Estoques crescendo mais que receita?
4. **Estrutura de capital**: dívida concentrada em curto prazo?
5. **Working capital**: ciclo de conversão de caixa razoável?
6. **Evolução do PL**: cresce com lucros retidos ou com emissões?

### Indicadores Derivados

| Indicador | Fórmula | Saudável |
|-----------|---------|----------|
| Liquidez Corrente | AC / PC | > 1,5 |
| Liquidez Seca | (AC - Estoques) / PC | > 1,0 |
| Dívida/PL | Dívida total / PL | < 1,0 |
| Dívida Líq/EBITDA | DL / EBITDA | < 3,0 |
| ROE | LL / PL médio | > custo de capital |

---

## Examples

> [!example] Balanço Simplificado (R$ milhões)
> | ATIVO | Valor | PASSIVO + PL | Valor |
> |-------|-------|---------------|-------|
> | Caixa | 200 | Fornecedores | 150 |
> | Recebíveis | 300 | Empréstimos CP | 100 |
> | Estoques | 250 | **Passivo Circ.** | **250** |
> | **Ativo Circ.** | **750** | Empréstimos LP | 400 |
> | Imobilizado | 800 | **Passivo NC** | **400** |
> | Intangíveis | 250 | Capital | 500 |
> | **Ativo NC** | **1.050** | Reservas/Lucros | 650 |
> | | | **PL** | **1.150** |
> | **TOTAL** | **1.800** | **TOTAL** | **1.800** |
>
> Working Capital = 750 - 250 = 500
> Dívida Líquida = (100 + 400) - 200 = 300
> DL/EBITDA (com EBITDA=300) = 1,0x → saudável

---

## Gotchas

> [!warning] Sinais de Alerta
> - **Recebíveis crescendo mais que receita**: dificuldade de cobrança ou vendas forçadas
> - **Estoques inflando**: produto encalhando, risco de write-down
> - **Goodwill > 50% do ativo**: risco alto de impairment
> - **Dívida CP > caixa**: risco de refinanciamento
> - **Off-balance sheet items**: operações que não aparecem no balanço (leasing antes do IFRS 16)
> - **Imposto diferido relevante**: dependência de lucros futuros
> - **Reavaliação de ativos**: PL inflado artificialmente

---

## Brazilian Context

- **CPC 27 / IAS 16**: regras para imobilizado e depreciação
- **CPC 06 / IFRS 16**: leasing entra como ativo de uso e passivo (desde 2019)
- **CPC 04 / IAS 38**: intangíveis e P&D
- **JCP a pagar**: aparece no passivo circulante
- **Reserva legal**: 5% do lucro até atingir 20% do capital social (obrigatório)

> [!info] Investidor Iniciante
> Comece pelo balanço para entender se a empresa é **financeiramente sólida** antes de avaliar lucros e crescimento. Empresas alavancadas demais quebram em recessão.

---

## Formulas

```
# Equação fundamental
Ativo = Passivo + Patrimônio Líquido

# Capital de giro
Working Capital = Ativo Circulante - Passivo Circulante

# Dívida líquida
Dívida Líquida = Dívida Bruta - Caixa - Aplicações

# Liquidez
Liquidez Corrente = AC / PC
Liquidez Seca = (AC - Estoques) / PC
Liquidez Imediata = Caixa / PC

# Alavancagem
Dívida/PL = Dívida Total / PL
DL/EBITDA = (Dívida - Caixa) / EBITDA

# Tangible book value
TBV = PL - Goodwill - Intangíveis
```

---

## References

- Iudícibus, S. — *Análise de Balanços*
- White, Sondhi, Fried — *The Analysis and Use of Financial Statements*
- CPC 26 — Apresentação das Demonstrações

---

## Related

- [[financial-statements]] — Visão geral
- [[income-statement]] — DRE
- [[cash-flow-statement]] — DFC
- [[key-ratios]] — Indicadores
- [[red-flags-accounting]] — Manipulações
- [[ratio-formulas]] — Fórmulas
- [[valuation-dcf]] — Usa dívida líquida do balanço
