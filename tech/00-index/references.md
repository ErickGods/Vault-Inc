---
house: tech
domain: references
type: index
updated: 2026-08-01
---

# Índice — Referências

Tabelas de consulta: material para conferir um número ou uma sintaxe no meio do trabalho, não
para ler de ponta a ponta. As três notas moram em `tech/07-references/`.

| Nota | O que responde | Nível |
|---|---|---|
| [[big-o-notation]] | Estimar o custo de uma escolha antes de escrevê-la: a hierarquia de complexidades com valores concretos por tamanho de entrada (O(n²) já é 10¹² em n = 1 milhão), ordenação com melhor, médio, pior, espaço e estabilidade lado a lado, busca com o requisito de cada algoritmo, grafos por V e E, e as operações de cada estrutura de dados — arrays e listas, árvores (incluindo a B-Tree, que é o índice padrão do Postgres), hash table, heap, stack, queue e deque. Traz análise amortizada explicando por que `append` em array dinâmico é O(1) apesar do resize, e a tabela de custo das operações Python que mais surpreende na prática: `x in list` é O(n) contra O(1) em set, e `s += chunk` dentro de loop é O(n²) no total. O que essa nota acrescenta a decorar tabela é a seção **quando O(n²) vence O(n log n)** — n abaixo de 50, array quase ordenado, string curta em hash map: Big O ignora constantes, e para n pequeno são as constantes que decidem. | advanced |
| [[git-cheatsheet]] | Achar o comando exato sem tentativa e erro no repositório de verdade: branches com a forma moderna `switch`, `--merged` e `fetch --prune`; stash por arquivo, com mensagem e virando branch; rebase incluindo `--onto` para trocar a base, com a tabela de ações do modo interativo (`pick`, `reword`, `edit`, `squash`, `fixup`, `drop`, `exec`); cherry-pick por range e sem commitar; reflog como rede de segurança depois de reset acidental, com a receita de recriar branch a partir de `HEAD@{n}`; e bisect automatizado por `bisect run`, que encontra o commit culpado sem intervenção. Traz aliases prontos para `~/.gitconfig`, três workflows fechados de ponta a ponta (feature branch, hotfix com tag e `--follow-tags`, sync de fork por upstream) e a tabela de reset, revert e restore anotada pelo que é seguro fazer em produção. | advanced |
| [[regex-cheatsheet]] | Escrever ou ler uma expressão regular com intenção: quantificadores greedy contra lazy com o exemplo que expõe a diferença, os tipos de grupo (capturante, não-capturante, nomeado nas duas sintaxes — Python e JS/PCRE —, backreference e atômico), as quatro combinações de lookahead e lookbehind, classes de caractere, âncoras, e a tabela de flags comparando Python com JavaScript, incluindo o modo verbose que permite regex comentada em várias linhas. A metade prática é o catálogo de padrões prontos e testáveis: e-mail, URL, IPv4, semver com grupos nomeados, data ISO, telefone brasileiro nos três formatos, UUID, mascaramento de cartão e JWT — com uso em Python (`compile` para reaproveitar, `groupdict`, `finditer` com posições) e em TypeScript (`matchAll`, grupos nomeados). O aviso que evita incidente de produção: backtracking catastrófico do tipo `(a+)+b` é exponencial no pior caso. | advanced |
