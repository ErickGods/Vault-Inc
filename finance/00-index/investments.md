---
house: finance
domain: investments
type: index
updated: 2026-07-29
---

# Índice — Investimentos

## Renda variável — `finance/02-investments/equities/`

| Nota | O que responde | Nível |
|---|---|---|
| [[stocks-fundamentals]] | O que se compra ao comprar uma ação: ON/PN/Unit e o que cada sufixo implica em voto e dividendo, primário vs secundário, os quatro caminhos pelos quais a empresa cria valor para o acionista. Traz o passo a passo operacional no Brasil (corretora, home broker, D+2), os custos reais e a isenção de R$ 20k/mês em swing trade. | intro |
| [[dividends]] | Montar e avaliar uma carteira de renda: DY, payout, cobertura, datas com/ex, critérios de Bazin e a diferença fiscal entre dividendo isento e JCP com 15% retido. Diz como identificar dividend trap (DY alto porque a cota caiu) e por que payout acima de 100% ou dividendo financiado por dívida invalida a tese. | intermediate |
| [[growth-vs-value]] | Escolher entre os dois estilos e reconhecer o regime que favorece cada um (juros subindo → value; caindo → growth). Traz os filtros de screening de cada lado, PEG e GARP de Lynch, o fator HML de Fama-French, e como separar barato-e-fora-de-moda de value trap terminal. | intermediate |
| [[brazilian-market-b3]] | Operar na B3 sabendo onde se está pisando: segmentos de governança e o tag along de cada um, a família de índices (IBOV, IBrX, SMLL, IDIV, IFIX, setoriais), horários e liquidação. Quantifica o risco de concentração — top 10 do IBOV são ~55% do índice — e o peso de bancos e commodities na composição setorial. | intermediate |

## Renda fixa — `finance/02-investments/fixed-income/`

| Nota | O que responde | Nível |
|---|---|---|
| [[tesouro-direto]] | Escolher o título público certo por objetivo (Selic para reserva, IPCA+ para prazo longo, prefixado para aposta em queda de juros) e entender por que IPCA+ longo oscila 10-20% no curto prazo. Cobre IR regressivo, IOF dos 30 primeiros dias, taxa de custódia B3 e a comparação com renda fixa privada. | intro |
| [[cdb-lci-lca]] | Comparar corretamente um CDB tributado com uma LCI/LCA isenta — a conta `Taxa × (1 − IR)` mostra que 95% do CDI isento vence 110% do CDI tributado. Explica o FGC (R$ 250 mil por CPF/instituição, teto global de R$ 1 mi em 4 anos, e o que ele não cobre) e a carência de 90 dias das letras. | intro |
| [[bonds-international]] | Investir em renda fixa em dólar sendo brasileiro: tipos de Treasury, corporate IG vs high yield, YTM, duration e credit spread. Traz a tabela de ETFs por objetivo (TLT, IEF, SHY, AGG, LQD, HYG, TIP), os quatro caminhos de acesso a partir do Brasil e a tributação de exterior com isenção de R$ 35k/mês. | intermediate |
| [[yield-curve]] | Ler a curva de juros como sinal macro: formatos, spread 10y-2y como leading indicator de recessão, teorias da estrutura a termo, decomposição em real yield + inflação esperada + term premium. Cobre os quatro movimentos (bull/bear steepening e flattening), a curva DI brasileira, a inflação implícita entre prefixado e NTN-B — e o lag de 12-24 meses que impede usar a inversão como timing. | advanced |

## Fundos — `finance/02-investments/funds/`

| Nota | O que responde | Nível |
|---|---|---|
| [[fundos-de-investimento]] | Avaliar um fundo antes de aplicar: quem é gestor, administrador e custodiante, tipos sob a CVM 175, taxa de administração vs performance, prazos de cotização. Explica o come-cotas de maio e novembro e por que fundos de ações (FIA), isentos dele, são fiscalmente melhores no longo prazo. | intro |
| [[etfs]] | Por que o passivo vence na média e como montar carteira com ETF: mecanismo de criação/resgate pelos APs, comparação ponto a ponto com fundo ativo, three-fund portfolio de Bogle, DCA. Traz a tabela de ETFs da B3 e os riscos que a etiqueta "ETF" esconde — alavancados com path dependency, sintéticos com risco de contraparte, tracking error. | intermediate |
| [[fiis-real-estate]] | Selecionar FII para renda mensal isenta de IR: tipos (tijolo, papel, híbrido, FOF, desenvolvimento), DY, P/VPA, vacância física vs financeira, cap rate. Traz a tabela de critérios com faixas boas, as três condições que preservam a isenção (50+ cotistas, cotista com menos de 10%, negociação em bolsa) e por que DY alto demais é red flag. | intermediate |

## Derivativos — `finance/02-investments/derivatives/`

| Nota | O que responde | Nível |
|---|---|---|
| [[options-basics]] | Estruturar posição com opção sabendo o que se assume: call/put, americana vs europeia na B3, valor intrínseco vs extrínseco, moneyness, Black-Scholes e os cinco Greeks. Cobre as estratégias por objetivo (covered call e cash-secured put para renda, protective put e collar para hedge, straddle e spreads para especular), volatilidade implícita e VIX, e os riscos que zeram conta — naked short call, theta decay em OTM curto, exercício antecipado, pin risk. | advanced |
| [[futures]] | Dimensionar e usar futuros na B3: WIN e WDO com multiplicador, tick e margem, marcação a mercado diária, contango vs backwardation, `F = S·e^((r−q)t)`. Mostra a conta de quantos minis vender para hedgear R$ 200k em ações, a alavancagem efetiva de 1:10 a 1:20 e por que ~90% dos day traders perdem dinheiro no primeiro ano. | advanced |
| [[hedging-strategies]] | Decidir se vale transferir um risco e a que preço — hedge não remove risco de graça, o preço é o retorno esperado que se abre mão. Traz os instrumentos da B3 com um caso de uso cada (WIN para o beta da carteira, WDO para passivo em dólar, protective put e collar para posição concentrada que não pode ser vendida, DI futuro para curva), a conta de quantos contratos, por que hedge de 100% raramente é ótimo e o **basis risk** quando o instrumento não é a exposição. Alerta para os erros que custam dinheiro: hedgear depois do evento com vol implícita já alta, confundir hedge com aposta direcional, e a chamada de margem na perna do hedge que chega justamente quando o ativo protegido está subindo. | advanced |

## Alternativos — `finance/02-investments/alternatives/`

| Nota | O que responde | Nível |
|---|---|---|
| [[commodities]] | Onde commodities entram no portfólio (0-3% conservador até 20%+ em tese própria) e como acessá-las — ETF, ação de produtora, futuro, físico. Explica os drivers de preço, os três papéis do ouro, o roll yield negativo que faz ETF de futuro sangrar em contango, e por que o real é moeda de commodity. | intermediate |
| [[crypto-assets]] | Decidir exposição a cripto com as duas teses na mesa: supply fixo e censura-resistência de um lado, ausência de fluxo de caixa e drawdowns de -80% do outro. Cobre categorias, custódia hot vs cold vs exchange (FTX), sizing de 1-5%, o Marco Legal 14.478/22 e a isenção de R$ 35k/mês. | intermediate |
| [[private-equity]] | Entender o contrato antes de entrar num FIP: estrutura GP/LP, committed vs called capital, 2/20 e carried interest sobre hurdle, J-curve de retorno negativo nos primeiros anos. Diferencia IRR de MOIC/DPI/TVPI/PME, quantifica a power law do VC (um único deal salva o fundo) e lista o que trava o capital por 7-12 anos. | advanced |
