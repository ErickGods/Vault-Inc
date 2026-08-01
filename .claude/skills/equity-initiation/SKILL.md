---
name: equity-initiation
description: Produz um relatório de início de cobertura de uma ação — o entregável de ponta a ponta desta casa. Invoque quando for preciso assinar uma recomendação de compra, venda ou manutenção sobre uma empresa ainda não coberta, ou reabrir cobertura encerrada. Cobre tese falseável em uma frase, modelo de negócio, teste de moat com evidência, qualidade dos números, valuation por dois métodos com a divergência explicada, cenário bear com perda máxima, riscos nomeados especificamente, preço-alvo com horizonte e margem de segurança, e disclosures.
---

# Equity Initiation — início de cobertura

Esta skill é **rígida**. Os passos são numerados, obrigatórios e em ordem. A ordem carrega
conteúdo: quem faz valuation antes de entender como a empresa ganha dinheiro está calibrando uma
planilha, não avaliando um negócio, e quem escreve a recomendação antes do cenário bear já
decidiu o que quer concluir.

O produto é o primeiro entregável de ponta a ponta desta casa — **um documento assinado**, sobre
o qual alguém aloca patrimônio. A recomendação "não cobrir" é um desfecho legítimo e barato;
recomendação mal fundamentada é o produto mais caro que esta casa pode emitir.

Esta skill **não ensina análise fundamentalista**. O que é moat, o que o spread ROIC−WACC
significa e como se lê um múltiplo está nas notas do vault, citadas em cada passo. Aqui estão os
passos, a ordem e os critérios de saída.

---

## Condição de parada — leia antes de tudo

**Se a tese depender de uma afirmação quantitativa, não a afirme. Abra um Cross-Desk Request
para `quant-researcher` e siga sem ela.**

Afirmação quantitativa é toda regularidade estatística sobre uma população de ativos:

| Frase que dispara a parada | Por que é quantitativa |
|---|---|
| "Empresas com ROIC acima de 15% superam o índice." | Afirmação sobre uma população, testável, e nunca testada aqui |
| "Esse setor sempre se recupera depois do fim do ciclo de alta." | Regularidade temporal, com universo e período implícitos |
| "Ação com dividend yield alto cai menos em queda de mercado." | Comparação condicional entre grupos |
| "Small cap rende mais depois de corte de juros." | O caso de manual |

**Esta casa não produz evidência estatística.** Ela produz análise fundamentalista, julgamento
de qualidade de negócio e adequação a mandato. Afirmar sem passar pela casa quant é vender
anedota como evidência, com a assinatura da casa embaixo — e a assinatura é justamente o que
distingue este documento de um comentário.

O Cross-Desk Request **não trava a cobertura**. Ele vai para
`cross-desk/<YYYY-MM-DD>-finance-quant.md` no repositório privado, e o relatório segue com a
afirmação marcada como pendente de verificação — nunca como premissa da tese. A resposta pode
ser que o sinal não existe; se a tese não sobrevive a isso, ela dependia do sinal, e isso
precisava aparecer antes de o cliente comprar.

Distinção que importa na prática: **fato sobre a empresa não dispara a parada.** "O ROIC desta
empresa foi de 18% nos últimos cinco anos" é observação verificável na demonstração — é o passo
4. "Empresas com ROIC de 18% superam o índice" é hipótese sobre uma população — é a casa quant.
A primeira sustenta a tese; a segunda, se usada, a contamina.

---

## Passos

### 1. Escreva a tese em uma frase falseável

Uma frase. Antes de qualquer planilha, e no topo do documento.

A frase precisa nomear **o que o mercado está errando** e **o que fará o erro se corrigir**. Se
não há erro identificado, não há tese — há concordância com o preço, e concordar com o preço não
justifica um relatório.

| Não é tese | É tese |
|---|---|
| "É uma boa empresa com bom management." | "O mercado precifica a margem EBITDA convergindo para 18% até 2028; a expansão de capacidade contratada sustenta 23%, e cada trimestre de margem acima de 20% fecha o desconto." |
| "Está barata em relação ao setor." | "Negocia a 6x EV/EBITDA contra 11x dos peers por causa da alavancagem de 3,2x; o cronograma de amortização leva a 1,5x até 2027 sem nova captação, e o desconto de alavancagem não se sustenta." |
| "Setor com boas perspectivas." | "A tese é do setor, não da empresa — não cobrir individualmente." |

Teste: **existe um número futuro, observável, que faria você abandonar a tese?** Escreva-o
agora, junto da frase. Sem isso a cobertura não tem critério de revisão, e uma tese sem critério
de revisão nunca é abandonada — só reinterpretada a cada trimestre.

"É uma boa empresa" não é tese. É um adjetivo à espera de uma planilha que o confirme.

### 2. Descreva o negócio — como a empresa ganha dinheiro, e de quem

Antes de qualquer indicador. Escreva com números, não com o texto institucional da companhia:

- **De onde vem a receita**: por linha de produto, por geografia, por canal, com o percentual de
  cada uma. Se a abertura não é divulgada, isso é uma limitação declarada.
- **Quem paga** — e qual a concentração real. Percentual dos cinco maiores clientes. Contrato ou
  spot. Prazo médio e data das próximas renovações.
- **Como se forma o preço**: contrato indexado, tabela, leilão, commodity, regulação tarifária.
  Quem tem o poder de reajustar, e com que frequência.
- **Onde vai o dinheiro**: estrutura de custo fixo contra variável, e o que acontece com a
  margem numa queda de 20% de volume.
- **O que consome caixa**: ciclo de conversão em dias e capex de manutenção contra o de
  expansão. Ver [[cash-flow-statement]] e [[key-ratios]].
- **Quem controla e como** — controlador, free float, tag along, classe de listagem, histórico
  de transação com parte relacionada. Ver [[brazilian-market-b3]].

Teste de suficiência: você consegue explicar, sem consultar o documento, **o que precisa
acontecer no mundo real para a receita subir 10%**? Se não consegue, o passo não terminou, e
todo o resto será calibração de planilha sobre um negócio que você não entendeu.

### 3. Setor e posição competitiva — aplique o teste de moat, não afirme o moat

Estrutura do setor primeiro: concorrentes nomeados com share, poder de barganha de fornecedor e
de cliente, ameaça de entrante e de substituto, ciclo de preço se houver.

Depois, **o teste de [[moats]]**, que é o passo em que quase toda cobertura falha por atalho:

1. **Monte a série de 10 anos do spread `ROIC − WACC`.** Esta é a assinatura mensurável. Sem
   spread positivo e persistente, não há moat — por mais convincente que seja a narrativa, e
   independentemente do que a apresentação institucional afirme.
2. **Nomeie a fonte** entre as cinco — efeito de rede, custo de troca, vantagem de custo, ativo
   intangível, escala eficiente — e **aplique o teste específico daquela fonte**, que está na
   nota. Cada fonte tem um teste próprio e um falso positivo próprio.
3. **Escreva a evidência e de onde ela veio**: churn e NRR do release, market share do relatório
   setorial com o nome do provedor, ticket médio contra o IPCA, margem bruta contra o peer nomeado.

O que **não** é evidência de moat: a empresa dizer que tem; a marca ser conhecida; o setor ter
barreira regulatória genérica; margem alta num único ano; a ação ter subido.

Se nenhuma das cinco fontes sobrevive ao teste, a conclusão é **"sem moat identificável"** — não
"moat difuso" nem "moat em construção". Isso não impede recomendação de compra; impede assumir
spread positivo no valor terminal do passo 5. A assimetria está em [[moats]]: afirmar moat
inexistente autoriza múltiplo alto, `g` generoso e horizonte longo ao mesmo tempo, e é o erro
caro.

Escreva também a **hipótese de morte do moat**: qual evento específico o mata, e qual indicador
o antecipa. Sem isso, o monitoramento da cobertura vira torcida.

### 4. Qualidade dos números — antes de projetá-los

Não adianta projetar com precisão um lucro que não existe.

**a) Retorno sobre capital — [[roe-roic]].** Série de 10 anos de ROIC contra o WACC do período.
Reporte o spread, sua **duração** e sua **velocidade de erosão**. Abra o ROE por DuPont: ROE alto
que vem de alavancagem não é qualidade, é risco com outro nome. Confira o tratamento de
intangível de aquisição, que infla o capital investido e deprime o ROIC de quem cresce comprando
— o moat pode existir e a métrica não mostrar.

**b) Sinais de manipulação — [[red-flags-accounting]].** Passe o checklist inteiro da nota, e
reporte pelo menos:

- **divergência entre lucro e caixa operacional** ao longo de 5 anos — o sinal mais informativo
  e o mais barato de calcular;
- **contas a receber crescendo acima da receita**, e estoque acima do CMV;
- **capitalização de despesa** e mudança de critério contábil ou de estimativa;
- **transações com partes relacionadas**;
- **qualidade da opinião de auditoria** — ressalva, ênfase, troca de auditor, atraso de entrega.

Um red flag isolado é pergunta a fazer; um padrão de red flags é a tese. Se aparecer padrão,
**pare e escreva isso como a conclusão** — cobertura que documenta risco contábil é entrega, e
das mais valiosas que esta casa produz.

**c) Endividamento e liquidez.** Dívida líquida/EBITDA, cobertura de juros, cronograma de
amortização por ano, moeda e indexador da dívida, e o que acontece à cobertura num choque de
juros. Ver [[key-ratios]] e [[balance-sheet]].

### 5. Valuation por dois métodos — e **explique a divergência entre eles**

Nenhuma recomendação sai desta casa sem valuation explícita.

**a) DCF.** Invoque a skill `dcf-valuation` e siga todos os passos dela, inclusive a matriz de
sensibilidade WACC × `g` e a checagem do percentual do valor no valor terminal. Se a condição de
parada daquela skill disparar — banco, seguradora —, o método relativo vira o principal e o
segundo método passa a ser dividend discount ou P/VPA contra ROE.

**b) Múltiplos.** Por [[valuation-multiples]]: peers **verdadeiros** — mesmo setor, porte,
geografia e modelo de negócio, nomeados um a um — mediana e quartis, mais a série histórica de
múltiplo da própria empresa. Justifique prêmio ou desconto contra o grupo pelo que o passo 3
mostrou, não pela conveniência do resultado.

**c) A divergência é o passo, não os dois números.** Compare os dois preços justos e explique a
diferença:

> Dois métodos que concordam são evidência fraca — múltiplos de peers e DCF compartilham
> premissas de crescimento e risco, e concordância frequentemente significa apenas que a mesma
> expectativa entrou pelas duas portas. Dois métodos que **discordam** carregam informação: a
> divergência aponta exatamente qual premissa está fazendo o trabalho.

Trate a divergência assim:

| Padrão observado | O que investigar |
|---|---|
| DCF acima dos múltiplos | O modelo assume crescimento, margem ou duração de spread que o mercado não paga hoje pelo setor. Nomeie a premissa e defenda-a — ou é ela que está errada, e é ali que está a tese. |
| Múltiplos acima do DCF | O setor negocia acima do que os fluxos justificam, ou o WACC do modelo está alto demais. Verifique risco-país e beta antes de concluir que o setor está caro. |
| Divergência acima de 30% | Não escolha o número que agrada. Escreva a premissa responsável e leve-a para a matriz de sensibilidade do passo 7 do `dcf-valuation`. |

Nunca calcule os dois e reporte a média. A média apaga precisamente a informação que a
divergência produziu.

### 6. Cenário bear com perda máxima estimada

O cenário bear do passo 8 do `dcf-valuation` é o **insumo** deste passo, não um segundo cenário:
lá ele produz o preço justo sob deterioração; aqui ele ganha o mundo descrito, a perda máxima
contra o preço de entrada e a consequência de dimensionamento. Um único bear, escrito uma vez.

Um mundo descrito, não o canto ruim da planilha. O que precisa acontecer **com o negócio** para
a tese estar errada:

- o evento ou a deterioração concreta — margem, volume, contrato, entrante, regulação,
  refinanciamento;
- as premissas operacionais refeitas sob esse mundo;
- o **preço justo** resultante e a **perda máxima estimada** contra o preço de entrada, em
  percentual e em reais;
- o **indicador antecedente**: o número que avisa antes de o preço avisar.

Se a perda máxima estimada não muda o dimensionamento da posição, o cenário bear foi escrito
para cumprir tabela. Ver [[capital-allocation]] para a ligação com sizing.

### 7. Riscos nomeados especificamente

Risco genérico é ruído com aparência de diligência: ele nunca é acionável, nunca é monitorado e
nunca faz ninguém mudar de ideia. Cada risco desta seção precisa de **quatro elementos**:
o que é, **quantificado**, com **prazo**, e com o **indicador** que o antecipa.

| Não é risco | É risco |
|---|---|
| "Risco de mercado." | "Concentração de 40% da receita em um cliente com contrato vencendo em 2027; perda total dessa conta corta o EBITDA em 55% pela alavancagem operacional." |
| "Risco regulatório." | "Revisão tarifária em 2028 pode reduzir o WACC regulatório em até 150 bps, com impacto de R$ X no valor da concessão; a audiência pública abre em 2027." |
| "Risco cambial." | "62% do CPV é importado e 8% da receita é exportada; desvalorização de 20% do BRL comprime a margem bruta em 4,5 pp sem repasse." |
| "Risco de execução." | "R$ 2,1 bi de capex de expansão com entrada em operação prevista para 2027; atraso de 12 meses adia 30% da receita projetada e estoura o covenant de 3,0x no 2T28." |

Cubra no mínimo: concentração de cliente e de fornecedor, refinanciamento e covenants, câmbio,
regulação, execução de projeto, governança e sucessão, disrupção tecnológica, e o risco
específico da tese do passo 1. O que não se aplicar entra escrito como "não aplicável, por este
motivo" — omissão silenciosa e ausência de risco são indistinguíveis para quem lê.

### 8. Recomendação, preço-alvo, horizonte e margem de segurança — os quatro juntos

- **Recomendação**: comprar, manter ou vender. Palavra única, sem hedge verbal.
- **Preço-alvo**, saído do modelo do passo 5, com o método que o produziu declarado.
- **Horizonte** explícito — 12 meses, 24 meses. Preço-alvo sem horizonte não é falseável: nunca
  está errado, porque sempre pode "ainda acontecer". É a construção que faz uma cobertura ruim
  sobreviver anos.
- **Margem de segurança**, em percentual e nomeada como tal: a distância entre o preço justo e o
  preço de entrada recomendado. Ela **não** é o upside — é o quanto o modelo pode estar errado
  antes de o investidor perder dinheiro, e é função direta da dispersão da matriz de
  sensibilidade e da qualidade do moat do passo 3. Negócio sem moat identificável exige margem
  maior; o número escolhido vai justificado.
- **Gatilhos de revisão**: os eventos que reabrem a tese antes do fim do horizonte, incluindo o
  número falseável do passo 1.

### 9. Disclosures — conflitos e premissas-chave

Antes da conclusão no documento, nunca depois:

- **Conflito de interesse**: posição da casa, do analista ou de cliente no ativo; relação
  comercial com a companhia ou com o controlador; participação em oferta.
- **As três premissas que mais movem o resultado**, cada uma com o valor usado e o efeito de
  errá-la — tiradas da matriz de sensibilidade, não escolhidas por impressão.
- **Limitações de dado**: o que não foi divulgado, o que veio de provedor sem conferência contra
  a demonstração, e a data de extração.
- **Afirmações pendentes de Cross-Desk Request**, se a condição de parada disparou, com a data
  do pedido.
- **Aviso de suitability**: o relatório analisa o ativo, não o cliente. Adequação a perfil é
  decisão do IPS, e nenhum ativo entra em carteira só porque a cobertura recomendou compra.

---

## Estrutura do documento

Monte o relatório sobre [[stock-analysis-template]] — seções, tabelas e checklist final. Ver
[[templates]] para os demais entregáveis recorrentes da casa, e [[investment-checklist]] para a
due diligence completa que sustenta os passos 2 a 4.

Os passos acima não substituem o template: eles definem **o que precisa estar dentro de cada
seção** e em que ordem o trabalho é feito. O template define a forma; esta skill define o
conteúdo mínimo e os critérios de aceitação.

Todas as notas que sustentam a tese entram citadas por wikilink no corpo do relatório. Paráfrase
de memória não é citação, e tese que depende de algo que o vault não cobre tem um buraco a
declarar nos disclosures.

---

## Nunca

- **Nunca recomende sem valuation explícita.** Preço-alvo que não sai de um modelo declarado com
  sensibilidade é palpite formatado, e formatação é exatamente o que o faz parecer análise.
- **Nunca escreva risco genérico.** "Risco de mercado" não é acionável, não é monitorável e não
  muda decisão nenhuma — ocupa espaço fingindo diligência.
- **Nunca omita o cenário bear.** Relatório sem perda máxima estimada informa o upside e esconde
  o que o leitor está arriscando.
- **Nunca dê preço-alvo sem horizonte.** Sem prazo, a recomendação nunca pode ser avaliada, e
  cobertura que não pode errar não pode acertar.
- **Nunca afirme regularidade quantitativa sem Cross-Desk Request.** Ver condição de parada.
- **Nunca use um único método de valuation** quando os dois são aplicáveis, e nunca reporte a
  média dos dois no lugar da divergência.
- **Nunca afirme moat sem o teste e a evidência** de [[moats]]. Moat presumido é a premissa mais
  cara de um relatório, porque ela reaparece multiplicada no valor terminal.

---

## Critérios de saída

- [ ] Nenhuma afirmação quantitativa não verificada sustenta a tese — ou o Cross-Desk Request
      está aberto e a afirmação está marcada como pendente.
- [ ] Tese em **uma frase falseável**, com o número futuro que a derrubaria escrito ao lado.
- [ ] Modelo de negócio descrito com números: origem da receita, concentração de clientes,
      formação de preço, estrutura de custo, consumo de caixa e controle.
- [ ] Moat **testado** pelo roteiro de [[moats]], com fonte nomeada, evidência citada e hipótese
      de morte — ou a conclusão explícita de "sem moat identificável".
- [ ] Série de 10 anos do spread `ROIC − WACC`, com duração e erosão, e DuPont aberto.
- [ ] Checklist de [[red-flags-accounting]] percorrido, com a divergência lucro × caixa
      reportada.
- [ ] Valuation por **dois métodos**, com a skill `dcf-valuation` cumprida integralmente e os
      peers nomeados um a um.
- [ ] **Divergência entre os métodos explicada**, com a premissa responsável nomeada.
- [ ] Cenário bear descrito como mundo, com perda máxima estimada e indicador antecedente.
- [ ] Riscos com quantificação, prazo e indicador — nenhum risco genérico no documento.
- [ ] Recomendação com preço-alvo, **horizonte** e **margem de segurança** justificada.
- [ ] Disclosures de conflito, três premissas-chave, limitações de dado e data de extração.
- [ ] Documento estruturado sobre [[stock-analysis-template]], com as notas do vault citadas por
      wikilink.

Faltando qualquer item, o relatório não é assinado. Ele volta para o passo que falhou.

---

## Entregável

Repositório privado, nunca este vault:

```
reports/equity/<ticker>-<YYYY-MM-DD>.md
```

Cross-Desk Request aberto no caminho, quando houver:

```
cross-desk/<YYYY-MM-DD>-finance-quant.md
```

Conhecimento durável que sair da cobertura — um mecanismo setorial, uma armadilha contábil
recorrente, um teste de moat que se mostrou decisivo — **sobe para este vault** como nota nova, e
o índice do domínio ganha uma linha.
