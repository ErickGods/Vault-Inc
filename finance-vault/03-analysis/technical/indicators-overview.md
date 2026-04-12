---
tags:
  - finance
  - analysis
  - technical
  - indicators
aliases:
  - Indicadores Técnicos
  - Technical Indicators
complexity: intermediate
context: global
created: 2026-04-06
---

# Indicadores Técnicos (Technical Indicators)

## Overview

Indicadores técnicos são cálculos matemáticos baseados em preço, volume ou open interest de um ativo. Eles transformam dados brutos em sinais visuais que auxiliam na identificação de tendências, momentum, volatilidade e condições de sobrecompra/sobrevenda. Indicadores são ferramentas — não oráculos. Seu valor está na capacidade de confirmar ou questionar a leitura de [[price-action]], nunca de substituí-la.

> [!info] Classificação dos Indicadores
> - **Trend-following (rastreadores de tendência)**: Moving Averages, MACD
> - **Oscillators (osciladores)**: RSI, Stochastic
> - **Volatility (volatilidade)**: Bollinger Bands, ATR
> - **Volume**: OBV, VWAP

## Core Concepts

### Moving Averages (Médias Móveis)

As médias móveis suavizam o ruído do preço e revelam a tendência subjacente. São a base de muitos outros indicadores.

#### SMA — Simple Moving Average

Média aritmética dos últimos N períodos de fechamento.

$$SMA_n = \frac{\sum_{i=1}^{n} P_i}{n}$$

Onde $P_i$ é o preço de fechamento no período $i$ e $n$ é o número de períodos.

- **SMA(20)**: Tendência de curto prazo. Usada como suporte/resistência dinâmica em swing trading.
- **SMA(50)**: Tendência de médio prazo. Referência institucional.
- **SMA(200)**: Tendência de longo prazo. Ativos acima da SMA(200) estão em tendência de alta estrutural.

#### EMA — Exponential Moving Average

Atribui peso maior aos preços mais recentes, respondendo mais rapidamente às mudanças.

$$EMA_t = P_t \times k + EMA_{t-1} \times (1 - k)$$

Onde $k = \frac{2}{n + 1}$ é o fator de suavização (smoothing factor).

#### Crossovers (Cruzamentos)

| Crossover | Sinal | Descrição |
|-----------|-------|-----------|
| **Golden Cross** | Bullish | SMA(50) cruza acima da SMA(200) |
| **Death Cross** | Bearish | SMA(50) cruza abaixo da SMA(200) |
| **EMA(9) × EMA(21)** | Curto prazo | Popular para swing trading |

> [!warning] Indicador Atrasado
> Médias móveis são lagging indicators — confirmam tendências já em andamento. Não as use para prever reversões. Crossovers geram sinais tardios em mercados laterais (whipsaw).

### RSI — Relative Strength Index

Oscilador de momentum que mede a velocidade e magnitude das variações de preço. Criado por J. Welles Wilder Jr.

$$RSI = 100 - \frac{100}{1 + RS}$$

Onde:

$$RS = \frac{\text{Média dos ganhos nos últimos } n \text{ períodos}}{\text{Média das perdas nos últimos } n \text{ períodos}}$$

O período padrão é $n = 14$.

**Interpretação:**
- **RSI > 70**: Zona de sobrecompra (overbought). Potencial correção ou reversão para baixo.
- **RSI < 30**: Zona de sobrevenda (oversold). Potencial recuperação ou reversão para cima.
- **RSI = 50**: Linha neutra. Em tendências fortes de alta, o RSI tende a oscilar entre 40-80. Em tendências de baixa, entre 20-60.

> [!tip] Divergências RSI
> - **Divergência bullish**: Preço faz novos fundos, RSI faz fundos mais altos → possível reversão para cima.
> - **Divergência bearish**: Preço faz novos topos, RSI faz topos mais baixos → possível reversão para baixo.

### MACD — Moving Average Convergence Divergence

Indicador de tendência e momentum. Criado por Gerald Appel.

$$MACD = EMA(12) - EMA(26)$$

$$\text{Signal Line} = EMA(9) \text{ do MACD}$$

$$\text{Histogram} = MACD - \text{Signal Line}$$

**Sinais:**
- **MACD cruza acima da Signal Line**: Sinal de compra.
- **MACD cruza abaixo da Signal Line**: Sinal de venda.
- **Histograma crescente**: Momentum bullish aumentando.
- **Histograma decrescente**: Momentum bearish aumentando.
- **Divergências**: Mesma lógica do RSI — preço vs MACD divergindo indica possível reversão.

### Bollinger Bands (Bandas de Bollinger)

Indicador de volatilidade criado por John Bollinger. Consiste em três linhas:

$$\text{Banda Superior} = SMA(20) + 2\sigma$$

$$\text{Banda Central} = SMA(20)$$

$$\text{Banda Inferior} = SMA(20) - 2\sigma$$

Onde $\sigma$ é o desvio padrão dos últimos 20 períodos.

**Interpretação:**
- **Squeeze (bandas apertadas)**: Baixa volatilidade. Frequentemente precede um movimento explosivo.
- **Preço toca a banda superior**: Não é automaticamente sinal de venda. Em tendências fortes, o preço "anda" na banda (Bollinger Band Walk).
- **Preço toca a banda inferior**: Idem, não é automaticamente sinal de compra.
- **Largura das bandas (Bandwidth)**: Mede a volatilidade relativa. Mínimas históricas de bandwidth precedem breakouts.

### Volume Indicators

#### OBV — On Balance Volume

Acumula volume positivamente em dias de alta e negativamente em dias de baixa.

$$OBV_t = OBV_{t-1} + \begin{cases} Volume & \text{se } Close_t > Close_{t-1} \\ -Volume & \text{se } Close_t < Close_{t-1} \\ 0 & \text{se } Close_t = Close_{t-1} \end{cases}$$

Se o OBV sobe enquanto o preço está lateral, indica acumulação (smart money comprando).

#### VWAP — Volume Weighted Average Price

Preço médio ponderado pelo volume. Referência institucional para execução de ordens.

$$VWAP = \frac{\sum (Preço_{típico} \times Volume)}{\sum Volume}$$

Onde $Preço_{típico} = \frac{High + Low + Close}{3}$.

- Preço acima do VWAP: Compradores no controle.
- Preço abaixo do VWAP: Vendedores no controle.
- VWAP funciona como suporte/resistência dinâmica intraday.

### Stochastic Oscillator (Estocástico)

Oscilador que compara o preço de fechamento com a faixa de preço em um determinado período.

$$\%K = \frac{Close - Low_n}{High_n - Low_n} \times 100$$

$$\%D = SMA(3) \text{ de } \%K$$

Onde $n$ é tipicamente 14 períodos.

- **%K > 80**: Sobrecompra.
- **%K < 20**: Sobrevenda.
- **Cruzamento %K acima de %D em zona de sobrevenda**: Sinal de compra.
- **Cruzamento %K abaixo de %D em zona de sobrecompra**: Sinal de venda.

## How to Apply — Confluence (Confluência)

> [!important] Nunca Use Um Indicador Isolado
> A força dos indicadores está na confluência — quando múltiplos indicadores independentes apontam na mesma direção.

**Exemplo de setup confluente:**
1. Preço acima da SMA(200) → tendência de alta de longo prazo confirmada.
2. Pullback até a SMA(50) com RSI em 35 (próximo de sobrevenda) → correção dentro da tendência.
3. MACD histograma virando positivo → momentum retornando.
4. [[candlestick-patterns]] de reversão bullish (hammer) no nível da SMA(50).
5. Volume crescente no candle de reversão.

**Combinações recomendadas:**
- Trend + Oscillator: EMA + RSI
- Trend + Volume: MACD + OBV
- Volatility + Oscillator: Bollinger Bands + Stochastic

## Examples

**Golden Cross em PETR4**: Em março de 2023, a SMA(50) de PETR4 cruzou acima da SMA(200) com volume crescente. O papel subiu aproximadamente 25% nos 3 meses seguintes, acompanhado de RSI consistentemente acima de 50.

**Bollinger Squeeze em WEGE3**: Após semanas de consolidação com as bandas de Bollinger extremamente apertadas, o papel rompeu para cima com volume 3x acima da média, iniciando um rally de 15%.

## Gotchas

- **Paralisia por análise**: Usar muitos indicadores simultaneamente gera sinais conflitantes. Escolha 2-3 indicadores de categorias diferentes.
- **Otimização excessiva (curve fitting)**: Ajustar parâmetros de indicadores para se adequar ao passado não garante resultados futuros. Veja [[backtesting-basics]].
- **Mercados laterais**: Indicadores de tendência (médias móveis, MACD) geram muitos sinais falsos em mercados sem direção definida.
- **Indicadores atrasados vs antecedentes**: Médias móveis confirmam tendência (lagging). RSI e Stochastic antecipam reversões (leading). Saiba qual está usando.

## Brazilian Context

- **VWAP** é amplamente utilizado por day traders no mini índice (WIN) e mini dólar (WDO) na B3.
- A maioria das plataformas brasileiras (Profit, Tryd, MetaTrader) oferece todos estes indicadores nativamente.
- Para ações de menor liquidez na B3, indicadores de volume são menos confiáveis devido ao baixo número de negócios.
- O IFR (Índice de Força Relativa) é como o RSI é chamado em português no mercado brasileiro.

## Formulas — Resumo

| Indicador | Fórmula Principal |
|-----------|-------------------|
| SMA | $\frac{\sum P_i}{n}$ |
| EMA | $P_t \times k + EMA_{t-1} \times (1-k)$ |
| RSI | $100 - \frac{100}{1+RS}$ |
| MACD | $EMA(12) - EMA(26)$ |
| Bollinger | $SMA(20) \pm 2\sigma$ |
| OBV | $OBV_{t-1} \pm Volume$ |
| VWAP | $\frac{\sum(P_{típico} \times Vol)}{\sum Vol}$ |
| Stochastic | $\frac{C - L_n}{H_n - L_n} \times 100$ |

## References

- Wilder Jr., J. Welles. *New Concepts in Technical Trading Systems*. Trend Research, 1978.
- Appel, Gerald. *Technical Analysis: Power Tools for Active Investors*. FT Press.
- Bollinger, John. *Bollinger on Bollinger Bands*. McGraw-Hill.
- Murphy, John J. *Technical Analysis of the Financial Markets*. New York Institute of Finance.

## Related

- [[price-action]]
- [[support-resistance]]
- [[candlestick-patterns]]
- [[momentum-strategies]]
- [[backtesting-basics]]
