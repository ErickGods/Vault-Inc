---
house: tech
domain: templates
type: index
updated: 2026-08-01
---

# Índice — Templates

Estruturas prontas para os artefatos recorrentes desta casa. Não são conhecimento: são o
formato que o conhecimento assume quando vira entrega. Os três arquivos moram em
`tech/08-templates/`.

**Um deles alimenta este próprio vault e os outros dois não.** `technology-note` é o molde das
notas de `tech/01-skills/` — preenchê-lo produz conhecimento que fica aqui. `project-template` e
`weekly-review` produzem instância operacional, que carrega nome de projeto, prazo e estado de
trabalho: essa instância vai para o repositório privado, e só o molde permanece neste vault.

Os três são scaffolds do Templater: ao serem invocados dentro do Obsidian eles abrem prompts,
montam o frontmatter com as respostas e renomeiam o arquivo. Ler o `.md` cru mostra o bloco
`<%* ... %>` no topo antes do corpo — isso é o script, não o template.

Os campos entre chaves duplas — `{{NNNN}}` e semelhantes — são placeholders. O verificador de
links os ignora por forma, em qualquer pasta, então não os transforme em wikilink.

> `technology-note` chamava-se `skill-template`. O nome foi trocado porque "skill" já designa
> outra coisa no repositório — a skill do Claude Code, em `.claude/skills/` — e a colisão fazia
> agente abrir o arquivo errado.

| Template | Quando usar | Nível |
|---|---|---|
| [[technology-note]] | Abrir uma nota nova de tecnologia em `tech/01-skills/` com a mesma anatomia das que já existem: Overview com o problema que a tecnologia resolve, 3 a 7 Core Concepts, Patterns & Best Practices com o trade-off de cada um, **Common Gotchas** — a seção que carrega o valor real da nota, porque é onde entra o que só se aprende errando —, Code Snippets mínimos e executáveis, References e Related. Os prompts do Templater pedem categoria, nome da tecnologia, nível e aliases, e renomeiam o arquivo para kebab-case a partir do nome informado. | intermediate |
| [[project-template]] | Abrir a página de acompanhamento de um projeto: objetivo com critério de sucesso mensurável e escopo negativo declarado, tabela de stack por camada (frontend, backend, banco, auth, infra/CI, monitoramento), diagrama de arquitetura, backlog em sintaxe do plugin Tasks, timeline por milestone em data ISO, e um log corrido de decisão e bloqueio — o que serve de contexto sem ter peso de ADR. Prompts de nome, status, dono e URL do repositório; o arquivo é renomeado a partir do nome do projeto. | intermediate |
| [[weekly-review]] | Fechar a semana com registro comparável em vez de impressão: destaque em uma linha, energia e foco em escala de 1 a 5 escolhidos por prompt, wins, challenges, learnings e de 3 a 5 metas datadas para a semana seguinte. Traz uma query Dataview que lista as tasks concluídas dentro do intervalo — o que evita a revisão baseada em memória — mais um snapshot de métricas e os links para a revisão anterior e a seguinte, que encadeiam a série. | intro |
