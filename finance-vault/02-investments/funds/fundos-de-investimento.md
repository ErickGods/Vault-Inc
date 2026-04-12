---
tags: [finance, investments, funds, brazil, cvm]
status: active
complexity: basic
context: br
updated: 2026-04-07
aliases: [Fundos de Investimento, Mutual Funds]
---

# Fundos de Investimento

## Overview

Fundos de investimento são **veículos coletivos** que reúnem recursos de múltiplos investidores para aplicar em diferentes ativos sob gestão profissional. No Brasil, são regulados pela **CVM** (Resolução CVM 175 de 2022) e pela ANBIMA. Oferecem diversificação instantânea, gestão profissional e acesso a estratégias complexas — em troca de taxas e tributação peculiar (come-cotas).

Brasil tem ~R$ 8 trilhões em fundos, distribuídos em milhares de produtos.

---

## Core Concepts

### Tipos de Fundos (CVM 175)

- **Renda Fixa**: títulos públicos e privados de RF
- **Ações** (FIA): mínimo 67% em ações
- **Multimercado** (FIM): mandato amplo, pode tudo
- **Cambial**: lastro em moeda estrangeira
- **Previdência** (PGBL/VGBL): planos de aposentadoria
- **FIDC**: direitos creditórios
- **FIP**: participações (private equity)
- **FIIs**: imobiliários (negociados em bolsa)
- **ETFs**: fundos de índice (negociados em bolsa)

### Estrutura

- **Gestor**: define a estratégia e seleciona ativos
- **Administrador**: cuida de operações, controles, compliance
- **Custodiante**: guarda os ativos
- **Auditor**: certifica DFs anuais
- **Distribuidor**: vende cotas ao investidor

### Tipos de Cotização

- **D+0**: aplicação e resgate no mesmo dia (raros)
- **D+1, D+5, D+30, D+60+**: prazo para crédito após resgate
- **Aberto vs Fechado**: aberto permite entradas/saídas; fechado tem prazo definido

### Taxas

- **Taxa de administração**: % a.a. sobre patrimônio (0,2% - 3%+)
- **Taxa de performance**: % do retorno acima do benchmark (geralmente 20% sobre o que excede CDI ou IBOV)
- **Taxa de entrada/saída**: hoje rara

> [!warning] Custo Composto
> Uma taxa de 2% a.a. consome ~30% do retorno em 30 anos. Sempre comparar **retorno líquido** após taxas.

### Come-Cotas

Tributação semestral antecipada (maio e novembro) em fundos de longo prazo:
- **Curto prazo** (média ≤ 365d): 20% sobre rendimentos
- **Longo prazo** (média > 365d): 15% sobre rendimentos

No resgate, recolhe-se o complemento conforme tabela regressiva.

---

## How to Apply

### Como Avaliar um Fundo

1. **Histórico ≥ 5 anos** (idealmente 10+)
2. **Performance vs benchmark** consistente
3. **Volatilidade** e drawdown máximo
4. **Sharpe Ratio** vs peers
5. **Taxa total** (admin + performance)
6. **Tamanho do PL** (muito pequeno = ilíquido; muito grande = perda de alpha)
7. **Estabilidade da equipe gestora**
8. **Lâmina e regulamento**

### Tipos por Risco

| Tipo | Risco | Retorno Esperado |
|------|-------|------------------|
| RF DI | Baixíssimo | ~CDI |
| RF Crédito | Baixo-Médio | CDI + 1-3% |
| Multimercado | Médio | CDI + 2-5% |
| Ações Long Only | Alto | IBOV ± alfa |
| Long Short | Alto | CDI + 5-10% |
| Macro Global | Alto | CDI + 4-8% |

---

## Examples

> [!example] Comparação de Custo
> Fundo A: 0,3% admin, sem performance
> Fundo B: 2% admin + 20% sobre CDI
>
> Em CDI 10%, retorno líquido após 1 ano:
> Fundo A: 9,7%
> Fundo B (com retorno bruto 12%): 12% - 2% - 20%×(12-10) = 9,6%
>
> Fundo B precisa entregar muito mais bruto para compensar.

---

## Gotchas

> [!warning] Erros
> - **Comprar pelo desempenho recente**: top fund de 1 ano raramente repete
> - **Ignorar taxas**: comem retorno no longo prazo
> - **Não diversificar entre fundos** do mesmo gestor
> - **Esquecer come-cotas** ao planejar resgates
> - **Comprar fundo "espelho" com taxa dobrada**: distribuído por bancos

---

## Brazilian Context

### CVM 175 (2022)

Nova regulação trouxe:
- **Limitação de responsabilidade** dos cotistas (antes era ilimitada)
- **Possibilidade de classes** (mesmo fundo, regras diferentes)
- **Subclasses** para distribuição
- **Sandbox** para inovação

### Tributação

| Fundo | IR |
|-------|-----|
| RF Curto Prazo | 22,5%-20% (regressivo) + come-cotas |
| RF Longo Prazo | 22,5%-15% (regressivo) + come-cotas |
| Ações | 15% no resgate (sem come-cotas) |
| FIP/FIDC fechado | Tabela específica |
| FII | 20% sobre ganho (dividendo isento) |

> [!info] Dica Tributária
> Fundos de **ações** (FIA) não têm come-cotas — apenas IR de 15% no resgate. Mais eficiente fiscalmente para longo prazo.

---

## Formulas

```
# Cota
Cota_t = PL_t / nº cotas

# Retorno do investidor
Retorno = Cota_resgate / Cota_aplicação - 1

# Líquido após taxa de performance
Líquido = Bruto - Taxa_Adm - max(0, (Retorno - Bench) × Taxa_Perf)

# Sharpe Ratio
Sharpe = (Retorno - rf) / σ
```

---

## References

- CVM — *Resolução CVM 175* (2022)
- ANBIMA — *Códigos de Fundos*
- Cerbasi, G. — *Investimentos Inteligentes*
- Damodaran, A. — *Mutual Funds Performance*

---

## Related

- [[etfs]] — Alternativa passiva
- [[fiis-real-estate]] — Imobiliários
- [[capital-allocation]] — Onde alocar
- [[acronyms-br]] — CVM, ANBIMA, FIA, FIM
- [[tax-optimization-br]] — Come-cotas
