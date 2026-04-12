---
tags: [skill, tools, git]
status: active
level: advanced
updated: 2026-04-05
created: 2026-04-05
aliases: [Git, Git Advanced]
---

# Git Advanced

## Overview

Git vai muito além de `commit`, `push` e `pull`. No nível avançado, o fluxo de trabalho envolve **reescrita de histórico**, **recuperação de dados**, **automação via hooks** e **estratégias para monorepos**. Dominar essas ferramentas é essencial para manter um histórico limpo, reversível e auditável — especialmente em pipelines que integram com [[github-actions]], [[gitlab-ci]] e [[deployment-strategies]].

Esta nota cobre as técnicas que separam o desenvolvedor que usa Git do que **entende** Git.

---

## Core Concepts

### Interactive Rebase

Interactive rebase (`git rebase -i`) permite editar, reordenar, mesclar e dividir commits antes de publicar uma branch.

```bash
# Rebase interativo dos últimos 5 commits
git rebase -i HEAD~5
```

Commandos disponíveis no editor:

| Command  | Description                                      |
|----------|--------------------------------------------------|
| `pick`   | Keep commit as-is                                |
| `reword` | Change commit message                            |
| `edit`   | Stop to amend the commit (content + message)     |
| `squash` | Meld into previous commit, merge messages        |
| `fixup`  | Meld into previous commit, discard this message  |
| `drop`   | Remove the commit entirely                       |
| `exec`   | Run a shell command after the commit             |

```bash
# Squash automatico para commits marcados como "fixup!"
git rebase -i --autosquash HEAD~10

# Criar commit de fixup para o commit mais recente com "feat"
git commit --fixup=$(git log --oneline | grep "feat" | head -1 | awk '{print $1}')
```

### Worktrees

Git worktrees permitem checar múltiplas branches **simultaneamente** em diretórios separados, sem `stash` ou `clone` duplicado.

```bash
# Criar worktree para hotfix sem sair da branch atual
git worktree add ../hotfix-1.2.3 origin/release/1.2.3

# Listar worktrees ativos
git worktree list

# Remover worktree após uso
git worktree remove ../hotfix-1.2.3
git worktree prune
```

> [!tip] Worktrees + CI
> Use worktrees em pipelines do [[github-actions]] para rodar testes de múltiplas branches em paralelo num mesmo runner sem reclonagem.

### Bisect — Manual e Automatizado

`git bisect` faz busca binária no histórico para encontrar o commit que introduziu um bug.

```bash
# Modo manual
git bisect start
git bisect bad HEAD
git bisect good v2.3.0
# Git faz checkout do commit do meio; teste e marque:
git bisect good   # ou
git bisect bad
# Ao final:
git bisect reset

# Modo automatizado com script de teste
git bisect start HEAD v2.3.0
git bisect run ./scripts/test-regression.sh
```

```bash
# Script de teste para bisect automatizado
#!/usr/bin/env bash
# test-regression.sh — exit 0 = good, exit 1 = bad
npm ci --silent && npm test -- --testNamePattern="checkout flow" --silent
```

### Reflog Recovery

O `reflog` guarda **todo movimento de HEAD**, permitindo recuperar commits "perdidos" após reset, rebase ou drop.

```bash
# Ver histórico completo do reflog
git reflog show --all --date=iso

# Recuperar branch deletada
git reflog | grep "checkout: moving from deleted-branch"
git checkout -b recovered-branch <sha>

# Desfazer um rebase que deu errado
git reflog | grep "rebase"
git reset --hard HEAD@{3}
```

> [!warning] Reflog tem TTL
> Por padrão o reflog expira em **90 dias** (30 para commits não alcançáveis). Commits além desse prazo são varridos pelo `git gc`. Configure `gc.reflogExpire` para estender.

---

## Patterns

### Subtree vs Submodule

| Feature           | Submodule                        | Subtree                         |
|-------------------|----------------------------------|---------------------------------|
| History           | Pointer only (separate repo)     | Fully embedded in parent        |
| Clone behavior    | Requires `--recurse-submodules`  | Transparent, no extra steps     |
| Updates           | Manual `git submodule update`    | `git subtree pull`              |
| Contributor UX    | Complex, error-prone             | Simple, no special knowledge    |
| Monorepo fit      | Poor                             | Good                            |

```bash
# Adicionar subtree
git subtree add --prefix=libs/ui git@github.com:org/ui-lib.git main --squash

# Atualizar subtree
git subtree pull --prefix=libs/ui git@github.com:org/ui-lib.git main --squash

# Extrair subtree para novo repositório
git subtree split --prefix=libs/ui -b split-ui
git push git@github.com:org/new-ui-lib.git split-ui:main
```

### Hooks

Hooks são scripts executados automaticamente em eventos Git. Usados para enforçar qualidade antes de integrar com [[deployment-strategies]].

```bash
# .git/hooks/pre-commit — bloquear commits com secrets
#!/usr/bin/env bash
set -e
if git diff --cached --name-only | xargs grep -lE "(AKIA|password\s*=|secret\s*=)" 2>/dev/null; then
  echo "ERROR: Possible secret detected in staged files."
  exit 1
fi
```

```bash
# .git/hooks/commit-msg — enforçar Conventional Commits
#!/usr/bin/env bash
commit_msg=$(cat "$1")
pattern="^(feat|fix|docs|style|refactor|test|chore|ci|perf|revert)(\(.+\))?: .{1,72}$"
if ! echo "$commit_msg" | grep -qP "$pattern"; then
  echo "ERROR: Commit message does not follow Conventional Commits format."
  echo "Expected: <type>(<scope>): <description>"
  exit 1
fi
```

```bash
# .git/hooks/pre-push — rodar testes antes de push
#!/usr/bin/env bash
set -e
echo "Running pre-push checks..."
npm run lint && npm run test:unit
```

> [!info] Compartilhar hooks com a equipe
> `.git/hooks` não é versionado. Use `core.hooksPath` apontando para um diretório versionado:
> ```bash
> git config core.hooksPath .githooks
> ```

### Cherry-Pick Strategies

```bash
# Cherry-pick simples
git cherry-pick <sha>

# Range de commits (não inclui o primeiro)
git cherry-pick abc123..def456

# Cherry-pick sem commit imediato (staging apenas)
git cherry-pick --no-commit <sha>

# Cherry-pick com estratégia de merge explícita
git cherry-pick -X theirs <sha>

# Ao resolver conflito durante cherry-pick
git cherry-pick --continue
git cherry-pick --abort
```

### Monorepo — Sparse Checkout

Sparse checkout permite fazer checkout de apenas subdiretórios de um monorepo gigante, economizando disco e tempo de clone.

```bash
# Clone com sparse checkout
git clone --filter=blob:none --sparse git@github.com:org/monorepo.git
cd monorepo

# Definir padrões de sparse
git sparse-checkout set apps/api libs/shared

# Adicionar mais caminhos
git sparse-checkout add apps/web

# Ver configuração atual
git sparse-checkout list
```

### filter-repo

`git filter-repo` (substituto do `git filter-branch`) reescreve histórico com muito mais performance.

```bash
# Remover arquivo sensível de todo o histórico
git filter-repo --path secrets.env --invert-paths

# Renomear diretório no histórico
git filter-repo --path-rename old-name/:new-name/

# Extrair subdiretório para novo repo
git filter-repo --subdirectory-filter apps/api
```

### rerere (Reuse Recorded Resolution)

`rerere` grava resoluções de conflitos e as reaplicam automaticamente em rebases futuros.

```bash
# Habilitar rerere globalmente
git config --global rerere.enabled true

# Ver resoluções gravadas
git rerere status
git rerere diff

# Limpar resoluções antigas
git rerere gc
```

---

## Gotchas

> [!danger] Nunca reescreva histórico público
> `rebase`, `filter-repo`, `reset --hard` em branches já publicadas causam divergência para todos os colaboradores. Limite reescrita a branches pessoais antes do merge.

> [!warning] Submodule state hell
> Submodules ficam em "detached HEAD" após `git submodule update`. Sempre verifique com `git submodule status` antes de commitar alterações dentro de um submodule.

> [!warning] Cherry-pick duplica contexto
> Cherry-pick cria um **novo commit** com o mesmo diff. Se a branch original for mergeada depois, o histórico terá o patch duas vezes, podendo causar conflitos ou duplicação em `git log`.

---

## Snippets

```bash
# Ver todos os commits que tocaram um arquivo, incluindo renames
git log --follow --diff-filter=R --summary -- path/to/file.ts

# Encontrar quem introduziu uma linha específica
git log -S "texto exato da linha" --source --all

# Comparar branch local com remota antes de push
git log origin/main..HEAD --oneline

# Listar tags ordenadas por data de criação (semver)
git tag --sort=-version:refname | head -10

# Stash apenas arquivos não-rastreados
git stash push -u -m "WIP: new files only"

# Contar commits por autor no último mês
git shortlog -sn --after="1 month ago"
```

---

## References

- [Pro Git Book — Rewriting History](https://git-scm.com/book/en/v2/Git-Tools-Rewriting-History)
- [git filter-repo documentation](https://github.com/newren/git-filter-repo)
- [Conventional Commits specification](https://www.conventionalcommits.org/)
- [Git Worktrees — official docs](https://git-scm.com/docs/git-worktree)

---

## Related

- [[github-actions]]
- [[gitlab-ci]]
- [[deployment-strategies]]
- [[git-cheatsheet]]
- [[docker]]
