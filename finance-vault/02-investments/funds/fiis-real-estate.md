---
tags: [finance, investments, funds, fiis, real-estate, brazil]
status: active
complexity: intermediate
context: br
updated: 2026-04-07
aliases: [FIIs, Fundos Imobiliários, Real Estate Funds]
---

# FIIs (Fundos Imobiliários)

## Overview

FIIs (Fundos de Investimento Imobiliário) são fundos brasileiros que investem em ativos imobiliários — imóveis físicos, recebíveis ou outros FIIs — e distribuem **mensalmente** a maior parte da receita aos cotistas. Sua maior atratividade: **dividendos são isentos de IR para pessoa física** (com regras específicas), tornando-os o veículo favorito de quem busca renda passiva no Brasil.

O mercado de FIIs cresceu de R$ 60 bi em 2018 para mais de R$ 200 bi em 2024, com mais de 2 milhões de investidores.

---

## Core Concepts

### Tipos de FIIs

- **Tijolo**: detêm imóveis físicos
  - **Lajes corporativas** (HGRE, HGLG)
  - **Shopping centers** (XPML, HSML)
  - **Logística/galpões** (HGLG, BTLG, VILG)
  - **Varejo** (HGBS, VISC)
  - **Hospitais e educacionais** (HCRI)
  - **Hotéis** (XPHT)
- **Papel**: detêm recebíveis (CRIs)
  - **CRI High Grade** (KNCR, BCRI)
  - **CRI High Yield** (HCTR, DEVA)
- **Híbridos**: misturam tijolo e papel
- **FOFs**: fundos de fundos imobiliários (KFOF, BCFF)
- **Desenvolvimento**: investem em construção (mais arriscados)

### Métricas-Chave

**Dividend Yield (DY)**:
```
DY = Distribuição 12m / Preço da cota
```

**P/VPA (Price-to-Book)**:
```
P/VPA = Preço da cota / Valor patrimonial
```

P/VPA < 1 sugere desconto sobre o patrimônio (oportunidade ou red flag).

**Vacância**:
- **Física**: % de área desocupada
- **Financeira**: % da receita esperada não recebida

**Cap Rate**: Receita líquida / Valor do imóvel.

### IFIX

Índice de Fundos Imobiliários da B3, equivalente do Ibovespa para FIIs.

---

## How to Apply

### Como Investir

1. Abrir conta em corretora
2. Pesquisar tickers (sufixo "11")
3. Comprar via home broker (1 cota = ~R$ 100 tipicamente)
4. Receber **dividendos mensais** automaticamente
5. **DARF não necessária** para dividendos (isentos)

### Critérios de Seleção

| Critério | Bom Sinal |
|----------|-----------|
| DY (12m) | 8-12% (mas não muito acima — red flag) |
| P/VPA | 0,90-1,05 |
| Vacância | < 10% |
| Liquidez diária | > R$ 500k/dia |
| Nº de imóveis | > 5 (diversificação interna) |
| Inquilino dominante | < 30% da receita |
| Gestora | reconhecida (XP, BTG, Kinea, BlueMacaw) |

### Diversificação

> [!tip] Carteira Modelo
> 8-15 FIIs distribuídos entre:
> - 30% Logística (HGLG, BTLG)
> - 25% Lajes corporativas (HGRE, BRCR)
> - 20% Recebíveis (KNCR, BCRI)
> - 15% Shopping (XPML, HSML)
> - 10% FOFs (BCFF) ou outros

---

## Examples

> [!example] Cálculo de Renda Passiva
> R$ 200.000 em FIIs com DY médio de 9% a.a.:
> Renda mensal = R$ 200k × 0,09 / 12 = **R$ 1.500/mês isentos**
> Equivalente bruto em CDI a 12% (com 15% IR): R$ 1.770 (precisaria ~R$ 177k)

---

## Gotchas

> [!warning] Erros Comuns
> - **DY muito alto**: pode ser sinal de problema (cota caiu por motivo)
> - **FII de monoinquilino**: risco concentrado no inquilino
> - **Confundir P/VPA com DCF**: VPA é contábil, pode estar defasado
> - **FOFs caros**: dupla camada de taxas
> - **Ignorar vacância tendência**: vacância subindo pré-anuncia queda de DY
> - **Comprar antes da emissão**: novas emissões diluem o yield

> [!warning] Regra dos Cotistas
> Para manter isenção de IR sobre dividendos:
> - FII deve ter 50+ cotistas
> - Cotista PF deve ter < 10% do fundo
> - Cotas devem ser negociadas em bolsa

---

## Brazilian Context

### Tributação

- **Dividendos**: **isentos** de IR para PF (cumprindo regras)
- **Ganho de capital na venda**: 20% (sem isenção R$ 20k)
- **Day trade**: 20%
- **DARF**: até último dia útil do mês seguinte (cód. 6015)

### Riscos Específicos

- **Reforma tributária** (PL 1087): proposta de tributar dividendos a 15% — acompanhar
- **Risco de juros**: Selic alta = competição com renda fixa, pressão sobre cotas
- **Risco imobiliário**: vacância, inadimplência, depreciação
- **Liquidez vs B3 ações**: spreads maiores

> [!info] Onde Acompanhar
> - **Funds Explorer**: maior portal de análise de FIIs (gratuito)
> - **Status Invest**: análise rápida e screener
> - **B3**: emissões, atos e fatos relevantes
> - **Relatórios mensais**: cada FII publica RG mensal

---

## Formulas

```
# Dividend Yield
DY = Distribuição (12m) / Preço cota

# P/VPA
P/VPA = Preço cota / VPA por cota

# Cap Rate
Cap Rate = NOI anual / Valor do imóvel

# Yield on Cost (yield sobre preço de compra)
YoC = Distribuição atual / Preço de compra

# Renda mensal
Renda = Patrimônio × DY / 12
```

---

## References

- Funds Explorer — fundsexplorer.com.br
- B3 — *Manual de FIIs*
- ANBIMA — *Códigos de FIIs*
- Mendonça, B. — *FIIs: Investindo em Renda Passiva*

---

## Related

- [[etfs]] — Outro veículo de bolsa
- [[fundos-de-investimento]] — Estrutura
- [[dividends]] — Estratégia paralela
- [[fire-movement]] — FIIs como base de FIRE BR
- [[tax-optimization-br]] — Isenção de IR
- [[capital-allocation]] — Posição no portfólio
- [[acronyms-br]] — IFIX, FII
