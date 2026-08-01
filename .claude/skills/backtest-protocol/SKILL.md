---
name: backtest-protocol
description: Roda ou revisa um backtest de estratégia com guarda-corpos. Invoque antes de tratar qualquer resultado de backtest como evidência — próprio, herdado de outro analista ou vindo de fora — e antes de levar uma estratégia para capital real. Cobre auditoria do dado, teste de look-ahead, separação out-of-sample, custos, Deflated Sharpe, drawdown e sua duração, e confronto com o critério de rejeição escrito de antemão.
---

# Backtest Protocol

Esta skill é **rígida**. Os passos são numerados, obrigatórios e em ordem. A ordem não é
estilística: auditar o dado depois de ver o resultado já não é auditoria, e aplicar custo
depois de decidir que a estratégia é boa já não é teste.

Vale tanto para rodar um backtest novo quanto para **revisar um que já existe**. Na revisão,
cada passo vira uma pergunta a ser respondida com evidência — não com a garantia de quem
rodou.

---

## Condição de parada — leia antes de tudo

**Precisa existir uma hipótese formulada pela skill `hypothesis-test`, com critério de
rejeição escrito.** Se não existe, pare e rode `hypothesis-test` primeiro.

Isto não é formalidade de processo. Backtest sem critério de rejeição prévio não produz
resultado — produz **racionalização**. O mecanismo é conhecido e não depende de má-fé: o
número aparece na tela, e o critério que se formula em seguida é inevitavelmente um critério
que aquele número atende. Quem escreve o critério depois nunca reprova a própria estratégia.

Se o backtest sob revisão foi rodado sem hipótese prévia, o resultado **não é evidência**.
Ele pode ser tratado como exploração, e a estratégia precisa ser reformulada como hipótese e
testada de novo em amostra que ainda não foi vista.

---

## Passos

### 1. Audite o dado antes do modelo

Antes de olhar qualquer retorno. Quatro perguntas, cada uma com resposta escrita:

| Pergunta | Se a resposta for "não" |
|---|---|
| O dado é **point-in-time**? Fundamento entra por data de divulgação? | Limitação declarada. O viés é sempre a favor da estratégia. |
| Proventos estão ajustados? Splits, dividendos, **JCP**, bonificações? | Limitação declarada, com o efeito estimado no retorno total. |
| As **deslistadas** estão no universo, com data e motivo de saída? | Limitação declarada. Retorno está superestimado, e mais em estratégia de valor. |
| Qual a **política de faltantes**? Houve forward-fill? | Declare o método e quantos pontos foram preenchidos. |

Resposta "não" **não interrompe** o estudo. Ela vira **limitação declarada**, escrita no
relatório, antes do resultado. O que é proibido é descobrir a limitação depois e apresentá-la
como ressalva.

Em caso de dúvida sobre correção financeira do dado, o dono da pergunta é `market-data-quant`.

### 2. Teste de look-ahead

**Atrase o sinal em um período e rode de novo.**

O resultado **precisa piorar**. É a expectativa correta: informação mais fresca vale mais, e
tirar um período de frescor tem que custar performance.

Se o resultado **não piorar** — ou pior, se melhorar — **pare imediatamente e ache o
vazamento.** Não prossiga, não relativize, não anote como curiosidade. Não existe explicação
benigna comum para esse padrão. Os lugares onde o vazamento costuma estar:

- normalização, z-score ou winsorização calculados sobre a amostra inteira;
- universo montado com a composição de hoje;
- join de fundamento por data de referência em vez de divulgação;
- preenchimento de faltantes que olha para frente;
- sinal gerado no fechamento e executado no mesmo fechamento;
- rótulo de deslistagem ou de evento conhecido antes do evento.

Backtest com look-ahead é pior do que nenhum backtest, porque parece um resultado.

### 3. Out-of-sample

Separe **train / validation / test antes de olhar qualquer número**. Depois de ver, a
separação já não é honesta — nenhuma disciplina compensa ter visto.

- Otimização só no train.
- Escolha entre configurações só no validation.
- **O test é aberto uma vez.** Nunca se ajusta parâmetro no test; se você ajustou, ele virou
  validation e você não tem mais out-of-sample.
- Walk-forward quando o período permitir, com as janelas declaradas. O desempenho da
  estratégia é o resultado OOS concatenado, não o do histórico completo. Ver
  [[backtesting-basics]].

### 4. Aplique custos, com premissa declarada para cada um

Corretagem, emolumentos, **spread bid-ask**, slippage e impacto de mercado. Cada um com o
número usado e a justificativa. Custo genérico não declarado é custo que ninguém pode
contestar — e portanto custo que provavelmente está baixo demais.

Calibre por liquidez: spread de blue chip da B3 não é spread de small cap, e a diferença é de
uma ordem de grandeza. Estratégias de **giro alto morrem aqui** — e é muito melhor que morram
aqui do que no capital. Uma estratégia que só sobrevive bruta de custo já foi decidida.

Backtest bruto de custo é válido **apenas** como verificação de lógica, e não sai do passo 4
como resultado.

### 5. Sharpe e depois Deflated Sharpe

Calcule o Sharpe líquido de custos. Depois calcule o **Deflated Sharpe**, usando o `N` do
**passo 6 de `hypothesis-test`** — o número de variações já tentadas.

O DSR penaliza simultaneamente o número de tentativas e a não-normalidade dos retornos (skew
e curtose). A metodologia, as fórmulas e o bloco mínimo de reporte estão em [[sharpe-ratio]].

Reporte junto: `T`, `N`, skew, curtose, autocorrelação de primeira ordem, `S₀` e DSR. Se a
série tiver autocorrelação positiva material, **não anualize por √n sem corrigir**.

Se `N` não foi registrado durante a pesquisa, o Sharpe **não é interpretável** — declare isso
em vez de estimar um número por baixo.

### 6. Drawdown máximo **e sua duração**

Os dois números, sempre juntos. A duração é a que costuma decidir a viabilidade:

> Uma perda de 40% que leva **3 anos** para se recuperar é inviável na prática mesmo com um
> Sharpe bom. Ninguém — nem cliente, nem comitê, nem o próprio gestor — permanece alocado 3
> anos abaixo do pico. A estratégia é abandonada no fundo, que é exatamente o pior momento, e
> o retorno do backtest nunca é realizado por ninguém.

Reporte: drawdown máximo, data de início, data do fundo, data de recuperação, duração total e
o segundo pior drawdown — que diz se o pior foi um evento único ou o comportamento normal da
estratégia.

### 7. Confronte contra o critério de rejeição escrito de antemão

Abra o documento da hipótese, leia o critério do passo 5, e compare com o resultado. Sem
reinterpretar, sem "mas", sem ajustar a métrica de decisão.

**Se o critério rejeita, a rejeição é o entregável — e é um resultado válido e valioso.**
Escreva o relatório completo do mesmo jeito, com todos os números. Uma tese rejeitada com
evidência é conhecimento que a casa passa a ter: ninguém precisa testar aquilo de novo, e o
motivo da falha frequentemente ensina mais do que uma aprovação ensinaria.

Estudo que "não deu em nada" e por isso não é escrito é o desperdício mais caro da casa,
porque a mesma ideia volta em seis meses.

### 8. Nomeie o regime de falha, com evidência

Identifique o **pior subperíodo** do backtest e explique **o que estava acontecendo no
mercado** naquele momento. Não basta apontar o intervalo: caracterize o regime — juros,
volatilidade, liquidez, direção do mercado, evento específico.

Depois confronte com o regime de falha nomeado no passo 7 de `hypothesis-test`:

- Bateu? Boa notícia — o mecanismo é entendido, e você sabe quando desligar.
- Não bateu? A estratégia falha por um motivo que você não previu. Investigue antes de
  aprovar; sinal que falha por motivo desconhecido volta a falhar por motivo desconhecido.
- **Não houve subperíodo ruim?** Isso não é um bom sinal. Volte ao passo 2.

---

## Nunca

- **Nunca reporte Sharpe sem o número de variações testadas.** Sharpe sozinho, escolhido entre
  muitos, é uma estatística de máximo — positiva por construção mesmo sem habilidade nenhuma.
- **Nunca ajuste parâmetro no conjunto de teste.** No instante em que você ajusta, o test
  virou validation e o estudo ficou sem out-of-sample. Não há como desfazer.
- **Nunca omita o pior subperíodo.** Ele é o dado mais informativo do backtest inteiro, e
  omiti-lo é a diferença entre um relatório e uma peça de venda.
- **Nunca apresente backtest bruto de custo como resultado.** Sem custo não é resultado, é
  verificação de lógica.

---

## Critérios de saída

- [ ] Auditoria do dado feita **antes** do modelo, com as quatro respostas escritas e as
      limitações declaradas.
- [ ] Teste de look-ahead executado, e o resultado **piorou** com o sinal atrasado.
- [ ] Train / validation / test separados antes de qualquer número; test aberto uma vez.
- [ ] Custos aplicados, com premissa declarada item por item.
- [ ] Sharpe **e** Deflated Sharpe, com `T`, `N`, skew, curtose e autocorrelação.
- [ ] Drawdown máximo **e duração**, mais o segundo pior drawdown.
- [ ] Resultado confrontado com o critério de rejeição prévio, sem reinterpretação.
- [ ] Regime de falha nomeado, com o pior subperíodo identificado e caracterizado.

---

## Entregável

Repositório privado, nunca este vault:

```
reports/quant/<estrategia>-<YYYY-MM-DD>.md
```

Vale igualmente para aprovação e para rejeição — a rejeição é entregue com o mesmo nível de
detalhe.

Conhecimento durável que sair do estudo **sobe para este vault** como nota nova, e o índice do
domínio ganha uma linha.
