---
tags: [quant, risk-analytics, performance, sharpe]
aliases: [Sharpe Ratio, índice de Sharpe, IS]
house: quant
domain: risk-analytics
level: intermediate
status: active
created: 2026-07-29
updated: 2026-07-29
---

# Sharpe Ratio

O Sharpe Ratio mede retorno em excesso à taxa livre de risco por unidade de volatilidade — quanto de prêmio a estratégia entrega para cada unidade de oscilação que o investidor teve de suportar.

---

## A fórmula

```
S = (Rp − Rf) / σp
```

| Termo | O que é |
|-------|---------|
| `Rp` | Retorno do portfólio ou da estratégia no período. |
| `Rf` | Taxa livre de risco no mesmo período — no Brasil, CDI/Selic acumulado. Ver [[capm]] para a discussão do proxy correto. |
| `Rp − Rf` | Retorno em excesso. É isso que se está remunerando; retorno bruto sem descontar `Rf` não é Sharpe. |
| `σp` | Desvio-padrão dos **retornos em excesso**, não dos retornos brutos. A distinção importa quando `Rf` é volátil, o que no Brasil acontece. |

### Anualização

```
S_anual = S_periodo · √n
```

Onde `n` é o número de períodos por ano — 252 (dias úteis; use 246–248 para o calendário B3), 52 (semanas), 12 (meses).

> [!warning] A raiz de n assume i.i.d.
> A regra `√n` só vale se os retornos forem **independentes e identicamente distribuídos**. Retornos com autocorrelação positiva têm variância de longo prazo maior do que `n · σ²_periodo`, e a anualização ingênua **superestima o Sharpe**. Estratégias de trend following, carry e qualquer coisa com posição persistente tipicamente exibem autocorrelação positiva de primeira ordem — anualizar por `√252` nesses casos infla o número de forma sistemática.
>
> A correção padrão é a de Lo (2002), que substitui `√n` por um fator que incorpora as autocorrelações `ρk`:
>
> ```
> fator = n / sqrt( n + 2 · Σ_{k=1..n−1} (n − k) · ρk )
> ```
>
> Com `ρ1 = 0,2` e anualização mensal→anual, o fator correto fica cerca de 15% abaixo de `√12`. Se você reporta Sharpe anualizado, **teste a autocorrelação da série antes** e diga qual fator usou.

---

## Deflated Sharpe

Esta é a seção que sustenta o padrão da casa: **Sharpe reportado com o número de tentativas**.

### O problema

Se você testa `N` configurações de estratégia e reporta a melhor, o Sharpe dessa melhor é uma **estatística de máximo**, não uma estimativa não-viesada. Mesmo que nenhuma das `N` tenha habilidade real — Sharpe verdadeiro zero para todas — o máximo entre elas será positivo, e crescerá com `N`. O viés é grande e é aritmético, não uma questão de sorte.

O valor esperado do máximo de `N` Sharpes amostrais com Sharpe verdadeiro zero é aproximadamente:

```
E[max S] ≈ σ_S · [ (1 − γ) · Z⁻¹(1 − 1/N) + γ · Z⁻¹(1 − 1/(N·e)) ]
```

onde `σ_S` é o desvio-padrão dos Sharpes entre as tentativas, `γ ≈ 0,5772` (Euler-Mascheroni) e `Z⁻¹` é a inversa da normal padrão. A intuição operacional é a que importa: esse é o **piso** que uma estratégia precisa superar só para não ser ruído. Com poucas dezenas de tentativas o piso já é material; com centenas, ele engole Sharpes que pareceriam ótimos isoladamente.

Isso é a mesma patologia descrita como data mining em [[backtesting-basics]], quantificada.

### O ajuste

O **Deflated Sharpe Ratio (DSR)** de Bailey e López de Prado (2014) converte o Sharpe observado numa **probabilidade** de que o Sharpe verdadeiro seja maior que zero, penalizando por duas coisas simultaneamente:

**1. Número de tentativas (`N`).** Entra via o benchmark `S₀ = E[max S]` acima. O Sharpe observado não é comparado contra zero, é comparado contra o que o melhor de `N` sorteios produziria por acaso.

**2. Não-normalidade dos retornos — skew (`γ₃`) e curtose (`γ₄`).** O erro-padrão do estimador de Sharpe não é o da normal quando a distribuição tem cauda. A forma correta:

```
σ(Ŝ) = sqrt( (1 − γ₃·Ŝ + ((γ₄ − 1)/4)·Ŝ²) / (T − 1) )
```

E o DSR:

```
DSR = Z( (Ŝ − S₀) · sqrt(T − 1) / sqrt(1 − γ₃·Ŝ + ((γ₄ − 1)/4)·Ŝ²) )
```

Leia o denominador com atenção, porque ele contém a lição prática:

- **Skew negativo (`γ₃ < 0`)** — o termo `−γ₃·Ŝ` vira positivo, aumenta o erro-padrão, **derruba** o DSR. Estratégias que ganham pouco com frequência e perdem muito raramente são punidas, corretamente.
- **Curtose excessiva (`γ₄ > 3`)** — aumenta o erro-padrão, derruba o DSR. Cauda gorda significa que a σ amostral é uma estimativa pior do que aparenta.
- **`T` pequeno** — o denominador não é compensado, o DSR cai. Amostra curta não vira evidência por otimismo.

### Como reportar nesta casa

Nenhum backtest é entregue com Sharpe sozinho. O bloco mínimo:

| Campo | Exemplo |
|-------|---------|
| Sharpe observado (líquido de custos) | 0,82 |
| Período e universo | 2012-01 a 2025-12, IBrX-100 point-in-time |
| `T` (observações) | 168 meses |
| **`N` — tentativas** | 47 configurações testadas |
| Skew / curtose | −0,61 / 6,2 |
| `S₀` (benchmark de N tentativas) | 0,51 |
| **DSR** | 0,73 |

`N` é o número **honesto** de configurações que você olhou, não as que você reportou. Cada variação de janela de lookback, de limiar de rebalanceamento, de filtro de liquidez, de universo, conta. Reotimizar depois de ver o resultado conta. Se você não registrou `N` durante a pesquisa, você não sabe `N`, e o Sharpe não é interpretável — declare isso em vez de inventar um número.

Regra prática da casa: **DSR abaixo de 0,95 não é aprovação.** Um Sharpe de 1,2 com `N = 300` frequentemente tem DSR abaixo de 0,5 — ou seja, é mais provável que seja ruído do que habilidade.

---

## Quando o Sharpe mente

### (a) Retornos assimétricos ou de cauda gorda

O Sharpe usa desvio-padrão, que trata ganho e perda simetricamente e não enxerga o formato da cauda. Uma estratégia vendida em volatilidade — venda sistemática de opções, carry em moeda de juro alto, arbitragem de convergência alavancada — produz uma série de retornos pequenos e regulares, σ baixíssimo e Sharpe espetacular, por anos. O risco não desapareceu; ele foi movido para um evento raro que a série amostral ainda não contém.

O padrão é reconhecível: **Sharpe alto + skew negativo forte + curtose alta**. Sempre reporte os três momentos juntos. Um Sharpe de 2,5 com skew de −3 é um perfil de risco pior do que um Sharpe de 0,8 com skew zero, e o Sharpe sozinho diz o oposto. Esta é a mesma limitação da variância como medida de risco discutida em [[portfolio-theory-mpt]].

### (b) Séries autocorrelacionadas

Autocorrelação positiva **subestima σ** medido em alta frequência, e portanto infla o Sharpe. Onde isso aparece:

- **Ativos ilíquidos** — o preço observado é stale; o ativo não negociou, então o retorno registrado é zero e a volatilidade some. Small caps brasileiras de baixo giro, debêntures, FIIs de tijolo pouco negociados.
- **Marcação a modelo** — private equity, crédito privado, imóveis. O valor é uma estimativa suavizada, não um preço de transação. Suavização é autocorrelação por construção.
- **Estratégias com posição persistente** — trend following mantém a mesma posição por semanas; os retornos diários não são independentes.

Diagnóstico: rode o teste de Ljung-Box na série de retornos e olhe `ρ1`. Se `ρ1` for materialmente positivo, aplique a correção de Lo antes de anualizar, ou reporte o Sharpe na frequência nativa sem anualizar. Um Sharpe de 1,8 numa série com `ρ1 = 0,35` pode virar 1,2 depois da correção.

### (c) Amostras curtas

O próprio Sharpe é uma estimativa com erro-padrão grande. Sob normalidade, o erro-padrão é aproximadamente `sqrt((1 + Ŝ²/2)/T)`. Com 3 anos de dados mensais (`T = 36`) e Sharpe estimado de 1,0, o erro-padrão é cerca de 0,20 — intervalo de confiança de 95% indo de ~0,6 a ~1,4. Com dados diários o `T` é maior, mas a autocorrelação e a não-normalidade são piores, então o ganho é menor do que parece.

Consequência direta: **não se distingue estatisticamente uma estratégia com Sharpe 1,0 de uma com Sharpe 0,6 em três anos de dados.** Ranquear estratégias por Sharpe em amostra curta é ranquear ruído. Declare `T` sempre, e o intervalo de confiança quando `T` for pequeno.

---

## Alternativas

| Métrica | Fórmula | Quando é preferível |
|---------|---------|---------------------|
| **Sortino** | `(Rp − Rf) / σ_downside`, onde `σ_downside` usa só retornos abaixo do alvo | Quando a distribuição é assimétrica e a volatilidade de alta não é risco. Penaliza apenas desvio negativo, então não pune uma estratégia por ter meses excepcionalmente bons — mas não resolve cauda gorda, e é ainda mais sensível a amostra curta porque usa menos observações. |
| **Calmar** | `Retorno anualizado / \|Max Drawdown\|` | Quando a restrição real é a tolerância a perda de pico a vale — capital de terceiros com risco de resgate, ou mandato com stop de drawdown. É a métrica que fala a língua de quem decide se continua alocado. Fraqueza: max drawdown é um único evento da amostra, então é uma estatística instável e fortemente dependente do período. |

Na prática, use as três em conjunto. Sharpe para eficiência média, Sortino para o formato da distribuição, Calmar para a experiência do alocador. Divergência entre elas é informação, não inconveniente: Sharpe alto com Calmar baixo significa que a estratégia é eficiente na média mas teve um evento que quebraria o mandato. O dimensionamento em [[position-sizing]] depende mais do Calmar e do drawdown do que do Sharpe.

---

## Referência de leitura

**Sharpe sozinho nunca é critério de aprovação nesta casa.** Um número de Sharpe desacompanhado é um resultado sem contexto, e a casa não aceita resultado sem contexto.

Um resultado é aceitável quando traz, no mínimo:

- período, universo e **critério de rejeição declarado antes de rodar**;
- custos de transação embutidos — Sharpe bruto de custos não é resultado;
- viés de sobrevivência tratado e declarado, ou a ausência de point-in-time declarada;
- **o número de tentativas `N`**, e o DSR correspondente;
- momentos de ordem superior (skew, curtose) e a autocorrelação de primeira ordem;
- **cenário de falha explícito** — em que regime esta estratégia perde dinheiro.

Os padrões completos estão em `quant/CLAUDE.md`. O protocolo de validação está em [[backtesting-basics]]; a decomposição entre alpha e exposição a fatores, que responde a pergunta complementar "esse retorno é habilidade ou é beta?", está em [[capm]] e [[factor-investing]]. Uma estratégia de [[momentum-strategies]] com Sharpe alto pode ser inteiramente exposição ao fator WML — Sharpe não distingue.

---

## References

- Sharpe, William F. "The Sharpe Ratio." *Journal of Portfolio Management*, 1994.
- Bailey, David H. & López de Prado, Marcos. "The Deflated Sharpe Ratio: Correcting for Selection Bias, Backtest Overfitting, and Non-Normality." *Journal of Portfolio Management*, 2014.
- Bailey, D. H.; Borwein, J.; López de Prado, M.; Zhu, Q. J. "The Probability of Backtest Overfitting." *Journal of Computational Finance*, 2017.
- Lo, Andrew W. "The Statistics of Sharpe Ratios." *Financial Analysts Journal*, 2002.
- Harvey, Campbell R. & Liu, Yan. "Backtesting." *Journal of Portfolio Management*, 2015.
- Harvey, C. R.; Liu, Y.; Zhu, H. "…and the Cross-Section of Expected Returns." *Review of Financial Studies*, 2016.
- Sortino, Frank A. & Price, Lee N. "Performance Measurement in a Downside Risk Framework." *Journal of Investing*, 1994.

---

## Related

- [[backtesting-basics]] — protocolo onde o DSR entra
- [[capm]] — a pergunta complementar: alpha ou beta?
- [[portfolio-theory-mpt]] — de onde vem a razão retorno/volatilidade
- [[position-sizing]] — onde a métrica vira decisão de exposição
- [[factor-investing]] — Sharpe por fator e o problema de atribuição
- [[momentum-strategies]] — caso típico de Sharpe inflado por autocorrelação
