---
tags:
  - finance
  - analysis
  - quantitative
  - backtesting
aliases:
  - Backtesting
  - Teste Histórico
complexity: advanced
context: global
created: 2026-04-06
---

# Backtesting Basics (Fundamentos de Teste Histórico)

## Overview

Backtesting é o processo de testar uma estratégia de investimento ou trading usando dados históricos para avaliar como ela teria performado no passado. É uma etapa indispensável no desenvolvimento de qualquer estratégia quantitativa — sem backtesting rigoroso, você está operando com base em intuição e não em evidência. No entanto, backtesting é uma faca de dois gumes: feito incorretamente, pode dar uma falsa sensação de segurança e levar a perdas significativas quando a estratégia é aplicada em tempo real.

> [!warning] A Armadilha Fundamental
> "Past performance is not indicative of future results" — mas sem testar no passado, você não tem base alguma. O desafio é construir testes que sejam **honestos** e **robustos**, minimizando vieses que inflam resultados artificialmente.

## Core Concepts

### Walk-Forward Analysis

A abordagem mais robusta de backtesting. Em vez de otimizar parâmetros em todo o histórico e depois avaliar no mesmo período (o que garante overfitting), o walk-forward divide os dados em janelas sequenciais.

**Processo:**

1. **In-Sample (IS)**: Use os primeiros N anos para otimizar parâmetros da estratégia.
2. **Out-of-Sample (OOS)**: Aplique os parâmetros otimizados nos próximos M meses (sem reotimizar).
3. **Role a janela**: Avance a janela e repita.
4. **Concatene os resultados OOS**: O desempenho real da estratégia é apenas o resultado OOS concatenado.

```
|--- IS (otimização) ---|--- OOS (teste) ---|
          |--- IS (otimização) ---|--- OOS (teste) ---|
                    |--- IS (otimização) ---|--- OOS (teste) ---|
```

> [!tip] Proporção IS/OOS
> Uma regra prática é usar 70-80% do período como in-sample e 20-30% como out-of-sample. Para walk-forward, janelas de IS de 3-5 anos com OOS de 6-12 meses são comuns.

### In-Sample vs Out-of-Sample

| Aspecto | In-Sample | Out-of-Sample |
|---------|-----------|---------------|
| **Propósito** | Desenvolver e otimizar a estratégia | Validar a estratégia |
| **Dados** | Conhecidos durante o desenvolvimento | Nunca vistos durante o desenvolvimento |
| **Resultado esperado** | Performance inflada (otimização) | Performance mais realista |
| **Analogia** | Estudar com a prova na mão | Fazer a prova sem ter visto |

> [!important] Regra de Ouro
> Se você não separou dados out-of-sample ANTES de começar a desenvolver a estratégia, seus resultados são suspeitos. A tentação de "dar uma olhada" nos dados futuros contamina todo o processo.

### Vieses (Biases) que Invalidam Backtests

#### Survivorship Bias (Viés de Sobrevivência)

Testar a estratégia apenas com ações que existem hoje, ignorando as que foram deslistadas (falência, aquisição, etc.). Empresas que faliram não aparecem nos dados atuais, inflando artificialmente os retornos.

- **Exemplo**: Se você testa uma estratégia de Value no período 2008-2020 usando apenas ações que existem em 2020, você exclui empresas que quebraram em 2008-2009 — exatamente as que uma estratégia de "ações baratas" teria comprado.
- **Solução**: Use bases de dados point-in-time que incluam empresas deslistadas (ex: CRSP nos EUA, Economatica no Brasil com flag de deslistagem).

#### Look-Ahead Bias (Viés de Antecipação)

Usar informações no backtest que não estariam disponíveis no momento da decisão real.

- **Exemplo clássico**: Usar dados fundamentalistas do Q4 (publicados em março do ano seguinte) para decisões de investimento em janeiro. Na vida real, esses dados ainda não existiriam.
- **Exemplo sutil**: Usar o preço de fechamento de hoje para gerar um sinal e executar a ordem no mesmo fechamento — na prática, a ordem seria executada no dia seguinte.
- **Solução**: Adicionar lag entre geração do sinal e execução. Usar dados com timestamps corretos de publicação.

#### Overfitting (Sobreajuste)

Otimizar tantos parâmetros que a estratégia se ajusta perfeitamente ao ruído dos dados históricos, mas falha com dados novos.

> [!warning] Sinais de Overfitting
> - A estratégia tem muitos parâmetros (>5 parâmetros para uma estratégia simples é suspeito).
> - Performance in-sample espetacular, mas OOS decepcionante.
> - Pequenas mudanças nos parâmetros causam grandes mudanças nos resultados (instabilidade paramétrica).
> - A estratégia funciona apenas em um ativo ou período específico.

**Regra de bolso**: Para cada parâmetro livre na estratégia, você deveria ter pelo menos 200-300 trades no backtest para ter significância estatística.

### Modelagem de Custos de Transação

Um backtest sem custos de transação é ficção. Custos incluem:

- **Corretagem**: Taxa por operação (fixa ou variável).
- **Emolumentos**: Taxas da bolsa (na B3, ~0.03% do volume).
- **Spread bid-ask**: Diferença entre preço de compra e venda. Em ações líquidas da B3, ~0.05-0.15%. Em small caps, pode ser >1%.
- **Impacto de mercado**: Ordens grandes movem o preço contra você. Mais relevante para estratégias com grande capital.

**Modelagem simplificada:**

$$\text{Custo por trade} = \text{Corretagem} + \text{Spread}/2 + \text{Emolumentos}$$

$$\text{Custo total} = \text{Custo por trade} \times 2 \times \text{Número de trades}$$

(Multiplicar por 2 porque cada round-trip tem entrada e saída.)

### Slippage

Slippage é a diferença entre o preço esperado de uma operação e o preço realmente executado. Ocorre por:

- Delay entre geração do sinal e execução.
- Liquidez insuficiente no preço desejado.
- Volatilidade no momento da execução.

**Modelagem**: Adicione 0.05-0.20% de slippage por trade como premissa conservadora. Em ativos ilíquidos ou em momentos de alta volatilidade, pode ser significativamente maior.

### Ferramentas de Backtesting

#### Python

| Biblioteca | Tipo | Destaque |
|-----------|------|----------|
| **zipline** | Event-driven | Criada pela Quantopian. Robusta para backtests realistas com calendar awareness. |
| **backtrader** | Event-driven | Flexível, boa documentação, suporta live trading. |
| **vectorbt** | Vectorized | Extremamente rápida para backtests de portfólio. Ideal para otimização massiva. |
| **bt** | Tree-based | Framework para backtests de alocação de portfólio. |
| **QuantLib** | Pricing | Mais voltada para derivativos, mas útil para modelagem de risco. |

#### R

| Biblioteca | Tipo | Destaque |
|-----------|------|----------|
| **quantstrat** | Rule-based | Framework completo para estratégias baseadas em regras. |
| **PerformanceAnalytics** | Análise | Cálculo de métricas de performance (Sharpe, drawdown, etc.). |
| **TTR** | Indicadores | Technical Trading Rules — indicadores técnicos para R. |

> [!note] Recomendação para Iniciantes
> Comece com **vectorbt** em Python para prototipar rapidamente. Migre para **backtrader** ou **zipline** quando precisar de simulações mais realistas com gestão de ordens. Veja [[python-finance-snippets]] para exemplos de código.

### Métricas-Chave de Avaliação

#### Sharpe Ratio

$$\text{Sharpe} = \frac{R_p - R_f}{\sigma_p}$$

Retorno em excesso por unidade de risco. Sharpe > 1.0 é bom. Sharpe > 2.0 é excelente (e raro em estratégias reais depois de custos).

#### Maximum Drawdown

$$\text{Max DD} = \max_{t} \left( \frac{\text{Peak}_t - \text{Trough}_t}{\text{Peak}_t} \right)$$

A maior queda do pico ao vale. Mede o pior cenário que o investidor teria enfrentado. Max DD de -50% significa que a estratégia perdeu metade do capital antes de se recuperar.

#### Win Rate

$$\text{Win Rate} = \frac{\text{Trades vencedores}}{\text{Total de trades}}$$

Win rate > 50% é desejável, mas não obrigatório. Estratégias de trend following frequentemente têm win rate de 30-40% com lucros grandes nos winners compensando perdas pequenas nos losers.

#### Profit Factor

$$\text{Profit Factor} = \frac{\sum \text{Lucros}}{\sum \text{Perdas}}$$

Profit Factor > 1.5 é bom. Profit Factor > 2.0 é excelente.

#### Calmar Ratio

$$\text{Calmar} = \frac{R_p \text{ (anualizado)}}{|\text{Max Drawdown}|}$$

Similar ao Sharpe, mas usa max drawdown como medida de risco. Calmar > 1.0 é desejável.

#### Sortino Ratio

$$\text{Sortino} = \frac{R_p - R_f}{\sigma_{downside}}$$

Variação do Sharpe que penaliza apenas a volatilidade negativa (downside deviation), mais alinhado com a percepção de risco do investidor.

### Monte Carlo Simulation

Monte Carlo permite avaliar a robustez dos resultados do backtest ao introduzir aleatoriedade controlada.

**Métodos:**
1. **Resampling de trades**: Embaralhar a ordem dos trades e recalcular equity curve. Repetir milhares de vezes para gerar uma distribuição de resultados possíveis.
2. **Perturbação de parâmetros**: Variar levemente os parâmetros da estratégia e observar a estabilidade dos resultados.
3. **Bootstrap de retornos**: Amostrar retornos com reposição para gerar cenários alternativos.

**O que observar:**
- Distribuição de Sharpe Ratio: Se o percentil 5% ainda é positivo, a estratégia é robusta.
- Distribuição de Max Drawdown: Qual o pior cenário razoável?
- Probabilidade de ruína: Qual a chance de a estratégia perder X% do capital?

## How to Apply

1. **Defina a estratégia com regras claras** ANTES de olhar os dados. Documente cada regra.
2. **Separe dados OOS** antes de começar qualquer análise.
3. **Implemente sem custos** primeiro para verificar a lógica.
4. **Adicione custos realistas** (corretagem, spread, slippage, impostos).
5. **Rode walk-forward analysis** para validar estabilidade temporal.
6. **Aplique Monte Carlo** para testar robustez.
7. **Compare com benchmarks**: A estratégia supera buy-and-hold do índice de mercado após custos?
8. **Paper trading**: Antes de capital real, opere a estratégia em simulado por pelo menos 3-6 meses.

## Examples

**Backtest de Momentum no Brasil**: Usando vectorbt em Python com dados da B3 de 2010 a 2023. Estratégia de cross-sectional momentum (12-1 meses) nas 100 ações mais líquidas. Resultados antes de custos: Sharpe 0.85, Max DD -35%. Após custos (0.15% por trade): Sharpe 0.55, Max DD -38%. Walk-forward de janelas de 5 anos IS e 1 ano OOS: Sharpe OOS médio de 0.45. Conclusão: prêmio de momentum existe, mas custos são relevantes.

## Gotchas

- **O passado não garante o futuro**: O backtest mais perfeito do mundo ainda é uma simulação histórica. O futuro pode ser estruturalmente diferente.
- **Complexidade não é virtude**: Estratégias simples (2-3 regras) tendem a ser mais robustas OOS do que estratégias complexas (10+ regras/parâmetros).
- **Dados de qualidade são caros**: Dados gratuitos frequentemente têm erros, gaps e não incluem empresas deslistadas. Investir em dados de qualidade é essencial.
- **Não otimize até encontrar algo que funcione**: Se você testa 100 estratégias e apresenta apenas a melhor, você está fazendo data mining, não pesquisa. Aplique correção de múltiplas comparações (ex: Bonferroni).
- **Resultados muito bons são suspeitos**: Se o seu backtest mostra Sharpe > 3 e Max DD < 5%, provavelmente há um bug ou viés no código.
- **Live trading é diferente**: Latência, fills parciais, erros de execução, psicologia — tudo isso existe no live e não no backtest.

## Brazilian Context

- **Dados históricos da B3**: Economatica é a fonte mais completa para dados de ações brasileiras, incluindo empresas deslistadas. Alternativas mais acessíveis incluem Yahoo Finance (com limitações) e APIs como a da StatusInvest.
- **Custos na B3**: Emolumentos (~0.03%), taxa de liquidação, ISS sobre corretagem, e IR de 15% sobre lucro em operações normais e 20% em day trade. Modele todos esses custos.
- **Liquidez**: Poucas ações no Brasil têm liquidez comparável ao mercado americano. Backtests com ações de baixa liquidez são pouco confiáveis.
- **Plataformas brasileiras**: MetaTrader 5 (usado por muitos traders brasileiros) possui backtester embutido, mas limitado para estratégias de portfólio. Para análises mais sofisticadas, Python é a recomendação.
- **NEFIN-USP**: Disponibiliza dados de fatores (veja [[factor-investing]]) e retornos de mercado para o Brasil, úteis para backtests acadêmicos.

> [!tip] Começando com Backtesting no Brasil
> 1. Instale Python + vectorbt.
> 2. Obtenha dados via `yfinance` (limitado) ou Economatica.
> 3. Comece com uma estratégia simples (ex: momentum 12-1 no IBOV).
> 4. Adicione custos e compare com CDI e IBOV como benchmarks.
> 5. Veja [[python-finance-snippets]] para código de referência.

## Formulas

**Sharpe Ratio Anualizado:**

$$\text{Sharpe} = \frac{\bar{r} - r_f}{\sigma_r} \times \sqrt{252}$$

Onde 252 é o número de dias úteis no ano (ajuste para 246-248 no Brasil).

**Maximum Drawdown:**

$$DD_t = \frac{V_t - \max_{s \leq t} V_s}{\max_{s \leq t} V_s}$$

$$\text{Max DD} = \min_t DD_t$$

**Profit Factor:**

$$PF = \frac{\sum_{i \in W} |r_i|}{\sum_{j \in L} |r_j|}$$

## References

- Pardo, Robert. *The Evaluation and Optimization of Trading Strategies*. Wiley, 2008.
- Aronson, David R. *Evidence-Based Technical Analysis*. Wiley, 2006.
- López de Prado, Marcos. *Advances in Financial Machine Learning*. Wiley, 2018.
- Bailey, David H. et al. "The Deflated Sharpe Ratio." *Journal of Portfolio Management*, 2014.
- Harvey, Campbell R. & Liu, Yan. "Backtesting." *Journal of Portfolio Management*, 2015.

## Related

- [[factor-investing]]
- [[momentum-strategies]]
- [[python-finance-snippets]]
- [[risk-and-return]]
- [[indicators-overview]]
- [[portfolio-theory-mpt]]
