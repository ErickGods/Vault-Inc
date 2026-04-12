---
tags:
  - finance
  - analysis
  - technical
  - support-resistance
aliases:
  - Suporte e Resistência
  - Support and Resistance
complexity: basic
context: global
created: 2026-04-06
---

# Suporte e Resistência (Support and Resistance)

## Overview

Suporte e resistência são os conceitos mais fundamentais da análise técnica. Representam níveis de preço onde a dinâmica de oferta e demanda tende a causar pausa, reversão ou aceleração no movimento do ativo. Suporte é o nível onde a demanda (compradores) é forte o suficiente para impedir que o preço caia mais. Resistência é o nível onde a oferta (vendedores) é forte o suficiente para impedir que o preço suba mais. Dominar a identificação desses níveis é pré-requisito para qualquer estratégia de trading.

> [!info] Conceito Chave
> Suporte e resistência não são linhas exatas — são **zonas** de preço. O mercado não é preciso ao pip; trate esses níveis como faixas com margem de alguns ticks ou percentuais.

## Core Concepts

### Como Identificar Níveis de S/R

#### Swing Highs e Swing Lows

O método mais direto: marque os pontos onde o preço reverteu no passado. Topos anteriores (swing highs) funcionam como resistência. Fundos anteriores (swing lows) funcionam como suporte.

- **Quanto mais vezes um nível foi testado**, mais significativo ele é.
- **Quanto mais recente o teste**, mais relevante o nível.
- **Quanto maior o timeframe**, mais forte o nível. Um suporte no gráfico semanal é mais relevante que no gráfico de 15 minutos.

#### Volume Profile

O Volume Profile mostra a distribuição de volume negociado em cada faixa de preço, revelando onde houve maior atividade.

- **High Volume Nodes (HVN)**: Faixas de preço com alto volume negociado — funcionam como ímãs que atraem o preço (equilíbrio de mercado). Atuam como S/R fortes.
- **Low Volume Nodes (LVN)**: Faixas com pouco volume — o preço tende a atravessá-las rapidamente. Atuam como espaços vazios.
- **Point of Control (POC)**: O nível de preço com maior volume negociado no período. Referência de valor justo.

### Fibonacci Retracements

Ferramenta baseada na sequência de Fibonacci para projetar níveis de correção dentro de uma tendência. Os ratios são derivados das relações entre números da sequência.

**Níveis principais:**

| Nível | Significado |
|-------|-------------|
| **23.6%** | Correção rasa — tendência muito forte |
| **38.2%** | Correção moderada — nível frequente de suporte em uptrends saudáveis |
| **50.0%** | Não é Fibonacci puro, mas amplamente utilizado (nível psicológico) |
| **61.8%** | Golden ratio — correção profunda, último bastião antes de invalidar tendência |
| **78.6%** | Correção severa — quase reversão total do movimento |

> [!tip] Como Traçar Fibonacci
> Em uma tendência de alta, trace do fundo (swing low) ao topo (swing high). Os níveis de retração indicam onde o preço pode encontrar suporte durante a correção. Em tendência de baixa, trace do topo ao fundo.

**Cálculo:**

$$\text{Nível de Retração} = \text{Topo} - (\text{Topo} - \text{Fundo}) \times \text{Ratio}$$

Exemplo: Se o ativo subiu de R$20 para R$30, a retração de 38.2% estará em:

$$30 - (30 - 20) \times 0.382 = 30 - 3.82 = R\$26.18$$

### Pivot Points

Pivot Points são calculados a partir dos dados de preço do período anterior e geram níveis automáticos de S/R para o período atual. Muito utilizados por day traders.

**Fórmulas (Classic Pivot):**

$$PP = \frac{High + Low + Close}{3}$$

$$R1 = 2 \times PP - Low$$

$$S1 = 2 \times PP - High$$

$$R2 = PP + (High - Low)$$

$$S2 = PP - (High - Low)$$

$$R3 = High + 2 \times (PP - Low)$$

$$S3 = Low - 2 \times (High - PP)$$

> [!note] Variações de Pivot
> Existem variações como Woodie, Camarilla e Fibonacci Pivots, cada uma com pesos diferentes nos cálculos. O Classic (Standard) é o mais utilizado.

### Números Redondos como Níveis Psicológicos

Preços redondos atuam naturalmente como suporte e resistência porque:

- Ordens de stop loss e take profit são frequentemente colocadas em números redondos.
- O viés psicológico humano favorece números "limpos" (R$10, R$50, R$100, 100.000 pontos no IBOV).
- Grandes ordens institucionais frequentemente usam preços redondos como referência.

Exemplos clássicos: IBOV em 100k, 120k, 130k pontos. Dólar em R$5,00, R$5,50. Bitcoin em $30.000, $50.000, $100.000.

### Suporte Vira Resistência (e Vice-Versa)

> [!important] Princípio da Polaridade
> Quando um nível de suporte é rompido, ele tende a se tornar resistência. Quando uma resistência é rompida, ela tende a se tornar suporte. Esse princípio é chamado de **polarity flip** ou **role reversal**.

**Por que isso acontece?**

Imagine que muitos traders compraram em um nível de suporte em R$25. Quando o preço cai abaixo de R$25, esses traders estão no prejuízo. Quando o preço retorna a R$25, muitos vendem para "sair no zero a zero" — gerando oferta nesse nível, que agora funciona como resistência.

### Volume at Price

A análise de volume at price complementa os níveis horizontais tradicionais:

- Níveis com alto volume acumulado representam consenso de preço — o mercado "aceita" aquele valor como justo.
- Rompimentos de níveis de alto volume são mais significativos e tendem a ser sustentados.
- Áreas de baixo volume entre dois HVNs criam um "vácuo" onde o preço se move rapidamente de um nível ao outro.

## How to Apply

1. **Comece pelo timeframe superior** (semanal/mensal) para identificar os S/R macro.
2. **Desça para o diário** e marque níveis intermediários.
3. **Use múltiplas ferramentas**: Combine swing highs/lows com Fibonacci e pivots. Quando múltiplas ferramentas apontam para o mesmo nível, a confluência aumenta a confiabilidade.
4. **Observe o comportamento do preço** ao se aproximar do nível. Veja os padrões de [[candlestick-patterns]] para sinais de reversão ou continuação.
5. **Volume é o juiz**: S/R sem confirmação de volume é fraco. Use [[indicators-overview]] como OBV e VWAP para validar.

## Examples

**Fibonacci + Suporte Horizontal em VALE3**: O papel sobe de R$60 a R$80 e inicia correção. A retração de 50% cai em R$70, que coincide com um topo anterior (suporte horizontal). Confluência de dois métodos no mesmo nível gera uma zona de suporte de alta probabilidade.

**Polarity Flip no Dólar Futuro**: O dólar rompe suporte em R$5,00 com forte volume. Dias depois, tenta retornar a R$5,00 mas encontra vendedores agressivos — o antigo suporte agora é resistência. O preço rejeita o nível e retoma a queda.

## Gotchas

- **Não trate S/R como linhas exatas**: Use zonas. Um ativo pode ultrapassar o nível em alguns centavos antes de reverter.
- **Excesso de linhas no gráfico**: Se você tem mais de 5-6 níveis visíveis, está poluindo a análise. Mantenha apenas os mais relevantes.
- **Fibonacci não é mágico**: Os níveis funcionam porque muitos traders os observam (self-fulfilling prophecy). Não há nada místico na "proporção áurea" nos mercados.
- **S/R de timeframes curtos são frágeis**: Um suporte no gráfico de 5 minutos pode ser varrido por um único lote de mercado. Priorize níveis de timeframes maiores.
- **Contexto de tendência**: Em tendências fortes, o preço pode romper múltiplos S/R sem pausar. Não compre em suporte contra a tendência dominante.

## Brazilian Context

- **Mini Índice (WIN)** e **Mini Dólar (WDO)**: Pivot Points são amplamente utilizados para day trading desses contratos na B3. Muitas plataformas brasileiras calculam automaticamente.
- O IBOV tem níveis psicológicos muito claros em múltiplos de 10.000 pontos (100k, 110k, 120k, 130k).
- Fibonacci é especialmente popular entre traders brasileiros — praticamente toda sala de análise e curso de AT no Brasil ensina essa ferramenta como central.
- Volume Profile está disponível em plataformas como Profit Pro e Tryd, muito utilizadas no Brasil.

## Formulas

**Fibonacci Retracement:**

$$\text{Nível} = \text{Extremo} - (\text{Range}) \times \text{Ratio}$$

**Classic Pivot Point:**

$$PP = \frac{H + L + C}{3}$$

**Range de S/R:**

$$\text{Força do Nível} \propto \text{Toques} \times \text{Timeframe} \times \text{Volume}$$

## References

- Murphy, John J. *Technical Analysis of the Financial Markets*. New York Institute of Finance.
- Kirkpatrick, Charles D. & Dahlquist, Julie R. *Technical Analysis: The Complete Resource for Financial Market Technicians*. FT Press.
- Dalton, James F. *Mind Over Markets*. Traders Press.
- Bulkowski, Thomas. *Encyclopedia of Chart Patterns*. Wiley.

## Related

- [[price-action]]
- [[indicators-overview]]
- [[candlestick-patterns]]
- [[investor-psychology]]
