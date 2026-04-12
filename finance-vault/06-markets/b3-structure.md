---
tags:
  - finance
  - markets
  - b3
aliases:
  - B3 Estrutura
  - Bolsa B3
  - Segmentos B3
complexity: intermediate
context: br
---

# B3 — Estrutura da Bolsa Brasileira

## Overview

A B3 (Brasil, Bolsa, Balcão) é a bolsa de valores oficial do Brasil e uma das maiores do mundo em valor de mercado. Resultado de décadas de consolidação do mercado de capitais brasileiro, a B3 opera como bolsa de valores, mercadorias e futuros, além de atuar como câmara de compensação (clearinghouse) e depositária central. Entender sua estrutura é fundamental para qualquer investidor que opere no mercado brasileiro, pois ela define as regras, horários, segmentos de listagem e mecanismos de liquidação de todas as operações.

## Core Concepts

### História: Bovespa → BM&FBovespa → B3

- **Bovespa** (Bolsa de Valores de São Paulo): fundada em 1890, era a principal bolsa de ações do Brasil
- **BM&F** (Bolsa de Mercadorias & Futuros): focada em derivativos — futuros de juros (DI), câmbio (dólar), commodities
- **2008**: fusão Bovespa + BM&F = **BM&FBovespa**, criando uma das maiores bolsas do mundo
- **2017**: fusão com a CETIP (Central de Custódia e Liquidação Financeira de Títulos) = **B3**
- Hoje, a B3 é uma empresa listada com ticker **B3SA3**, com capitalização superior a R$ 70 bilhões

> [!info] Monopólio Natural
> A B3 é a única bolsa de valores do Brasil, operando como monopólio. Isso garante concentração de liquidez, mas também gera debates sobre competição e custos de transação. Não há concorrente direto, diferente dos EUA onde NYSE e NASDAQ competem ([[us-markets-overview]]).

### Segmentos de Mercado

#### Mercado à Vista (Spot)

O principal segmento, onde ações são negociadas para liquidação em D+2.

- **Lote padrão**: 100 ações (negociado no book principal)
- **Mercado fracionário**: lotes de 1 a 99 ações (sufixo F — ex: VALE3F)
- **Horário**: 10:00 às 17:00 (pode variar com horário de verão)
- **Call de abertura**: 9:45 às 10:00
- **Call de fechamento**: 16:55 às 17:00
- **After-market**: 17:25 às 17:45 (oscilação máxima de 2%)

#### Mercado de Futuros ([[futures]])

Contratos futuros são negociados com alta liquidez, especialmente:

- **DI Futuro**: principal instrumento de juros, referência para toda a curva
- **Dólar Futuro**: contratos de câmbio USD/BRL (DOL — cheio, WDO — mini)
- **Índice Futuro**: contratos sobre o Ibovespa (IND — cheio, WIN — mini)
- **Commodities**: café, boi gordo, milho, soja
- Liquidação pode ser física ou financeira dependendo do contrato

#### Mercado de Opções ([[options-basics]])

Opções sobre ações, índices e outros ativos. Vencimento na terceira sexta-feira de cada mês para opções de ações. Mercado relativamente menos líquido que o americano, com concentração em poucos ativos (PETR4, VALE3, BOVA11).

### Segmentos de Governança Corporativa

A B3 classifica empresas listadas por nível de governança:

| Segmento | Requisitos Principais |
|----------|----------------------|
| **Novo Mercado** | Apenas ON (tag along 100%), free float mínimo 25%, câmara de arbitragem, conselho independente |
| **Nível 2 (N2)** | ON e PN permitidas, tag along 100% para ON e 80% para PN, câmara de arbitragem |
| **Nível 1 (N1)** | Free float mínimo 25%, divulgação adicional de informações |
| **Bovespa Mais** | Segmento para empresas em fase de crescimento, IPOs menores, prazo de 7 anos para atingir free float |
| **Bovespa Mais N2** | Bovespa Mais com permissão para emitir PN |
| **Básico** | Requisitos mínimos legais |

> [!tip] Preferência por Novo Mercado
> Investidores institucionais e estrangeiros geralmente preferem empresas do Novo Mercado pela maior proteção ao acionista minoritário. A maioria dos IPOs recentes são feitos nesse segmento.

### Clearinghouse — Câmara de Compensação

A B3 atua como **contraparte central (CCP)** de todas as operações, eliminando o risco de contraparte entre compradores e vendedores. Funções:

- **Compensação**: cálculo de posições líquidas
- **Liquidação**: transferência efetiva de ativos e dinheiro
- **Gerenciamento de risco**: chamadas de margem, garantias depositadas
- **Controle de inadimplência**: mecanismos de default management

### Ciclo de Liquidação (Settlement)

- **Ações**: D+2 (dois dias úteis após a negociação)
- **Derivativos**: varia conforme o contrato (futuros de índice/câmbio têm ajuste diário em D+1)
- **Tesouro Direto**: D+1

> [!warning] Atenção ao D+2
> Se você vende ações na segunda-feira, o dinheiro só estará disponível na quarta. Se compra na sexta, a liquidação ocorre na terça. Isso afeta planejamento de caixa e operações de day trade (que liquidam no mesmo dia).

### Infraestrutura e Sistemas

- **PUMA Trading System**: plataforma de negociação de alta performance, com capacidade para milhões de ordens por dia
- **CBLC (Companhia Brasileira de Liquidação e Custódia)**: braço de custódia da B3, responsável pela guarda de ativos
- **SINACOR**: sistema integrado de administração de corretoras, usado para controle de posições, margem e relatórios
- **iBalcão**: plataforma de registro de operações de balcão (OTC)
- **Co-location**: servidores instalados no data center da B3 para HFTs e algoritmos

### CVM — Regulação do Mercado

A **Comissão de Valores Mobiliários (CVM)** é o regulador do mercado de capitais brasileiro:

- Fiscaliza e pune irregularidades (insider trading, manipulação)
- Aprova ofertas públicas (IPOs, follow-ons)
- Regula fundos de investimento, gestores e consultores
- Instrução CVM 400 (ofertas públicas) e 476 (ofertas restritas) são referências fundamentais
- Equivalente brasileira da SEC americana

### B3 como Empresa Listada (B3SA3)

A própria B3 é uma empresa listada no Novo Mercado, com ticker B3SA3. Características:

- Receita baseada em taxas de negociação, listagem, dados e tecnologia
- Modelo de negócio com forte moat (monopólio regulado)
- Margens operacionais elevadas (acima de 60%)
- Receita correlacionada com volume de negociação (ADTV)
- Ação considerada proxy do mercado de capitais brasileiro

## How to Apply

1. **Escolha do segmento**: para ações, concentre-se em empresas do Novo Mercado ou N2 pela melhor governança
2. **Horários de operação**: programe ordens considerando os calls de abertura/fechamento para melhor price discovery ([[how-markets-work]])
3. **Mercado fracionário**: ideal para quem tem capital limitado — não deixe de investir por não ter R$ 3.000+ para um lote de 100 ações
4. **Entenda a liquidação D+2**: planeje fluxo de caixa considerando o prazo de compensação
5. **Acompanhe custos B3**: taxas de emolumentos, liquidação e registro impactam especialmente day traders

## Examples

> [!example] Exemplo: Estrutura de Custos na B3
> Ao comprar 100 ações de VALE3 a R$ 70,00 (total R$ 7.000):
> - Corretagem: R$ 0 (maioria das corretoras zerou)
> - Emolumentos B3: ~0,003% = R$ 0,21
> - Taxa de liquidação: ~0,0275% = R$ 1,93
> - ISS: 5% sobre emolumentos
> - Total de custos: ~R$ 2,25 (0,032% do valor)

## Gotchas

- **Horário de verão**: os horários de negociação podem mudar quando os EUA entram/saem do horário de verão (para manter sincronia)
- **Monopólio**: a falta de competição significa que a B3 tem poder de precificação sobre taxas
- **Mercado fracionário**: liquidez menor e spreads maiores em comparação ao lote padrão
- **Garantias em derivativos**: chamadas de margem podem exigir depósitos adicionais rapidamente
- **Ticker changes**: empresas podem mudar de ticker ao trocar de segmento de listagem

## Brazilian Context

A B3 é peça central do mercado de capitais brasileiro e reflete suas idiossincrasias:

- Concentração de volume em poucos ativos (PETR4, VALE3, ITUB4 respondem por parcela significativa do ADTV)
- Mercado de derivativos altamente desenvolvido (DI Futuro é um dos mais líquidos do mundo)
- Crescimento acelerado de investidores PF desde 2019 ([[market-participants]])
- Integração vertical (bolsa + clearinghouse + custódia) é única globalmente
- Relação próxima com CVM e BCB na regulação e supervisão

## Formulas

$$\text{ADTV} = \frac{\sum \text{Volume Diário}}{n \text{ (dias úteis)}}$$

$$\text{Free Float (\%)} = \frac{\text{Ações em Circulação}}{\text{Total de Ações Emitidas}} \times 100$$

$$\text{Custo Total} = \text{Emolumentos} + \text{Liquidação} + \text{Corretagem} + \text{ISS}$$

## References

- B3 — Site oficial: regulamentos, manuais de negociação e dados de mercado
- CVM — Instruções normativas e processos administrativos
- Fortuna, E. — *Mercado Financeiro: Produtos e Serviços*
- Assaf Neto, A. — *Mercado Financeiro*

## Related

- [[brazilian-market-b3]]
- [[how-markets-work]]
- [[market-participants]]
- [[futures]]
- [[options-basics]]
