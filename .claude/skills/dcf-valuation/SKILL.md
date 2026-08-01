---
name: dcf-valuation
description: Executa o valuation de uma empresa por fluxo de caixa descontado. Invoque quando for preciso chegar a um valor intrínseco ou a um preço-alvo por DCF — cobertura nova, revisão de tese, checagem de um modelo alheio ou o passo de valuation de um relatório de equity. Cobre coleta e datação das demonstrações, projeção explícita com premissa justificada uma a uma, casamento entre fluxo e taxa (FCFF/WACC, FCFE/Ke), montagem do WACC, valor terminal com teto em `g`, matriz de sensibilidade obrigatória e cenário bear com perda máxima.
---

# DCF Valuation — executar o valuation

Esta skill é **rígida**. Os passos são numerados, obrigatórios e em ordem. A ordem não é
estilística: escolher a taxa depois de ver o preço que sai, ou justificar a premissa depois de
olhar o resultado, produz um número que sempre confirma a expectativa de quem montou o modelo.

Esta skill **não explica DCF**. O que é FCFF, por que o valor terminal domina e como o WACC se
monta está em [[valuation-dcf]] e [[wacc]] — leia lá. Aqui estão os passos, a ordem e os
critérios de saída.

Vale tanto para montar um valuation novo quanto para **revisar um que já existe**. Na revisão,
cada passo vira uma pergunta respondida com a premissa escrita do modelo — não com a confiança
de quem o montou.

---

## Condição de parada — leia antes de tudo

**Se a empresa for financeira — banco, seguradora, resseguradora, financeira, corretora — pare
aqui. Não rode DCF.**

Não é conservadorismo, é inaplicabilidade. Em empresa financeira a estrutura de capital **é o
negócio**: dívida é matéria-prima, não financiamento. Isso quebra o DCF em dois pontos ao mesmo
tempo:

- **FCFF não existe** de forma econômica. Capex e capital de giro não descrevem o
  reinvestimento; o que restringe o crescimento é capital regulatório, não máquina.
- **WACC não é definível.** Ele pressupõe separar capital que financia de capital que opera —
  separação que num banco não existe. O `D/V` de um banco não é escolha de estrutura de capital,
  é balanço operacional.

O que usar no lugar:

| Caminho | Quando | Onde ler |
|---|---|---|
| Múltiplos de equity — **P/VPA contra ROE**, P/L | Padrão para banco e seguradora | [[valuation-multiples]] |
| Dividend discount / fluxo ao acionista descontado por `Ke` | Quando o payout é estável e o capital regulatório está folgado | [[valuation-dcf]] (seção FCFE) e [[wacc]] (custo de equity) |

O par P/VPA × ROE é o que carrega informação aqui: com custo de equity `Ke` e crescimento `g`,
`P/VPA justo ≈ (ROE − g)/(Ke − g)`. Banco que negocia a 2,0x book com ROE de 12% e `Ke` de 15%
está caro, e isso se enxerga sem nenhum fluxo projetado.

**Casos de fronteira** — holding com braço financeiro relevante, varejista com carteira de
crédito própria, empresa com banco cativo: separe os segmentos e avalie cada um pelo método que
lhe cabe. Não rode um DCF consolidado e chame de conservador.

---

## Passos

### 1. Leia as duas notas antes de abrir a planilha

[[valuation-dcf]] e [[wacc]]. As duas, inteiras, **antes** de coletar dado.

Não é ritual. Os erros que esta skill mais previne — descontar FCFE pelo WACC, usar peso
contábil, aplicar `(1−T)` duas vezes, misturar fluxo real com taxa nominal — são erros de
consistência, não de estimativa. Quem os comete não erra a conta; erra o desenho, e a conta sai
perfeita a partir de um desenho errado. Nenhuma sensibilidade posterior corrige isso, porque a
tabela inteira herda o mesmo defeito.

### 2. Colete 5 anos de demonstrações — com fonte e data escritas

DRE, balanço e fluxo de caixa dos últimos 5 exercícios, mais os trimestres do ano corrente.
Ver [[financial-statements]] e [[cash-flow-statement]] para o que extrair de cada uma.

Para cada bloco de dado, registre no relatório:

| Registro | Por quê |
|---|---|
| **Fonte** — Formulário de Referência, ITR/DFP na CVM, release da companhia, provedor | Provedor e demonstração auditada divergem em ajustes; a divergência precisa ser rastreável |
| **Data de extração** | Preço, dívida e número de ações se movem; um valuation sem data não é reproduzível |
| **Número de ações** — total, e o critério (básico ou diluído) | Diluição por opções e debêntures conversíveis muda o preço por ação sem mudar o valor da empresa |
| **Dívida líquida** — bruta, caixa, e o que foi tratado como caixa excedente | É a ponte de EV para equity value; erro aqui não aparece em lugar nenhum do modelo |
| **Itens não recorrentes** identificados e o tratamento dado a cada um | Normalizar é decisão do analista, e decisão declarada é decisão contestável |

Se algum dado veio de provedor sem conferência contra a demonstração, isso é **limitação
declarada agora**, no documento — não uma ressalva descoberta depois.

### 3. Projete o FCFF explícito por 5 a 10 anos — cada premissa justificada por escrito

Uma linha de justificativa por premissa, no relatório, ao lado do número. Sem exceção:

- **crescimento de receita**, ano a ano — ancorado em volume, preço, share ou capacidade
  instalada, não em "CAGR histórico projetado adiante";
- **margem operacional** — e para onde ela converge, com o motivo da convergência;
- **capex** — manutenção e expansão separados, contra o D&A e contra o histórico;
- **variação de capital de giro** — em dias de ciclo, não em percentual solto da receita;
- **alíquota efetiva** — e por que ela difere da nominal, se diferir.

O horizonte explícito termina quando o negócio atinge **estado estacionário**: crescimento,
margem e reinvestimento estáveis. Empresa em maturação exige horizonte mais longo. Encurtar o
explícito não simplifica o modelo — empurra para o valor terminal a parte do valor que você não
quis projetar, e o passo 6 mostra o que isso custa.

**Uma premissa que você não consegue defender em voz alta, sem consultar a planilha, não é
premissa — é o valuation inteiro.** É ela que produz o resultado, e ninguém vai auditá-la
depois porque ela está enterrada numa célula. Se não consegue defender, corte a linha e projete
algo que consiga.

Teste de sanidade obrigatório antes de seguir: a projeção implica que a empresa ganha share, que
o mercado cresce, ou as duas coisas? Some o share implícito ao dos concorrentes. Se a soma passa
de 100%, a projeção já está errada e o resto do modelo não importa. As armadilhas clássicas —
hockey stick, capex abaixo do D&A, working capital ignorado — estão listadas em [[valuation-dcf]].

### 4. Case o fluxo com a taxa — **antes** de calcular qualquer coisa

Escreva no topo do modelo qual fluxo está sendo projetado e qual taxa o desconta:

| Fluxo | Taxa | Resultado |
|---|---|---|
| **FCFF** | **WACC** | Enterprise Value → subtrair dívida líquida → equity value |
| **FCFE** | **Custo de equity (`Re`)** | Equity value direto |

Trocar o par não gera erro, alerta nem número absurdo: gera um preço-alvo **silenciosamente
errado**, com sinal previsível. FCFE descontado por WACC conta o benefício da dívida duas vezes
— uma no fluxo, que já subtraiu juros, e outra na taxa, que já é menor pelo tax shield — e
**infla** o valor tanto mais quanto mais alavancada a empresa. O inverso subestima. A mecânica
está em [[wacc]].

No mesmo passo, fixe e escreva o **regime**: nominal ou real, e em qual moeda. Fluxo e taxa no
mesmo regime, sempre. Fluxo real descontado por taxa nominal é o erro que menos deixa rastro na
planilha e o que mais destrói o resultado.

### 5. Monte o WACC, item por item

Cada componente com o número, a fonte e a data. Metodologia completa em [[wacc]]; derivação do
custo de equity em [[quant/03-factor-models/capm]].

1. **`Rf`** — no prazo e na moeda dos fluxos. NTN-B longa para modelo real, prefixado longo para
   nominal. Não é a Selic: descontar fluxo de dez anos por taxa overnight é erro de casamento de
   prazo.
2. **`β`** — setorial, desalavancado pela estrutura do setor e realavancado pela estrutura-alvo
   da empresa. Beta de regressão de ação ilíquida com dois anos de histórico é ruído; se for o
   único disponível, declare isso.
3. **`ERP` + prêmio de risco-país** — com a data do prêmio usado, porque ele abre em estresse
   fiscal sem que nada tenha mudado na empresa. Some risco-país **uma vez só**: se o `Rf`
   escolhido já embute risco soberano, dizer isso e não somar de novo.
4. **`Rd` marginal, depois de imposto** — a taxa de captação **de hoje**, não despesa financeira
   sobre dívida média. A média histórica carrega contrato antigo, linha subsidiada de BNDES e
   outro regime de juros, e subestima sistematicamente.
5. **Pesos a valor de mercado.** Nunca patrimônio líquido contábil. O viés tem sinal conhecido:
   empresa boa negocia acima do book, o peso contábil dá peso demais à dívida barata e produz
   WACC baixo demais — logo preço-alvo alto demais.
6. **Trajetória**, se a estrutura de capital mudar ao longo do período explícito. WACC constante
   numa empresa que está desalavancando por decisão explícita é inconsistente com a própria
   projeção do passo 3.

Teste de sanidade: o WACC está entre o custo de dívida e o custo de equity? Um WACC nominal em
BRL abaixo da Selic corrente é quase sempre erro aritmético — ver [[selic-and-monetary-policy]].

### 6. Valor terminal — `g` **não pode** exceder o crescimento nominal de longo prazo do PIB

Sem exceção, sem "a empresa é especial", sem "só um pouco acima". `g` acima do crescimento da
economia implica que a empresa se torna, no limite, maior que a economia inteira — a matemática
não admite outra leitura, e a única questão é em quantas décadas. Referência de crescimento de
longo prazo em [[gdp-and-growth]].

Consistência de regime: modelo em termos **reais** usa `g` real; modelo **nominal** usa `g`
nominal, isto é, crescimento real de longo prazo mais inflação de longo prazo. Comparar um `g`
nominal contra um PIB real é como o teto é burlado sem ninguém perceber.

**O valor terminal costuma ser 60% a 80% do valor total.** A consequência prática é que este
único input decide o valuation, e o trabalho detalhado dos passos 2 e 3 responde pela minoria do
resultado. Duas obrigações daí:

- **Reporte o percentual do valor que está no TV.** Acima de 80%, o modelo diz que você não
  projetou o negócio — apenas escolheu uma perpetuidade. Volte ao passo 3 e alongue o horizonte
  explícito.
- **Cheque o múltiplo implícito da perpetuidade**: `TV / FCFF_{n+1} = 1/(WACC − g)`. Traduza-o
  para EV/EBITDA de saída e compare com o múltiplo de peers em [[valuation-multiples]] e com o
  histórico da própria empresa. Um implícito muito acima do que o mercado paga hoje pelo setor
  maduro é a premissa de moat entrando escondida no modelo — se ela existe, ela vai declarada, e
  o teste está em [[moats]].

Método alternativo — múltiplo de saída — é aceitável, com o múltiplo justificado. Rodar os dois
e comparar é o melhor uso: divergência grande entre Gordon e múltiplo de saída significa que uma
das duas premissas está fora de lugar.

### 7. Matriz de sensibilidade WACC × `g` — obrigatória

Não é anexo, é o resultado. Grade mínima de **5 × 5**: WACC em passos de 0,5 pp cobrindo ±1 pp
em torno do central, `g` em passos de 0,25 pp cobrindo ±0,5 pp. Nas células, o preço justo por
ação; opcionalmente o upside contra o preço corrente.

Reporte junto com a matriz:

- o **intervalo** de preço justo entre o canto mais conservador e o mais agressivo;
- **onde o preço de mercado cai dentro da matriz** — isto é, qual par (WACC, `g`) o mercado está
  precificando hoje. Essa é a pergunta mais informativa do valuation inteiro: ela transforma "a
  ação está barata" em "o mercado está exigindo WACC de 18% ou assumindo `g` de 1%, e eu discordo
  por este motivo";
- a variável à qual o resultado é **mais sensível**, medida na própria matriz.

**Um DCF apresentado como número único é enganoso**, mesmo quando o número está certo. A falsa
precisão de "preço justo de R$ 27,43" esconde que o intervalo defensável vai de R$ 19 a R$ 38, e
quem lê o report toma decisão de alocação sobre a precisão aparente, não sobre a dispersão real.
A dispersão **é** o resultado. Exigência da casa em `finance/CLAUDE.md`, não escolha editorial.

Se uma premissa operacional do passo 3 move o resultado mais que o WACC — tipicamente margem
terminal ou capex —, rode a segunda matriz sobre ela. A matriz WACC × `g` é o piso, não o teto.

### 8. Cenário bear com perda máxima estimada

Não é o canto inferior da matriz do passo 7. É um **mundo descrito**: o que precisa acontecer com
o negócio — não com a taxa de desconto — para a tese estar errada.

Escreva:

- o **evento ou a deterioração** concreta: margem que comprime por qual motivo, volume que cai
  por qual causa, contrato que não renova, entrante que chega, regulação que muda;
- as **premissas do passo 3 refeitas** sob esse mundo, não apenas um WACC maior;
- o **preço justo** resultante e a **perda máxima estimada** contra o preço de entrada, em
  percentual e em reais;
- o **indicador que antecipa** esse cenário — o número a monitorar que avisa antes do preço.

Um bear que só mexe na taxa de desconto não é cenário bear; é a mesma tese com outro humor.

---

## Nunca

- **Nunca apresente um DCF como número único.** Sem a matriz de sensibilidade, o que foi
  entregue é falsa precisão, e a decisão de alocação é tomada sobre uma exatidão que não existe.
- **Nunca use `g` acima do crescimento nominal de longo prazo do PIB.** Não há empresa que
  justifique a exceção, porque a exceção implica ultrapassar a economia inteira.
- **Nunca desconte FCFE pelo WACC** — nem FCFF pelo custo de equity. O erro não gera alerta
  nenhum: gera um preço-alvo errado com aparência de certo.
- **Nunca omita a sensibilidade** porque o resultado "ficou robusto". Robustez é uma afirmação
  sobre a matriz, e ela só pode ser feita depois de a matriz existir.
- **Nunca carregue uma premissa que você não consegue defender em voz alta.** Se ela precisa da
  planilha aberta para ser explicada, ela não foi decidida — foi herdada.
- **Nunca rode DCF de banco ou seguradora.** Ver condição de parada.
- **Nunca use peso contábil no WACC** nem `Rd` histórico. Os dois erros empurram o valor para
  cima, e empurram na mesma direção.

---

## Critérios de saída

- [ ] A empresa **não** é financeira — ou o método foi trocado conforme a condição de parada.
- [ ] [[valuation-dcf]] e [[wacc]] lidas antes da coleta.
- [ ] 5 anos de demonstrações coletados, com **fonte e data** de extração escritas, mais número
      de ações, dívida líquida e tratamento dos não recorrentes.
- [ ] Projeção explícita de 5 a 10 anos com **uma justificativa escrita por premissa**.
- [ ] Par fluxo × taxa declarado no topo do modelo, e o regime (nominal/real, moeda) fixado.
- [ ] WACC montado item por item — `Rf`, `β`, `ERP`, risco-país, `Rd` marginal após imposto,
      pesos a mercado — com fonte e data de cada um, e teste de sanidade feito.
- [ ] `g` **igual ou inferior** ao crescimento nominal de longo prazo do PIB, no mesmo regime do
      fluxo.
- [ ] Percentual do valor no TV reportado, e múltiplo implícito da perpetuidade confrontado com
      peers.
- [ ] **Matriz de sensibilidade WACC × `g`** de 5 × 5, com o intervalo de preço justo e o par
      que o mercado está precificando.
- [ ] Cenário bear descrito como mundo, com perda máxima estimada e o indicador que o antecipa.

Faltando qualquer item, o valuation não sai como recomendação. Ele volta para o passo que falhou.

---

## Entregável

Repositório privado, nunca este vault:

```
reports/equity/<ticker>-<YYYY-MM-DD>.md
```

Quando o DCF é o passo de valuation de uma cobertura, ele **não vira arquivo próprio**: entra na
seção de valuation do relatório produzido pela skill `equity-initiation`, no mesmo caminho.

Conhecimento durável que sair do trabalho — uma armadilha setorial de projeção, um tratamento
contábil recorrente, uma fonte de dado melhor — **sobe para este vault** como nota nova, e o
índice do domínio ganha uma linha.
