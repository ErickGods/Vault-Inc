---
tags:
  - finance
  - analysis
  - quantitative
  - momentum
aliases:
  - Momentum
  - Estratégias de Momentum
complexity: advanced
context: global
created: 2026-04-06
---

# Momentum Strategies (Estratégias de Momentum)

## Overview

Momentum é a tendência empiricamente documentada de que ativos com bons retornos recentes continuam a ter bons retornos no futuro próximo, e ativos com retornos ruins continuam a ter retornos ruins. É um dos fatores de investimento mais robustos e persistentes, presente em diversas classes de ativos (ações, bonds, commodities, moedas) e em mercados ao redor do mundo. Apesar de desafiar a hipótese de mercados eficientes na sua forma forte, o prêmio de momentum tem sido documentado desde os trabalhos seminais de Jegadeesh e Titman (1993).

> [!info] Paradoxo do Momentum
> Momentum é o fator com maior retorno histórico documentado (~7-8% a.a. nos EUA), mas também o que apresenta os crashes mais violentos. Essa dualidade é central para entender a estratégia.

## Core Concepts

### Cross-Sectional Momentum

A forma clássica de momentum: comparar o desempenho relativo de ativos dentro de um universo e comprar os vencedores enquanto vende os perdedores.

**Implementação padrão (12-1 month):**

1. Calcular o retorno acumulado de cada ação nos últimos 12 meses, **excluindo o mês mais recente** (para evitar o efeito de reversão de curto prazo / short-term reversal).
2. Ranquear todas as ações por esse retorno.
3. Comprar o decil superior (winners) e vender o decil inferior (losers).
4. Manter a posição por 1-6 meses.
5. Rebalancear.

$$\text{Momentum Score}_i = \frac{P_{t-1}}{P_{t-12}} - 1$$

> [!tip] Por que excluir o último mês?
> O último mês apresenta um efeito de reversão de curto prazo (short-term reversal), possivelmente causado por pressão de market making e bid-ask bounce. Incluí-lo degradaria a performance da estratégia.

**Variações de lookback period:**

| Lookback | Holding Period | Comentário |
|----------|---------------|------------|
| 12-1 meses | 1 mês | Clássico Jegadeesh-Titman |
| 6-1 meses | 1 mês | Momentum de médio prazo |
| 12-1 meses | 3 meses | Reduz custos de transação |
| 12-1 meses | 6 meses | Mais estável, menor turnover |

### Time-Series Momentum (Trend Following)

Diferente do cross-sectional, o time-series momentum olha para o retorno absoluto de cada ativo individualmente — sem comparar com outros ativos.

- Se o ativo teve retorno positivo nos últimos N meses → comprar (long).
- Se o ativo teve retorno negativo nos últimos N meses → vender (short) ou ficar fora.

$$\text{Signal}_i = \text{sign}(R_{i,t-12:t-1})$$

**Vantagens sobre cross-sectional:**
- Pode reduzir a zero a exposição ao mercado em crises (todos os ativos com momentum negativo → carteira em cash).
- Funciona bem em mercados de futuros (commodities, moedas, bonds).
- Base do CTA / Managed Futures industry.

> [!note] Trend Following vs Momentum
> Trend following é essencialmente time-series momentum aplicado a futuros de diversas classes de ativos. CTAs (Commodity Trading Advisors) são os principais praticantes dessa abordagem.

### Dual Momentum — Gary Antonacci

Gary Antonacci popularizou o conceito de **Dual Momentum** em seu livro de 2014, combinando dois tipos de momentum:

1. **Relative Momentum (Cross-Sectional)**: Compare ativos entre si e escolha o de melhor performance recente.
2. **Absolute Momentum (Time-Series)**: Verifique se o ativo escolhido tem retorno positivo absoluto. Se não, vá para um ativo seguro (bonds/cash).

**Algoritmo simplificado (Global Equities Momentum - GEM):**

```
1. Calcular retorno de 12 meses de:
   - S&P 500
   - MSCI EAFE (International)
   - T-Bills (ativo livre de risco)

2. Se ambos os mercados de equity tiverem retorno < T-Bills:
   → Alocar 100% em bonds (aggregate bonds)

3. Caso contrário:
   → Alocar 100% no mercado de equity com maior retorno
```

> [!tip] Simplicidade do Dual Momentum
> O GEM de Antonacci usa apenas 3 ativos e rebalanceia mensalmente. Apesar da simplicidade, historicamente superou o S&P 500 com drawdowns significativamente menores. A chave é a combinação de relative + absolute momentum.

### Momentum Crash Risk

O maior risco de estratégias de momentum são os **crashes de momentum** — reversões abruptas e severas que ocorrem quando o mercado se recupera rapidamente após uma crise.

**Mecanismo:**
1. Durante crises, os "losers" caem muito (ações de empresas em dificuldade).
2. Quando o mercado se recupera, esses losers fazem rallies explosivos (short squeeze + beta alto).
3. Simultaneamente, os "winners" que se mantiveram durante a crise sofrem realização de lucros.
4. O portfólio long-short de momentum é atingido dos dois lados.

**Exemplos históricos:**
- **2009 (março-maio)**: Momentum crash de ~40% em dois meses durante a recuperação pós-GFC.
- **2001 (janeiro)**: Reversão abrupta após o estouro da bolha dot-com.
- **2020 (novembro)**: Rotação violenta de growth para value após anúncio de vacinas COVID.

> [!warning] Proteção contra Momentum Crashes
> - Usar absolute momentum como filtro (Dual Momentum).
> - Limitar exposição ao fator momentum a uma parcela do portfólio.
> - Combinar com fatores de baixa correlação (Value tem correlação negativa com Momentum). Veja [[factor-investing]].
> - Reduzir exposição quando a volatilidade do mercado está extremamente elevada.

### Detalhes de Implementação

**Lookback Period**: 12-1 meses é o padrão acadêmico, mas 6-1 meses também funciona. Períodos muito curtos (<3 meses) capturam reversão, não momentum.

**Holding Period**: 1-6 meses. Períodos mais longos reduzem turnover e custos de transação, mas podem diluir o sinal.

**Rebalanceamento**: Mensal é o mais comum. Alguns praticantes usam rebalanceamento escalonado (staggered) — dividir o portfólio em sub-portfólios rebalanceados em semanas diferentes para suavizar o impacto de timing.

**Custos de transação**: Momentum tem alto turnover (~100-200% a.a. para cross-sectional). Custos devem ser modelados cuidadosamente. Veja [[backtesting-basics]].

**Universo de ativos**: Filtrar por liquidez mínima é essencial. Ações ilíquidas podem ter momentum espúrio (bid-ask bounce, dados ruins).

**Volatility scaling**: Normalizar posições pela volatilidade de cada ativo melhora o risk-adjusted return.

$$w_i = \frac{1/\sigma_i}{\sum_j 1/\sigma_j}$$

## How to Apply

1. **Defina o universo**: Escolha ações com liquidez adequada (ex: IBOV ou IBrX-100 no Brasil).
2. **Calcule o momentum score**: Retorno acumulado de 12-1 meses para cada ação.
3. **Ranqueie e selecione**: Compre o quintil superior (top 20%).
4. **Aplique filtro de absolute momentum**: Se o retorno absoluto do portfólio é negativo, vá para renda fixa.
5. **Rebalanceie mensalmente**: Rode o ranking novamente e ajuste posições.
6. **Monitore custos**: Considere usar threshold de rebalanceamento (só troca se a ação caiu abaixo do percentil 40, por exemplo) para reduzir turnover.

## Examples

**Dual Momentum no Brasil**: Comparar IBOV vs S&P 500 (via IVVB11) nos últimos 12 meses. Alocar no de melhor performance. Se ambos perdem do CDI, alocar em Tesouro Selic. Rebalancear mensalmente. Estratégia simples com apenas 3 ativos.

**Cross-Sectional no IBrX-100**: Ranquear as 100 ações do IBrX pelo retorno de 12-1 meses. Comprar as 20 melhores com pesos iguais. Rebalancear trimestralmente. Historicamente, superou o IBrX com Sharpe Ratio superior.

## Gotchas

- **Momentum não funciona em todos os regimes**: Em períodos de alta volatilidade e reversões bruscas (como transições de bear para bull market), o fator sofre perdas severas.
- **Custos de transação**: O alto turnover pode corroer grande parte do prêmio, especialmente em mercados com custos de corretagem e spread elevados.
- **Impostos**: No Brasil, vendas acima de R$20.000/mês em ações são tributadas a 15% sobre o lucro. O alto turnover de momentum gera frequentes eventos tributáveis.
- **Survivorship bias**: Em backtests, é crucial incluir empresas que foram deslistadas. Ignorá-las infla artificialmente o retorno. Veja [[backtesting-basics]].
- **Factor timing é difícil**: Tentar prever quando momentum vai performar bem ou mal é tão difícil quanto timing do mercado em geral.
- **Implementação long-short no Brasil**: Alugar ações para vender a descoberto é caro e burocrático na B3. A maioria dos investidores implementa apenas a ponta long.

## Brazilian Context

- **Evidência acadêmica no Brasil**: Estudos do NEFIN-USP confirmam a existência do prêmio de momentum no mercado acionário brasileiro, embora com maior volatilidade que nos EUA.
- **Dados de fatores**: O NEFIN (nefin.com.br) calcula e disponibiliza séries do fator WML para o Brasil.
- **Custos relevantes**: A B3 tem custos de transação relativamente altos (emolumentos, corretagem, spread), o que impacta estratégias de alto turnover como momentum.
- **Liquidez concentrada**: Apenas ~50-80 ações na B3 têm liquidez suficiente para implementação confiável de momentum.
- **ETFs**: Não existem ETFs de momentum puro no Brasil (até 2026). A implementação requer conta em corretora e execução manual ou algorítmica.

## Formulas

**Cross-Sectional Momentum Score:**

$$MOM_i = \frac{P_{i,t-1}}{P_{i,t-12}} - 1$$

**Time-Series Momentum Signal:**

$$TSMOM_i = \text{sign}\left(\sum_{k=1}^{12} r_{i,t-k}\right)$$

**Volatility-Adjusted Momentum:**

$$MOM_i^{adj} = \frac{MOM_i}{\sigma_i}$$

**Dual Momentum Decision:**

$$\text{Asset} = \begin{cases} \arg\max(R_{equity}) & \text{se } R_{equity} > R_f \\ \text{Bonds} & \text{caso contrário} \end{cases}$$

## References

- Jegadeesh, Narasimhan & Titman, Sheridan. "Returns to Buying Winners and Selling Losers: Implications for Stock Market Efficiency." *Journal of Finance*, 1993.
- Asness, Clifford S., Moskowitz, Tobias J. & Pedersen, Lasse H. "Value and Momentum Everywhere." *Journal of Finance*, 2013.
- Antonacci, Gary. *Dual Momentum Investing*. McGraw-Hill, 2014.
- Moskowitz, Tobias J., Ooi, Yao Hua & Pedersen, Lasse H. "Time Series Momentum." *Journal of Financial Economics*, 2012.
- Daniel, Kent & Moskowitz, Tobias J. "Momentum Crashes." *Journal of Financial Economics*, 2016.

## Related

- [[factor-investing]]
- [[backtesting-basics]]
- [[indicators-overview]]
- [[price-action]]
- [[risk-and-return]]
- [[portfolio-theory-mpt]]
