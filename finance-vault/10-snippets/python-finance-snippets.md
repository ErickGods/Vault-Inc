---
tags:
  - finance
  - snippets
  - python
aliases:
  - Python Finanças
  - Python Finance Code
complexity: advanced
context: global
created: 2026-04-06
updated: 2026-04-06
---

# Python Finance Snippets

> [!info] Referência Rápida
> Coleção de snippets Python prontos para uso em análise financeira. Todos os códigos são independentes e executáveis. Comentários em português, variáveis e funções em inglês (convenção do mercado).

---

## 1. Download de Dados de Ações (yfinance)

```python
import yfinance as yf
import pandas as pd

# Baixar dados históricos de uma ação brasileira
ticker = "PETR4.SA"
dados = yf.download(ticker, start="2020-01-01", end="2026-01-01")

# Visualizar primeiras linhas
print(dados.head())

# Salvar em CSV para uso offline
dados.to_csv(f"{ticker}_historico.csv")

# Baixar múltiplos ativos de uma vez
tickers = ["VALE3.SA", "ITUB4.SA", "WEGE3.SA", "BBDC4.SA"]
carteira = yf.download(tickers, start="2020-01-01", end="2026-01-01")["Close"]
print(carteira.head())
```

---

## 2. Cálculo de Retornos (Diário, Mensal, Acumulado)

```python
import pandas as pd
import numpy as np

# Supondo que 'dados' já foi carregado com yfinance
precos = dados["Close"]

# Retornos diários (log returns — preferidos para análise quantitativa)
retornos_diarios = np.log(precos / precos.shift(1)).dropna()

# Retornos diários simples (aritméticos)
retornos_simples = precos.pct_change().dropna()

# Retornos mensais
retornos_mensais = precos.resample("ME").last().pct_change().dropna()

# Retorno acumulado
retorno_acumulado = (1 + retornos_simples).cumprod() - 1
print(f"Retorno acumulado total: {retorno_acumulado.iloc[-1]:.2%}")

# Retorno anualizado
anos = len(retornos_diarios) / 252
retorno_anualizado = (1 + retorno_acumulado.iloc[-1]) ** (1 / anos) - 1
print(f"Retorno anualizado: {retorno_anualizado:.2%}")
```

---

## 3. Retorno e Volatilidade de Portfólio

```python
import numpy as np
import pandas as pd

# Pesos da carteira (devem somar 1.0)
pesos = np.array([0.30, 0.25, 0.25, 0.20])

# Retornos diários da carteira (DataFrame com múltiplos ativos)
retornos = carteira.pct_change().dropna()

# Retorno esperado anualizado do portfólio
retorno_port = np.dot(pesos, retornos.mean()) * 252
print(f"Retorno esperado anualizado: {retorno_port:.2%}")

# Matriz de covariância anualizada
cov_matrix = retornos.cov() * 252

# Volatilidade do portfólio (desvio padrão)
vol_port = np.sqrt(np.dot(pesos.T, np.dot(cov_matrix, pesos)))
print(f"Volatilidade anualizada: {vol_port:.2%}")

# Sharpe Ratio (usando Selic como risk-free)
selic = 0.1375  # 13.75% ao ano
sharpe = (retorno_port - selic) / vol_port
print(f"Sharpe Ratio: {sharpe:.2f}")
```

---

## 4. Modelo DCF Simplificado

```python
def dcf_valuation(fcf_atual, taxa_crescimento, wacc, taxa_perpetuidade, anos=5):
    """
    Calcula o valor intrínseco via DCF simplificado.

    Parâmetros:
        fcf_atual: Fluxo de Caixa Livre atual (em milhões)
        taxa_crescimento: Taxa de crescimento anual do FCF
        wacc: Custo médio ponderado de capital
        taxa_perpetuidade: Taxa de crescimento na perpetuidade
        anos: Período de projeção explícita
    """
    # Projeção dos fluxos de caixa
    fluxos = []
    fcf = fcf_atual
    for t in range(1, anos + 1):
        fcf *= (1 + taxa_crescimento)
        valor_presente = fcf / (1 + wacc) ** t
        fluxos.append(valor_presente)
        print(f"Ano {t}: FCF = {fcf:.1f}M | VP = {valor_presente:.1f}M")

    # Terminal Value
    fcf_terminal = fcf * (1 + taxa_perpetuidade)
    tv = fcf_terminal / (wacc - taxa_perpetuidade)
    tv_presente = tv / (1 + wacc) ** anos

    # Valor total da firma
    valor_firma = sum(fluxos) + tv_presente
    print(f"\nSoma VP dos FCFs: {sum(fluxos):.1f}M")
    print(f"VP do Terminal Value: {tv_presente:.1f}M")
    print(f"Valor da Firma: {valor_firma:.1f}M")
    return valor_firma

# Exemplo de uso
valor = dcf_valuation(
    fcf_atual=500,        # R$500M de FCF
    taxa_crescimento=0.10, # 10% ao ano
    wacc=0.12,             # WACC de 12%
    taxa_perpetuidade=0.04 # 4% na perpetuidade
)
```

Veja também [[valuation-dcf]] para a teoria completa.

---

## 5. Médias Móveis e RSI

```python
import pandas as pd
import numpy as np

def calcular_medias_moveis(precos, curta=20, longa=50):
    """Calcula médias móveis simples (SMA) e exponenciais (EMA)."""
    df = pd.DataFrame({"Close": precos})
    df[f"SMA_{curta}"] = df["Close"].rolling(window=curta).mean()
    df[f"SMA_{longa}"] = df["Close"].rolling(window=longa).mean()
    df[f"EMA_{curta}"] = df["Close"].ewm(span=curta, adjust=False).mean()
    # Sinal: cruzamento da média curta acima da longa (Golden Cross)
    df["Sinal"] = np.where(df[f"SMA_{curta}"] > df[f"SMA_{longa}"], 1, -1)
    return df

def calcular_rsi(precos, periodo=14):
    """Calcula o Relative Strength Index (RSI)."""
    delta = precos.diff()
    ganho = delta.where(delta > 0, 0.0)
    perda = -delta.where(delta < 0, 0.0)
    media_ganho = ganho.rolling(window=periodo).mean()
    media_perda = perda.rolling(window=periodo).mean()
    rs = media_ganho / media_perda
    rsi = 100 - (100 / (1 + rs))
    return rsi

# Uso
rsi = calcular_rsi(dados["Close"])
print(f"RSI atual: {rsi.iloc[-1]:.1f}")
# RSI < 30 = sobrevendido | RSI > 70 = sobrecomprado
```

---

## 6. Simulação de Monte Carlo

```python
import numpy as np
import matplotlib.pyplot as plt

# Parâmetros da simulação
preco_atual = 30.0
retorno_medio_diario = 0.0005
vol_diaria = 0.02
dias_simulacao = 252
num_simulacoes = 1000

# Executar simulações
np.random.seed(42)
simulacoes = np.zeros((dias_simulacao, num_simulacoes))
simulacoes[0] = preco_atual

for t in range(1, dias_simulacao):
    choque = np.random.normal(retorno_medio_diario, vol_diaria, num_simulacoes)
    simulacoes[t] = simulacoes[t - 1] * (1 + choque)

# Estatísticas dos preços finais
precos_finais = simulacoes[-1]
print(f"Preço médio final: R${np.mean(precos_finais):.2f}")
print(f"Mediana: R${np.median(precos_finais):.2f}")
print(f"Percentil 5%: R${np.percentile(precos_finais, 5):.2f}")
print(f"Percentil 95%: R${np.percentile(precos_finais, 95):.2f}")

# Plotar resultado
plt.figure(figsize=(12, 6))
plt.plot(simulacoes[:, :50], alpha=0.3)  # Plotar 50 cenários
plt.title("Simulação de Monte Carlo — Preço da Ação")
plt.xlabel("Dias"); plt.ylabel("Preço (R$)")
plt.tight_layout(); plt.show()
```

---

## 7. Fronteira Eficiente (Markowitz)

```python
import numpy as np
import pandas as pd
from scipy.optimize import minimize
import matplotlib.pyplot as plt

def portfolio_stats(pesos, retornos_medios, cov_matrix):
    """Retorna retorno, volatilidade e Sharpe do portfólio."""
    ret = np.dot(pesos, retornos_medios) * 252
    vol = np.sqrt(np.dot(pesos.T, np.dot(cov_matrix * 252, pesos)))
    sharpe = (ret - 0.1375) / vol  # Selic como risk-free
    return ret, vol, sharpe

def fronteira_eficiente(retornos, num_portfolios=5000):
    """Gera e plota a fronteira eficiente via simulação."""
    retornos_medios = retornos.mean()
    cov_matrix = retornos.cov()
    n_ativos = len(retornos.columns)
    resultados = np.zeros((3, num_portfolios))
    pesos_salvos = []

    for i in range(num_portfolios):
        pesos = np.random.dirichlet(np.ones(n_ativos))
        ret, vol, sharpe = portfolio_stats(pesos, retornos_medios, cov_matrix)
        resultados[0, i] = vol
        resultados[1, i] = ret
        resultados[2, i] = sharpe
        pesos_salvos.append(pesos)

    # Portfólio de máximo Sharpe
    idx_max_sharpe = resultados[2].argmax()
    print("Pesos do portfólio ótimo (max Sharpe):")
    for ativo, peso in zip(retornos.columns, pesos_salvos[idx_max_sharpe]):
        print(f"  {ativo}: {peso:.2%}")

    # Plotar
    plt.figure(figsize=(10, 7))
    plt.scatter(resultados[0], resultados[1], c=resultados[2], cmap="viridis", s=5)
    plt.colorbar(label="Sharpe Ratio")
    plt.scatter(resultados[0, idx_max_sharpe], resultados[1, idx_max_sharpe],
                c="red", marker="*", s=200, label="Max Sharpe")
    plt.title("Fronteira Eficiente"); plt.xlabel("Volatilidade"); plt.ylabel("Retorno")
    plt.legend(); plt.tight_layout(); plt.show()

# Uso: fronteira_eficiente(carteira.pct_change().dropna())
```

Veja [[portfolio-theory-mpt]] e [[factor-investing]] para teoria.

---

## 8. Framework de Backtesting Simples

```python
import pandas as pd
import numpy as np

def backtest_sma_crossover(precos, curta=20, longa=50, capital=100000):
    """
    Backtesting de estratégia de cruzamento de médias móveis.
    Compra quando SMA curta cruza acima da longa; vende no cruzamento inverso.
    """
    df = pd.DataFrame({"Close": precos})
    df["SMA_curta"] = df["Close"].rolling(curta).mean()
    df["SMA_longa"] = df["Close"].rolling(longa).mean()
    df["Sinal"] = 0
    df.loc[df["SMA_curta"] > df["SMA_longa"], "Sinal"] = 1   # Comprado
    df.loc[df["SMA_curta"] <= df["SMA_longa"], "Sinal"] = -1  # Vendido/fora
    df["Posicao"] = df["Sinal"].shift(1)  # Evitar look-ahead bias
    df["Retorno_Mercado"] = df["Close"].pct_change()
    df["Retorno_Estrategia"] = df["Posicao"] * df["Retorno_Mercado"]
    df = df.dropna()

    # Métricas
    ret_acum_mercado = (1 + df["Retorno_Mercado"]).cumprod().iloc[-1] - 1
    ret_acum_estrat = (1 + df["Retorno_Estrategia"]).cumprod().iloc[-1] - 1
    vol_estrat = df["Retorno_Estrategia"].std() * np.sqrt(252)
    sharpe = (df["Retorno_Estrategia"].mean() * 252) / vol_estrat

    print(f"Retorno acumulado mercado: {ret_acum_mercado:.2%}")
    print(f"Retorno acumulado estratégia: {ret_acum_estrat:.2%}")
    print(f"Volatilidade anualizada: {vol_estrat:.2%}")
    print(f"Sharpe Ratio: {sharpe:.2f}")
    return df

# backtest_sma_crossover(dados["Close"])
```

Veja [[backtesting-basics]] para boas práticas e armadilhas comuns.

---

## 9. Heatmap de Correlação

```python
import seaborn as sns
import matplotlib.pyplot as plt

def plot_correlacao(retornos, titulo="Matriz de Correlação"):
    """Gera heatmap de correlação entre ativos."""
    corr = retornos.corr()
    plt.figure(figsize=(10, 8))
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="RdYlGn",
                center=0, vmin=-1, vmax=1, square=True,
                linewidths=0.5)
    plt.title(titulo)
    plt.tight_layout()
    plt.show()
    return corr

# Uso: plot_correlacao(carteira.pct_change().dropna())
```

---

## 10. Consulta Selic/CDI via API do Banco Central

```python
import requests
import pandas as pd

def buscar_selic_historica(inicio="01/01/2020", fim="31/12/2025"):
    """
    Busca a taxa Selic diária via API do Banco Central do Brasil.
    Código da série: 432 (Selic diária anualizada)
    """
    url = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.432/dados"
    params = {"formato": "json", "dataInicial": inicio, "dataFinal": fim}
    resp = requests.get(url, params=params)
    dados = pd.DataFrame(resp.json())
    dados["data"] = pd.to_datetime(dados["data"], format="%d/%m/%Y")
    dados["valor"] = dados["valor"].astype(float)
    dados.set_index("data", inplace=True)
    return dados

def buscar_cdi_acumulado(inicio="01/01/2020", fim="31/12/2025"):
    """
    Busca o CDI diário (série 12).
    """
    url = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.12/dados"
    params = {"formato": "json", "dataInicial": inicio, "dataFinal": fim}
    resp = requests.get(url, params=params)
    dados = pd.DataFrame(resp.json())
    dados["data"] = pd.to_datetime(dados["data"], format="%d/%m/%Y")
    dados["valor"] = dados["valor"].astype(float)
    dados.set_index("data", inplace=True)
    # Calcular CDI acumulado
    dados["cdi_acum"] = (1 + dados["valor"] / 100).cumprod()
    return dados

# Uso
selic = buscar_selic_historica()
print(f"Selic atual: {selic['valor'].iloc[-1]:.2f}% a.a.")
```

---

## Referências Cruzadas

- [[backtesting-basics]] — Fundamentos de backtesting
- [[valuation-dcf]] — Modelo DCF detalhado
- [[factor-investing]] — Investimento baseado em fatores
- [[portfolio-theory-mpt]] — Teoria Moderna de Portfólio

---

> [!tip] Dica Prática
> Instale as dependências com: `pip install yfinance pandas numpy scipy matplotlib seaborn requests`. Para ambientes de produção, considere usar `poetry` ou `conda` para gerenciar ambientes virtuais.

> [!warning] Atenção
> Estes snippets são para fins educacionais e de prototipagem. Antes de usar em decisões reais de investimento, valide os dados, trate edge cases e considere custos de transação, slippage e impostos.
