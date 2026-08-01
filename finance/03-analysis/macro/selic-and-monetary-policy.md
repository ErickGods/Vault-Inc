---
tags: [finance, analysis, macro, monetary-policy, selic]
aliases: [Selic, Política Monetária, Copom]
house: finance
domain: analysis/macro
level: intermediate
status: active
created: 2026-07-29
updated: 2026-07-29
---

# Selic e Política Monetária no Brasil

## Overview

A Selic é o preço do dinheiro de um dia no Brasil, e por consequência a âncora de toda a curva de
juros, de todo desconto de fluxo de caixa e de boa parte do câmbio. Nenhuma decisão de alocação no
mercado brasileiro é independente dela.

O ponto que separa quem opera de quem comenta: **o mercado não reage à Selic, reage à surpresa em
relação à Selic esperada.** A decisão de hoje já está no preço dos ativos há semanas — o que move
preço é a decisão que ninguém esperava, ou a mudança de tom sobre as próximas.

Esta nota trata do regime brasileiro — instituição, mecanismo, comunicação e efeito por classe de
ativo. Para o ciclo de juros como fenômeno geral e a comparação com o Fed, ver
[[interest-rate-cycles]].

---

## Core Concepts

### Selic meta e Selic efetiva

São duas coisas distintas, e a confusão entre elas aparece em relatório profissional com frequência
desconfortável.

| | Selic meta | Selic efetiva (Selic over) |
|---|---|---|
| O que é | Alvo definido pelo Copom | Taxa média das operações compromissadas de 1 dia com lastro em título público, apurada e divulgada diariamente pelo BC |
| Quem determina | Comitê, por decisão | O mercado, dentro do intervalo que o BC administra |
| Onde aparece | Manchete, comunicado | Rentabilidade real do Tesouro Selic, base do CDI |
| Comportamento | Degraus discretos | Flutua alguns centésimos abaixo da meta |

A efetiva costuma rodar marginalmente **abaixo** da meta. Para o investidor, a consequência prática
é que o Tesouro Selic rende a efetiva, não a manchete — e o CDI, que remunera boa parte da renda
fixa privada, acompanha a efetiva de perto.

### Quem decide: o Copom

- **Comitê de Política Monetária do Banco Central**, formado pelo presidente do BC e pelos diretores.
- **Oito reuniões por ano**, a cada ~45 dias, em dois dias (terça e quarta), com a decisão anunciada
  na quarta após o fechamento.
- A decisão sai acompanhada de um **comunicado**; a **ata** é publicada na terça-feira seguinte.
- O BC brasileiro tem **autonomia formal** desde a LC 179/2021, com mandatos fixos e não coincidentes
  com o do presidente da República — o que não elimina a pressão política, apenas encarece o custo
  dela.
- Diferente do Fed, o BCB **não tem dual mandate**. O objetivo é a inflação; atividade e emprego
  entram como determinantes da inflação futura, não como objetivo próprio.

### O mecanismo de transmissão — e o lag

A Selic não afeta a inflação diretamente. Ela percorre uma cadeia:

```
Selic ↑
  ├─► Crédito mais caro ──► ↓ consumo durável, ↓ investimento
  ├─► Renda fixa mais atraente ──► ↓ apetite por risco, ↓ efeito riqueza
  ├─► Diferencial de juros ↑ ──► entrada de capital ──► R$ aprecia ──► ↓ inflação importada
  └─► Expectativas ancoradas ──► ↓ repasse de preços, ↓ reajustes
        ↓
   ↓ Demanda agregada
        ↓
   ↓ Inflação   (com defasagem de 6 a 9 meses para o efeito principal)
```

A defasagem é a informação operacional mais importante da política monetária. **A Selic de hoje
combate a inflação de daqui a 6 a 9 meses** — e o efeito pleno leva ainda mais, até 18 meses. Isso
implica:

- O BC atua sobre **projeção**, não sobre o IPCA divulgado. Cobrar do Copom reação ao número do mês
  é cobrar algo que já não pode ser mudado.
- Ciclos são **prolongados até depois** de a inflação ceder, porque o efeito ainda está em trânsito.
- O canal cambial é o mais **rápido** (dias a semanas); o canal de crédito é o mais **lento**.
- Erros de política só ficam visíveis quando é tarde para corrigi-los sem custo — daí a insistência
  do BC no vocabulário de "cautela" e "perseverança".

No Brasil o canal cambial pesa mais que na média dos países desenvolvidos, porque alimentos e
combustíveis — dolarizados e de alto peso no IPCA — repassam rápido.

### O regime de metas de inflação

Vigente desde 1999. A arquitetura tem três peças:

1. **A meta**, definida pelo **CMN** (Conselho Monetário Nacional: ministro da Fazenda, ministro do
   Planejamento e presidente do BC) — não pelo Copom. O Copom recebe a meta e persegue; quem a
   define é o CMN.
2. **A banda de tolerância**, de ±1,5 pp em torno do centro. Com meta de 3,0%, o intervalo é de 1,5%
   a 4,5%. A banda existe porque choques de oferta (seca, petróleo, câmbio) não devem ser combatidos
   com toda a força do instrumento — fazê-lo custaria mais atividade do que a inflação evitada vale.
3. **A prestação de contas quando a meta é descumprida**: o presidente do BC escreve uma **carta
   aberta** ao ministro da Fazenda explicando as causas do descumprimento, as providências e o prazo
   esperado para o retorno à meta. A carta é pública e é o mecanismo formal de accountability do
   regime.

> [!info] Meta contínua
> A partir de 2025 o regime passou a ser de **meta contínua**: o cumprimento deixa de ser avaliado
> pelo ano-calendário e passa a ser avaliado mês a mês pela inflação acumulada em 12 meses, com o
> descumprimento configurado após seis meses consecutivos fora da banda. Muda o horizonte de
> avaliação, não a lógica do regime — e reduz o incentivo de "queimar" política monetária para
> fechar o ano dentro da banda.

A carta aberta importa para o analista menos pelo ritual e mais pelo que ela sinaliza: metas
descumpridas com frequência **desancoram expectativas**, e expectativa desancorada torna a
desinflação muito mais cara em termos de atividade. A variável a monitorar não é o IPCA corrente, é
a expectativa de IPCA para os anos seguintes no [[global-macro-indicators|Relatório Focus]].

### Efeito sobre cada classe de ativo

**Renda fixa.** É onde o efeito é mais direto e mais mal compreendido.

- *Pós-fixado* (Tesouro Selic, CDB % do CDI): acompanha a taxa, sem marcação relevante. Selic
  subindo é bom, na hora.
- *Prefixado e IPCA+*: o preço é valor presente. Quando a taxa de mercado sobe, o preço cai —
  proporcionalmente à **duration**. Uma NTN-B 2045 pode perder 15-20% em meses num choque de juros.
  Esse é o mecanismo pelo qual "renda fixa" gera prejuízo, e ele surpreende o investidor de varejo
  todo ciclo. Ver [[tesouro-direto]] e [[yield-curve]].
- O que a curva precifica não é a Selic de hoje, é a **trajetória esperada**. Por isso o prefixado
  longo pode cair no dia de um corte, se o corte veio com comunicado duro.

**Renda variável.** Dois canais somados:

- *Taxa de desconto*: Selic mais alta eleva `Rf` e o [[wacc]], comprime o valor presente dos fluxos.
  O efeito é **maior em empresas de crescimento**, cujo valor está concentrado em fluxos distantes,
  e menor em empresas maduras com caixa próximo.
- *Fundamentos setoriais*: setores sensíveis a crédito (varejo discricionário, construção civil,
  concessionárias de veículos, small caps alavancadas) sofrem duas vezes — desconto maior e lucro
  menor. Bancos podem ganhar no spread, mas perdem em inadimplência e volume adiante. Empresas com
  caixa líquido ganham receita financeira; empresas com dívida em CDI veem a despesa financeira
  subir dentro do mesmo trimestre.
- *Concorrência de alocação*: com Selic elevada, o ativo livre de risco entrega retorno real alto, e
  o prêmio exigido do equity sobe. É o efeito mais forte no Brasil e o que mais drena fluxo da bolsa.

**Câmbio.** O diferencial de juros contra o exterior remunera o carry trade: Selic alta com juro
americano baixo atrai capital e tende a apreciar o real. Mas o diferencial é apenas um dos termos —
risco fiscal, prêmio de risco-país e apetite global por risco frequentemente dominam. Selic subindo
com deterioração fiscal pode conviver com real depreciando, e essa combinação já ocorreu no Brasil
mais de uma vez.

### Como ler o Copom

O que produz P&L não é a decisão, é o que ela revela sobre as próximas. Roteiro:

1. **Antes**: qual é o consenso? Focus, curva DI e a mediana de projeções dos bancos. A curva de
   juros futuros dá a probabilidade implícita de cada movimento — é a melhor leitura do que já está
   no preço.
2. **A decisão**: comparar com o consenso, não com a taxa anterior. Manter quando o mercado esperava
   corte é aperto.
3. **O comunicado**: texto curto, mudado marginalmente a cada reunião. **O que importa é o diff
   contra o comunicado anterior** — palavra retirada, advérbio acrescentado, forward guidance
   mantido ou abandonado. "Cautela", "perseverança", "não se compromete com o ritmo": cada mudança
   dessas move a curva mais que a decisão em si.
4. **Placar de votos**: decisão dividida sinaliza ciclo prestes a virar.
5. **A ata, na terça seguinte**: traz o raciocínio, o balanço de riscos e as projeções condicionais.
   É onde se descobre *por que*, e é a peça que permite antecipar a próxima reunião.
6. **O Relatório de Política Monetária** (trimestral, antigo Relatório de Inflação): cenários e
   projeções condicionais completas.

> [!tip] A regra que resume
> Decisão precificada não move preço. O que move é a mudança de **expectativa** sobre a trajetória —
> e ela vive no comunicado e na ata, não no número.

---

## How to Apply

### Do juro nominal para a decisão de alocação

- **Use sempre o juro real.** Selic de 13,75% com IPCA esperado de 11% é política frouxa; Selic de
  9% com IPCA de 3% é apertada. `(1+i_real) = (1+i_nominal)/(1+π_esperada)`. A referência mais limpa
  do juro real ex-ante brasileiro é a taxa da NTN-B, negociada e observável.
- **Compare com o juro neutro.** Juro real acima do neutro estimado (hoje discutido na faixa de
  4,5-5,5% no Brasil) é política contracionista; abaixo, expansionista. É essa distância, e não o
  nível nominal, que informa o quanto ainda falta de ciclo.
- **Posicione o portfólio pela fase, não pela manchete.** Início de ciclo de alta: encurtar duration,
  privilegiar pós-fixado, reduzir setores sensíveis a crédito. Fim de ciclo de alta, com o mercado
  já precificando cortes: alongar duration em prefixado e IPCA+ longo é onde está o maior retorno
  assimétrico — e também onde está o maior risco de errar o timing.
- **Não confunda ciclo com timing.** Acertar que o ciclo vai virar é diferente de acertar quando.
  Antecipar em seis meses um alongamento de duration custa marcação a mercado no meio do caminho.

### Para valuation

Selic entra no [[wacc]] indiretamente, e a forma correta importa: **não se usa a Selic como taxa
livre de risco**. `Rf` é a taxa de prazo compatível com a duration dos fluxos (NTN-B longa em termos
reais, prefixado longo em nominais). A Selic afeta o WACC porque ancora toda a curva e porque define
o custo da dívida indexada a CDI — mas usá-la diretamente descasa o prazo. Ver [[valuation-dcf]].

---

## Examples

> [!example] Corte que derrubou a bolsa
> Copom corta 25 bps, exatamente o esperado, mas retira do comunicado a expressão que indicava
> cortes de mesma magnitude nas reuniões seguintes e cita "desancoragem das expectativas". A curva
> de juros **abre** (juros longos sobem), o prefixado longo cai de preço, e o Ibovespa recua.
> Juro cortado, condição financeira apertada. A decisão era conhecida; o guidance não era.

> [!example] Marcação a mercado que assusta o investidor de varejo
> Cliente compra NTN-B 2045 a IPCA+5,5%. Seis meses depois, choque fiscal leva a taxa a IPCA+6,8%.
> Com duration ~12 anos: `ΔP/P ≈ −12 × 1,3 pp ≈ −15,6%`. O título não deu calote e, levado ao
> vencimento, entrega IPCA+5,5% como contratado. A perda é de marcação, não de crédito — mas é real
> se o cliente vender, e é por isso que prazo do título tem que casar com prazo do objetivo. Ver
> [[tesouro-direto]].

---

## Gotchas

> [!warning] Erros de leitura
> - **Confundir meta com efetiva**, e projetar rendimento de Tesouro Selic pela manchete.
> - **Ler o nível nominal e ignorar o real.** Selic de 15% pode ser frouxa.
> - **Achar que a Selic controla a curva inteira.** O Copom controla a ponta curta; a ponta longa é
>   dominada por risco fiscal e prêmio de prazo, e pode subir com a Selic caindo.
> - **Ignorar a defasagem** e cobrar do BC reação à inflação já divulgada.
> - **Tratar renda fixa longa como se não tivesse volatilidade.** Ela tem, e é da ordem de grandeza
>   da bolsa em choques de juros.
> - **Operar a decisão em vez da surpresa.** Comprar bolsa "porque vem corte" quando a curva já
>   precifica três cortes é comprar o consenso.
> - **Extrapolar a Selic corrente para a perpetuidade** do DCF. Nem a Selic do pico nem a do vale
>   descrevem o juro estrutural.
> - **Supor que Selic alta sempre aprecia o real.** Risco fiscal domina o diferencial de juros com
>   frequência.

---

## Brazilian Context

- **Juro real estruturalmente alto.** O Brasil convive há décadas com juros reais entre os maiores do
  mundo. As explicações concorrentes — dívida pública elevada e de prazo curto, poupança doméstica
  baixa, crédito direcionado e subsidiado que reduz a potência da política monetária, histórico
  inflacionário — não são consensuais, mas o fato é. Ele explica por que o WACC brasileiro é alto e
  por que os múltiplos de bolsa são estruturalmente menores.
- **Dominância fiscal.** Quando o mercado passa a duvidar da solvência do Estado, subir a Selic pode
  **piorar** a expectativa de inflação: juro maior aumenta a despesa financeira, deteriora a dívida e
  deprecia o câmbio. Nesse regime o instrumento perde potência, e o prêmio na ponta longa sobe
  independentemente do Copom. Reconhecer quando o mercado está precificando esse risco é parte da
  leitura macro.
- **CDI como referência universal.** Quase toda a renda fixa privada é cotada em % do CDI ou CDI+.
  O CDI acompanha a Selic efetiva de perto, então mudar a Selic reprecifica instantaneamente o
  estoque de renda fixa privada e a despesa financeira das empresas endividadas em CDI.
- **Crédito direcionado.** BNDES, crédito rural e imobiliário com taxas administradas são parcela
  relevante do crédito e respondem pouco à Selic — o que concentra o aperto sobre o crédito livre e
  exige um movimento maior para o mesmo efeito agregado.
- **Focus, toda segunda-feira.** Mediana das projeções de mercado para Selic, IPCA, PIB e câmbio.
  É o termômetro oficial da ancoragem das expectativas e insumo direto do próprio Copom.
- **Copom e FOMC não são independentes.** Juro americano alto reduz o espaço para corte no Brasil,
  porque comprime o diferencial e pressiona o câmbio.

---

## Formulas

```
# Juro real (Fisher)
(1 + i_real) = (1 + i_nominal) / (1 + π_esperada)
i_real ≈ i_nominal − π_esperada

# Postura da política
Gap = juro real ex-ante − juro real neutro
Gap > 0 → contracionista | Gap < 0 → expansionista

# Regra de Taylor (referência)
i = r* + π + 0,5×(π − π*) + 0,5×(y − y*)

# Marcação a mercado de título prefixado / IPCA+
ΔP/P ≈ −Duration × Δtaxa
ΔP/P ≈ −Duration × Δy + ½ × Convexidade × (Δy)²

# Inflação implícita (breakeven)
π_implícita = [(1 + taxa prefixada) / (1 + taxa NTN-B)] − 1

# Paridade coberta de juros (referência cambial)
Forward = Spot × (1 + i_BRL) / (1 + i_USD)

# Meta e banda
Banda = meta ± 1,5 pp   (meta de 3,0% → 1,5% a 4,5%)
```

---

## References

- Banco Central do Brasil — Comunicados e Atas do Copom; Relatório de Política Monetária
- Banco Central do Brasil — Relatório Focus (semanal)
- Lei Complementar 179/2021 — autonomia do Banco Central
- Decreto 3.088/1999 — instituição do regime de metas para a inflação
- CMN — Resoluções que definem a meta e o regime de meta contínua
- Bernanke, B. — *21st Century Monetary Policy*
- Mishkin, F. — *The Economics of Money, Banking, and Financial Markets*
- Blanchard, O. (2004) — "Fiscal Dominance and Inflation Targeting: Lessons from Brazil"

---

## Related

- [[interest-rate-cycles]] — O ciclo de juros como fenômeno geral e a comparação com o Fed
- [[yield-curve]] — Onde a expectativa de Selic vira preço observável
- [[tesouro-direto]] — Efeito prático sobre cada título público
- [[wacc]] — Como o juro entra na taxa de desconto
- [[inflation]] — O alvo da política monetária
- [[global-macro-indicators]] — Focus, IPCA, IBC-Br e o calendário de divulgações
- [[valuation-dcf]] — Sensibilidade do valuation à taxa de desconto
- [[market-cycles]] — Como o mercado responde às fases do ciclo
- [[acronyms-br]] — Selic, CDI, Copom, CMN
