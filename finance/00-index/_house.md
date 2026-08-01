---
house: finance
type: house-index
updated: 2026-07-29
---

# Casa Finance — Índice Mestre

Este é o primeiro arquivo a carregar ao trabalhar nesta casa. Ele não contém conhecimento;
contém o mapa. Use assim: identifique na tabela de domínios ativos qual território cobre a
tarefa, carregue o índice daquele domínio, leia a coluna "O que responde" e abra **apenas**
as notas que a tarefa exige. Três saltos, e nada de varrer o vault com Glob.

**Como abrir uma nota.** Wikilinks **dentro desta casa** não carregam caminho — são
identificadores, não paths. O arquivo fica em `<pasta>/<nome-da-nota>.md`, onde `<pasta>` vem da
coluna **Pasta** da tabela abaixo. Exemplo: a nota `compound-interest`, listada em
[[fundamentals]], é o arquivo `finance/01-fundamentals/compound-interest.md`.

**Link que cruza casa é a exceção e carrega o caminho inteiro.** `_house.md` e `_topics.md`
existem em `finance/`, `quant/` e — depois da E3 — em `tech/`, então o basename sozinho é
ambíguo. Por isso `wacc` cita `[[quant/03-factor-models/capm]]` e não `[[capm]]`. Ao linkar para
fora desta casa, sempre qualifique; o verificador reporta link nu para basename ambíguo.

**Dois domínios desta casa têm subpastas** — [[investments]] (5) e [[analysis]] (3). Para eles
a célula **Pasta** dá apenas a **raiz do domínio**, e o caminho exato mora nos **títulos de
seção do próprio índice de domínio**: em [[investments]], a seção "Renda fixa" declara
`finance/02-investments/fixed-income/`, e é ali que a nota `tesouro-direto` mora — não em
`finance/02-investments/`. Um agente que parar neste arquivo para esses dois domínios vai
montar um caminho que não existe. Desça até o índice do domínio e leia o título da seção antes
de abrir o arquivo.

Os índices de domínio e o `_topics.md` têm pasta fixa em vez de vir da tabela: ficam sempre em
`finance/00-index/`, com o nome do arquivo igual ao do wikilink — [[markets]] é o arquivo
`finance/00-index/markets.md`.

> **Não deduza o caminho.** Os prefixos numéricos **não são deriváveis** do nome do domínio nem
> da ordem em que os domínios aparecem aqui. Leia a coluna Pasta; inferir o prefixo leva a um
> caminho inexistente, e o fallback natural (`ls -R`) é exatamente a varredura que a regra
> proíbe.

## Domínios ativos

| Domínio | Índice | Pasta | Cobre |
|---|---|---|---|
| Fundamentos | [[fundamentals]] | `finance/01-fundamentals/` | valor no tempo, juros compostos, inflação, risco e retorno, diversificação, as três demonstrações |
| Investimentos | [[investments]] | `finance/02-investments/` (5 subpastas) | ações e B3, renda fixa e curva de juros, fundos e ETFs, FIIs, opções e futuros, commodities, cripto, private equity |
| Análise | [[analysis]] | `finance/03-analysis/` (3 subpastas) | valuation por DCF e por múltiplos, frameworks de qualidade e de deep value, ciclos macro e indicadores, análise técnica |
| Finanças pessoais | [[personal-finance]] | `finance/04-personal-finance/` | escada patrimonial, orçamento, reserva de emergência, FIRE, tributação do investidor PF, seguros |
| Contabilidade | [[accounting]] | `finance/05-accounting/` | DRE, balanço, fluxo de caixa, indicadores e DuPont, detecção de manipulação contábil |
| Mercados | [[markets]] | `finance/06-markets/` | mecânica da ordem e do book, infraestrutura da B3, participantes e fluxo, ciclos de mercado, mercado americano |
| Psicologia | [[psychology]] | `finance/07-psychology/` | prospect theory, catálogo de vieses cognitivos, ciclo emocional do investidor, tolerância vs capacidade de risco |
| Frameworks de decisão | [[frameworks]] | `finance/08-frameworks/` | alocação estratégica e rebalanceamento, checklist de due diligence |
| Glossário | [[glossary]] | `finance/09-glossary/` | siglas brasileiras e vocabulário técnico de A a Z |
| Snippets | [[snippets]] | `finance/10-snippets/` | cheatsheets de valuation e de indicadores, código Python de análise |
| Templates | [[templates]] | `finance/11-templates/` | estruturas dos entregáveis recorrentes: cobertura de ação, earnings call, revisão de carteira, trade journal |

## Temas transversais

Se a pergunta é sobre uma **preocupação** e não sobre um território — tributação do investidor,
custo que corrói retorno, sensibilidade a juros, câmbio, liquidez, viés cognitivo, concentração
do mercado brasileiro, correlação em crise — comece por [[_topics]]. Nenhum domínio da tabela
acima responde essas perguntas sozinho: tributação do investidor PF atravessa seis domínios, e
escolher um deles aqui perde material que está nos outros cinco. O `_topics.md` diz qual nota
abrir primeiro para cada tema.

## Regra de manutenção

Uma nota nova custa **exatamente uma linha** no índice do seu domínio e **zero edições em
qualquer prompt de agente**. Nenhum agente cita nota por nome: os agentes citam este arquivo,
e este arquivo cita os índices de domínio. Se um prompt de agente começar a listar notas
individuais, a propriedade que faz este desenho escalar foi quebrada. Pelo mesmo motivo, **este
arquivo não lista notas** — ele mapeia domínios. Nota só aparece no índice do seu domínio.

**Teto de tamanho: um índice de domínio passando de ~15–20 linhas deve ser dividido em
subdomínios, não engordado.** Acima disso a tabela deixa de ser escaneável e o agente passa a
lê-la como leria uma listagem de diretório — que é exatamente o custo que o salto 2 existe para
evitar. Dividir preserva a propriedade; crescer a destrói silenciosamente, porque o índice
continua existindo e parecendo funcionar enquanto já não filtra nada.

**O teto vale para tabela plana; subseção é o remédio.** [[investments]] está em 17 linhas
distribuídas em 5 subseções de 3 a 4 linhas cada, e [[analysis]] em 15 linhas em 3 subseções de
4 a 6 — o agente escaneia títulos de subseção, não dezessete linhas seguidas. Quando um domínio
chegar ao teto, o primeiro movimento é abrir subseções por território; separar em índices
distintos só quando nem as subseções segurarem.

> **Estes números defasam.** Foram conferidos em 2026-07-29 e já estavam errados uma vez —
> o texto dizia 16 e 11 depois que seis notas novas entraram. Como a regra de teto é avaliada
> contra eles, conferir antes de usar como argumento:
> ```bash
> for f in finance/00-index/*.md; do printf "%-20s %2d\n" "$(basename $f .md)" "$(grep -c '^| \[\[' $f)"; done
> ```

**O teto entre domínios não é o teto que aperta.** Medido num teste real de cobertura de equity:
o agente abriu 10 de 74 notas da casa (13,5%) e 3 de 17 em [[investments]] — mas **4 das 6 notas
de `analysis/fundamental`**. O índice economiza contexto **entre** domínios e quase nada **dentro
da subseção onde a tarefa cai**, porque ali as notas são mutuamente relevantes por construção.
Se uma subseção crescer mantendo essa densidade, o custo por tarefa cresce junto e o índice
continua parecendo funcionar. **Vigie a subseção, não o domínio.**

**Nota nova cujo tema já aparece em outro domínio ganha uma linha em [[_topics]].** O teste é
dispersão entre domínios, não contagem de notas: se algum domínio responde a pergunta sozinho,
o tema pertence ao índice daquele domínio. Essa é a única exceção à regra de uma linha em um
lugar, e ela é deliberada — o mapa transversal mora num arquivo só, justamente para não obrigar
edição em N índices quando uma nota nova toca um tema comum.

O campo `Nível` **não é sinal de roteamento.** No vault inteiro os valores são fortemente
enviesados e há vocabulários concorrentes em uso (`intro`, `basic`, `intermediate`,
`advanced`). A coluna faz parte do formato e será normalizada depois; até lá, roteie pela
coluna "O que responde".
