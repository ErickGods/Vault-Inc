---
tags: [finance, accounting, profitability]
aliases: [ROE, ROIC, Retorno sobre Capital]
house: finance
domain: accounting
level: intermediate
status: active
created: 2026-07-29
updated: 2026-07-29
---

# ROE e ROIC — Retorno sobre Capital

## Overview

ROE e ROIC respondem a perguntas diferentes, e confundi-las é o erro mais caro da análise de
rentabilidade.

- **ROE** responde: *quanto o acionista ganhou sobre o capital dele?* É uma medida de retorno **ao
  acionista**, e ela incorpora — de propósito — o efeito da alavancagem.
- **ROIC** responde: *quanto o negócio ganhou sobre todo o capital que usa?* É uma medida da
  **qualidade do negócio**, deliberadamente cega à forma como esse negócio foi financiado.

As duas são úteis. Mas quando a pergunta é "esse negócio é bom?", a resposta está no ROIC, porque o
ROE pode ser inflado sem que nada tenha melhorado na operação. E quando a pergunta é "esse negócio
cria valor?", nenhuma das duas responde sozinha — a resposta é o **spread contra o custo de
capital**: ver [[wacc]] e [[moats]].

## Core Concepts

### As duas fórmulas

```
ROE  = Lucro Líquido / Patrimônio Líquido Médio × 100

NOPAT           = EBIT × (1 − alíquota efetiva de IR)
Capital Investido = PL + Dívida Onerosa − Caixa não operacional
ROIC = NOPAT / Capital Investido Médio × 100
```

Sempre com denominador **médio** entre abertura e fechamento do período. Empresa que fez aumento de
capital ou grande aquisição em dezembro tem ROE de fim de ano artificialmente deprimido se o
denominador for o saldo final.

### Capital investido, explicitamente

Esta é a definição que mais varia entre analistas, e a inconsistência inutiliza comparações. As duas
rotas equivalentes:

**Pelo passivo (financiamento):**
```
Capital Investido = Patrimônio Líquido
                  + Dívida onerosa (curto e longo prazo, incluindo arrendamentos IFRS 16)
                  + Participação de minoritários
                  − Caixa e aplicações não operacionais
```

**Pelo ativo (aplicação):**
```
Capital Investido = Capital de giro operacional (AC operacional − PC não oneroso)
                  + Imobilizado líquido
                  + Intangíveis e goodwill
                  + Direito de uso (IFRS 16)
                  − Caixa excedente
```

Regras que fecham as duas rotas:

- **Passivo não oneroso sai.** Fornecedores, salários e impostos a pagar são financiamento
  espontâneo do negócio, não capital que alguém exigiu remuneração para fornecer. Deixá-los dentro
  infla o capital investido e deprime o ROIC.
- **Caixa operacional fica, caixa excedente sai.** A empresa precisa de um mínimo de caixa para
  operar; o excesso é um ativo financeiro que não pertence ao negócio operacional. Manter o caixa
  excedente dentro do denominador é a causa mais frequente de ROIC subestimado em empresa com
  balanço líquido.
- **IFRS 16 entra dos dois lados.** Pós-2019, arrendamento vira direito de uso no ativo e passivo de
  arrendamento no passivo. Comparar ROIC pré e pós-2019 sem ajustar produz uma queda que é
  puramente contábil — crítico em varejo e logística, onde a base de lojas e galpões é arrendada.
- **NOPAT tem que ser consistente com o denominador.** Se o capital inclui arrendamento, o EBIT tem
  que estar depois da depreciação do direito de uso e antes do juro do arrendamento.
- **Alíquota efetiva, não nominal.** Usar 34% quando a empresa paga 22% por JCP ou incentivo fiscal
  subestima o NOPAT e o ROIC.

### Por que o ROIC julga melhor o negócio

O ROE é **inflável por alavancagem**. É o ponto central, e ele se demonstra em vez de se afirmar.

O mesmo negócio — mesma receita, mesma margem operacional, mesmos ativos — financiado de duas
formas diferentes:

```
Negócio: Ativo Operacional 1.000 | EBIT 150 | alíquota 34% | NOPAT 99
Custo da dívida: 12% a.a.

              Sem dívida                Com 500 de dívida
PL                1.000                       500
Dívida                0                       500
EBIT                150                       150
Juros                 0                       (60)
LAIR                150                        90
IR (34%)            (51)                      (31)
Lucro Líquido        99                        59

ROE          99/1.000 = 9,9%          59/500  = 11,9%   ← subiu
ROIC         99/1.000 = 9,9%          99/1.000 = 9,9%   ← não mudou
```

O ROE subiu 2 pontos percentuais. O negócio é exatamente o mesmo. A única coisa que mudou foi que os
acionistas passaram a correr mais risco: o mesmo EBIT agora sustenta juros fixos, e uma queda de
40% no EBIT que antes reduzia o lucro proporcionalmente agora o zera.

É por isso que **ROE alto não é virtude por si**. ROE de 25% com D/E de 3,0x é um preço de risco, não
um prêmio de qualidade. ROE de 25% com dívida líquida negativa é outra coisa inteiramente — e só o
ROIC (ou o DuPont) distingue os dois casos.

Consequência para o analista: o ROE é a métrica certa para bancos (onde a alavancagem *é* o
negócio, regulada pelo índice de Basileia) e para medir o retorno efetivo do acionista. O ROIC é a
métrica certa para julgar a máquina operacional e para comparar empresas com estruturas de capital
diferentes.

### DuPont — de onde vem o ROE

A decomposição existe justamente para separar as três origens possíveis de um ROE alto:

```
ROE = Margem Líquida × Giro do Ativo × Alavancagem

ROE = (Lucro Líquido / Receita) × (Receita / Ativo Total) × (Ativo Total / PL)
```

| Componente | O que revela | Modelo de negócio típico |
|---|---|---|
| **Margem líquida** | Poder de preço e disciplina de custo — quanto de cada real de receita sobra | Software, marcas premium, farmacêutica |
| **Giro do ativo** | Eficiência de uso do capital — quantas vezes o ativo se converte em receita no ano | Varejo alimentar, distribuição, atacarejo |
| **Alavancagem** | Quanto do ativo é financiado por terceiros — **amplifica os dois anteriores, para cima e para baixo** | Bancos, utilities, imobiliário |

A leitura é comparativa e estrutural: dois varejistas com ROE de 18% podem ser negócios opostos —
um com margem de 8% e giro de 1,1x, outro com margem de 2% e giro de 4,5x. O primeiro sobrevive a
uma guerra de preço; o segundo, não. Ambos morrem por causas diferentes, e o número agregado esconde
isso.

A versão de 5 fatores separa ainda o efeito fiscal e o financeiro:

```
ROE = (LL/LAIR) × (LAIR/EBIT) × (EBIT/Receita) × (Receita/Ativo) × (Ativo/PL)
       tax burden  interest burden  margem EBIT   giro         alavancagem
```

O **interest burden** é o termo diagnóstico: se `LAIR/EBIT` está caindo ano a ano, a dívida está
comendo o resultado operacional, e o ROE que ainda parece bom está sendo sustentado pelo último
termo — que é exatamente o que amplifica a perda quando o ciclo vira. Ver [[key-ratios]] para a
decomposição com exemplo numérico fechado e [[income-statement]] para as margens que a alimentam.

### ROIC vs WACC — o teste de criação de valor

O ROIC sozinho não diz se a empresa cria valor. Uma empresa com ROIC de 14% num setor cujo custo de
capital é 17% está **destruindo** valor a cada real reinvestido, mesmo parecendo lucrativa na DRE.

```
Spread = ROIC − WACC

Spread > 0  →  cada real reinvestido cria valor; crescer é bom
Spread ≈ 0  →  crescimento é neutro; a empresa é uma máquina de girar capital
Spread < 0  →  cada real reinvestido destrói valor; crescer piora a situação
```

Duas consequências que mudam recomendação:

1. **Crescimento não é bom em si.** Com spread negativo, a empresa que cresce mais rápido destrói
   valor mais rápido. A recomendação correta para ela é distribuir caixa ou encolher, não investir.
2. **O spread é a assinatura do moat.** Retorno acima do custo de capital atrai concorrência; se ele
   persiste por uma década, há uma barreira, e ela precisa ser nomeada — ver [[moats]].

O nível de referência muda com o WACC do país e do ciclo. No Brasil, com WACC nominal em BRL
tipicamente entre 13% e 18% (ver [[wacc]]), a régua americana de "ROIC acima de 10% é bom" não se
aplica: ali, 10% é destruição de valor.

## How to Apply

1. **Puxe 10 anos**, não um ano. Um único exercício não separa retorno estrutural de janela
   favorável, venda de ativo ou reversão de provisão.
2. **Calcule ROIC e ROE lado a lado.** A distância entre os dois *é* a informação: ROE muito acima
   do ROIC mede a alavancagem em pontos percentuais.
3. **Decomponha o ROE por DuPont** e veja qual dos três termos explica o nível — e qual explica a
   *variação* no período.
4. **Compare o ROIC ao WACC do mesmo período**, não ao WACC de hoje. Empresa que rendeu 15% quando o
   custo de capital era 11% e rende 15% agora que ele é 17% mudou de lado sem mudar de número.
5. **Normalize cíclicas.** Use média de 5-10 anos, ou o ROIC no preço de longo prazo da commodity.
6. **Cheque a consistência do capital investido** entre a empresa e os peers antes de rankear. Se as
   definições diferirem, o ranking é ficção.
7. **Cruze com o caixa.** ROIC alto com FCO baixo é sinal de accrual, não de rentabilidade — ver
   [[cash-flow-statement]] e [[red-flags-accounting]].

> [!tip] O que reportar
> Num report de equity, o par útil não é "ROE de 22%". É: *ROIC de 16% contra WACC de 13%, spread de
> 3 pp mantido por 8 dos últimos 10 anos, com ROE de 22% do qual 6 pp vêm de alavancagem de 1,8x.*
> Isso é uma tese; o número solto é um dado.

## Examples

> [!example] Mesmo ROE, negócios opostos (DuPont)
> | | Varejista A | Varejista B |
> |---|---|---|
> | Margem líquida | 7,5% | 1,9% |
> | Giro do ativo | 1,10x | 4,60x |
> | Alavancagem | 2,20x | 2,05x |
> | **ROE** | **18,2%** | **17,9%** |
> | ROIC | 12,1% | 11,4% |
>
> ROE quase idêntico. A vive de margem — vulnerável a entrada de concorrente com preço agressivo.
> B vive de giro — vulnerável a qualquer soluço de volume, porque a margem de 1,9% não absorve
> alavancagem operacional negativa. Comprar "o ROE" trata os dois riscos como o mesmo.

> [!example] ROIC que sobe por queda no denominador
> Empresa reconhece impairment de R$ 800 mi de goodwill. NOPAT do ano seguinte fica estável em
> R$ 300 mi, mas o capital investido cai de R$ 2,6 bi para R$ 1,8 bi.
> ```
> ROIC antes:   300 / 2.600 = 11,5%
> ROIC depois:  300 / 1.800 = 16,7%
> ```
> A rentabilidade "melhorou" 520 bps porque a empresa **admitiu ter destruído capital**. Sem ler a
> nota explicativa, o screener mostra uma empresa que virou de qualidade.

## Gotchas

- **Patrimônio líquido negativo ou muito pequeno.** Com PL negativo, o ROE fica negativo com lucro
  positivo — sem significado. Com PL residual (após anos de recompra agressiva), o ROE explode para
  centenas por cento. Nos dois casos, a métrica é inutilizável e só o ROIC informa.
- **Intangível de aquisição inflando o capital investido.** Empresa que cresce comprando carrega
  goodwill no denominador e mostra ROIC menor que a concorrente que cresceu organicamente com a
  mesma operação. Calcular o ROIC **com e sem goodwill** separa duas perguntas diferentes: "o
  negócio é bom?" (sem goodwill) e "a gestão pagou um preço que se justifica?" (com goodwill). As
  duas importam, e a segunda é o teste de alocação de capital — ver [[capital-allocation]].
- **Um ano não é sinal.** Venda de ativo, reversão de provisão, crédito tributário extemporâneo ou
  variação cambial produzem ROE e ROIC de um ano que não se repetem. Exija a série.
- **Recompra de ações eleva o ROE mecanicamente** ao reduzir o PL — sem qualquer melhora operacional,
  e com o mesmo aumento de risco da alavancagem.
- **Empresa em ramp-up.** Capital já investido, resultado ainda não. ROIC baixo aqui é fase, não
  qualidade — o teste correto é o ROIC do ativo maduro, não o consolidado.
- **Bancos e seguradoras** não comportam o ROIC no formato acima: a dívida é matéria-prima, não
  financiamento. Use ROE, ROA, NIM e índice de Basileia.
- **Stock-based compensation não deduzida** infla NOPAT e ROIC em empresas de tecnologia.
- **Média com denominador distorcido**: se houve aumento de capital no meio do ano, a média simples
  de abertura e fechamento subestima o capital efetivamente empregado.

## Brazilian Context

- **JCP deprime o ROE contábil.** Juros sobre Capital Próprio são despesa financeira dedutível, o
  que reduz o IR **e** o lucro líquido. Empresa que distribui via JCP mostra ROE menor que a que
  distribui via dividendo, com a mesma rentabilidade econômica. Para comparação justa, some o JCP de
  volta ao lucro líquido — ou compare pelo ROIC, que passa pelo EBIT e não é afetado.
- **Alíquota efetiva longe da nominal.** Os 34% combinados de IR e CSLL raramente são o que a empresa
  paga: JCP, subvenção de ICMS, Lei do Bem e incentivos regionais (SUDENE/SUDAM) frequentemente
  levam a alíquota efetiva para 20-26%. Usar a nominal no NOPAT subestima o ROIC de forma
  sistemática.
- **CDI alto infla o ROE de empresa com caixa.** A receita financeira sobre um caixa grande entra no
  lucro líquido e sobe o ROE sem qualquer contribuição operacional. O ROIC calculado com caixa
  excedente **excluído** do capital investido e com NOPAT partindo do EBIT não sofre essa distorção
  — é uma das razões práticas de preferi-lo no Brasil.
- **Custo de capital alto muda a régua.** Com WACC nominal na faixa de 13-18%, o critério de
  Greenblatt/Buffett de ROIC acima de 15% não é "excelente" — é aproximadamente o mínimo para não
  destruir valor. Empresas brasileiras com spread consistentemente positivo são poucas, e é
  justamente essa escassez que sustenta o prêmio de múltiplo delas.
- **Inflação e ativo antigo.** Imobilizado registrado a custo histórico em regime de inflação
  persistente subavalia o capital investido e **superestima** o ROIC de empresas capital-intensivas
  com parque antigo. Onde isso for material, o teste é comparar com o custo de reposição.

## Formulas

```
# Retornos
ROE   = Lucro Líquido / PL Médio
ROA   = Lucro Líquido / Ativo Total Médio
ROIC  = NOPAT / Capital Investido Médio
NOPAT = EBIT × (1 − alíquota efetiva)

# Capital investido (pelo financiamento)
CI = PL + Dívida onerosa + Minoritários − Caixa não operacional

# Capital investido (pela aplicação)
CI = Capital de giro operacional + Imobilizado + Intangíveis + Direito de uso − Caixa excedente

# DuPont 3 fatores
ROE = (LL/Receita) × (Receita/Ativo) × (Ativo/PL)

# DuPont 5 fatores
ROE = (LL/LAIR) × (LAIR/EBIT) × (EBIT/Receita) × (Receita/Ativo) × (Ativo/PL)

# Criação de valor
Spread = ROIC − WACC
EVA    = (ROIC − WACC) × Capital Investido

# Crescimento sustentável
g_sustentável = ROIC × Taxa de reinvestimento
Taxa de reinvestimento = (Capex − D&A + ΔWC) / NOPAT

# Ajuste JCP (comparabilidade)
ROE ajustado = (Lucro Líquido + JCP bruto) / PL Médio
```

## References

- Koller, Goedhart, Wessels — *Valuation*, cap. sobre ROIC, invested capital e fade rates
- Damodaran, A. — *Investment Valuation*, cap. sobre measures of return
- Greenblatt, J. — *The Little Book That Beats the Market* (ROIC como um dos dois critérios)
- Penman, S. — *Financial Statement Analysis and Security Valuation*, cap. 11-12 (análise de
  rentabilidade e alavancagem)
- Assaf Neto, A. — *Estrutura e Análise de Balanços*
- Stern Stewart — literatura original de EVA
- CPC 06 (R2) / IFRS 16 — Arrendamentos, para o ajuste de capital investido

## Related

- [[key-ratios]] — Referência central de indicadores, com DuPont numérico completo
- [[wacc]] — O custo de capital contra o qual o ROIC é medido
- [[moats]] — O que sustenta ROIC acima do WACC ao longo do tempo
- [[income-statement]] — Origem do EBIT, das margens e da alíquota efetiva
- [[balance-sheet]] — Origem do PL, da dívida e do capital investido
- [[cash-flow-statement]] — Checagem de que o retorno vira caixa
- [[red-flags-accounting]] — Retorno alto demais para o setor como sinal de alerta
- [[capital-allocation]] — ROIC como critério de decisão de reinvestimento
- [[warren-buffett-framework]] — ROIC alto e persistente como filtro de qualidade
- [[ratio-formulas]] — Fórmulas consolidadas
