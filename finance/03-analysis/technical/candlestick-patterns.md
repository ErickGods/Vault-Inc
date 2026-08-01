---
tags:
  - finance
  - analysis
  - technical
  - candlesticks
aliases:
  - Candlesticks
  - Padrões de Candle
  - Japanese Candlesticks
house: finance
domain: analysis/technical
level: intro
status: active
created: 2026-04-06
updated: 2026-07-29
---

# Candlestick Patterns (Padrões de Candle)

## Overview

Os candlesticks (velas japonesas) são a forma mais popular de representação gráfica de preços, originada no Japão do século XVIII por comerciantes de arroz. Cada candle encapsula quatro informações essenciais — abertura, máxima, mínima e fechamento — em uma representação visual que revela a psicologia do mercado naquele período. A leitura de padrões de candlestick é uma habilidade central em [[price-action]] e complementa diretamente a análise de [[support-resistance]].

> [!info] Origem Histórica
> Munehisa Homma, comerciante japonês de arroz em Sakata no século XVIII, é creditado como o pioneiro da análise de candlesticks. Seus métodos foram sistematizados e popularizados no Ocidente por Steve Nison na década de 1990.

## Core Concepts

### Anatomia de um Candle

```
    │         ← Upper Shadow (Sombra Superior / Pavio)
    │
 ┌──┴──┐     ← High
 │     │
 │ BODY│     ← Corpo (diferença entre Open e Close)
 │     │
 └──┬──┘     ← Low
    │
    │         ← Lower Shadow (Sombra Inferior / Pavio)
```

- **Open (Abertura)**: Preço no início do período.
- **Close (Fechamento)**: Preço no final do período.
- **High (Máxima)**: Preço mais alto atingido no período.
- **Low (Mínima)**: Preço mais baixo atingido no período.
- **Body (Corpo)**: Área entre open e close. Corpo cheio/vermelho = close < open (bearish). Corpo vazio/verde = close > open (bullish).
- **Shadows/Wicks (Sombras/Pavios)**: Linhas finas acima e abaixo do corpo, representando os extremos de preço rejeitados.

> [!tip] O que as sombras dizem
> Sombra superior longa = vendedores empurraram o preço para baixo (pressão de venda). Sombra inferior longa = compradores empurraram o preço para cima (pressão de compra). O corpo mostra quem venceu a batalha; as sombras mostram como foi a luta.

### Padrões de Reversão (Reversal Patterns)

#### Doji

Candle onde o preço de abertura e fechamento são praticamente iguais. Representa indecisão.

```
    │
    │
  ──┼──       ← Open ≈ Close (corpo mínimo)
    │
    │
```

- **Standard Doji**: Sombras superior e inferior equilibradas. Indecisão pura.
- **Dragonfly Doji**: Longa sombra inferior, sem sombra superior. Em fundo, é bullish.
- **Gravestone Doji**: Longa sombra superior, sem sombra inferior. Em topo, é bearish.

> [!warning] Doji Isolado
> Um doji isolado NÃO é sinal de reversão. Ele sinaliza indecisão — a reversão só é confirmada pelo candle seguinte. Sempre espere confirmação.

#### Hammer (Martelo)

Candle com corpo pequeno na parte superior e longa sombra inferior (pelo menos 2x o corpo). Indica rejeição de preços mais baixos.

```
  ┌─┐
  │ │         ← Corpo pequeno (no topo)
  └┬┘
   │
   │          ← Sombra inferior longa (≥ 2x corpo)
   │
```

- Aparece em **fundos** (após tendência de baixa).
- Cor do corpo é secundária, mas hammer verde (bullish) é mais forte.
- Confirmação: candle seguinte fecha acima do corpo do hammer.

#### Inverted Hammer (Martelo Invertido)

Corpo pequeno na parte inferior, longa sombra superior. Aparece em fundos.

```
   │
   │          ← Sombra superior longa
   │
  ┌┴┐
  │ │         ← Corpo pequeno (na base)
  └─┘
```

- Menos confiável que o hammer. Requer forte confirmação.

#### Shooting Star (Estrela Cadente)

Visualmente idêntico ao inverted hammer, mas aparece em **topos** (após tendência de alta). Sinaliza possível reversão bearish.

```
   │
   │          ← Sombra superior longa (pressão vendedora)
   │
  ┌┴┐
  │ │         ← Corpo pequeno (na base)
  └─┘
```

#### Engulfing (Engolfo)

Padrão de dois candles onde o segundo corpo "engolfa" completamente o primeiro.

**Bullish Engulfing:**
```
  ┌─┐
  │▓│  ┌───┐
  │▓│  │   │
  └─┘  │   │     ← Corpo verde engolfa corpo vermelho anterior
       │   │
       └───┘
```

- Aparece em fundos. O segundo candle (bullish) abre abaixo e fecha acima do corpo do primeiro (bearish).

**Bearish Engulfing:**
- Inverso. Aparece em topos. Candle bearish engolfa o bullish anterior.

> [!note] Confiabilidade
> Engulfing patterns em níveis de [[support-resistance]] com volume acima da média são dos padrões mais confiáveis. Taxa de acerto significativamente maior que a maioria dos padrões de candle único.

#### Morning Star (Estrela da Manhã)

Padrão de três candles — reversão bullish:

1. Candle bearish longo (continuação da tendência de baixa).
2. Candle de corpo pequeno (gap down) — indecisão (pode ser doji).
3. Candle bullish longo que fecha acima do ponto médio do primeiro candle.

#### Evening Star (Estrela da Noite)

Inverso da morning star — reversão bearish:

1. Candle bullish longo.
2. Candle de corpo pequeno (gap up).
3. Candle bearish longo que fecha abaixo do ponto médio do primeiro.

### Padrões de Continuação (Continuation Patterns)

#### Marubozu

Candle de corpo longo sem sombras (ou sombras mínimas). Demonstra domínio absoluto de compradores (bullish marubozu) ou vendedores (bearish marubozu).

```
  ┌───┐
  │   │
  │   │       ← Corpo longo, sem sombras
  │   │
  └───┘
```

- Indica forte convicção na direção. Continuação provável.

#### Three White Soldiers (Três Soldados Brancos)

Três candles bullish consecutivos com corpos longos, cada um abrindo dentro do corpo anterior e fechando acima do fechamento anterior.

- Sinal forte de reversão bullish quando aparece após tendência de baixa.
- Se os corpos diminuem progressivamente, indica enfraquecimento do momentum.

#### Three Black Crows (Três Corvos Negros)

Inverso dos Three White Soldiers — três candles bearish consecutivos.

- Sinal forte de reversão bearish quando aparece após tendência de alta.

### Ranking de Confiabilidade dos Padrões

| Padrão | Tipo | Confiabilidade |
|--------|------|---------------|
| Engulfing (em S/R) | Reversão | Alta |
| Morning/Evening Star | Reversão | Alta |
| Three White Soldiers / Black Crows | Reversão | Média-Alta |
| Hammer (em suporte) | Reversão | Média-Alta |
| Shooting Star (em resistência) | Reversão | Média |
| Doji (isolado) | Indecisão | Baixa (precisa confirmação) |
| Inverted Hammer | Reversão | Média-Baixa |
| Marubozu | Continuação | Média |

> [!important] Contexto é Rei
> A confiabilidade de qualquer padrão de candlestick **depende inteiramente do contexto**. Um hammer em uma zona de suporte forte com divergência bullish no RSI (ver [[indicators-overview]]) tem probabilidade muito maior de sucesso do que um hammer no meio de uma tendência de baixa sem nenhum nível de referência.

## How to Apply

1. **Identifique a tendência** e os níveis de [[support-resistance]] antes de procurar padrões de candle.
2. **Busque padrões apenas em zonas relevantes** — topos, fundos, suportes, resistências, médias móveis.
3. **Confirme com volume**: Padrões de reversão com volume crescente são mais confiáveis.
4. **Espere confirmação**: Candles de reversão individuais (hammer, doji, shooting star) precisam de um candle seguinte confirmando a direção.
5. **Use stop loss**: Posicione o stop além da sombra do padrão (abaixo do hammer, acima do shooting star).

## Examples

**Hammer em Suporte de BBDC4**: BBDC4 corrige até a região de R$14, que é um suporte testado 3 vezes no passado. Forma um hammer com sombra inferior de R$0,80 e corpo de R$0,30. Volume 2x acima da média. No dia seguinte, gap up confirma reversão. Entrada em R$14,30 com stop em R$13,50 e alvo em R$16.

**Bearish Engulfing no Topo de MGLU3**: Após rally de 40%, MGLU3 forma um bearish engulfing em resistência com volume recorde. O segundo candle abre acima da máxima anterior e fecha abaixo da mínima. Início de correção de 25% nas semanas seguintes.

## Gotchas

- **Não decore padrões sem entender a lógica**: O hammer funciona porque mostra que vendedores tentaram empurrar o preço para baixo e falharam — compradores reagiram com força. Entenda o porquê.
- **Padrões em timeframes muito curtos (1min, 5min)** são pouco confiáveis e geram muito ruído.
- **Gaps são raros na B3 intraday** devido ao livro de ofertas contínuo. Padrões como morning star que dependem de gaps funcionam melhor no gráfico diário.
- **Cor do corpo é menos importante que a estrutura**: Um hammer vermelho em suporte forte ainda é um sinal relevante.
- **Backtesting é fundamental**: Teste seus padrões favoritos estatisticamente antes de confiar neles. Veja [[backtesting-basics]].

## Brazilian Context

- Na B3, o gráfico diário é o mais popular para análise de candlesticks, especialmente para swing trading.
- Termos em português comuns: martelo (hammer), engolfo (engulfing), estrela da manhã/noite (morning/evening star), doji, enforcado (hanging man).
- Para mini índice e mini dólar, padrões de candle no gráfico de 5 e 15 minutos são utilizados por day traders, mas sempre com confirmação de [[indicators-overview]].
- Muitos traders brasileiros combinam candlesticks com Fibonacci (ver [[support-resistance]]) como método principal de operação.

## Formulas

**Tamanho relativo do corpo:**

$$\text{Body Ratio} = \frac{|Close - Open|}{High - Low}$$

Body Ratio > 0.6 indica domínio claro de uma das forças. Body Ratio < 0.2 indica indecisão (doji-like).

**Sombra Inferior Ratio (para identificar hammers):**

$$\text{Lower Shadow Ratio} = \frac{Min(Open, Close) - Low}{High - Low}$$

Lower Shadow Ratio > 0.6 com Body Ratio < 0.3 = hammer.

## References

- Nison, Steve. *Japanese Candlestick Charting Techniques*. Prentice Hall, 2001.
- Nison, Steve. *Beyond Candlesticks*. Wiley, 1994.
- Bulkowski, Thomas. *Encyclopedia of Candlestick Charts*. Wiley, 2008.
- Morris, Gregory L. *Candlestick Charting Explained*. McGraw-Hill.

## Related

- [[price-action]]
- [[support-resistance]]
- [[indicators-overview]]
- [[investor-psychology]]
- [[backtesting-basics]]
