---
house: quant
type: house-index
updated: 2026-07-29
---

# Casa Quant — Índice Mestre

Este é o primeiro arquivo a carregar ao trabalhar nesta casa. Ele não contém conhecimento;
contém o mapa. Use assim: identifique na tabela de domínios ativos qual território cobre a
tarefa, carregue o `_index.md` daquele domínio, leia a coluna "O que responde" e abra
**apenas** as notas que a tarefa exige. Três saltos, e nada de varrer o vault com Glob.

**Como abrir uma nota.** Wikilinks (`[[capm]]`) não carregam caminho — são identificadores,
não paths. O arquivo fica em `<pasta>/<nome-da-nota>.md`, onde `<pasta>` vem da coluna
**Pasta** da tabela abaixo. Exemplo: `[[capm]]` é o arquivo `capm.md` dentro da pasta
`quant/03-factor-models/`. Os índices de domínio e o `_topics.md` têm pasta fixa em vez de
vir da tabela: ficam sempre em `quant/00-index/`, com o nome do arquivo igual ao do wikilink —
`[[risk-analytics]]` é o arquivo `quant/00-index/risk-analytics.md`.

> **Não deduza o caminho.** Os prefixos numéricos **não são sequenciais** e **não são
> deriváveis** do nome do domínio nem da ordem em que os domínios aparecem aqui. Domínios
> planejados seguram números reservados sem existir em disco — por isso não há `01` nem `02`
> na casa quant hoje, e `strategies` é `04`, não `03`. Leia a coluna Pasta; inferir o prefixo
> leva a um caminho inexistente, e o fallback natural (`ls -R`) é exatamente a varredura que
> a regra proíbe.

## Domínios ativos

| Domínio | Índice | Pasta | Cobre |
|---|---|---|---|
| Modelos de fatores | [[factor-models]] | `quant/03-factor-models/` | CAPM, beta, Fama-French, Carhart, prêmios de fator |
| Estratégias | [[strategies]] | `quant/04-strategies/` | momentum cross-sectional e time-series, trend following, dual momentum |
| Backtesting | [[backtesting]] | `quant/05-backtesting/` | walk-forward, vieses, custos e slippage, métricas, Monte Carlo, event study, poder estatístico e MDE |
| Risco e performance | [[risk-analytics]] | `quant/06-risk-analytics/` | Sharpe e Deflated Sharpe, média-variância, dimensionamento de posição |

## Temas transversais

Se a pergunta é sobre uma **preocupação** e não sobre um território — custo de transação,
viés de sobrevivência, point-in-time, overfitting, correlação em crise, drawdown, liquidez —
comece por [[quant/00-index/_topics|_topics]]. Nenhum domínio acima responde essas perguntas sozinho: custo de
transação aparece nas sete notas da casa, e escolher um domínio aqui perde material que está
nos outros três. O `_topics.md` diz qual nota abrir primeiro para cada tema.

## Domínios planejados

A coluna **Pasta** lê `—` porque a pasta **não existe em disco**. O número entre parênteses
está reservado e explica os buracos na numeração dos domínios ativos.

| Domínio | Vai cobrir | Pasta | Status |
|---|---|---|---|
| Fundamentos matemáticos | probabilidade, álgebra linear, cálculo estocástico, otimização | — (reservado: `01-math-foundations`) | planned |
| Séries temporais | estacionariedade, cointegração, GARCH, regime switching | — (reservado: `02-time-series`) | planned |
| Execução | microestrutura, slippage, impacto de mercado, TCA | — (reservado: `07-execution`) | planned |
| ML em finanças | features, walk-forward, overfitting | — (reservado: `08-ml-finance`) | planned |
| Dados de mercado | point-in-time, corporate actions, vendors, B3 vs US | — (reservado: `09-market-data`) | planned |

## Regra de manutenção

Uma nota nova custa **exatamente uma linha** no índice do seu domínio e **zero edições em
qualquer prompt de agente**. Nenhum agente cita nota por nome: os agentes citam este arquivo,
e este arquivo cita os índices de domínio. Se um prompt de agente começar a listar notas
individuais, a propriedade que faz este desenho escalar foi quebrada.

Quando um domínio planejado ganhar a primeira nota: crie o `_index.md` dele em
`quant/00-index/`, com o mesmo formato de tabela (`Nota | O que responde | Nível`), e **mova a
linha** da tabela de planejados para a de ativos, agora com wikilink. Enquanto o índice não
existir, a linha permanece sem link — link para arquivo inexistente quebra o verificador.
**No mesmo movimento, preencha a célula `Pasta`** com o caminho real que passou a existir —
o número reservado deixa de ser promessa e vira path. Linha ativa sem Pasta preenchida deixa
o agente sem como abrir a nota, que é a falha que essa coluna existe para impedir.

**Teto de tamanho: um índice de domínio passando de ~15–20 linhas deve ser dividido em
subdomínios, não engordado.** Acima disso a tabela deixa de ser escaneável e o agente passa a
lê-la como leria uma listagem de diretório — que é exatamente o custo que o salto 2 existe
para evitar. Dividir preserva a propriedade; crescer a destrói silenciosamente, porque o
índice continua existindo e parecendo funcionar enquanto já não filtra nada.

**Nota nova cujo tema já aparece em outro domínio ganha uma linha em [[quant/00-index/_topics|_topics]].** O teste é
dispersão entre domínios, não contagem de notas: se algum domínio responde a pergunta sozinho,
o tema pertence ao índice daquele domínio. Essa é a única exceção à regra de uma linha em um
lugar, e ela é deliberada — o mapa transversal mora num arquivo só, justamente para não obrigar
edição em N índices quando uma nota nova toca um tema comum.

O campo `Nível` **não é sinal de roteamento.** No vault inteiro a maioria esmagadora das notas
declara o mesmo valor, e há vocabulários concorrentes em uso (`intro`, `basic`, `intermediate`,
`advanced`). A coluna faz parte do formato e será normalizada depois; até lá, roteie pela
coluna "O que responde".
