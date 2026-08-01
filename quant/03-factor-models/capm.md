---
tags: [quant, factor-models, capm, asset-pricing]
aliases: [CAPM, Capital Asset Pricing Model, modelo de precificação de ativos]
house: quant
domain: factor-models
level: intermediate
status: active
created: 2026-07-29
updated: 2026-07-29
---

# CAPM — Capital Asset Pricing Model

O CAPM afirma que, em equilíbrio, o retorno esperado de um ativo é função exclusiva da sua exposição ao risco não-diversificável do mercado — todo o resto é risco específico, diversificável, e portanto não remunerado.

---

## A equação

```
E(Ri) = Rf + βi · (E(Rm) − Rf)
```

| Termo | O que é |
|-------|---------|
| `Rf` | Taxa livre de risco — retorno de um ativo sem risco de default nem de reinvestimento no horizonte considerado. |
| `βi` | Sensibilidade do ativo `i` ao movimento do mercado; quanto do risco sistemático ele carrega. |
| `E(Rm) − Rf` | Prêmio de risco de mercado (equity risk premium) — a compensação por carregar uma unidade de beta. |

A leitura operacional: o CAPM não precifica volatilidade, precifica **co-movimento**. Um ativo com σ de 60% e β de 0,2 tem retorno esperado baixo pelo modelo, por mais violento que seja o seu histórico isolado. É a mesma lógica de contribuição marginal ao risco que sustenta a [[portfolio-theory-mpt]] — o CAPM é a extensão daquele framework para o preço de um ativo individual.

---

## Beta

```
βi = Cov(Ri, Rm) / Var(Rm)
```

Em regressão: `βi` é o coeficiente angular de `Ri − Rf` contra `Rm − Rf`.

| Beta | Interpretação |
|------|---------------|
| `β = 1` | Move-se com o mercado. O ativo é o mercado, em termos de risco sistemático. |
| `β < 1` | Defensivo — amplitude menor que a do índice. Utilities, saneamento, energia elétrica regulada. |
| `β > 1` | Alavancado ao ciclo — amplifica movimentos do índice em ambas as direções. Cíclicas, small caps, alta alavancagem operacional ou financeira. |
| `β < 0` | Raro e geralmente artefato de amostra. Ouro e alguns hedges cambiais ocasionalmente exibem, mas raramente de forma estável. |

> [!warning] Beta não é um parâmetro, é uma estimativa
> O beta que você calcula é o beta **daquela janela**, **naquela frequência**, contra **aquele proxy de mercado**. Mude qualquer um dos três e o número muda materialmente. Petrobras estimada em janela de 60 meses mensais e em 252 dias diários dá betas diferentes; incluir ou não 2020 no período muda de novo. Erros-padrão de beta em ativos brasileiros com 60 observações mensais são frequentemente da ordem de 0,15–0,25 — ou seja, um beta reportado de 1,10 é estatisticamente indistinguível de 0,80.

Implicações práticas para quem vai usar o número:

- **Declare sempre janela, frequência e proxy.** Beta sem esses três é anedota, pela mesma regra que se aplica a qualquer resultado nesta casa.
- **Beta é não-estacionário.** Estrutura de capital, mix de receita e regime macro mudam o beta verdadeiro ao longo do tempo. Beta de 2015 não descreve a mesma empresa em 2026.
- **Shrinkage é o default sensato.** O ajuste de Blume (`β_ajustado = 2/3 · β_estimado + 1/3 · 1`) empurra a estimativa na direção de 1 e historicamente prevê o beta futuro melhor do que a estimativa crua. Use, e diga que usou.
- **Cuidado com iliquidez.** Ativos que não negociam todo dia produzem beta viesado para baixo por não-sincronia de preços. Correções tipo Dimson (somar betas de leads e lags) atenuam, mas o sinal continua ruim.

---

## O que o modelo assume

O CAPM não é uma descrição do mercado; é um teorema com hipóteses. Elas são fortes e todas falsas em algum grau:

1. **Mercados eficientes** — preços refletem toda a informação disponível e ninguém tem vantagem informacional persistente.
2. **Investidores racionais e avessos a risco** — decidem exclusivamente sobre média e variância, e sempre preferem menos variância para o mesmo retorno.
3. **Ausência de custos de transação e impostos** — rebalancear é gratuito, e o retorno bruto é o retorno do investidor.
4. **Tomar e emprestar ilimitadamente à taxa livre de risco** — qualquer investidor pode alavancar ou desalavancar a qualquer volume ao mesmo `Rf`.
5. **Expectativas homogêneas** — todos os participantes têm as mesmas estimativas de retorno, variância e covariância, e portanto todos identificam o mesmo portfólio tangente.

A hipótese (4) merece destaque porque é o ponto de falha empírico mais direto. Investidores reais enfrentam restrição de alavancagem; quem quer mais retorno e não pode alavancar compra ativos de beta alto em vez de alavancar o portfólio de mercado. Isso infla o preço de ativos de beta alto e achata a Security Market Line — que é exatamente o mecanismo que Frazzini e Pedersen usam para explicar a anomalia Betting Against Beta descrita em [[factor-investing]].

---

## Limitações

### (a) Crítica de Roll (1977)

O portfólio de mercado do CAPM é o portfólio de **todos os ativos com risco** — ações, títulos privados, imóveis, capital humano, empresas fechadas. Ele é inobservável. Qualquer teste do CAPM é, na prática, um teste conjunto de duas coisas: o modelo estar certo **e** o proxy escolhido ser mean-variance eficiente. Rejeitar o teste não diz qual das duas falhou.

A consequência é dura e frequentemente ignorada: o CAPM **não é estritamente testável**. Quando alguém diz "o CAPM foi rejeitado empiricamente", o que foi rejeitado é o CAPM condicionado ao S&P 500 ou ao Ibovespa como proxy. Isso não invalida o uso do modelo como ferramenta, mas invalida a pretensão de que ele é uma hipótese científica falseável no sentido estrito.

### (b) Beta explica pouco do corte transversal

Fama e MacBeth (1973) e depois Fama e French (1992) documentaram que, na seção cruzada, a relação entre beta e retorno médio é fraca e em alguns períodos praticamente plana. O R² de regressões cross-sectional de retorno contra beta é baixo. Pior: a relação empírica é mais plana do que a SML prevê — ativos de beta baixo entregam retorno acima do previsto e ativos de beta alto abaixo, o que é a assinatura da restrição de alavancagem descrita acima.

### (c) As anomalias de size e value

Duas características não relacionadas a beta previam retorno de forma sistemática:

- **Size** — empresas de baixa capitalização de mercado entregaram retorno acima do que o beta delas justificava.
- **Value** — empresas com alto book-to-market entregaram retorno acima do previsto, e o efeito era mais forte que o de size.

Essas duas anomalias são a motivação direta do modelo de três fatores de Fama-French (1993), que adiciona SMB e HML ao fator de mercado. A evolução completa — de um fator para três, quatro e cinco — está em [[factor-investing]].

> [!note] O que sobrevive
> O CAPM morreu como teoria descritiva e sobreviveu como **linguagem**. Beta continua sendo a forma padrão de decompor risco sistemático de específico, e o fator de mercado continua sendo o primeiro termo de todo modelo multifatorial. O erro é usá-lo como se fosse preditivo de retorno individual.

---

## No contexto brasileiro

### Proxy para `Rf`

| Proxy | A favor | Contra |
|-------|---------|--------|
| **Selic / CDI** | É a taxa efetivamente disponível, líquida diária, sem risco de marcação. Casa com o horizonte de rebalanceamento de estratégias quantitativas. | É taxa **nominal e de curtíssimo prazo**. Em fluxos longos (valuation, custo de capital), descontar com uma taxa de 1 dia é inconsistente com o horizonte do fluxo. |
| **NTN-B (Tesouro IPCA+)** | Taxa **real** e de prazo casado com o fluxo. É a escolha correta para custo de capital e para qualquer coisa descontada em termos reais. | Carrega prêmio de prazo e risco soberano brasileiro embutido; não é livre de risco em nenhum sentido estrito, e marca a mercado com volatilidade relevante. |

Regra de bolso da casa: **Selic/CDI para métricas de performance de curto prazo** (excesso de retorno, Sharpe de estratégia com rebalanceamento frequente); **NTN-B de prazo compatível para custo de capital e valuation**. O erro comum é misturar — calcular prêmio de risco com Selic e depois descontar fluxo de 10 anos com a mesma taxa. Qualquer que seja a escolha, declare-a junto do resultado.

### Proxy para `E(Rm)`

O **Ibovespa** é o default por falta de alternativa melhor com histórico. O IBrX-100 é preferível quando o estudo é sobre o mercado acionário amplo, porque tem critério de composição mais estável e menos dependente de liquidez pontual. Os problemas são estruturais:

- **Amostra curta e quebrada.** O histórico utilizável começa efetivamente após a estabilização do Plano Real (1994–1995). Antes disso, a hiperinflação e as trocas de moeda tornam a série econômica incomparável. São ~30 anos, e o desvio-padrão do prêmio de risco anual brasileiro é alto o bastante para que o erro-padrão da média histórica seja da ordem de vários pontos percentuais. Traduzindo: **o prêmio de risco brasileiro estimado a partir do histórico local é estatisticamente inútil como estimativa pontual.**
- **Rotatividade alta do índice.** A composição do Ibovespa muda de forma substancial ao longo de uma década — empresas entram, saem, deslistam. Regredir contra o índice implicitamente regride contra uma carteira cuja definição mudou.
- **Concentração pesada.** Vale, Petrobras e o bloco de bancos respondem historicamente por uma fração muito grande do índice. Um beta contra o Ibovespa é, em boa medida, um beta contra minério, petróleo e crédito bancário doméstico. Para uma empresa de consumo ou tecnologia, isso é um proxy ruim de "o mercado".

> [!tip] Prática recomendada
> Para custo de capital de empresa brasileira, o caminho mais defensável é montar em base americana (equity risk premium dos EUA, com histórico longo) e adicionar um prêmio de risco-país via spread do CDS soberano ou do EMBI+ Brasil, ajustado pela razão de volatilidade equity/bond. É o approach Damodaran. Estimar o ERP direto do Ibovespa produz números que oscilam entre negativo e absurdo dependendo da janela — teste isso antes de confiar em qualquer estimativa local.

Beta local também sofre: o beta de uma empresa contra o Ibovespa é contaminado pela concentração do índice. Para setores sub-representados, betas setoriais de comparáveis globais desalavancados e realavancados pela estrutura de capital brasileira costumam ser mais estáveis do que a regressão direta.

---

## Onde a casa usa

**1. Custo de capital próprio dentro do WACC.**
O CAPM é o método padrão para o componente de equity no custo médio ponderado de capital (WACC) usado em valuation por fluxo de caixa descontado. Não é usado por ser preciso — é usado por ser transparente e auditável: cada input (`Rf`, beta, prêmio) é declarável e contestável isoladamente. A alternativa (arbitrar uma taxa de desconto) não é auditável. A entrega deve trazer os três inputs explícitos e uma análise de sensibilidade do valor ao beta, porque a incerteza do beta domina a incerteza do resultado.

**2. Comparação ajustada a risco, ao lado do Sharpe.**
Beta e alpha de CAPM respondem "quanto do retorno desta estratégia é apenas exposição ao mercado?", enquanto o [[sharpe-ratio]] responde "quanto de retorno por unidade de volatilidade total?". As duas perguntas são diferentes e ambas são necessárias antes de aprovar qualquer coisa. Uma estratégia com Sharpe alto e beta 1,2 pode não ter alpha algum — é beta alavancado vendido como habilidade. Rodar a regressão de CAPM sobre a série de retornos do backtest é o primeiro filtro; se o alpha não sobrevive a custos de transação, a estratégia não passou.

**3. Insumo de dimensionamento.**
O beta agregado da carteira entra na decisão de exposição em [[position-sizing]] — carteira com beta 1,4 tem exposição efetiva ao mercado 40% maior do que o capital alocado sugere, e o limite de risco tem que refletir isso.

> [!warning] Cenário de falha
> O CAPM aplicado a um ativo individual falha de forma mais severa exatamente quando mais se precisa dele: em regime de estresse. Correlações convergem para 1, o beta estimado em período calmo subestima a perda realizada, e a decomposição entre risco sistemático e específico deixa de valer porque tudo vira sistemático. Não use beta de janela calma para dimensionar risco de cauda — para isso, ver [[position-sizing]] e testes de estresse dedicados.

---

## Como testar (protocolo mínimo)

Se a tarefa é verificar se o CAPM explica o corte transversal de um universo:

1. **Universo e período declarados.** Ex.: IBrX-100, composição point-in-time, 2010-01 a 2025-12, retornos mensais.
2. **Sobrevivência tratada.** Inclua deslistadas com o retorno de deslistagem. Sem isso, o teste está viesado e o resultado não vale.
3. **Primeiro estágio.** Estime beta por ativo em janela móvel (ex.: 36 ou 60 meses), sem usar dado futuro.
4. **Segundo estágio (Fama-MacBeth).** Regrida cross-section de retorno contra beta a cada mês; teste se a média das inclinações é significativa e se o intercepto é igual a `Rf`.
5. **Critério de rejeição declarado antes de rodar.** Ex.: "o CAPM é rejeitado se a inclinação média não for significativa a 5% ou se características (size, book-to-market) mantiverem poder explicativo após controlar por beta".
6. **Número de especificações testadas reportado.** Janelas, frequências e proxies alternativos contam como tentativas. Ver [[sharpe-ratio]] para o ajuste correspondente, e [[backtesting-basics]] para o protocolo geral.

---

## References

- Sharpe, William F. "Capital Asset Prices: A Theory of Market Equilibrium under Conditions of Risk." *Journal of Finance*, 1964.
- Lintner, John. "The Valuation of Risk Assets and the Selection of Risky Investments." *Review of Economics and Statistics*, 1965.
- Roll, Richard. "A Critique of the Asset Pricing Theory's Tests." *Journal of Financial Economics*, 1977.
- Fama, Eugene F. & MacBeth, James D. "Risk, Return, and Equilibrium: Empirical Tests." *Journal of Political Economy*, 1973.
- Fama, Eugene F. & French, Kenneth R. "The Cross-Section of Expected Stock Returns." *Journal of Finance*, 1992.
- Frazzini, Andrea & Pedersen, Lasse H. "Betting Against Beta." *Journal of Financial Economics*, 2014.
- Blume, Marshall E. "Betas and Their Regression Tendencies." *Journal of Finance*, 1975.
- Damodaran, Aswath. *Equity Risk Premiums: Determinants, Estimation and Implications* (atualização anual).

---

## Related

- [[factor-investing]] — o que veio depois, e por quê
- [[portfolio-theory-mpt]] — o framework de onde o CAPM deriva
- [[sharpe-ratio]] — a outra métrica de retorno ajustado a risco
- [[position-sizing]] — onde o beta agregado vira decisão de exposição
- [[momentum-strategies]] — anomalia que o CAPM não explica
- [[backtesting-basics]] — protocolo de validação
