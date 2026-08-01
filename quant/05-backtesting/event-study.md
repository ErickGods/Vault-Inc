---
tags: [quant, backtesting, event-study, methodology]
aliases: [Event Study, Estudo de Evento, Análise de Eventos]
house: quant
domain: backtesting
level: advanced
status: active
created: 2026-08-01
updated: 2026-08-01
---

# Event Study — quando o tempo pertence ao evento

Backtest contínuo mede uma **estratégia**: uma regra aplicada a cada período, avaliada por uma
série de retornos. Event study mede uma **resposta**: o que acontece com preços depois de algo —
decisão de política monetária, divulgação de resultado, entrada num índice, follow-on, anúncio
de fusão. Toda pergunta da forma *"o que acontece quando X"* é um event study.

Tratá-la como backtest contínuo produz duas distorções, e ambas favorecem o pesquisador: um `n`
inflado e um contrafactual errado. Esta nota existe para as duas.

## A unidade amostral é o evento

Vinte anos de dados diários parecem 5.000 observações. Se a pergunta é sobre ciclos de política
monetária, **são ~8 observações** — o número de ciclos completos desde o regime de metas, não o
número de pregões dentro deles.

A consequência prática vem antes de qualquer coleta: com `n` de eventos pequeno, o efeito mínimo
detectável costuma ser maior do que o efeito plausível, e o estudo nasce incapaz de responder.
Faça a conta de [[statistical-power]] **antes** de montar a base. Se o desenho não enxerga o
efeito que procura, a resposta honesta é redesenhar ou declarar o tema não-testável — que é um
resultado, e barato.

## Datar o evento é o passo que decide tudo

Três datas diferentes se disfarçam de "a data do evento":

| Data | O que é | Erro se confundida |
|---|---|---|
| **Da informação** | Quando o fato econômico ocorreu | Usá-la assume que o mercado sabia antes do anúncio |
| **Do anúncio** | Quando o mercado soube | A correta para medir resposta |
| **Da disponibilidade no dataset** | Quando o vendor consolidou | Usá-la injeta look-ahead silencioso |

Regras práticas no Brasil: decisão de Copom e a maioria dos resultados corporativos saem **após
o fechamento** — a primeira barra que pode reagir é a abertura de D+1, e entrada "em D" é
look-ahead. Guidance revisado, prévia operacional e fato relevante têm hora de publicação na CVM;
use-a. E o **drift pré-evento é diagnóstico**: retorno anormal sistemático *antes* da sua data de
evento indica que o mercado soube antes — a data está errada ou há vazamento de informação, e nos
dois casos a janela precisa começar antes.

## Janelas e retorno anormal

Três janelas, com papéis distintos:

- **Estimação** (ex.: D−120 a D−20): calibra o que seria "normal" para o ativo — beta contra o
  mercado ou média simples. Termina antes do evento para não contaminar o normal com a resposta.
- **Evento** (ex.: D−1 a D+1): captura a reação imediata. Curta, senão vira ruído.
- **Pós-evento** (ex.: D+2 a D+90): onde mora a pergunta de drift ou reversão.

O retorno anormal é o retorno observado menos o esperado pelo modelo da janela de estimação.
Para agregar no tempo, duas convenções com vieses opostos:

- **CAR** (soma dos anormais): estável, mas ignora composição — subestima horizontes longos.
- **BHAR** (retorno composto do ativo menos composto do benchmark): fiel ao que um investidor
  ganharia, mas de cauda pesada e assimétrica — a média engana; reporte mediana junto.

Horizonte até ~1 mês: CAR. Horizontes de meses: BHAR com mediana e teste não-paramétrico.

## O contrafactual, ou o estudo mede beta

O erro mais comum do formato: medir o retorno pós-evento e compará-lo com zero. Se a janela
pós-evento coincide com mercado subindo, todo ativo "responde positivamente" ao evento — o estudo
mediu o período, não o efeito.

O desenho correto é **diferença em diferenças**: a resposta do grupo afetado menos a resposta de
um controle não afetado (ou menos a resposta do próprio ativo em janelas sem evento, pareadas por
regime de volatilidade). Sem contrafactual declarado, o resultado não é interpretável — e a
escolha do controle é uma premissa a defender por escrito, não um detalhe de implementação.

## Sobreposição e clustering: o `n` encolhe de novo

Dois eventos com janelas sobrepostas não são duas observações independentes. E o caso extremo é
o evento **macro**: uma decisão de Copom atinge todos os ativos no mesmo dia. Medir 80 ações na
mesma data não dá `n = 80` — a correlação transversal entre elas faz o `n` efetivo ficar muito
mais perto de **1 por evento**. Tratar cada ação como observação independente é a forma mais
comum de inventar significância em event study.

Tratamentos: agregue o corte transversal em **um portfólio por evento** e teste a série de
eventos; use **bootstrap por bloco** (reamostrando eventos inteiros, nunca dias soltos); e para
sobreposição parcial, elimine ou modele explicitamente a covariância.

## Vieses específicos do formato

- **Definição de evento ex post.** "Início de ciclo de corte" definido olhando o ciclo inteiro é
  look-ahead na classificação: em tempo real ninguém sabia que aquele corte era o primeiro de um
  ciclo. Toda regra de classificação de evento precisa ser aplicável com a informação disponível
  na data — e escrita antes de rodar.
- **Seleção de sobreviventes no universo do evento.** O conjunto "empresas que divulgaram
  resultado" já exclui as que quebraram antes. Mesmo tratamento de sobrevivência de
  [[backtesting-basics]], aplicado à lista de eventos.
- **Eventos condicionados ao resultado.** Estudar "quedas seguidas de recuperação" seleciona pela
  resposta — o evento precisa ser definível sem olhar o que veio depois.

## Checklist antes de reportar

- [ ] `n` = número de eventos declarado, com a conta de [[statistical-power]] feita antes da coleta
- [ ] Data do evento = data do anúncio, com regra de entrada compatível com o horário de publicação
- [ ] Regra de classificação do evento aplicável em tempo real, escrita antes do teste
- [ ] Janelas de estimação, evento e pós-evento declaradas, com justificativa
- [ ] Contrafactual explícito (diff-in-diff ou controle pareado) — nunca comparação contra zero
- [ ] Clustering tratado: um portfólio por evento macro, bootstrap por bloco
- [ ] CAR para janelas curtas, BHAR com mediana para longas
- [ ] Drift pré-evento inspecionado e explicado
- [ ] Sobrevivência tratada na lista de eventos, não só no universo de ativos

## References

- MacKinlay (1997), "Event Studies in Economics and Finance" — o survey canônico do desenho
- Kothari & Warner (2007) — vieses de BHAR em horizonte longo

## Related

- [[backtesting-basics]] — os vieses gerais que este formato herda
- [[statistical-power]] — a conta que decide se o estudo pode existir
- [[sharpe-ratio]] — número de tentativas e inferência com amostra curta
- [[finance/03-analysis/macro/selic-and-monetary-policy]] — o evento macro brasileiro mais
  recorrente, com o detalhe operacional do anúncio pós-fechamento
