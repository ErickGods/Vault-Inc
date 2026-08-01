---
house: quant
type: topic-index
updated: 2026-07-29
---

# Casa Quant — Índice de Temas Transversais

Alguns problemas não moram em um domínio. Custo de transação aparece nas sete notas desta
casa; viés de sobrevivência, em quatro delas, espalhadas por três domínios. Para essas
perguntas, escolher um domínio em `_house.md` é escolher errado por construção — qualquer
escolha perde material que está em outro lugar.

Use este arquivo quando a pergunta for sobre **uma preocupação**, não sobre um território.
A coluna **Onde começar** nomeia a nota que trata o tema de forma mais direta: abra só ela
e pare, se responder. A coluna **Também tratado em** existe para o caso de não responder —
é a divulgação honesta de que o tema é distribuído, não uma lista de leitura obrigatória.

Se a pergunta for sobre um território (fatores, estratégias, backtesting, risco), volte para
`_house.md` e desça pelo domínio.

## Temas

| Tema | Onde começar | Também tratado em |
|---|---|---|
| Custos de transação e slippage | [[backtesting-basics]] | [[momentum-strategies]], [[factor-investing]], [[position-sizing]], [[capm]], [[sharpe-ratio]] |
| Viés de sobrevivência | [[backtesting-basics]] | [[capm]], [[momentum-strategies]], [[sharpe-ratio]] |
| Look-ahead bias | [[backtesting-basics]] | [[capm]] |
| Dados point-in-time | [[backtesting-basics]] | [[capm]], [[sharpe-ratio]] |
| Overfitting e validação out-of-sample | [[backtesting-basics]] | [[sharpe-ratio]], [[factor-investing]] |
| Número de tentativas (`N`) e Sharpe inflado | [[sharpe-ratio]] | [[backtesting-basics]], [[capm]] |
| Amostra curta e efeito mínimo detectável | [[statistical-power]] | [[sharpe-ratio]] (erro-padrão do Sharpe em `T` pequeno), [[event-study]] (`n` = eventos, e o clustering que o encolhe) |
| Correlação instável em crise | [[portfolio-theory-mpt]] | [[capm]], [[position-sizing]], [[momentum-strategies]] |
| Não-normalidade e risco de cauda | [[sharpe-ratio]] | [[portfolio-theory-mpt]], [[momentum-strategies]], [[capm]] |
| Drawdown — cálculo e uso como restrição | [[backtesting-basics]] | [[sharpe-ratio]], [[position-sizing]], [[factor-investing]], [[momentum-strategies]] |
| Taxa livre de risco e proxies brasileiros | [[capm]] | [[sharpe-ratio]], [[portfolio-theory-mpt]], [[momentum-strategies]] |
| Liquidez e restrições da B3 | [[momentum-strategies]] | [[backtesting-basics]], [[position-sizing]], [[factor-investing]], [[capm]], [[sharpe-ratio]] |

## Critério de inclusão

Um tema entra aqui quando é tratado **em mais de um domínio** — não quando aparece em muitas
notas. O teste é: existe uma escolha de domínio em `_house.md` que responde a pergunta
sozinha? Se existe, o tema pertence ao índice daquele domínio e não a este arquivo. Índice de
temas que cresce sem esse filtro vira um segundo índice de tudo, e volta a custar o contexto
que os três saltos economizam.

Note que "custo de transação" está em sete notas e "look-ahead bias" em duas — as duas linhas
são legítimas pelo mesmo critério, porque as duas atravessam domínios. Contagem de notas não
é o teste; dispersão entre domínios é.
