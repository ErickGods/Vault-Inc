---
tags:
  - finance
  - analysis
  - quantitative
  - factors
aliases:
  - Factor Investing
  - Smart Beta
  - Fatores
complexity: advanced
context: global
created: 2026-04-06
---

# Factor Investing

## Overview

Factor Investing é uma abordagem de investimento que busca capturar retornos sistemáticos (prêmios de risco) associados a características específicas de ativos financeiros — os chamados **fatores**. Em vez de selecionar ações individualmente, o investidor constrói portfólios orientados por exposição a fatores que, historicamente e com fundamentação acadêmica, demonstraram gerar retornos superiores ajustados ao risco. É o ponto de convergência entre finanças acadêmicas e gestão de portfólios, sendo a base do que o mercado chama de **Smart Beta**.

> [!info] De CAPM a Multi-Factor
> O CAPM (Capital Asset Pricing Model) propunha que o único fator relevante era o mercado (beta). As pesquisas de Fama, French e Carhart demonstraram que múltiplos fatores explicam os retornos de forma mais precisa, dando origem ao factor investing moderno.

## Core Concepts

### Fama-French 3-Factor Model (1993)

Eugene Fama e Kenneth French expandiram o CAPM adicionando dois fatores que explicavam retornos que o beta de mercado não capturava.

$$R_i - R_f = \alpha_i + \beta_1(R_m - R_f) + \beta_2 \cdot SMB + \beta_3 \cdot HML + \epsilon_i$$

| Fator | Nome | Descrição |
|-------|------|-----------|
| **Market** | $R_m - R_f$ | Prêmio de risco do mercado (equity risk premium) |
| **Size (SMB)** | Small Minus Big | Ações de empresas pequenas tendem a superar as grandes |
| **Value (HML)** | High Minus Low | Ações de valor (alto book-to-market) tendem a superar as de crescimento |

### Fama-French 5-Factor Model (2015)

Fama e French adicionaram dois fatores adicionais para melhorar o poder explicativo do modelo.

$$R_i - R_f = \alpha_i + \beta_1(R_m - R_f) + \beta_2 \cdot SMB + \beta_3 \cdot HML + \beta_4 \cdot RMW + \beta_5 \cdot CMA + \epsilon_i$$

| Fator | Nome | Descrição |
|-------|------|-----------|
| **Profitability (RMW)** | Robust Minus Weak | Empresas mais lucrativas superam as menos lucrativas |
| **Investment (CMA)** | Conservative Minus Aggressive | Empresas que investem conservadoramente superam as que investem agressivamente |

### Carhart 4-Factor Model (1997)

Mark Carhart adicionou o fator momentum ao modelo de 3 fatores de Fama-French.

$$R_i - R_f = \alpha_i + \beta_1(R_m - R_f) + \beta_2 \cdot SMB + \beta_3 \cdot HML + \beta_4 \cdot WML + \epsilon_i$$

| Fator | Nome | Descrição |
|-------|------|-----------|
| **Momentum (WML)** | Winners Minus Losers | Ações com retornos positivos recentes continuam subindo (e vice-versa) |

### Os Principais Fatores com Evidência Acadêmica

#### Value (Valor) — HML

- **Definição**: Comprar ações "baratas" (alto book-to-market, baixo P/E, baixo P/B) e vender ações "caras".
- **Evidência**: Prêmio médio de ~4.5% a.a. nos EUA (1927-2023). Presente em praticamente todos os mercados estudados.
- **Métricas**: P/B, P/E, EV/EBITDA, Dividend Yield.
- **Risco**: O fator valor pode ter longos períodos de underperformance (2007-2020 nos EUA).

#### Size (Tamanho) — SMB

- **Definição**: Ações de empresas de menor capitalização tendem a superar as de maior capitalização.
- **Evidência**: Prêmio médio de ~3.0% a.a. historicamente, mas tem diminuído nas últimas décadas.
- **Risco**: Small caps são menos líquidas, mais voláteis e mais suscetíveis a crises.

#### Momentum — WML

- **Definição**: Ações que subiram nos últimos 3-12 meses tendem a continuar subindo. Veja [[momentum-strategies]] para detalhes de implementação.
- **Evidência**: Prêmio médio de ~7-8% a.a. nos EUA. O fator com maior retorno histórico.
- **Risco**: Sujeito a crashes violentos (momentum crash), como em 2009.

#### Quality (Qualidade) — QMJ

- **Definição**: Empresas com alta lucratividade, baixo endividamento, earnings estáveis e boa governança. "Quality Minus Junk" (Asness et al., 2019).
- **Métricas**: ROE, ROA, margem bruta, accruals, alavancagem, estabilidade de lucros.
- **Evidência**: Prêmio consistente com menor drawdown que outros fatores. Funciona como proteção em crises.

#### Low Volatility (Baixa Volatilidade) — BAB

- **Definição**: Ações de menor volatilidade tendem a ter retornos ajustados ao risco superiores. "Betting Against Beta" (Frazzini & Pedersen, 2014).
- **Evidência**: Desafia diretamente o CAPM, que prediz que mais risco = mais retorno.
- **Explicação**: Leverage constraints e lottery preferences de investidores inflam o preço de ações voláteis.

> [!warning] Factor Premiums Não São Garantidos
> Prêmios de fator são médias de longo prazo. Cada fator pode ter anos ou até décadas de underperformance. O Value underperformou de 2007 a 2020. Momentum teve crashes severos em 2009. Diversificar entre fatores é essencial.

### Factor Premiums — Dados Históricos

| Fator | Prêmio Anual Médio (EUA) | Período | Sharpe Ratio |
|-------|--------------------------|---------|--------------|
| Market | ~7-8% | 1927-2023 | ~0.40 |
| Value (HML) | ~4-5% | 1927-2023 | ~0.35 |
| Size (SMB) | ~2-3% | 1927-2023 | ~0.20 |
| Momentum (WML) | ~7-8% | 1927-2023 | ~0.50 |
| Quality (QMJ) | ~4-5% | 1957-2023 | ~0.55 |
| Low Vol (BAB) | ~8-10% | 1931-2023 | ~0.75 |

> [!note] Dados de Kenneth French
> Os dados dos fatores Fama-French estão disponíveis publicamente em: https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html

### Como Construir Factor Portfolios

**Metodologia básica:**

1. **Ranquear** o universo de ações pela métrica do fator (ex: P/B para Value).
2. **Dividir em quintis ou decis** — comprar o quintil "melhor" e (opcionalmente) vender o quintil "pior" (long-short).
3. **Ponderar** equally-weighted ou por market cap.
4. **Rebalancear** periodicamente (mensal, trimestral ou anual, dependendo do fator).
5. **Considerar custos** de transação — fatores de alta rotatividade (momentum) têm custos maiores.

**Multi-factor approach**: Combinar múltiplos fatores no mesmo portfólio para diversificar o risco de fator individual. Pode ser feito via:
- **Mixing**: Alocar em ETFs/fundos dedicados a cada fator separadamente.
- **Integrating**: Construir um score composto que incorpora todos os fatores simultaneamente para cada ação.

## How to Apply

1. Defina seus fatores-alvo com base em horizonte de investimento e tolerância a risco.
2. Escolha entre implementação via ETFs (mais simples) ou construção própria de portfólio (mais controle).
3. Diversifique entre fatores — a correlação entre Value e Momentum, por exemplo, é historicamente negativa, o que melhora a diversificação.
4. Rebalanceie conforme a frequência adequada ao fator.
5. Monitore exposições fatoriais do portfólio usando ferramentas de análise de risco. Veja [[backtesting-basics]] para validação.

## Examples

**Portfólio Multi-Factor Simples**: 25% Value (ETF de Value), 25% Momentum (ETF de Momentum), 25% Quality (ETF de Quality), 25% Low Volatility (ETF de Min Vol). Rebalanceamento trimestral. Historicamente, essa combinação teria superado o índice de mercado com menor drawdown.

## Gotchas

- **Factor crowding**: Quando muitos investidores perseguem o mesmo fator, o prêmio pode diminuir ou desaparecer temporariamente.
- **Data mining**: Existem centenas de "fatores" publicados na literatura. A maioria não sobrevive a testes out-of-sample. Foque nos fatores com décadas de evidência.
- **Custos de implementação**: Fatores de alta rotatividade (momentum) podem ter custos de transação que corroem o prêmio, especialmente em mercados menos líquidos.
- **Regime changes**: Fatores podem se comportar diferentemente em regimes macroeconômicos distintos (inflação alta, recessão, etc.).
- **Horizonte longo necessário**: Factor investing é uma estratégia de longo prazo. Períodos de 3-5 anos de underperformance são normais.

## Brazilian Context

- **ETFs de Fatores no Brasil**: A oferta é limitada comparada aos EUA, mas cresce. Exemplos incluem SMALL11 (small caps), DIVO11 (dividendos/value), IVVB11 (mercado americano).
- **Factor premiums no Brasil**: Estudos acadêmicos confirmam a presença dos prêmios de Value e Momentum no mercado brasileiro, embora com magnitudes diferentes dos EUA.
- **Liquidez é uma restrição**: O fator Size (SMB) é difícil de implementar no Brasil porque muitas small caps têm liquidez extremamente baixa.
- **Fundos quantitativos brasileiros**: Gestoras como Kadima, Giant Steps e Murano utilizam modelos multi-factor.
- **Dados**: A Economatica e o NEFIN-USP fornecem dados de fatores para o mercado brasileiro. O NEFIN calcula os fatores Fama-French para o Brasil: https://nefin.com.br/

> [!tip] Para Investidores Brasileiros
> Considere exposição a fatores via [[etfs]] globais (IVVB11 para mercado, ou ETFs de fator americanos via conta internacional). A diversificação geográfica potencializa os benefícios do factor investing. Veja também [[portfolio-theory-mpt]] e [[risk-and-return]].

## Formulas

**Alpha de um portfólio no modelo multi-factor:**

$$\alpha = R_p - R_f - \sum_{k} \beta_k \cdot F_k$$

Se $\alpha > 0$, o portfólio gera retorno acima do explicado pelos fatores.

**Information Ratio:**

$$IR = \frac{\alpha}{\sigma(\epsilon)}$$

Mede a habilidade do gestor em gerar alpha por unidade de risco residual.

## References

- Fama, Eugene F. & French, Kenneth R. "Common Risk Factors in the Returns on Stocks and Bonds." *Journal of Financial Economics*, 1993.
- Fama, Eugene F. & French, Kenneth R. "A Five-Factor Asset Pricing Model." *Journal of Financial Economics*, 2015.
- Carhart, Mark M. "On Persistence in Mutual Fund Performance." *Journal of Finance*, 1997.
- Asness, Clifford S. et al. "Quality Minus Junk." *Review of Accounting Studies*, 2019.
- Frazzini, Andrea & Pedersen, Lasse H. "Betting Against Beta." *Journal of Financial Economics*, 2014.
- Ang, Andrew. *Asset Management: A Systematic Approach to Factor Investing*. Oxford University Press, 2014.
- Berkin, Andrew & Swedroe, Larry. *Your Complete Guide to Factor-Based Investing*. BAM Alliance Press, 2016.

## Related

- [[momentum-strategies]]
- [[growth-vs-value]]
- [[portfolio-theory-mpt]]
- [[etfs]]
- [[risk-and-return]]
- [[backtesting-basics]]
