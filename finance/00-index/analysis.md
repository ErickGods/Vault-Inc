---
house: finance
domain: analysis
type: index
updated: 2026-07-29
---

# Índice — Análise

## Fundamentalista — `finance/03-analysis/fundamental/`

| Nota | O que responde | Nível |
|---|---|---|
| [[valuation-dcf]] | Chegar a um preço justo por ação partindo do fluxo de caixa: os 7 passos de projetar receita a descontar, FCFF vs FCFE e qual taxa desconta cada um, valor terminal por Gordon ou múltiplo de saída, ponte de Enterprise Value para Equity Value. Alerta que 60-80% do valor mora no terminal e exige tabela de sensibilidade em WACC e g. Traz os ajustes brasileiros — NTN-B longa como taxa livre de risco em vez da Selic, prêmio de risco-país de 200-400 bps, histórico curto que dificulta estimar beta. | advanced |
| [[wacc]] | Montar a taxa que desconta o FCFF e conseguir defendê-la: cada termo de `(E/V)×Re + (D/V)×Rd×(1−T)`, custo de equity por CAPM com beta setorial desalavancado e realavancado, custo de dívida **marginal** e não histórico, pesos a valor de mercado. Mostra em números o que o peso contábil faz com o valor terminal, por que o WACC desconta FCFF e nunca FCFE, e os ajustes brasileiros — NTN-B ou prefixado longo como `Rf` em vez da Selic, prêmio de risco-país, dívida curta e indexada a CDI que move o WACC junto com o ciclo monetário. | advanced |
| [[valuation-multiples]] | Avaliar por comparação sem cair nas armadilhas do método: quando usar múltiplo de EV em vez de múltiplo de equity (alavancagens diferentes), P/L, earnings yield, PEG, EV/EBITDA e o P/L justificado de Gordon. Traz o processo de seleção de peers, a tabela de múltiplos típicos por setor no Brasil e os erros que invalidam a conta — cíclica no pico do ciclo, lucro não-recorrente, EBITDA ajustado, JCP distorcendo comparação internacional. | intermediate |
| [[warren-buffett-framework]] | Julgar qualidade de negócio antes de preço: os 4 filtros, os cinco tipos de vantagem competitiva de Dorsey, owner earnings (que separa capex de manutenção do de crescimento, ao contrário do FCF) e o critério de ROIC acima de 15% por 10 anos. Traz o checklist em quatro blocos — negócio, financeiro, gestão, preço — e por que copiar 13F sem entender a tese é receita de prejuízo. | intermediate |
| [[moats]] | Decidir se a vantagem competitiva é real e quanto ela dura, em vez de afirmá-la: a definição operacional (ROIC persistentemente acima do WACC) e as cinco fontes — efeito de rede, custo de troca, vantagem de custo, ativo intangível, escala eficiente — cada uma com o **teste** que a confirma ou derruba, e o falso positivo típico. Traz o roteiro de verificação (série de 10 anos de ROIC, estabilidade de share, repasse acima do IPCA), as três causas de morte de um moat, e por que a barreira regulatória de utilities e concessões no Brasil é sólida na planilha e frágil ao ciclo político. | intermediate |
| [[graham-net-net]] | Aplicar deep value quantitativo: NCAV, o gatilho de comprar abaixo de 2/3 do NCAV por ação, Graham Number e os 7 critérios do investidor defensivo. Explica por que a estratégia exige 20-30 posições simultâneas (algumas vão à falência), por que net-nets somem em bull market, e a adaptação de Bazin para o Brasil — DY sustentável de 6% em vez de valuation. | advanced |

## Macro — `finance/03-analysis/macro/`

| Nota | O que responde | Nível |
|---|---|---|
| [[ray-dalio-machine]] | Situar o momento atual em três forças sobrepostas — produtividade, ciclo de dívida curto de 5-8 anos, ciclo longo de 50-75 anos — e reconhecer as quatro saídas de um deleveraging. Traz a matriz de regime (Goldilocks, stagflation, reflation, deflation) com os ativos vencedores de cada um, a composição do All Weather, e a ressalva de que risk parity depende de correlação negativa bonds-ações que falhou em 2022. | intermediate |
| [[interest-rate-cycles]] | Mapear em que fase do ciclo de juros se está e o que isso implica por classe de ativo: mecanismos de transmissão, lag de 12-18 meses até a inflação, Taylor Rule, calendários de FOMC e Copom. Insiste que o que importa é o juro **real** — Selic 13,75% com inflação 11% é frouxa — e cobre as particularidades brasileiras (prêmio fiscal na ponta longa, ausência de dual mandate, carry trade). | intermediate |
| [[selic-and-monetary-policy]] | Ler o Copom e traduzir juros em decisão de alocação no Brasil: meta vs efetiva, as 8 reuniões por ano, o mecanismo de transmissão com defasagem de 6 a 9 meses, o regime de metas com banda de ±1,5 pp e a carta aberta no descumprimento. Traz o efeito por classe de ativo (marcação a mercado por duration na renda fixa, taxa de desconto e setores sensíveis a crédito na bolsa, diferencial de juros no câmbio) e a regra que organiza tudo — o que move preço é a **surpresa** contra o consenso, que mora no comunicado e na ata, não na decisão. | intermediate |
| [[gdp-and-growth]] | Usar PIB sem errar o básico: as três óticas e por que a da despesa (`C+I+G+X−M`) é a que diagnostica, nominal vs real, o deflator (que não é o IPCA) e por que comparar nominal entre anos é erro. Cobre a divulgação trimestral do IBGE com ~60 dias de defasagem, as revisões que alteram a série, a composição setorial brasileira e a volatilidade que a safra injeta no trimestre — e o uso que mais importa em valuation: o crescimento nominal de longo prazo da economia como **teto do `g` de perpetuidade**. | intro |
| [[global-macro-indicators]] | Saber qual indicador antecipa e qual apenas confirma: leading (PMI, curva, building permits, initial claims), coincident (PIB, payroll, varejo) e lagging (desemprego, CPI core). Traz o calendário de releases por frequência, a hierarquia de importância, a leitura por surpresa em vez de nível, e a tabela de indicadores brasileiros com fonte e periodicidade (IBC-Br como proxy mensal do PIB, Caged vs PNAD, Focus). | intermediate |

## Técnica — `finance/03-analysis/technical/`

| Nota | O que responde | Nível |
|---|---|---|
| [[support-resistance]] | Marcar os níveis onde o preço tende a parar e por quê: swing highs/lows, Volume Profile com HVN, LVN e POC, retrações de Fibonacci com o cálculo, pivot points clássicos, números redondos. Explica o polarity flip (suporte rompido vira resistência) pela mecânica dos traders presos no nível, e insiste que S/R é zona e não linha. | intro |
| [[price-action]] | Ler tendência sem indicador: higher highs/higher lows, padrões de reversão (OCO, topo e fundo duplo) e de continuação (triângulos, bandeiras, cunhas, flâmulas) com projeção de alvo. Distingue breakout legítimo de fakeout pelo volume e pelo fechamento, cobre o retest como entrada de menor risco e a análise multi-timeframe (superior para contexto, inferior para timing). | intermediate |
| [[indicators-overview]] | Escolher e combinar indicadores por categoria: SMA/EMA e crossovers, RSI com divergências, MACD, Bandas de Bollinger e squeeze, OBV, VWAP, Estocástico — cada um com a fórmula. Ensina a montar confluência com 2-3 indicadores de famílias diferentes e alerta contra paralisia por análise, curve fitting e uso de indicador de tendência em mercado lateral. | intermediate |
| [[candlestick-patterns]] | Interpretar a vela como registro da disputa entre compra e venda: anatomia, doji e suas variantes, hammer, shooting star, engolfo, morning/evening star, marubozu, three soldiers/crows. Traz um ranking explícito de confiabilidade por padrão e a regra que governa todos — o padrão só vale no contexto (em S/R, com volume, e com o candle seguinte confirmando). | intro |
