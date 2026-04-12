---
tags: [finance, frameworks, capital-allocation, asset-allocation]
status: active
complexity: intermediate
context: global
updated: 2026-04-07
aliases: [Alocação de Capital, Asset Allocation]
---

# Capital Allocation

## Overview

Capital Allocation é o processo de distribuir capital entre **classes de ativos** (ações, renda fixa, imóveis, alternativos, caixa) de acordo com objetivos, horizonte e tolerância a risco do investidor. Estudos clássicos (Brinson, Hood, Beebower 1986) mostram que **>90% da variabilidade de retornos de longo prazo vem da alocação**, não da seleção de ativos individuais.

A decisão de alocação é a alavanca mais importante do investidor — mais do que stock-picking ou market-timing.

---

## Core Concepts

### Strategic vs Tactical Allocation

- **Strategic (SAA)**: alocação-alvo de longo prazo baseada em objetivos e perfil
- **Tactical (TAA)**: desvios de curto prazo baseados em visão de mercado

### Os 3 Inputs Fundamentais

1. **Objetivos**: aposentadoria, compra de imóvel, geração de renda
2. **Horizonte**: curto (<3a), médio (3-10a), longo (>10a)
3. **Tolerância a risco**: capacidade financeira × tolerância emocional

### Regras Heurísticas Clássicas

> [!tip] Regra dos "100 menos a idade"
> Percentual em ações = 100 - idade. Aos 30 anos: 70% ações, 30% bonds.
> Versão moderna usa 110 ou 120 dada maior longevidade.

### Bucket Strategy

Dividir capital em "baldes" por horizonte:
- **Curto prazo** (0-2a): caixa e equivalentes
- **Médio prazo** (2-7a): bonds e renda fixa
- **Longo prazo** (7+a): ações e alternativos

---

## How to Apply

### Processo de 5 Passos

1. **Definir metas e horizontes** explicitamente em valores e prazos
2. **Avaliar perfil de risco** via questionário e simulação de drawdowns
3. **Construir alocação-alvo** consistente com [[portfolio-theory-mpt|MPT]]
4. **Implementar** via instrumentos eficientes ([[etfs]], fundos, ações diretas)
5. **Rebalancear** quando desvios excederem bandas (ex: ±5%)

### Métodos de Rebalanceamento

| Método | Descrição | Prós/Contras |
|--------|-----------|--------------|
| Calendar | Trimestral/anual | Simples, mas ignora oportunidades |
| Threshold | ±5% do alvo | Mais eficiente, mais ativo |
| Híbrido | Anual + threshold | Equilibrado |

---

## Examples

> [!example] Investidor Moderado, 40 anos, Brasil
> **Alocação-alvo:**
> - Renda Fixa: 40% (Tesouro IPCA+ 50%, CDBs 30%, Debêntures 20%)
> - Ações Brasil: 25% (50% large caps, 30% small caps, 20% dividendos)
> - Ações Internacionais: 15% (S&P 500, MSCI World)
> - FIIs: 12%
> - Ouro/Cripto: 5%
> - Caixa: 3%
>
> **Rebalanceamento**: anual + threshold ±5%

---

## Gotchas

> [!warning] Erros Comuns
> - **Recência**: aumentar peso da classe que mais subiu recentemente
> - **Home bias**: sub-alocar internacional por familiaridade com Brasil
> - **Confundir liquidez com segurança**: caixa parece seguro mas perde para inflação
> - **Ignorar correlações**: ações + FIIs + cripto podem se mover juntos em crises
> - **Rebalancear demais**: gera custos e impostos sem benefício marginal

---

## Brazilian Context

Particularidades da alocação no Brasil:

- **Selic alta** distorce comparação risk/return — renda fixa pública é competitiva com ações
- **IR regressivo** em renda fixa favorece prazos longos (>720d → 15%)
- **LCI/LCA** isentos de IR melhoram retorno líquido
- **Câmbio volátil** torna exposição USD um hedge natural ao risco-Brasil
- **Previdência** (PGBL/VGBL) com benefícios fiscais para acúmulo de longo prazo

> [!info] Allocação Global Recomendada
> Mesmo investidores conservadores deveriam ter 15-25% em ativos internacionais para reduzir risco-país. Brasil é ~2% do PIB global e ~0,5% do market cap mundial.

---

## Formulas

```
# Desvio do alvo
Desvio_i = (Peso_atual_i - Peso_alvo_i)

# Trigger de rebalanceamento
Rebalancear se |Desvio_i| > Banda

# Peso após aporte (sem venda)
Aporte_i = Aporte_total × (Peso_alvo_i × Patrimônio_total - Valor_atual_i) / Σ(...)
```

---

## References

- Brinson, Hood, Beebower — *Determinants of Portfolio Performance* (1986)
- Bernstein, W. — *The Intelligent Asset Allocator*
- Swensen, D. — *Unconventional Success*
- Bogle, J. — *The Little Book of Common Sense Investing*

---

## Related

- [[portfolio-theory-mpt]] — Base teórica
- [[diversification]] — Princípio fundamental
- [[position-sizing]] — Alocação dentro de uma classe
- [[risk-tolerance]] — Determinante-chave
- [[wealth-building-stages]] — Alocação por fase de vida
- [[investment-checklist]] — Validação pré-decisão
