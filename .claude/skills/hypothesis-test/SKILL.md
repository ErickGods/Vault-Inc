---
name: hypothesis-test
description: Transforma uma tese de investimento discricionária em hipótese testável. Invoque quando alguém perguntar se um padrão de mercado "funciona" — "small caps sobem mais depois de corte de juros?", "vale a pena comprar quem paga dividendo?", "esse setor está barato?" — ou antes de qualquer backtest, porque backtest sem hipótese formulada produz racionalização, não resultado. Produz universo, período, definição operacional do sinal, critério de rejeição declarado antes do teste e regime de falha.
---

# Hypothesis Test — da tese à hipótese

Esta skill é **rígida**. Os passos são numerados, obrigatórios e em ordem. Pular um passo
invalida os seguintes: o passo 5 só tem valor porque vem antes de qualquer resultado, e o
passo 6 só tem valor porque é honesto.

O produto desta skill **não é uma resposta**. É uma pergunta bem formulada — a única coisa
que um backtest sabe responder.

---

## Condição de parada — leia antes de tudo

**Se a tese não puder ser escrita como afirmação falseável, pare aqui.** Não prossiga, não
"aproxime", não escolha uma interpretação razoável. Devolva a tese para ser reformulada e
diga por que ela ainda não é uma hipótese.

| Não é hipótese | É hipótese |
|---|---|
| "WEGE3 é uma empresa de qualidade." | "Empresas com ROIC acima de 15% por 5 anos consecutivos superam o índice em 12 meses." |
| "Small cap sofre mais em ciclo de alta de juros." | "No decil inferior de valor de mercado do IBrX, o retorno em 6 meses após a primeira alta da Selic de um ciclo é inferior ao do decil superior." |
| "O mercado está caro." | "Quando o P/L do IBrX está acima do percentil 80 da série de 10 anos, o retorno subsequente de 12 meses é inferior ao CDI." |

O teste é simples: **existe um resultado numérico que faria você abandonar a tese?** Se não
existe, não há o que testar — há uma opinião, e opinião não passa por backtest, só por
concordância.

Devolver uma tese malformada é entrega. É a entrega mais barata que esta casa produz.

---

## Passos

### 1. Escreva a hipótese nula primeiro

Antes da hipótese que você quer testar, escreva a que você quer derrubar. Ela é quase sempre:
**o sinal não existe; a diferença observada é ruído amostral.**

Escrever a nula primeiro fixa a direção do ônus da prova. Sem isso, o estudo inteiro tende a
virar uma busca por confirmação — não por má-fé, mas porque quem procura acha.

### 2. Defina o universo — **incluindo as deslistadas**

- Quais ativos, com qual filtro de liquidez e qual critério de entrada e saída.
- **As empresas que deixaram de existir precisam estar no universo**, com data e motivo de
  saída. Universo montado a partir da lista de hoje é amostra condicionada ao sucesso.
- A composição do universo é a de cada data, não a de hoje. Índice muda de carteira.

Se a base disponível não tem as deslistadas, isso **não** interrompe o estudo — mas vira uma
limitação declarada agora, no documento, e não uma descoberta depois.

### 3. Defina o período e diga quantos ciclos ele cobre

Não basta a data inicial e final. Escreva **quantos ciclos econômicos** o período contém e
quais regimes ele **não** contém.

> Exemplo concreto: um estudo brasileiro começando depois de 2016 não viu nenhuma recessão
> própria, um ciclo completo de Selic de dois dígitos para um dígito e de volta, nem um
> choque político doméstico com gap de abertura. Um sinal que só foi testado nesse período
> não foi testado — foi observado num regime.

Período que contém um único regime produz resultado sobre aquele regime. Diga isso
explicitamente.

### 4. Operacionalize o sinal

A regra não pode admitir interpretação. Especifique, item por item:

- **Qual dado** — campo exato, fonte, e se é point-in-time. Fundamento entra por **data de
  divulgação**, não de referência.
- **Qual transformação** — ranking, z-score, variação percentual, média móvel, com a janela
  exata e o que acontece nos primeiros períodos.
- **Qual limiar** — número, não adjetivo. E o que acontece exatamente no limiar.
- **Qual frequência de rebalanceamento** — e em que momento do dia a ordem é gerada e
  executada. Sinal no fechamento executado no mesmo fechamento é look-ahead.

Teste de suficiência: **duas pessoas implementando esta definição isoladamente chegam à mesma
série?** Se não, a definição está incompleta e o passo não terminou.

### 5. Declare o critério de rejeição — **agora, antes de ver qualquer resultado**

Este é o passo que separa pesquisa de racionalização. Escreva, em números:

- qual métrica decide (Sharpe líquido de custos, retorno em excesso, hit rate, o que for);
- **qual valor** faz a hipótese ser rejeitada;
- em qual amostra a decisão é tomada (out-of-sample, não a de desenvolvimento);
- o que acontece com resultado ambíguo — porque ambíguo é o desfecho mais comum, e sem regra
  prévia ele sempre acaba lido como favorável.

Critério escrito **depois** do resultado acomoda o resultado. Sempre. Isso não é uma acusação
de desonestidade; é uma descrição de como a cognição humana funciona quando o número já está
na tela.

Uma vez escrito, o critério **não é renegociado**. Se ele estava errado, isso é um achado
sobre o desenho do estudo, e o estudo recomeça — não é um ajuste.

### 6. Declare quantas variações desta ideia já foram tentadas

O número honesto, `N`. Contam:

- cada janela de lookback testada;
- cada limiar experimentado;
- cada filtro de liquidez;
- cada recorte de universo ou de período;
- variações rodadas e descartadas sem reportar;
- reotimizações feitas **depois** de ver um resultado;
- tentativas de estudos anteriores sobre a mesma ideia.

Este número alimenta o **Deflated Sharpe** no protocolo de backtest. Ver [[sharpe-ratio]]:
o Sharpe da melhor entre `N` tentativas é uma estatística de máximo, positiva por construção
mesmo quando nenhuma das `N` tem habilidade real.

Se `N` não foi registrado durante a pesquisa, **você não sabe `N`** — declare isso, em vez de
estimar por baixo. "Não registrado" é informação; um número inventado não é.

### 7. Nomeie o regime de falha

Em que cenário este sinal **deve** parar de funcionar? Seja específico: qual regime de juros,
de volatilidade, de liquidez, de estrutura de mercado, de crowding.

> Se você não consegue imaginar um regime de falha, a hipótese provavelmente está malformada
> — ou você não entendeu o mecanismo por trás dela. Sinal sem mecanismo é correlação, e
> correlação sem mecanismo não tem motivo para persistir fora da amostra.

O regime de falha nomeado aqui vira, mais tarde, o teste de sanidade do resultado: se o sinal
funcionou **inclusive** no regime em que deveria falhar, a explicação mais provável não é que
ele seja robusto — é que há vazamento.

---

## Critérios de saída

A hipótese está pronta quando **todos** os itens estão marcados:

- [ ] A tese está escrita como afirmação falseável, com um resultado numérico capaz de
      derrubá-la.
- [ ] A hipótese nula está escrita, explicitamente.
- [ ] O universo está definido, com filtro de liquidez, e **inclui as deslistadas** — ou a
      ausência delas está declarada como limitação.
- [ ] O período está definido, com o **número de ciclos econômicos** que cobre e os regimes
      que **não** cobre.
- [ ] O sinal está operacionalizado: dado, transformação, limiar, frequência e momento de
      execução — sem espaço para interpretação.
- [ ] O **critério de rejeição** está escrito, em números, e nenhum resultado foi visto ainda.
- [ ] `N` — o número de variações já tentadas — está declarado, ou a ausência de registro
      está declarada.
- [ ] O **regime de falha** está nomeado.

Faltando qualquer item, a hipótese não segue para backtest. Ela volta para o passo que falhou.

---

## Entregável

Repositório privado, nunca este vault:

```
cross-desk/<YYYY-MM-DD>-hypothesis-<slug>.md
```

O documento é o insumo obrigatório da skill `backtest-protocol` — que se recusa a rodar sem
ele, e especificamente sem o critério de rejeição do passo 5.

Conhecimento durável que sair do estudo — um mecanismo compreendido, uma armadilha de dado
mapeada, um regime caracterizado — **sobe para este vault** como nota nova, e o índice do
domínio ganha uma linha.
