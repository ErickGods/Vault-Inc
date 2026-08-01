---
tags: [finance, investments, derivatives, hedging]
aliases: [Hedge, Estratégias de Hedge, Hedging]
house: finance
domain: investments/derivatives
level: advanced
status: active
created: 2026-07-29
updated: 2026-07-29
---

# Estratégias de Hedge

## Overview

Hedge é **transferência de risco a um preço** — não eliminação de risco de graça. Alguém do outro
lado assume a exposição que você não quer, e cobra por isso. O preço às vezes é explícito (prêmio
de opção, custo de carrego do futuro) e às vezes é implícito (o retorno esperado que você abre mão
ao travar o preço). Ele é sempre positivo em expectativa; se parecesse gratuito, seria arbitragem, e
não existiria.

A consequência que organiza toda decisão de hedge: **o hedge reduz a variância e reduz o retorno
esperado**. Isso não é defeito, é a natureza do instrumento — você paga um seguro. A pergunta certa
nunca é "quero eliminar esse risco?" (a resposta é sempre sim) e sim: *esse risco específico ameaça
um compromisso que eu tenho, e o preço de transferi-lo é menor que o custo de carregá-lo?*

Corolários que decorrem direto disso:

- **Hedge permanente de tudo é caro e sem propósito.** Quem quer menos risco de mercado em regime
  permanente reduz a posição — é mais barato. Hedge serve para exposição que você quer manter mas
  cujo risco não pode correr **agora**, por razão específica: evento datado, casamento com passivo,
  covenant, limite de mandato, necessidade de caixa numa data.
- **Hedge não é diversificação.** Diversificação reduz risco sem custo explícito de prêmio, mas não
  garante nada e falha justamente quando as correlações convergem na crise. Hedge tem custo certo e
  proteção contratual. São ferramentas complementares — ver [[diversification]].
- **Se o hedge tem retorno esperado positivo, não é hedge.** É uma posição direcional a mais, e
  precisa ser dimensionada e justificada como tal.

---

## Core Concepts

### Instrumentos na B3, e para que serve cada um

| Instrumento | Contrato | O que trava | Caso de uso típico |
|---|---|---|---|
| **Futuro de índice** | IND (cheio), WIN (mini) | Beta da carteira de ações contra o Ibovespa | Gestor com carteira long que quer atravessar uma eleição ou um payroll sem zerar posições e sem realizar imposto |
| **Futuro de dólar** | DOL (cheio), WDO (mini) | Taxa de câmbio numa data | Importador que tem pagamento em USD daqui a 90 dias e receita em BRL |
| **Opções** | Sobre ações e sobre índice | Piso (put) ou faixa (collar) de preço | Sócio com posição concentrada e restrição de venda que precisa de piso, não de venda |
| **Futuro de DI** | DI1 | Taxa de juros — exposição a marcação de renda fixa prefixada | Tesouraria com carteira de prefixados que quer neutralizar risco de curva antes de uma reunião do Copom |

Detalhes de multiplicador, tick, margem e ajuste diário estão em [[futures]]; estrutura, gregas e
mecânica de exercício em [[options-basics]].

A diferença econômica entre as duas famílias determina a escolha:

- **Futuro é simétrico.** Trava o preço nos dois sentidos: elimina a perda e elimina o ganho. Não
  tem prêmio a pagar, mas tem custo de carrego embutido no preço futuro e exige margem com ajuste
  diário.
- **Opção é assimétrica.** Compra o piso e mantém o teto, ao custo de um prêmio pago à vista. É mais
  cara justamente porque preserva o lado bom.

### Hedge cambial

**Para quem faz sentido**, concretamente:

- Quem tem **passivo em moeda estrangeira** e receita em reais — importador, empresa com dívida em
  USD, cliente com mensalidade de curso no exterior. Aqui o hedge casa um fluxo com outro; é a
  aplicação mais defensável de todas.
- Quem tem **compromisso datado em moeda estrangeira** — intercâmbio, aquisição, viagem grande.
- Quem tem **exposição cambial acidental** dentro de um mandato que não a autoriza.

**Para quem geralmente não faz sentido**: o investidor pessoa física brasileiro que aloca parte do
patrimônio no exterior justamente **porque** quer a exposição ao dólar. Hedgear a moeda de uma
carteira internacional é anular a principal razão de tê-la. Ver [[bonds-international]].

**O custo é o carrego, e ele não é pequeno no Brasil.** O preço futuro do dólar sai da paridade de
juros:

```
Forward = Spot × (1 + i_BRL) / (1 + i_USD)
```

Com juro brasileiro estruturalmente acima do americano, o dólar futuro negocia **acima** do spot.
Quem vende dólar futuro para se proteger de alta está travando um preço melhor que o spot — recebe o
carrego. Quem **compra** dólar futuro para se proteger de alta paga esse diferencial, e ele é
recorrente a cada rolagem. Com diferencial de 8 pp ao ano, hedge de compra de dólar custa ~8% ao ano
antes de qualquer movimento cambial. Em cinco anos, o custo acumulado supera boa parte dos cenários
de depreciação que o hedge protegeria.

> [!warning] Direção importa
> "Hedge cambial" descreve duas operações de sinal oposto e custo oposto no Brasil. Quem tem
> passivo em dólar paga o carrego; quem tem ativo em dólar o recebe. Não trate as duas como a mesma
> decisão.

### Protective put e collar

**Protective put** — comprar put sobre o ativo que você já tem.

```
Posição: ação + put comprada (strike K)
Piso    = K − prêmio pago
Teto    = ilimitado, menos o prêmio
Custo   = prêmio, pago à vista, sempre
```

É o seguro no formato mais puro: perda máxima definida, upside preservado. O custo é o prêmio, e ele
é uma **função direta da volatilidade implícita**. É aqui que o erro mais caro acontece: o prêmio
sobe exatamente quando o medo sobe. Comprar proteção depois do susto é comprar seguro contra
incêndio com a casa já pegando fogo — a apólice existe, mas o preço já embute o sinistro. Ver
[[options-basics]] sobre volatilidade implícita.

**Collar** — comprar put e vender call sobre a mesma posição.

```
Posição: ação + put comprada (K_put) + call vendida (K_call)
Piso    = K_put
Teto    = K_call            ← você entregou a alta acima daqui
Custo   = prêmio da put − prêmio da call   (pode ser ≈ zero: "zero-cost collar")
```

O collar **financia a proteção vendendo o upside**. Chamar de "zero cost" é rigorosamente falso: o
custo não é zero, é o ganho acima de `K_call`, que você entregou. O desembolso é que é zero. Num
ativo que sobe 40%, o collar montado a `K_call` de +12% custou 28 pontos percentuais.

Onde o collar é a ferramenta certa: posição **concentrada** que não pode ser vendida — sócio com
lock-up, herdeiro com bloco relevante, executivo com ações restritas, cliente com ganho de capital
que não quer realizar agora. Nesses casos a alternativa ao collar não é "ficar exposto"; é "não
poder fazer nada". A troca de upside por piso é boa.

Onde o collar é errado: numa carteira diversificada e líquida, em que reduzir posição resolve o
mesmo problema sem prêmio, sem margem e sem risco de exercício.

### Hedge ratio — e por que 100% quase nunca é o ponto certo

```
Nº de contratos = (Valor da exposição × β) / (Valor nocional de 1 contrato)
```

Hedge de 100% zera a exposição direcional e, com ela, o retorno esperado dela. Quatro razões para
raramente ser o ótimo:

1. **Custo linear, benefício decrescente.** Cada ponto de hedge custa o mesmo; a redução marginal de
   risco relevante é maior nos primeiros pontos. Sair de 0% para 50% de proteção elimina a maior
   parte da perda que ameaçaria o compromisso; ir de 50% para 100% custa outro tanto para eliminar
   perdas que talvez fossem toleráveis.
2. **O objetivo raramente é variância zero.** É evitar a perda que quebra o mandato, o covenant ou o
   IPS. Isso é uma perda-alvo, não a variância inteira.
3. **Convicção parcial.** Hedge total afirma certeza sobre o timing do risco. Hedge parcial é a
   expressão honesta de uma convicção parcial.
4. **Base risk** (abaixo) — acima de certo ponto, mais contratos param de adicionar proteção e
   passam a adicionar risco de outra natureza.

O `β` da fórmula é a peça frágil: ele é estimado, instável, e sobe justamente em crises. Um hedge
calculado com `β` de período calmo fica subdimensionado exatamente quando é acionado.

### Basis risk

**Base = preço do ativo protegido − preço do instrumento de hedge.** Base risk é o risco de que essa
diferença se mova. Ele aparece sempre que o instrumento **não é** a exposição, e nunca é:

- **Descasamento de ativo.** Uma carteira de small caps hedgeada com WIN: se o Ibovespa (concentrado
  em bancos e commodities) sobe e as small caps caem, você perde nas duas pontas. O hedge não
  protegeu — piorou.
- **Descasamento de prazo.** Exposição de 9 meses hedgeada com futuro de 3 meses exige duas
  rolagens, cada uma a um preço desconhecido hoje.
- **Descasamento de quantidade.** Contratos são padronizados; o resíduo fica descoberto (ou
  sobre-hedgeado, o que é uma posição direcional invertida).
- **Proxy hedge.** Proteger exposição ao euro com futuro de dólar, ou uma ação específica com o
  índice. Funciona enquanto a correlação histórica se mantiver — e a razão de você estar hedgeando é
  justamente que algo anormal pode acontecer.

O caso mais didático é o proxy hedge de ação individual pelo índice: ele protege o risco de mercado
e **não protege nada do risco específico** — que costuma ser exatamente o motivo da preocupação.

> [!warning] O hedge que virou a perda
> Basis risk transforma "protegido" em "perdendo dos dois lados". É o risco que mais surpreende,
> porque o hedge foi montado com a aritmética certa e a exposição errada.

---

## How to Apply

### Antes de montar

1. **Escreva a exposição em uma frase**, com valor e prazo. "R$ 3,2 mi em ações brasileiras que não
   posso realizar antes de março." Se não couber numa frase, o hedge vai ser mal desenhado.
2. **Nomeie o risco específico.** Mercado? Moeda? Taxa? Crédito? Cada um pede instrumento diferente,
   e o instrumento errado é caro e inútil ao mesmo tempo.
3. **Escreva o preço do hedge em reais e em % ao ano.** Prêmio, carrego, custos operacionais,
   upside entregue. Se você não sabe o custo, não sabe se o hedge vale a pena.
4. **Defina a data de desmonte antes de montar.** Hedge sem data de saída vira posição direcional
   permanente com custo permanente.
5. **Dimensione a margem e o pior caso de chamada.** A perna do hedge exige caixa quando o ativo
   protegido está ganhando — ver abaixo.
6. **Compare com a alternativa simples**: reduzir a posição. Se reduzir resolve e é permitido, o
   hedge precisa justificar por que não.

### Escolha do instrumento

| Situação | Instrumento | Por quê |
|---|---|---|
| Evento datado, carteira ampla, quero manter as posições | Futuro de índice vendido | Simétrico, líquido, sem prêmio, desmonte fácil |
| Posição concentrada e ilíquida, preciso de piso | Protective put | Preserva o upside, que é o motivo de ainda ter a posição |
| Posição concentrada, prêmio da put é proibitivo | Collar | Financia o piso entregando o teto |
| Passivo em USD com data | Futuro de dólar comprado (ou NDF) | Casa fluxo com fluxo |
| Carteira prefixada antes de decisão de juros | DI futuro | Neutraliza a curva sem vender os títulos |

---

## Examples

> [!example] Hedge de carteira com futuro de índice
> Carteira de R$ 800 mil, `β` de 1,15 contra o Ibovespa. Ibovespa em 130.000 pontos; WIN vale
> R$ 0,20/ponto → nocional de R$ 26.000 por contrato.
> ```
> Contratos = (800.000 × 1,15) / 26.000 = 35,4  →  35 minis vendidos
> ```
> Queda de 10% no índice: carteira perde ~R$ 92.000 (β 1,15); o short ganha
> `35 × 13.000 × 0,20 = R$ 91.000`. Protegido — **se** o `β` de 1,15 se confirmar na queda. Se a
> carteira for de small caps e cair 16% enquanto o índice cai 10%, a perda líquida é de
> R$ 37.000 mesmo com o hedge "correto". Isso é basis risk, não erro de conta.

> [!example] Collar num bloco concentrado
> Sócio com R$ 12 mi numa única ação a R$ 40, sem poder vender por 18 meses.
> ```
> Put strike 36 (−10%)   : prêmio pago     R$ 1,90/ação
> Call strike 48 (+20%)  : prêmio recebido R$ 1,80/ação
> Desembolso líquido: R$ 0,10/ação ≈ R$ 30 mil
> ```
> Faixa travada entre R$ 36 e R$ 48. Se a ação for a R$ 62, o "zero-cost collar" terá custado
> R$ 14/ação — R$ 4,2 mi de upside entregue. Foi o preço de ter piso numa posição que não podia ser
> vendida, e a decisão pode ter sido certa mesmo assim. O que não pode é chamar isso de grátis.

> [!example] O custo de carrego que ninguém somou
> Cliente com passivo de US$ 500 mil em 12 meses compra dólar futuro. Juro em BRL de 11%, em USD de
> 4%. O forward embute ~6,7% acima do spot. O hedge custa ~R$ 190 mil em carrego antes de o câmbio
> se mover. Se o real não depreciar, esse é o resultado da operação — e ele estava contratado desde
> o primeiro dia.

---

## Gotchas

> [!warning] Os erros que aparecem em conta real
> - **Hedgear depois do evento.** É o mais comum e o mais caro: a volatilidade implícita já
>   explodiu, o prêmio já embute o susto, e frequentemente o pior já passou. Proteção se contrata
>   antes, quando é barata e parece desnecessária — é exatamente esse desconforto que é o preço.
> - **Confundir hedge com especulação direcional.** Vender índice "porque acho que vai cair", sem
>   exposição correspondente, não é hedge; é uma posição short. A diferença não é semântica: muda o
>   sizing, muda o limite de risco e muda o que o mandato autoriza.
> - **Ignorar chamada de margem na perna do hedge.** Este é o erro que quebra conta. O short em
>   futuro exige ajuste diário **em dinheiro**, e ele é acionado justamente quando o ativo protegido
>   está subindo — ou seja, quando você está "ganhando" no papel e precisa depositar caixa que não
>   tem. Ativo protegido ilíquido mais hedge com ajuste diário é um descasamento de liquidez, e ele
>   já forçou liquidação de hedges corretos no pior momento possível. Reserve caixa para o pior
>   cenário de margem antes de montar.
> - **Esquecer a rolagem.** Futuro vence. Cada rolagem tem custo e reprecifica o carrego.
> - **Hedge permanente por conforto psicológico.** Custa retorno todo ano para evitar um desconforto
>   que a redução de posição resolveria de graça.
> - **Sobre-hedgear.** Passar de 100% inverte o sinal: você fica short líquido e não percebeu.
> - **Ignorar tributação.** No Brasil, o resultado de derivativo é apurado e tributado
>   separadamente do resultado das ações, com regras próprias e sem compensar automaticamente entre
>   os dois. Um hedge que funcionou economicamente pode gerar imposto a pagar sobre o ganho da perna
>   protetora enquanto a perda da carteira fica em outro balde. Ver [[tax-optimization-br]].
> - **Achar que hedge protege contra risco de crédito ou de liquidez.** Ele protege preço. Emissor
>   que quebra e ativo que não negocia são outros problemas.

---

## Brazilian Context

- **Carrego caro nos dois sentidos.** O diferencial de juros elevado torna o hedge de compra de
  dólar estruturalmente caro e o de venda estruturalmente remunerado. Isso muda o cálculo em relação
  a manuais escritos para o mercado americano.
- **Liquidez concentrada.** WIN e WDO são extremamente líquidos e cobrem a maior parte das
  necessidades de hedge de índice e câmbio. Opções, no entanto, têm liquidez concentrada em poucos
  nomes (PETR4, VALE3, BOVA11) e em vencimentos próximos — hedge com opção de ação de segunda linha
  encontra spread largo e profundidade rasa justamente na hora do estresse.
- **Ibovespa como proxy imperfeito.** O índice é concentrado — os dez maiores pesos somam algo em
  torno de 55%, com predomínio de bancos e commodities. Hedgear com WIN uma carteira de consumo
  doméstico e small caps embute basis risk grande e sistemático. Ver [[brazilian-market-b3]].
- **NDF no balcão.** Para hedge cambial de valor e prazo customizados, o Non-Deliverable Forward
  contratado com banco evita o resíduo de padronização do futuro — ao custo de risco de contraparte
  e menor transparência de preço.
- **Hedge accounting.** Empresas que designam formalmente a relação de hedge sob o CPC 48 / IFRS 9
  conseguem casar o reconhecimento contábil do derivativo com o do item protegido, evitando
  volatilidade artificial no resultado. Exige documentação prévia e teste de efetividade — não se
  aplica retroativamente a um hedge já montado.
- **Memória institucional.** 2008 deixou o precedente brasileiro mais citado sobre o tema:
  exportadoras que reportaram "hedge cambial" carregavam, na verdade, estruturas alavancadas de
  venda de volatilidade — com ganho limitado e perda ilimitada. Quando o real depreciou, as perdas
  foram de bilhões. A lição operacional: **um hedge cujo payoff é assimétrico contra você não é
  hedge.** Se a estrutura pode perder mais do que a exposição que protege, ela é uma posição
  vendida com outro nome, e a pergunta a fazer ao produto estruturado é sempre "qual é a perda
  máxima desta perna, isoladamente?".

---

## Formulas

```
# Número de contratos (hedge de índice)
N = (Valor da carteira × β) / (Pontos do índice × Multiplicador do contrato)

# Hedge ratio de mínima variância
h* = ρ × (σ_spot / σ_futuro)
     ρ = correlação entre variação do ativo e do instrumento

# Base
Base = Preço à vista − Preço futuro
Base risk = volatilidade da base ao longo da vida do hedge

# Paridade coberta (dólar futuro)
Forward = Spot × (1 + i_BRL) / (1 + i_USD)
Custo de carrego anualizado ≈ i_BRL − i_USD

# Protective put
Piso  = Strike − Prêmio pago
Perda máxima = Preço de entrada − Strike + Prêmio

# Collar
Piso  = K_put
Teto  = K_call
Custo líquido = Prêmio da put − Prêmio da call
Custo econômico real = custo líquido + (Preço final − K_call), se positivo

# Hedge de renda fixa com DI
N ≈ (Valor da carteira × Duration_carteira) / (Nocional do DI × Duration_DI)

# Efetividade
Efetividade = 1 − (Var do resultado hedgeado / Var do resultado sem hedge)
```

---

## References

- Hull, J. — *Options, Futures and Other Derivatives*, cap. sobre hedging strategies using futures
- B3 — Especificações de contratos (IND, WIN, DOL, WDO, DI1) e manual de margens
- Natenberg, S. — *Option Volatility and Pricing*
- CPC 48 / IFRS 9 — Instrumentos Financeiros: contabilidade de hedge
- Receita Federal — tributação de operações com derivativos por pessoa física
- CFA Institute — *Derivatives*, leituras sobre risk management applications

---

## Related

- [[futures]] — Mecânica, multiplicadores, margem e ajuste diário dos contratos
- [[options-basics]] — Prêmio, gregas, volatilidade implícita e mecânica de exercício
- [[diversification]] — A alternativa sem prêmio, e por que ela falha na crise
- [[risk-and-return]] — Por que reduzir variância reduz retorno esperado
- [[bonds-international]] — Exposição cambial que geralmente não se quer hedgear
- [[brazilian-market-b3]] — Concentração do Ibovespa e o basis risk que ela cria
- [[commodities]] — Hedge de produtor e roll yield
- [[yield-curve]] — Exposição a taxa que o DI futuro neutraliza
- [[tax-optimization-br]] — Apuração separada do resultado de derivativos
- [[portfolio-review-template]] — Onde a decisão de hedge é registrada e revisada
