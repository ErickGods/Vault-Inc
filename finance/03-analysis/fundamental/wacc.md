---
tags: [finance, analysis, fundamental, wacc, cost-of-capital]
aliases: [WACC, Custo Médio Ponderado de Capital]
house: finance
domain: analysis/fundamental
level: advanced
status: active
created: 2026-07-29
updated: 2026-07-29
---

# WACC — Custo Médio Ponderado de Capital

## Overview

O WACC é o retorno mínimo que uma empresa precisa entregar sobre **todo** o capital empregado para
não destruir valor. Ele é ao mesmo tempo duas coisas:

- o **custo de oportunidade** dos provedores de capital — o que acionistas e credores exigiriam
  para colocar o dinheiro em outro ativo de risco equivalente;
- a **taxa de desconto do FCFF** num DCF, e portanto o número que, junto com o `g` de
  perpetuidade, define a maior parte do valor de uma empresa.

Duas consequências práticas. Primeira: `ROIC − WACC` é o teste de criação de valor — ver
[[roe-roic]] e [[moats]]. Segunda: num DCF típico, mover o WACC em 1 ponto percentual muda o preço
justo em 15-25%. Não existe "WACC aproximado"; existe WACC declarado, com premissas visíveis e
tabela de sensibilidade, ou não existe valuation.

---

## Core Concepts

### A equação

```
WACC = (E/V) × Re + (D/V) × Rd × (1 − T)
```

| Termo | O que é | Onde se obtém |
|---|---|---|
| `E` | Valor de **mercado** do equity | Market cap = preço × nº de ações |
| `D` | Valor de **mercado** da dívida onerosa | Preço das debêntures/bonds; na falta, valor contábil da dívida bruta |
| `V` | `E + D` — capital total | Soma |
| `E/V`, `D/V` | Pesos da estrutura de capital | Sempre a mercado, nunca contábeis |
| `Re` | Custo do equity | CAPM (abaixo) |
| `Rd` | Custo da dívida **antes** de imposto | Taxa marginal de captação hoje |
| `T` | Alíquota marginal de IR/CSLL | ~34% nominal no Brasil; usar a marginal aplicável |

`(1 − T)` é o **tax shield**: juros são despesa dedutível, então cada R$ 1 de juros custa
`R$ 1 × (1 − T)` de caixa efetivo para a empresa. Dividendo não é dedutível — por isso o equity não
carrega esse desconto.

### Custo do equity (Re) via CAPM

```
Re = Rf + β × ERP        (+ prêmio de risco-país, em mercados emergentes)
```

- `Rf` — taxa livre de risco, no mesmo prazo e na mesma moeda do fluxo projetado
- `β` — sensibilidade do retorno da ação ao retorno do mercado
- `ERP` (Equity Risk Premium) — prêmio exigido para carregar risco de mercado em vez de `Rf`

A derivação, as premissas e as fragilidades do CAPM estão em
[[quant/03-factor-models/capm]] — inclusive o ponto que mais importa aqui: o beta é uma estimativa
com erro padrão grande, e tratá-lo como número exato é o começo de quase todo erro de WACC.

Ajustes usuais sobre o beta bruto:

```
# Beta alavancado (Hamada) — reflete a estrutura de capital da empresa analisada
βL = βU × [1 + (1 − T) × D/E]

# Beta desalavancado — para tirar a estrutura de capital do peer e importar só o risco do negócio
βU = βL / [1 + (1 − T) × D/E]
```

O caminho robusto para empresa brasileira: pegar beta **setorial** de uma amostra ampla (Damodaran
publica), desalavancar pela estrutura média do setor, realavancar pela estrutura-alvo da empresa.
Isso evita o beta de regressão de uma ação ilíquida com dois anos de histórico.

### Custo da dívida (Rd) — marginal, não histórico

`Rd` é a taxa que a empresa pagaria para **captar hoje**, não a média que ela paga sobre a dívida
antiga. O valuation desconta fluxos futuros; o capital que os financia é o capital que a empresa
levantará ou rolará no futuro, ao custo de mercado de agora.

Como estimar, em ordem de preferência:

1. **YTM das debêntures ou bonds da própria empresa** no secundário — melhor fonte, quando há
   liquidez.
2. **`Rf` + spread de crédito** do rating (ou do rating sintético estimado por cobertura de juros,
   `EBIT / despesa financeira`).
3. **Taxa das captações recentes** divulgadas em nota explicativa (últimos 12 meses).
4. **Despesa financeira / dívida bruta média** — último recurso, e quase sempre **subestimado**:
   é a média de contratos antigos, muitos deles subsidiados ou tomados em outro regime de juros.

E por que **depois** de imposto: porque o fluxo descontado (FCFF) é calculado com
`EBIT × (1 − T)`, ou seja, **sem** deduzir juros. O benefício fiscal dos juros não está no
numerador — ele tem que aparecer no denominador, senão o tax shield some do modelo. Aplicar `(1−T)`
duas vezes, ou nenhuma, é erro de consistência entre numerador e denominador, não erro de estimativa.

Ressalva: se a empresa não tem lucro tributável, não há tax shield para capturar. Nesse caso
`(1 − T)` não se aplica no ano corrente e deve entrar apenas quando o modelo projeta lucro
tributável.

### Pesos a valor de mercado, sempre

`E/V` e `D/V` usam **valor de mercado**, nunca valor contábil. O motivo é que o WACC é custo de
oportunidade: o investidor decide sobre o capital que pode resgatar hoje ao preço de hoje, não sobre
o número que a contabilidade registrou anos atrás.

O erro de usar patrimônio líquido contábil como `E` é sistemático e de sinal previsível: empresa boa
negocia acima do book, então o peso contábil **subestima** `E/V`, dá peso demais à dívida (que é a
perna barata) e produz um WACC baixo demais — que por sua vez produz um preço justo alto demais.
Numa empresa com P/VP de 3,0x o viés não é marginal: é a diferença entre "comprar" e "vender".

Duas decisões relacionadas:

- **Estrutura atual ou estrutura-alvo?** Se a empresa está desalavancando ou alavancando por
  decisão explícita, o WACC do período explícito precisa acompanhar a trajetória, e o WACC da
  perpetuidade tem que usar a estrutura-alvo de longo prazo. Descontar dez anos de fluxo com o D/V
  de hoje numa empresa que vai zerar a dívida é inconsistente.
- **Caixa excedente.** Não se abate caixa de `D` para calcular pesos por atalho. O tratamento
  consistente é descontar o FCFF operacional pelo WACC e somar o caixa não operacional depois, na
  ponte para o equity value.

### WACC desconta FCFF — e não FCFE

Esta é a regra que mais aparece violada em modelo alheio, e ela não admite meio-termo:

| Fluxo | O que é | Taxa de desconto | Resultado |
|---|---|---|---|
| **FCFF** | Caixa disponível a **todos** os provedores de capital, antes de juros e amortização | **WACC** | Enterprise Value |
| **FCFE** | Caixa que sobra ao **acionista**, depois de juros, amortização e captação | **Re** (custo do equity) | Equity Value direto |

Descontar FCFE pelo WACC conta o benefício da dívida duas vezes: uma no fluxo (que já subtraiu
juros) e outra na taxa (que já é mais baixa por causa da dívida barata e do tax shield). O erro
sempre **infla** o valor, e infla mais quanto mais alavancada a empresa. O inverso — FCFF descontado
por `Re` — subestima. Ver [[valuation-dcf]] para a montagem completa e a ponte de EV para equity
value.

---

## How to Apply

### Roteiro

1. **Defina a moeda e o regime do fluxo** — nominal em BRL, real em BRL, ou nominal em USD. O WACC
   tem que estar no mesmo regime do FCFF. Fluxo real descontado por taxa nominal é o erro mais
   silencioso do valuation brasileiro, porque não deixa rastro na planilha.
2. **`Rf`**: NTN-B longa (real) ou prefixado longo / NTN-F (nominal), no prazo compatível com a
   duration dos fluxos.
3. **`β`**: setorial, desalavancado e realavancado pela estrutura-alvo.
4. **`ERP` e risco-país**: prêmio maduro (EUA) mais prêmio de risco-país, ou ERP local publicado.
5. **`Rd`**: marginal, pelas fontes em ordem de preferência acima.
6. **Pesos**: a mercado, com trajetória se a estrutura de capital mudar.
7. **Monte a tabela de sensibilidade** — WACC ±1 pp contra `g` ±0,5 pp. É exigência da casa
   (`finance/CLAUDE.md`), não opção editorial.
8. **Teste de sanidade**: o WACC calculado é maior que o custo de dívida da empresa e menor que o
   custo de equity? Se não, há erro aritmético ou de peso. E ele é plausível contra o CDI corrente
   — um WACC nominal em BRL abaixo da Selic é quase sempre erro. Ver [[selic-and-monetary-policy]].

---

## Examples

> [!example] WACC de uma industrial brasileira (nominal, BRL)
> ```
> Rf (NTN-F 10y)                 = 12,0%
> β desalavancado do setor       = 0,85
> D/E a mercado                  = 0,50   →  βL = 0,85 × [1 + 0,66 × 0,50] = 1,13
> ERP maduro                     = 5,0%
> Prêmio de risco-país           = 2,5%
>
> Re = 12,0% + 1,13 × 5,0% + 2,5% = 20,2%
>
> Rd (YTM da debênture no secundário) = 15,0%
> T = 34%   →  Rd × (1 − T) = 9,9%
>
> Pesos a mercado: E = 6.000, D = 3.000, V = 9.000  →  E/V = 66,7%, D/V = 33,3%
>
> WACC = 0,667 × 20,2% + 0,333 × 9,9% = 13,5% + 3,3% = 16,8%
> ```

> [!example] O mesmo caso com peso contábil — o erro
> PL contábil = 2.000 (a empresa negocia a P/VP 3,0x). Usando `E` contábil:
> ```
> E/V = 2.000/5.000 = 40%     D/V = 60%
> WACC = 0,40 × 20,2% + 0,60 × 9,9% = 8,1% + 5,9% = 14,0%
> ```
> 280 bps abaixo do correto. Num DCF com `g` de 4%, o perpetuity multiple sai de
> `1/(0,168−0,04) = 7,8x` para `1/(0,140−0,04) = 10,0x` — **+28% de valor terminal** produzidos por
> uma escolha de fonte de dado, não por nada que a empresa fez.

---

## Gotchas

> [!warning] Erros que invalidam o valuation
> - **Beta de janela curta.** Regressão de 1-2 anos em ação de baixa liquidez produz beta que é
>   quase ruído. Use beta setorial e diga isso no report.
> - **Pesos contábeis.** Viés de sinal conhecido e material (exemplo acima).
> - **Esquecer o tax shield** — ou aplicá-lo duas vezes, subtraindo juros do FCFF *e* usando
>   `Rd × (1−T)`.
> - **`Rd` histórico.** Despesa financeira sobre dívida média captura contratos antigos e subestima
>   o custo marginal, sobretudo depois de um ciclo de alta de juros.
> - **WACC constante numa empresa que muda de estrutura de capital** ao longo do período explícito.
> - **Descontar FCFE pelo WACC.** Infla o valor, e infla mais quanto maior a alavancagem.
> - **Mistura de regime**: fluxo real com WACC nominal, ou fluxo em BRL com WACC em USD.
> - **Prêmio de risco-país somado duas vezes** — uma no `Rf` (usando NTN-B, que já embute risco
>   soberano local) e outra como parcela explícita. Escolha um caminho e declare qual.
> - **WACC único para conglomerado.** Segmentos com risco diferente exigem WACC diferente; média
>   ponderada aplicada a todos subvaloriza o segmento seguro e supervaloriza o arriscado.

---

## Brazilian Context

### Qual `Rf` usar

Não se usa a Selic. A Selic é taxa **overnight** e o fluxo de um DCF tem duration de muitos anos —
descontar fluxo de 10 anos por taxa de 1 dia é erro de casamento de prazo, além de importar todo o
ciclo monetário corrente para dentro de uma premissa que deveria ser estrutural.

- **Modelo em termos reais**: NTN-B longa (10 anos ou mais) — entrega juro real puro observável.
- **Modelo em termos nominais**: prefixado longo / NTN-F de prazo compatível.
- **Modelo em USD**: Treasury de 10 anos **mais** prêmio de risco-país.

Nenhuma dessas é livre de risco de verdade — o título soberano brasileiro carrega risco soberano.
Por isso a decisão de somar (ou não) risco-país depende de qual `Rf` foi escolhido, e essa decisão
tem que estar escrita no report.

### Prêmio de risco-país

Faixa usual de 200 a 400 bps, estimada por spread do EMBI+ Brasil ou pelo default spread do rating
soberano, às vezes escalado pela volatilidade relativa do mercado acionário. Damodaran publica
anualmente prêmios por país, betas setoriais e alíquotas efetivas — é a fonte de referência da casa.

O prêmio **varia com o ciclo**: em estresse fiscal ele abre rapidamente, e um valuation feito com o
risco-país de um período calmo fica desatualizado sem que nenhuma premissa operacional tenha mudado.
Vale registrar a data do prêmio usado.

### A estrutura de capital brasileira é diferente

Não é só que o custo de dívida é mais alto — o **perfil** é outro:

- **Prazo curto.** Dívida corporativa brasileira é significativamente mais curta que a de mercados
  desenvolvidos. Isso significa risco de refinanciamento recorrente: a empresa volta ao mercado com
  frequência, e o `Rd` marginal de hoje importa muito mais do que importaria com dívida de 20 anos.
- **Indexação.** Boa parte da dívida é CDI+ ou IPCA+, então o `Rd` **flutua com a política
  monetária**. Um WACC calculado no fundo do ciclo de juros descreve uma empresa diferente da mesma
  empresa no pico.
- **Dívida subsidiada.** Linhas de BNDES, FINEP, crédito rural e incentivos regionais produzem custo
  histórico artificialmente baixo que **não é replicável na margem**. Usar essa média como `Rd` é
  precisamente o erro de custo histórico.
- **Alavancagem menor.** Como a dívida é cara e curta, empresas brasileiras costumam operar com
  `D/V` menor — o que empurra o WACC para perto do custo de equity, que é a perna cara.
- **JCP.** Juros sobre Capital Próprio criam um tax shield sobre parte da remuneração ao acionista,
  algo que o WACC padrão não modela. Em empresa que usa JCP de forma relevante, vale tratar o efeito
  explicitamente no fluxo em vez de tentar embuti-lo na taxa.

Efeito líquido: WACC nominal em BRL costuma cair na faixa de 13-18% para empresas de risco médio,
contra 7-9% de comparáveis americanas. Isso não é detalhe técnico — é a razão estrutural de os
múltiplos brasileiros serem menores que os americanos para o mesmo negócio.

---

## Formulas

```
# WACC
WACC = (E/V) × Re + (D/V) × Rd × (1 − T)
V    = E + D                      (ambos a valor de mercado)

# Custo do equity (CAPM + risco-país)
Re = Rf + β × ERP + Prêmio de risco-país

# Beta (Hamada)
βL = βU × [1 + (1 − T) × D/E]
βU = βL / [1 + (1 − T) × D/E]

# Custo da dívida
Rd = Rf + spread de crédito        (marginal, não histórico)
Custo efetivo = Rd × (1 − T)

# Consistência com o fluxo
FCFF = EBIT × (1 − T) + D&A − Capex − ΔWC     → descontar por WACC   → Enterprise Value
FCFE = FCFF − Juros × (1 − T) + Δ Dívida      → descontar por Re     → Equity Value

# Teste de criação de valor
Spread = ROIC − WACC
EVA    = (ROIC − WACC) × Capital Investido

# Múltiplo implícito da perpetuidade (sanidade)
TV / FCFF_{n+1} = 1 / (WACC − g)
```

---

## References

- Damodaran, A. — *Investment Valuation*, cap. 4 e 8 (cost of capital, risk-free rate em emergentes)
- Damodaran Online — https://pages.stern.nyu.edu/~adamodar/ (ERP por país, betas setoriais, tax rates)
- Koller, Goedhart, Wessels — *Valuation*, Parte 2 (cost of capital e estrutura-alvo)
- Modigliani, F.; Miller, M. (1963) — "Corporate Income Taxes and the Cost of Capital"
- Hamada, R. (1972) — efeito da estrutura de capital sobre o beta
- CFA Institute — *Corporate Finance*, leituras sobre cost of capital

---

## Related

- [[valuation-dcf]] — Onde o WACC é usado: taxa de desconto do FCFF
- [[quant/03-factor-models/capm]] — Derivação do custo de equity (casa quant)
- [[roe-roic]] — ROIC vs WACC é o teste de criação de valor
- [[moats]] — O que sustenta ROIC acima do WACC ao longo do tempo
- [[key-ratios]] — Alavancagem e cobertura de juros que alimentam o rating sintético
- [[yield-curve]] — De onde sai o `Rf` de longo prazo
- [[selic-and-monetary-policy]] — Por que o WACC brasileiro se move com o ciclo
- [[time-value-of-money]] — Base teórica do desconto
- [[valuation-formulas]] — Fórmulas consolidadas
