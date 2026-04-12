---
tags:
  - finance
  - markets
  - structure
aliases:
  - Como Funcionam os Mercados
  - Market Structure
  - Market Microstructure
complexity: basic
context: global
---

# Como Funcionam os Mercados

## Overview

Os mercados financeiros são sistemas organizados onde compradores e vendedores negociam ativos através de mecanismos padronizados de formação de preço. Entender a **market microstructure** — ou seja, como ordens são enviadas, processadas e executadas — é fundamental para qualquer investidor que queira operar de forma consciente, seja no mercado brasileiro ([[b3-structure]]) ou nos mercados internacionais ([[us-markets-overview]]).

A mecânica por trás de cada transação envolve tipos de ordens, o papel dos market makers, a dinâmica do order book e os mecanismos de proteção como circuit breakers. Sem esse conhecimento, o investidor opera às cegas.

## Core Concepts

### Tipos de Ordens (Order Types)

- **Market Order**: execução imediata ao melhor preço disponível. Prioriza velocidade sobre preço. Risco de slippage em ativos com baixa liquidez.
- **Limit Order**: define o preço máximo (compra) ou mínimo (venda) aceitável. Garante preço, mas não garante execução.
- **Stop Order (Stop Loss)**: torna-se uma market order quando o preço atinge o nível definido. Usado para proteção de posição.
- **Stop-Limit Order**: combina stop e limit — quando o preço de stop é atingido, uma limit order é enviada. Mais controle, mas risco de não execução em gaps.
- **Trailing Stop**: stop que se ajusta automaticamente conforme o preço se move a favor da posição.

> [!tip] Dica Prática
> Para ativos líquidos como PETR4 ou VALE3, market orders geralmente funcionam bem. Para small caps com spread largo, sempre use limit orders para evitar execuções desfavoráveis.

### Bid-Ask Spread

O **bid** é o maior preço que um comprador está disposto a pagar. O **ask** (ou offer) é o menor preço que um vendedor aceita. A diferença entre eles é o **spread**, que representa o custo implícito de transação.

- Ativos líquidos: spread estreito (ex: PETR4 com spread de R$ 0,01)
- Ativos ilíquidos: spread largo (ex: small caps com spread de R$ 0,10 ou mais)
- O spread tende a aumentar em momentos de alta volatilidade e incerteza

### Market Makers e Provisão de Liquidez

Market makers são participantes que se comprometem a manter ofertas de compra e venda continuamente no book de ofertas, garantindo liquidez ao mercado. Na B3, existem programas formais de market making, especialmente para opções e ETFs.

Eles lucram com o spread e com rebates oferecidos pela bolsa. Em contrapartida, assumem o risco de inventário — manter posições indesejadas quando o mercado se move contra eles.

### Order Book (Livro de Ofertas)

- **Level 1**: mostra apenas o melhor bid e o melhor ask (top of book), com volumes agregados.
- **Level 2 (Market Depth)**: mostra múltiplos níveis de preço com as respectivas quantidades, revelando a profundidade do mercado.

> [!info] Leitura do Book
> Observar o Level 2 permite identificar suportes e resistências de curto prazo baseados em volume. Ordens grandes em determinados preços funcionam como "paredes" temporárias. Porém, atenção: ordens podem ser canceladas a qualquer momento (spoofing é ilegal mas ocorre).

### Price Discovery (Descoberta de Preço)

O processo pelo qual o mercado determina o preço justo de um ativo através da interação entre oferta e demanda. Ocorre continuamente durante o pregão e de forma concentrada nos leilões de abertura e fechamento.

Na B3, o **call de abertura** (pré-abertura) e o **call de fechamento** são períodos onde ordens são acumuladas e executadas a um preço único que maximiza o volume negociado.

### Circuit Breakers

Mecanismo de proteção que interrompe as negociações quando o mercado cai de forma abrupta. Na B3, os gatilhos são:

| Nível | Queda do Ibovespa | Pausa |
|-------|-------------------|-------|
| 1º    | 10%               | 30 minutos |
| 2º    | 15%               | 1 hora |
| 3º    | 20%               | Prazo definido pela B3 |

> [!warning] Circuit Breakers Históricos no Brasil
> Os circuit breakers foram acionados diversas vezes: crise de 2008, Joesley Day (2017, queda de 8,8% — quase acionou), e múltiplas vezes em março de 2020 durante o COVID-19. Conhecer o mecanismo evita pânico.

### After-Hours Trading e Dark Pools

- **After-hours**: negociação fora do horário regular, com menor liquidez e spreads maiores. Mais comum nos EUA (pre-market das 4h às 9:30h e after-hours das 16h às 20h ET). Na B3, o after-market opera das 17:25 às 17:45 com limitação de oscilação de 2%.
- **Dark pools**: plataformas de negociação privadas onde ordens grandes são executadas sem exposição pública no order book. Usadas por institucionais ([[market-participants]]) para evitar impacto de mercado. Não existem formalmente no Brasil, mas são relevantes nos EUA.

### Best Execution

Obrigação regulatória de buscar a melhor execução possível para o cliente, considerando preço, velocidade, probabilidade de execução e custo total. Nos EUA, regulado pela Rule 606 da SEC. No Brasil, a CVM estabelece princípios semelhantes através de normas de conduta para intermediários.

## How to Apply

1. **Escolha o tipo de ordem adequado**: market orders para ativos líquidos quando velocidade importa; limit orders para controlar o preço de entrada/saída.
2. **Monitore o spread**: antes de operar, verifique o spread. Se for superior a 0,5% do preço do ativo, considere usar limit orders.
3. **Use stop loss**: defina sempre um nível de saída antes de entrar na operação. Stop-limit para ativos líquidos; stop regular para garantir execução.
4. **Observe o book**: o Level 2 revela pressão compradora ou vendedora de curto prazo.

## Examples

> [!example] Exemplo: Execução de uma Compra
> Você quer comprar 1.000 ações de ITUB4. O book mostra: Bid R$ 32,50 (500 ações) | Ask R$ 32,52 (300 ações). Se enviar market order de 1.000, comprará 300 a R$ 32,52 e as próximas 700 aos preços seguintes do ask (R$ 32,53, R$ 32,54, etc.). O preço médio será superior a R$ 32,52. Com limit order a R$ 32,52, você compraria apenas 300 e esperaria mais ofertas.

## Gotchas

- **Slippage em market orders**: em momentos de alta volatilidade, o preço executado pode diferir significativamente do exibido.
- **Ordens fantasma (spoofing)**: grandes ordens no book que são canceladas antes da execução para manipular a percepção de oferta/demanda.
- **After-market com baixa liquidez**: evite operar no after-market da B3 com ordens a mercado.
- **Gaps de abertura**: o preço de abertura pode diferir muito do fechamento anterior, invalidando stops colocados fora do horário.

## Brazilian Context

Na B3, a negociação ocorre das 10:00 às 17:00 (horário regular), com call de abertura às 9:45 e call de fechamento às 16:55-17:00. O settlement (liquidação) de ações é em **D+2** (dois dias úteis após a negociação). O sistema de negociação é o PUMA Trading System, plataforma de alta performance. O mercado fracionário permite negociar lotes menores que 100 ações (sufixo F, ex: PETR4F), ideal para investidores com menor capital. Veja mais em [[b3-structure]].

## Formulas

$$\text{Spread (\%)} = \frac{\text{Ask} - \text{Bid}}{\text{Midpoint}} \times 100$$

$$\text{Midpoint} = \frac{\text{Bid} + \text{Ask}}{2}$$

$$\text{VWAP} = \frac{\sum (P_i \times Q_i)}{\sum Q_i}$$

Onde VWAP (Volume Weighted Average Price) é o preço médio ponderado por volume, usado como benchmark de execução.

## References

- Harris, L. — *Trading and Exchanges: Market Microstructure for Practitioners*
- B3 — Regras e Procedimentos de Negociação (site oficial)
- CVM — Instruções sobre intermediação e best execution
- Investopedia — Order Types, Market Microstructure

## Related

- [[market-participants]]
- [[b3-structure]]
- [[us-markets-overview]]
- [[stocks-fundamentals]]
