---
house: quant
domain: backtesting
type: index
updated: 2026-08-01
---

# Índice — Backtesting

| Nota | O que responde | Nível |
|---|---|---|
| [[backtesting-basics]] | Montar um teste histórico honesto: separação in-sample/out-of-sample, walk-forward, detecção de overfitting, e os três vieses que invalidam resultado — sobrevivência, look-ahead e data mining. Traz modelagem de custos e slippage com números de B3, o menu de métricas de avaliação (Sharpe, max drawdown, profit factor, Calmar, Sortino), Monte Carlo para robustez, e qual biblioteca usar (vectorbt, backtrader, zipline, quantstrat). | intro |
| [[event-study]] | Desenhar estudo de evento em vez de backtest contínuo — toda pergunta "o que acontece quando X". Datar o evento pela data do anúncio (Copom e resultados saem pós-fechamento: entrada em D+1), janelas e retorno anormal (CAR vs BHAR), o contrafactual em diferença-em-diferenças, e o clustering que derruba o `n` efetivo para ~1 por evento macro. Traz o viés de classificação ex post ("primeiro corte do ciclo" só se sabe depois) e o checklist de reporte. | advanced |
| [[statistical-power]] | Calcular o efeito mínimo detectável **antes** de coletar dado, e decidir se o estudo consegue enxergar o efeito que procura: a conta `MDE ≈ 2,8·σ/√n`, o que aumenta poder de verdade (eventos, controles) contra o que só parece aumentar (ativos sob choque comum, granularidade), e a regra da casa — hipótese sem MDE declarado não vai a backtest, e `MDE >> efeito` arquiva o tema como não-testável, que é um resultado. | intermediate |
