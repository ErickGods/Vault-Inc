---
tags:
  - finance
  - analysis
  - technical
  - price-action
aliases:
  - Price Action
  - Ação do Preço
complexity: intermediate
context: global
created: 2026-04-06
---

# Price Action

## Overview

Price Action é a disciplina de análise técnica que se baseia exclusivamente no movimento do preço para tomar decisões de trading e investimento. Diferente de abordagens que dependem de indicadores derivados, o price action interpreta diretamente o que o mercado está comunicando através da dinâmica de oferta e demanda refletida nos gráficos. É considerada a forma mais pura de leitura de mercado, pois todo indicador técnico é, em última instância, derivado do preço.

> [!info] Princípio Fundamental
> O preço desconta tudo. Toda informação disponível — fundamentos, notícias, expectativas — já está refletida no preço atual do ativo.

## Core Concepts

### Identificação de Tendência (Trend Identification)

A base do price action está na leitura de **higher highs / higher lows** (topos e fundos ascendentes) para tendências de alta, e **lower highs / lower lows** (topos e fundos descendentes) para tendências de baixa.

- **Uptrend**: Sequência de topos mais altos e fundos mais altos. Cada pullback encontra suporte acima do fundo anterior.
- **Downtrend**: Sequência de topos mais baixos e fundos mais baixos. Cada rally encontra resistência abaixo do topo anterior.
- **Sideways / Range**: Preço oscila entre um suporte e uma resistência definidos, sem formar novos extremos.

> [!tip] Regra Prática
> Uma tendência de alta só é invalidada quando o preço fecha abaixo do último fundo relevante (swing low). Não confunda correções normais com reversões.

### Chart Patterns (Padrões Gráficos)

#### Padrões de Reversão

- **Head and Shoulders (Ombro-Cabeça-Ombro)**: Três topos, sendo o central (cabeça) o mais alto. A quebra da neckline confirma reversão bearish. Alvo projetado = distância da cabeça à neckline.
- **Inverse Head and Shoulders**: Versão invertida, sinaliza reversão bullish.
- **Double Top (Topo Duplo)**: Dois topos no mesmo nível de preço com um vale entre eles. Confirmado na quebra do vale intermediário.
- **Double Bottom (Fundo Duplo)**: Dois fundos no mesmo nível. Confirmado na quebra do pico intermediário.

#### Padrões de Continuação

- **Triangles (Triângulos)**: Ascending (bullish bias), Descending (bearish bias), Symmetrical (neutro — rompe para o lado da tendência predominante).
- **Flags (Bandeiras)**: Pequeno canal na direção oposta à tendência principal. Bull flag = correção em canal descendente dentro de uptrend.
- **Wedges (Cunhas)**: Rising wedge (bearish), Falling wedge (bullish). Convergência de linhas de tendência com inclinação na mesma direção.
- **Pennants (Flâmulas)**: Triângulos simétricos compactos após um movimento forte (mastro). Padrão de continuação de curto prazo.

### Volume Analysis e Confirmação

O volume é o combustível do mercado. Movimentos de preço acompanhados de volume crescente têm maior probabilidade de sustentação.

- **Volume confirma tendência**: Em uptrend, volume deve aumentar nos dias de alta e diminuir nos dias de correção.
- **Volume em breakouts**: Rompimentos com volume acima da média têm maior taxa de sucesso. Rompimentos com volume fraco são suspeitos de fakeout.
- **Climax de volume**: Volume extremamente alto pode indicar exaustão — capitulação em fundos ou euforia em topos.
- **Divergência preço-volume**: Preço fazendo novas máximas com volume decrescente é um sinal de alerta clássico.

### Breakout vs Fakeout

> [!warning] Armadilha Comum
> Estatisticamente, muitos breakouts falham. Espere por confirmação (candle fechando acima/abaixo do nível com volume) antes de entrar na operação.

- **Breakout legítimo**: Fechamento além do nível de [[support-resistance]] com volume acima da média e follow-through no período seguinte.
- **Fakeout (falso rompimento)**: Preço ultrapassa o nível brevemente mas retorna rapidamente. Frequentemente usado por institucionais para acumular posições (stop hunting).
- **Retest**: Após breakout, o preço frequentemente retorna ao nível rompido para testá-lo (suporte vira resistência e vice-versa). Essa é uma entrada de menor risco.

### Timeframes (Periodicidades)

A análise de price action deve considerar múltiplos timeframes para contexto:

| Timeframe | Uso Típico | Tipo de Trader |
|-----------|-----------|----------------|
| Mensal/Semanal | Tendência macro, S/R principais | Position trader |
| Diário | Tendência intermediária, setups | Swing trader |
| 4h / 1h | Timing de entrada e saída | Swing / Day trader |
| 15min / 5min | Execução precisa | Day trader / Scalper |

> [!note] Multi-Timeframe Analysis
> Analise sempre pelo menos dois timeframes: um superior para contexto (direção da tendência) e um inferior para timing de entrada. Nunca opere contra a tendência do timeframe superior.

## How to Apply

1. **Identifique a tendência** no timeframe superior (semanal ou diário).
2. **Marque os níveis-chave** de [[support-resistance]] — topos e fundos anteriores, gaps, áreas de alto volume.
3. **Busque padrões** gráficos e de [[candlestick-patterns]] na região dos níveis-chave.
4. **Confirme com volume** — o volume valida ou invalida o setup.
5. **Defina entrada, stop e alvo** antes de abrir a posição. Use risk/reward mínimo de 2:1.

## Examples

**Bull Flag no IBOV**: Após um rali forte de 115k para 130k, o índice corrige em canal descendente com volume decrescente até 125k. O rompimento para cima do canal com volume crescente projeta alvo em 140k (extensão do mastro).

**Fakeout em Ação do Setor Bancário**: ITUB4 rompe resistência de R$32 intraday, mas fecha abaixo com volume fraco. No dia seguinte, retorna abaixo de R$31,50. Traders que compraram o breakout sem esperar confirmação de fechamento foram penalizados.

## Gotchas

- **Viés de confirmação**: Cuidado para não ver padrões onde não existem. Nem toda formação é um Head and Shoulders.
- **Overtrading**: Nem todo movimento de preço é um setup. Price action exige paciência para esperar confluência de fatores.
- **Contexto importa**: Um hammer em uma região de suporte tem significado muito diferente de um hammer no meio de uma consolidação.
- **Backtesting é essencial**: Valide seus padrões preferidos com dados históricos antes de operar com capital real. Veja [[backtesting-basics]].

## Brazilian Context

No mercado brasileiro, price action funciona de forma similar aos mercados globais, com algumas particularidades:

- **Liquidez concentrada**: Poucos ativos (PETR4, VALE3, ITUB4, BBDC4) têm volume suficiente para price action confiável em timeframes curtos.
- **Influência do mercado externo**: O IBOV frequentemente segue o S&P 500, especialmente na abertura. Considere o contexto global.
- **Minicontratos (mini índice e mini dólar)**: São os instrumentos mais populares para day trading de price action no Brasil, com alta liquidez.
- **Gaps e leilões**: A B3 possui leilões de abertura e fechamento que podem gerar gaps significativos.

## Formulas

**Projeção de alvo por padrão gráfico:**

$$\text{Alvo} = \text{Ponto de Breakout} \pm \text{Altura do Padrão}$$

**Risk/Reward Ratio:**

$$R:R = \frac{\text{Alvo} - \text{Entrada}}{\text{Entrada} - \text{Stop Loss}}$$

## References

- Murphy, John J. *Technical Analysis of the Financial Markets*. New York Institute of Finance.
- Brooks, Al. *Trading Price Action Trends*. Wiley.
- Nison, Steve. *Japanese Candlestick Charting Techniques*. Prentice Hall.
- Bulkowski, Thomas. *Encyclopedia of Chart Patterns*. Wiley.

## Related

- [[support-resistance]]
- [[candlestick-patterns]]
- [[indicators-overview]]
- [[investor-psychology]]
- [[backtesting-basics]]
