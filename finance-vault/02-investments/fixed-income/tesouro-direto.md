---
tags: [finance, investments, fixed-income, tesouro-direto, brazil]
status: active
complexity: basic
context: br
updated: 2026-04-07
aliases: [Tesouro Direto, Títulos Públicos]
---

# Tesouro Direto

## Overview

O Tesouro Direto é o programa do Tesouro Nacional para venda de **títulos públicos federais** ao varejo, criado em 2002 em parceria com a B3. É o investimento mais seguro do Brasil — risco soberano, garantido pelo Tesouro Nacional. Acessível a partir de R$ 30, é o ponto de partida natural para quem começa a investir.

A maior parte da dívida pública brasileira é financiada por estes títulos, distribuídos via instituições intermediárias (corretoras).

---

## Core Concepts

### Tipos de Títulos

| Título | Indexador | Uso ideal |
|--------|-----------|-----------|
| **Tesouro Selic (LFT)** | Selic | Reserva de emergência, curto prazo |
| **Tesouro IPCA+ (NTN-B Princ.)** | IPCA + juro real | Longo prazo, hedge inflação |
| **Tesouro IPCA+ com Juros (NTN-B)** | IPCA + cupons semestrais | Renda passiva |
| **Tesouro Prefixado (LTN)** | Taxa fixa | Apostar em queda de juros |
| **Tesouro Prefixado com Juros (NTN-F)** | Taxa fixa + cupons | Renda fixa prefixada |
| **Tesouro Renda+ / Educa+** | IPCA + juros | Aposentadoria/educação |

### Marcação a Mercado

Títulos prefixados e IPCA+ são marcados diariamente. Se vender antes do vencimento, pode ter:
- **Ágio** (juros caíram desde a compra)
- **Deságio** (juros subiram desde a compra)

> [!warning] Volatilidade
> Tesouro IPCA+ longo (10+ anos) pode oscilar 10-20% no curto prazo. Apenas Tesouro Selic é estável diariamente.

### Tributação

- **IR regressivo**:
  - Até 180 dias: 22,5%
  - 181-360: 20%
  - 361-720: 17,5%
  - 720+ dias: **15%**
- **IOF**: regressivo apenas nos primeiros 30 dias
- **Custódia B3**: 0,20% a.a. (zerada para Tesouro Selic até R$ 10k)

---

## How to Apply

### Como Investir

1. Abrir conta em corretora ou banco (todas oferecem TD)
2. Transferir recursos
3. Acessar área de Tesouro Direto
4. Escolher título e quantidade
5. Confirmar compra

**Mínimo**: ~R$ 30 (1% de um título)
**Liquidez**: D+1 (Tesouro Nacional recompra diariamente)

### Por Objetivo

| Objetivo | Título Recomendado |
|----------|-------------------|
| Reserva de emergência | Tesouro Selic 2027 |
| Aposentadoria (25+ anos) | Tesouro IPCA+ 2045/2050 |
| Compra de imóvel (5a) | Tesouro IPCA+ 2029 |
| Educação dos filhos | Tesouro Educa+ |
| Renda passiva | Tesouro IPCA+ com Juros |

---

## Examples

> [!example] Cálculo Líquido — Tesouro Selic
> Investe R$ 10.000 em Tesouro Selic com Selic = 12%
> Em 2 anos: R$ 12.544 (bruto)
> IR (15%) sobre R$ 2.544 = R$ 381,60
> Líquido: **R$ 12.162,40** (≈ 10,2% a.a. líquido)

> [!example] Tesouro IPCA+ 2045
> Compra a IPCA + 6% a.a.
> Inflação média projetada: 4% → retorno nominal ~10% a.a.
> Em 20 anos, R$ 10k vira ~R$ 67k (nominais), ~R$ 32k (reais)

---

## Gotchas

> [!warning] Erros Comuns
> - **Vender prefixado/IPCA+ na baixa**: marcação a mercado machuca em alta de juros
> - **Achar que Tesouro Selic = poupança**: Selic supera poupança em ~3pp
> - **Ignorar IR e custódia** ao comparar com renda fixa privada
> - **Comprar prefixado curto** quando juros vão subir
> - **Confundir IPCA+ Principal com IPCA+ Juros**: o segundo paga cupom semestral (tributado)

---

## Brazilian Context

### Vantagens vs CDB/LCI/LCA

- **Risco soberano** (vs risco bancário com FGC)
- **Liquidez diária garantida**
- **Sem limite de valor** (FGC limita a R$ 250k)
- **Disponível para qualquer corretora**

### Desvantagens

- **Sem isenção de IR** (LCI/LCA são isentas)
- **Custódia B3** (0,20% a.a.)
- **Marcação a mercado** assusta iniciantes

> [!info] Tesouro Direto App
> Aplicativo oficial gratuito permite acompanhar carteira, simular investimentos e fazer aplicações. Recomendado.

---

## Formulas

```
# Retorno bruto Selic
Retorno = (1 + Selic)^t - 1 (aproximação)

# Retorno IPCA+
Retorno_real = (1 + juro_real)^t - 1
Retorno_nominal = (1+IPCA)(1+juro_real) - 1

# Marcação a mercado (preço ↔ taxa)
Δ% Preço ≈ -Duration × Δ taxa

# Líquido após IR
Líquido = Bruto - (Bruto - Investimento) × Alíquota
```

---

## References

- Tesouro Nacional — *Tesouro Direto*: tesourodireto.com.br
- BCB — *Demonstrativo da Dívida Pública*
- Cerbasi, G. — *Investimentos Inteligentes*

---

## Related

- [[cdb-lci-lca]] — Renda fixa privada
- [[bonds-international]] — Treasuries
- [[yield-curve]] — Estrutura a termo
- [[inflation]] — IPCA+
- [[selic-and-monetary-policy]] — Selic
- [[tax-optimization-br]] — IR regressivo
- [[emergency-fund]] — Tesouro Selic
- [[acronyms-br]] — LFT, NTN-B, LTN
