---
tags:
  - finance
  - accounting
  - ratios
aliases:
  - Indicadores Financeiros
  - Financial Ratios
  - KPIs
complexity: intermediate
context: global
created: 2026-04-06
---

# Key Financial Ratios (Indicadores Financeiros)

## Overview

Indicadores financeiros são ferramentas quantitativas que permitem **analisar**, **comparar** e **monitorar** empresas de forma padronizada. Derivados das três demonstrações financeiras — [[income-statement]], [[balance-sheet]] e [[cash-flow-statement]] — esses ratios condensam informações complexas em métricas acionáveis. Este arquivo é uma referência central para todos os indicadores utilizados na análise fundamentalista.

> [!info] Regra de ouro dos ratios
> Nenhum indicador isolado conta a história completa. Sempre analise indicadores em **conjunto**, compare com **pares do setor** e observe a **tendência temporal** (pelo menos 5 anos). Um ROE alto com alavancagem perigosa não é virtude — é risco.

## Core Concepts

---

### 1. Profitability Ratios (Rentabilidade)

#### ROE — Return on Equity (Retorno sobre o Patrimônio Líquido)

```
ROE = Lucro Líquido / Patrimônio Líquido Médio × 100
```

- **O que mede**: retorno gerado para cada R$ 1 investido pelos acionistas
- **Bom**: > 15% consistente | **Excelente**: > 20%
- **Atenção**: ROE alto pode ser inflado por alavancagem excessiva — usar DuPont para decompor

#### DuPont 3 Fatores

```
ROE = Margem Líquida × Giro do Ativo × Alavancagem Financeira

ROE = (Lucro Líq. / Receita) × (Receita / Ativo Total) × (Ativo Total / PL)
```

| Componente | O que revela |
|-----------|-------------|
| **Margem Líquida** | Eficiência em converter receita em lucro |
| **Giro do Ativo** | Eficiência no uso dos ativos para gerar receita |
| **Alavancagem** | Quanto dos ativos é financiado por dívida |

#### DuPont 5 Fatores

```
ROE = Tax Burden × Interest Burden × EBIT Margin × Asset Turnover × Leverage

ROE = (LL/LAIR) × (LAIR/EBIT) × (EBIT/Receita) × (Receita/Ativos) × (Ativos/PL)
```

Permite isolar o impacto de impostos e custos financeiros sobre o ROE.

#### ROA — Return on Assets (Retorno sobre Ativos)

```
ROA = Lucro Líquido / Ativo Total Médio × 100
```

- **O que mede**: eficiência da empresa em usar todos os seus ativos para gerar lucro
- **Bom**: > 5% para indústrias | > 10% para asset-light (tech, serviços)
- **Setorial**: bancos tipicamente 1-2% (ativos elevados)

#### ROIC — Return on Invested Capital (Retorno sobre Capital Investido)

```
NOPAT = EBIT × (1 - Alíquota Efetiva de IR)
Capital Investido = PL + Dívida Líquida (ou Ativo Total - Passivo Não-Oneroso)
ROIC = NOPAT / Capital Investido Médio × 100
```

- **O que mede**: retorno sobre **todo** o capital empregado (equity + dívida), independente da estrutura de capital
- **Regra fundamental**: se ROIC > WACC → empresa **cria** valor; se ROIC < WACC → empresa **destrói** valor
- **Bom**: > 12-15% | **Excelente**: > 20%
- É o indicador mais completo de eficiência na alocação de capital

> [!tip] ROIC vs ROE
> O ROE pode ser inflado por alavancagem. O ROIC neutraliza esse efeito porque considera o capital total (equity + dívida). Para value investors, o ROIC é o indicador superior. Warren Buffett busca empresas com ROIC consistentemente alto — indica **moat** (vantagem competitiva durável).

#### Margens de Lucratividade

```
Margem Bruta   = Lucro Bruto / Receita Líquida × 100
Margem EBITDA  = EBITDA / Receita Líquida × 100
Margem EBIT    = EBIT / Receita Líquida × 100
Margem Líquida = Lucro Líquido / Receita Líquida × 100
```

| Margem | Benchmark Geral | Variação Setorial |
|--------|----------------|-------------------|
| Bruta | > 30% | Varejo 25-35%, Software 60-80%, Commodities 15-25% |
| EBITDA | > 15% | Varejo 8-12%, Telecom 30-40%, Mineração 40-50% |
| Líquida | > 10% | Varejo 3-6%, Bancos 15-25%, Tech 20-35% |

---

### 2. Valuation Ratios (Múltiplos de Valuation)

#### P/E — Price/Earnings (P/L — Preço/Lucro)

```
P/L = Preço da Ação / LPA (últimos 12 meses)
P/L = Market Cap / Lucro Líquido
```

- **O que mede**: quantos anos de lucro atual o mercado paga pela empresa
- **Baixo** (< 10): pode estar barata ou com perspectivas ruins
- **Alto** (> 25): expectativa de crescimento ou sobrevalorização
- Usar com LPA normalizado (excluir itens não recorrentes)

#### P/B — Price/Book (P/VP — Preço/Valor Patrimonial)

```
P/VP = Preço da Ação / VPA
VPA = Patrimônio Líquido / Ações em Circulação
```

- **< 1**: ação cotada abaixo do valor contábil — potencial barganha ou destruição de valor
- **>> 1**: mercado paga prêmio por intangíveis, marca, crescimento
- Mais relevante para setores com ativos tangíveis (bancos, utilities, indústria)
- Ver [[balance-sheet]] para detalhes sobre book value

#### EV/EBITDA

```
EV (Enterprise Value) = Market Cap + Dívida Líquida + Participação Minoritária
EV/EBITDA = Enterprise Value / EBITDA
```

- **O que mede**: valor total da empresa relativo à geração operacional de caixa (proxy)
- **Vantagem**: independe da estrutura de capital (comparação entre empresas com alavancagens diferentes)
- **Baixo** (< 6): potencialmente barata | **Alto** (> 12): cara ou growth premium
- Para detalhes ver [[valuation-multiples]]

#### P/FCF — Price/Free Cash Flow

```
P/FCF = Market Cap / Free Cash Flow
```

- Similar ao P/L mas usando FCF em vez de lucro — mais conservador
- **Preferido** por investidores que desconfiam do lucro contábil (ver [[cash-flow-statement]])

#### Dividend Yield

```
Dividend Yield = Dividendos por Ação (12m) / Preço da Ação × 100
```

- **Bom**: > 4-5% para ações de renda
- **Armadilha**: DY muito alto (> 10%) pode indicar queda de preço por problemas, não generosidade real

#### PEG Ratio

```
PEG = P/L / Taxa de Crescimento do LPA (%)
```

- **< 1**: ação potencialmente subvalorizada relativa ao crescimento
- **= 1**: justamente precificada | **> 1**: cara relativa ao crescimento
- Peter Lynch popularizou esse indicador
- Limitação: depende de projeções de crescimento (subjetivas)

---

### 3. Leverage Ratios (Endividamento)

#### Debt/Equity (Dívida/PL)

```
D/E = Dívida Total / Patrimônio Líquido
```

- **< 0,5**: conservador | **0,5-1,5**: moderado | **> 2**: agressivo
- Setorial: utilities e imobiliárias operam com D/E mais altos

#### Net Debt/EBITDA (Dívida Líquida/EBITDA)

```
Net Debt/EBITDA = (Dívida Bruta - Caixa) / EBITDA
```

- **< 1x**: baixo endividamento | **1-2x**: saudável | **2-3x**: moderado
- **> 3x**: elevado — pode ter dificuldade em refinanciar
- **> 4x**: perigoso — covenants de debêntures frequentemente têm trigger nesse nível

> [!warning] Covenants
> Muitas debêntures e contratos de empréstimo no Brasil incluem covenant de Net Debt/EBITDA ≤ 3,0x ou 3,5x. Se a empresa ultrapassar, pode ter aceleração de dívida (vencimento antecipado). Monitorar trimestralmente.

#### Interest Coverage Ratio (Cobertura de Juros)

```
ICR = EBIT / Despesas Financeiras (juros)
```

- **> 5x**: confortável | **3-5x**: aceitável | **< 2x**: risco de insolvência
- **< 1x**: empresa não gera lucro operacional suficiente para pagar juros — "zombie company"

---

### 4. Liquidity Ratios (Liquidez)

#### Current Ratio (Liquidez Corrente)

```
Current Ratio = Ativo Circulante / Passivo Circulante
```

- **> 1,5**: confortável | **1,0-1,5**: aceitável | **< 1,0**: atenção

#### Quick Ratio (Liquidez Seca)

```
Quick Ratio = (Ativo Circulante - Estoques) / Passivo Circulante
```

- Exclui estoques (menos líquidos). **> 1,0** é saudável

#### Cash Ratio (Liquidez Imediata)

```
Cash Ratio = (Caixa + Equivalentes + Aplicações CP) / Passivo Circulante
```

- Medida mais conservadora. Raramente > 1,0 exceto em empresas com excesso de caixa (holding, tech)

---

### 5. Efficiency Ratios (Eficiência)

#### Asset Turnover (Giro do Ativo)

```
Giro do Ativo = Receita Líquida / Ativo Total Médio
```

- **Alto** (> 1,5): empresa capital-light eficiente | **Baixo** (< 0,5): capital-heavy ou ineficiente

#### Inventory Turnover e DIO

```
Giro de Estoques = CPV / Estoque Médio
DIO (Days Inventory Outstanding) = 365 / Giro de Estoques
```

- **DIO baixo**: estoques giram rápido (bom para perecíveis, varejo)
- **DIO alto**: estoques parados — risco de obsolescência

#### Receivables Turnover e DSO

```
Giro de Recebíveis = Receita Líquida / Contas a Receber Médio
DSO (Days Sales Outstanding) = 365 / Giro de Recebíveis
```

- **DSO crescente**: clientes demorando mais para pagar — red flag de qualidade de receita

#### Payables e DPO

```
DPO (Days Payable Outstanding) = (Fornecedores / CPV) × 365
```

#### Cash Conversion Cycle (CCC)

```
CCC = DIO + DSO - DPO
```

- Ver explicação detalhada em [[cash-flow-statement]]

---

### 6. Growth Ratios (Crescimento)

#### Revenue CAGR

```
CAGR = (Valor Final / Valor Inicial)^(1/n) - 1
```

#### EPS CAGR

```
EPS CAGR = (LPA Final / LPA Inicial)^(1/n) - 1
```

- Crescimento de LPA > crescimento de receita indica **expansão de margem** ou **recompra de ações**

---

## How to Apply

### DuPont Decomposition — Exemplo Completo

**IndusBR S.A. — Empresa industrial hipotética**

```
Dados (R$ milhões):
  Receita Líquida      = 5.000
  Lucro Líquido        =   500
  LAIR                 =   680
  EBIT                 =   800
  Ativo Total Médio    = 6.000
  PL Médio             = 2.500

DuPont 3 Fatores:
  Margem Líquida     = 500 / 5.000    = 10,0%
  Giro do Ativo      = 5.000 / 6.000  = 0,833x
  Alavancagem        = 6.000 / 2.500  = 2,40x

  ROE = 10,0% × 0,833 × 2,40 = 20,0% ✓
  Conferência: 500 / 2.500 = 20,0% ✓

DuPont 5 Fatores:
  Tax Burden         = 500 / 680      = 0,735  (carga tributária efetiva ~26,5%)
  Interest Burden    = 680 / 800      = 0,850  (juros consomem 15% do EBIT)
  EBIT Margin        = 800 / 5.000    = 0,160  (16,0%)
  Asset Turnover     = 5.000 / 6.000  = 0,833
  Leverage           = 6.000 / 2.500  = 2,400

  ROE = 0,735 × 0,850 × 0,160 × 0,833 × 2,400 = 20,0% ✓
```

> [!note] Insight DuPont
> O ROE de 20% da IndusBR é atrativo, mas a decomposição revela que a alavancagem (2,40x) contribui significativamente. Sem alavancagem (PL = Ativo), o ROE seria apenas ~8,3% (ROA). A margem operacional de 16% é sólida para indústria, e os juros consomem 15% do EBIT — monitorar se a dívida crescer.

## Examples

### Análise Completa: IndusBR S.A.

**Dados Financeiros (R$ milhões)**

```
DRE                              Balanço                         DFC
Receita Líq.     5.000           Ativo Circulante    2.800       CFO          650
CPV             (3.250)          Caixa                 400       Capex       (350)
Lucro Bruto      1.750           Recebíveis            900       FCF          300
Desp. Oper.       (950)          Estoques            1.200
EBIT               800           Ativo Não Circ.     3.200       Ações: 200M
D&A                250           Passivo Circ.       1.600       Preço: R$ 25
EBITDA           1.050           Passivo Não Circ.   1.900       Market Cap: 5.000
Desp. Financ.     (120)          PL                  2.500       Dív. Líquida: 1.700
LAIR               680                                           EV: 6.700
IR/CSLL           (180)          Dív. Bruta          2.100
Lucro Líq.         500           Fornecedores          700
LPA              R$ 2,50
```

**Dashboard de Indicadores:**

| Categoria | Indicador | Valor | Avaliação |
|-----------|-----------|-------|-----------|
| **Rentabilidade** | ROE | 20,0% | Excelente |
| | ROA | 8,3% | Bom (indústria) |
| | ROIC | 14,3%* | Bom (acima do WACC típico) |
| | Margem Bruta | 35,0% | Forte |
| | Margem EBITDA | 21,0% | Sólida |
| | Margem Líquida | 10,0% | Adequada |
| **Valuation** | P/L | 10,0x | Atrativo |
| | P/VP | 2,0x | Justo |
| | EV/EBITDA | 6,4x | Atrativo |
| | P/FCF | 16,7x | Razoável |
| | FCF Yield | 6,0% | Bom |
| **Endividamento** | D/E | 0,84x | Moderado |
| | Net Debt/EBITDA | 1,62x | Saudável |
| | ICR | 6,7x | Confortável |
| **Liquidez** | Current Ratio | 1,75x | Confortável |
| | Quick Ratio | 1,00x | Adequado |
| **Eficiência** | Giro do Ativo | 0,83x | Normal (indústria) |
| | DIO | 135 dias | Elevado — investigar |
| | DSO | 66 dias | Aceitável |
| | DPO | 79 dias | Bom poder de barganha |
| | CCC | 122 dias | Alto — típico de indústria |

*ROIC = EBIT×(1-0,265) / (2.500 + 1.700) = 588 / 4.200 = 14,0%

> [!tip] Conclusão IndusBR
> Empresa com boa rentabilidade (ROE 20%, ROIC 14%), valuation atrativo (P/L 10x, EV/EBITDA 6,4x), endividamento controlado (Net Debt/EBITDA 1,6x) e geração de FCF positiva. Pontos de atenção: DIO de 135 dias (estoques altos) e dependência de alavancagem para o ROE elevado. Candidata a análise aprofundada.

## Gotchas

- **ROE alto com PL negativo**: empresas com prejuízos acumulados podem ter PL negativo — ROE perde significado
- **P/L negativo**: empresa com prejuízo — usar EV/EBITDA ou P/Receita como alternativa
- **EV/EBITDA e leasing**: pós-IFRS 16, arrendamentos entram na dívida e no EBITDA — ajustar para comparar com histórico pré-2019
- **ROIC sensível à definição de capital investido**: diferentes analistas usam fórmulas diferentes — consistência é fundamental
- **Margens variam drasticamente entre setores**: nunca compare margem de banco com varejo
- **Indicadores backward-looking**: ratios usam dados passados — o mercado precifica expectativas futuras
- **Efeitos cambiais**: empresas exportadoras podem ter margens infladas por desvalorização do real — analisar em moeda constante
- **Stock-based compensation**: se não deduzida, infla EBITDA e distorce ROIC

## Brazilian Context

- **JCP distorce margens**: empresas que pagam Juros sobre Capital Próprio reduzem o IR mas também o lucro líquido — ROE fica "artificialmente" menor. Para comparação justa, somar JCP de volta ao lucro
- **Alíquota efetiva de IR**: a alíquota nominal combinada (IR+CSLL) é ~34%, mas subvenções, JCP e incentivos fiscais podem reduzir para 20-25%
- **Bancos**: indicadores específicos — ROE ajustado, NIM (Net Interest Margin), custo de crédito, índice de Basileia. Não comparar P/L de banco com P/L de indústria
- **Empresas de commodities**: margens flutuam com ciclo de preços — usar indicadores normalizados (média de 5-10 anos)
- **Inflação**: o CDI alto no Brasil faz com que empresas com caixa elevado tenham receita financeira significativa — pode inflar o lucro líquido e distorcer ROE/margens

## Formulas

```
# Rentabilidade
ROE              = Lucro Líquido / PL Médio
ROA              = Lucro Líquido / Ativo Total Médio
ROIC             = NOPAT / Capital Investido Médio
NOPAT            = EBIT × (1 - t)
Margem Bruta     = Lucro Bruto / Receita Líquida
Margem EBITDA    = EBITDA / Receita Líquida
Margem Líquida   = Lucro Líquido / Receita Líquida

# Valuation
P/L              = Preço / LPA  (ou Market Cap / Lucro Líquido)
P/VP             = Preço / VPA  (ou Market Cap / PL)
EV/EBITDA        = (Market Cap + Dívida Líquida) / EBITDA
P/FCF            = Market Cap / FCF
Dividend Yield   = DPA / Preço
PEG              = (P/L) / Crescimento do LPA (%)

# Endividamento
D/E              = Dívida Total / PL
Net Debt/EBITDA  = Dívida Líquida / EBITDA
ICR              = EBIT / Despesas Financeiras

# Liquidez
Current Ratio    = AC / PC
Quick Ratio      = (AC - Estoques) / PC
Cash Ratio       = (Caixa + Aplicações CP) / PC

# Eficiência
Giro do Ativo    = Receita / Ativo Total
DIO              = (Estoques / CPV) × 365
DSO              = (Recebíveis / Receita) × 365
DPO              = (Fornecedores / CPV) × 365
CCC              = DIO + DSO - DPO

# Crescimento
CAGR             = (VF / VI)^(1/n) - 1

# DuPont 3 Fatores
ROE = Margem Líq. × Giro do Ativo × (Ativo/PL)

# DuPont 5 Fatores
ROE = (LL/LAIR) × (LAIR/EBIT) × (EBIT/Receita) × (Receita/Ativo) × (Ativo/PL)
```

## References

- Damodaran, A. — *Investment Valuation*, Cap. 3-4: Financial Ratios and Multiples
- Penman, S. — *Financial Statement Analysis and Security Valuation*, Cap. 10-14
- Assaf Neto, A. — *Estrutura e Análise de Balanços*, Cap. 4-7
- Greenblatt, J. — *The Little Book That Beats the Market* (ROIC como critério central)
- CFA Institute — *Equity Asset Valuation*, Cap. 6-8
- Damodaran Online — https://pages.stern.nyu.edu/~adamodar/ (datasets de ratios por setor)

## Related

- [[income-statement]] — Fonte de dados para margens, ROE, P/L
- [[balance-sheet]] — Fonte de dados para liquidez, alavancagem, P/VP
- [[cash-flow-statement]] — Fonte de dados para FCF Yield, CCC, cash conversion
- [[valuation-multiples]] — Aprofundamento em múltiplos de valuation
- [[valuation-dcf]] — ROIC e WACC como inputs do DCF
- [[financial-statements]] — Visão integrada das demonstrações
- [[red-flags-accounting]] — Indicadores que ajudam a detectar manipulação
