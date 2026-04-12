---
tags: [finance, investments, fixed-income, cdb, lci, lca, brazil]
status: active
complexity: basic
context: br
updated: 2026-04-07
aliases: [CDB, LCI, LCA, Renda Fixa Privada]
---

# CDB, LCI & LCA

## Overview

CDB, LCI e LCA são os principais instrumentos de **renda fixa privada bancária** do Brasil. Todos têm garantia do **FGC (Fundo Garantidor de Crédito)** até R$ 250.000 por CPF/instituição (limite global de R$ 1 milhão a cada 4 anos). LCI e LCA têm a vantagem adicional de serem **isentas de IR** para pessoa física.

São o segundo passo natural após Tesouro Direto para diversificar a renda fixa.

---

## Core Concepts

### CDB (Certificado de Depósito Bancário)

- Empréstimo do investidor ao banco
- Tributado pela tabela regressiva de IR (22,5% → 15%)
- Geralmente paga % do CDI (ex: 110% CDI)
- Pode ter liquidez diária ou só no vencimento
- Garantia FGC

### LCI (Letra de Crédito Imobiliário)

- Lastreada em créditos imobiliários
- **Isenta de IR** para PF
- Liquidez geralmente após 90 dias (carência mínima legal)
- Garantia FGC

### LCA (Letra de Crédito do Agronegócio)

- Lastreada em créditos do agronegócio
- **Isenta de IR** para PF
- Demais características similares à LCI
- Garantia FGC

### LC (Letra de Câmbio)

- Emitida por **financeiras** (não bancos)
- Tributada como CDB
- Garantia FGC
- Geralmente paga taxas mais altas (maior risco percebido)

---

## How to Apply

### Comparação Líquida (CDI vs Isento)

Para comparar um CDB tributado com uma LCI/LCA isenta após IR:

```
CDI_equivalente_isento = CDI × (1 - alíquota IR)
```

> [!example] Comparação
> CDB 110% CDI por 2 anos (IR 15%):
> Líquido = 110% × (1 - 0,15) = **93,5% CDI**
>
> LCA 95% CDI isenta:
> Líquido = **95% CDI**
>
> A LCA vence apesar de oferecer "menos".

### Tabela Regressiva (CDB e LC)

| Prazo | IR |
|-------|-----|
| Até 180 dias | 22,5% |
| 181-360 | 20% |
| 361-720 | 17,5% |
| 720+ | 15% |

### Critérios de Escolha

1. **Rating do emissor**: bancos AA-AAA são mais seguros
2. **Prazo vs liquidez**: alinhar com objetivo
3. **Limite FGC**: não concentrar > R$ 250k em uma instituição
4. **Comparar taxa líquida** considerando IR e isenção
5. **Isenção LCI/LCA** ganha em prazos longos

---

## Examples

> [!example] Carteira de Renda Fixa Diversificada
> R$ 200.000 distribuídos:
> - R$ 50.000 em Tesouro Selic (reserva)
> - R$ 50.000 em CDB 115% CDI Banco Inter (2 anos)
> - R$ 50.000 em LCI 92% CDI Caixa (2 anos)
> - R$ 50.000 em LCA 93% CDI BB (3 anos)
>
> Bem dentro do limite FGC por instituição.

---

## Gotchas

> [!warning] Atenção
> - **Liquidez não é garantida**: muitos CDBs só pagam no vencimento
> - **Carência LCI/LCA**: 90 dias mínimo
> - **Bancos pequenos**: oferecem mais, mas risco maior (FGC cobre, mas há perda de tempo no resgate)
> - **Concentração no FGC**: respeitar limite de R$ 250k por CPF/instituição
> - **Limite global FGC**: R$ 1 milhão a cada 4 anos
> - **CDB pós-fixado em queda de juros**: rendimento despenca

---

## Brazilian Context

### FGC — Como Funciona

- Garante até **R$ 250.000 por CPF, por instituição**
- Limite global: **R$ 1 milhão a cada 4 anos**
- Cobre: CDB, LCI, LCA, LC, LH, RDB, poupança
- **Não cobre**: ações, fundos, debêntures, CRI, CRA
- Pagamento típico: 30-60 dias após decretação

### Tipos de Indexação

- **Pós-fixado** (CDI ou Selic): mais comum, segue juros
- **Prefixado**: taxa fixa (12% a.a., por ex.)
- **Híbrido (IPCA+)**: protege contra inflação

> [!info] Onde Comparar
> Plataformas como Renda Fixa.com.br, Yubb e os apps das próprias corretoras (XP, Rico, NuInvest, BTG) listam ofertas atualizadas com taxas, prazos e ratings.

---

## Formulas

```
# Comparação líquida
Liquido = Taxa × (1 - alíquota IR)

# Equivalente isento
CDI_eq = CDI_tributado × (1 - IR)

# Retorno ao final
VF = VP × (1 + i)^t

# Líquido CDB
Líquido = VP × (1+i)^t - [VP × ((1+i)^t - 1)] × IR
```

---

## References

- FGC — fgc.org.br
- BCB — Resoluções CMN sobre RDB e CDB
- Anbima — *Códigos de Distribuição*
- Cerbasi, G. — *Investimentos Inteligentes*

---

## Related

- [[tesouro-direto]] — Renda fixa pública
- [[bonds-international]] — Renda fixa internacional
- [[emergency-fund]] — Onde guardar
- [[tax-optimization-br]] — Estratégia fiscal
- [[acronyms-br]] — FGC, CDI, IR
- [[wealth-building-stages]] — Por estágio
