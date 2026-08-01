---
tags: [quant, backtesting, statistics, power, study-design]
aliases: [Poder Estatístico, Statistical Power, Efeito Mínimo Detectável, MDE]
house: quant
domain: backtesting
level: intermediate
status: active
created: 2026-08-01
updated: 2026-08-01
---

# Poder estatístico e efeito mínimo detectável

Antes de coletar qualquer dado, um desenho de estudo precisa responder uma pergunta sobre si
mesmo: **qual o menor efeito que este desenho consegue enxergar?** Esse número é o efeito mínimo
detectável (MDE). Se o efeito economicamente plausível for menor que o MDE, o estudo nasce
incapaz de responder — vai terminar "inconclusivo" com qualquer dado, e o inconclusivo será lido
como "não funciona", que é uma conclusão que ele não tem poder para sustentar.

A casa exige essa conta **antes** do teste pelo mesmo motivo que exige critério de rejeição
antes do teste: depois de ver o resultado, toda justificativa acomoda o resultado.

## A conta de guardanapo

Para detectar um efeito médio com significância de 5% e poder de 80%:

```
MDE ≈ 2,8 × σ / √n
```

onde `σ` é o desvio-padrão da métrica **por observação** e `n` é o número de observações
independentes. Para comparação entre dois grupos (tratado × controle, como num
diff-in-diff), multiplique por √2:

```
MDE ≈ 4,0 × σ / √n
```

Os 2,8 vêm de `z(97,5%) + z(80%) = 1,96 + 0,84`. Não decore: o que importa é a forma — o MDE cai
com a **raiz** de `n`, então dobrar a amostra melhora o desenho em só 29%, e nenhum refinamento
de métrica compensa uma ordem de grandeza de eventos faltando.

**Exemplo com números redondos:** um event study sobre ciclos de política monetária no Brasil
tem, no máximo, ~8 eventos desde o regime de metas. Com `n = 8`, o MDE de uma comparação contra
controle é `4,0/√8 ≈ 1,4σ` — o efeito precisa ser **quase um desvio-padrão e meio** da métrica
para ser detectável. Se a métrica é um spread de retornos com σ de ~15 pontos percentuais por
ciclo, o estudo só enxerga efeitos acima de ~20 pp. Um efeito real de 8 pp — economicamente
enorme — é invisível para esse desenho, e o estudo reportaria "sem evidência" para uma tese
verdadeira.

## O que aumenta poder — e o que só parece aumentar

**Aumenta de verdade:**

- **Mais eventos independentes** — período mais longo, ou eventos análogos de outros mercados,
  se a hipótese sobreviver à agregação (premissa a declarar, não a assumir).
- **Reduzir σ** — controles que absorvem variância: diff-in-diff contra grupo pareado, ajuste
  por fatores conhecidos, métrica menos ruidosa (mediana em vez de média para caudas pesadas).
- **Redesenhar a pergunta** — um efeito contínuo ("a magnitude da surpresa prevê a magnitude da
  resposta") usa mais informação por evento do que um efeito binário ("subiu ou não").

**Só parece aumentar:**

- **Mais ativos sob um choque comum.** 80 ações na mesma data de Copom não são 80 observações —
  a correlação transversal derruba o `n` efetivo para perto de 1 por evento. Ver o clustering em
  [[event-study]].
- **Mais granularidade temporal.** Trocar retornos mensais por diários multiplica linhas, não
  informação sobre um efeito que vive na janela do evento.

## Os dois lados do mesmo erro

Poder estatístico e Deflated Sharpe são as duas metades da inferência honesta, e a casa exige as
duas declaradas:

| | Pergunta | Erro que controla |
|---|---|---|
| **Deflated Sharpe** ([[sharpe-ratio]]) | Vi um padrão — é real, dado que tentei `N` vezes? | Tipo I: ver padrão onde não há |
| **Poder / MDE** | Não vi padrão — o desenho conseguiria vê-lo? | Tipo II: não ver padrão que existe |

Reportar só o primeiro vicia a casa em falsos "não funciona"; só o segundo, em falsos "funciona".
Um resultado nulo sem MDE declarado não é evidência de ausência — é ausência de desenho.

## Regra da casa

**Nenhuma hipótese vai a backtest sem o MDE calculado e comparado ao efeito economicamente
relevante.** Três desfechos possíveis, todos legítimos:

1. `MDE < efeito plausível` — o desenho enxerga o que procura; siga para o teste.
2. `MDE ≈ efeito plausível` — declare a zona cinzenta: o inconclusivo é o desfecho mais provável
   e precisa de regra de leitura pré-escrita ("vira *não sabemos*, não *não funciona*").
3. `MDE >> efeito plausível` — redesenhe ou arquive como **não-testável**. Arquivar é resultado:
   impede a casa de gastar num estudo que não pode responder, e de vender um nulo sem poder como
   se fosse um "não".

## Related

- [[event-study]] — onde `n` é o número de eventos, e o clustering que encolhe o `n` efetivo
- [[sharpe-ratio]] — erro-padrão do Sharpe em amostra curta e o Deflated Sharpe
- [[backtesting-basics]] — o protocolo geral que esta conta antecede
