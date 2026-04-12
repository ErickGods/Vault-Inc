---
tags: [reference, git]
status: active
level: advanced
updated: 2026-04-05
aliases: [Git Cheatsheet]
created: 2026-04-05
---

# Git Cheatsheet

Referência rápida de comandos Git organizados por categoria. Complementa [[git-advanced]] e [[github-actions]]. Para scripts de automação, veja [[bash-snippets]]. Filtros com regex em [[regex-cheatsheet]]. Deploy com [[deployment-strategies]].

---

## Branches

| Comando | Descrição | Exemplo |
|---------|-----------|---------|
| `git branch` | Listar branches locais | `git branch -a` (incluindo remotas) |
| `git branch <name>` | Criar branch | `git branch feature/login` |
| `git switch <name>` | Mudar de branch (moderno) | `git switch main` |
| `git switch -c <name>` | Criar e mudar de branch | `git switch -c fix/auth-bug` |
| `git branch -d <name>` | Deletar branch local (seguro) | `git branch -d feature/old` |
| `git branch -D <name>` | Forçar deleção de branch | `git branch -D wip/experiment` |
| `git push origin --delete <name>` | Deletar branch remota | `git push origin --delete fix/auth` |
| `git branch -m <old> <new>` | Renomear branch | `git branch -m master main` |
| `git branch --merged` | Listar branches já mergeadas | `git branch --merged main` |
| `git fetch --prune` | Remover referências remotas deletadas | `git fetch origin --prune` |

---

## Stash

| Comando | Descrição | Exemplo |
|---------|-----------|---------|
| `git stash` | Guardar mudanças não commitadas | `git stash` |
| `git stash push -m <msg>` | Stash com mensagem | `git stash push -m "wip: auth refactor"` |
| `git stash list` | Listar todos os stashes | `git stash list` |
| `git stash pop` | Aplicar e remover último stash | `git stash pop` |
| `git stash apply stash@{n}` | Aplicar stash específico sem remover | `git stash apply stash@{2}` |
| `git stash drop stash@{n}` | Remover stash específico | `git stash drop stash@{0}` |
| `git stash clear` | Remover todos os stashes | `git stash clear` |
| `git stash show -p stash@{n}` | Ver diff de um stash | `git stash show -p stash@{1}` |
| `git stash branch <name>` | Criar branch a partir de stash | `git stash branch fix/stashed` |
| `git stash push -- <file>` | Guardar arquivo específico | `git stash push -- src/auth.py` |

---

## Rebase

| Comando | Descrição | Exemplo |
|---------|-----------|---------|
| `git rebase <branch>` | Rebase sobre branch | `git rebase main` |
| `git rebase -i HEAD~<n>` | Rebase interativo (n commits) | `git rebase -i HEAD~5` |
| `git rebase --onto <new> <old> <branch>` | Rebase mudando base | `git rebase --onto main old-base feature` |
| `git rebase --continue` | Continuar após resolver conflito | `git rebase --continue` |
| `git rebase --abort` | Cancelar rebase em andamento | `git rebase --abort` |
| `git rebase --skip` | Pular commit atual no rebase | `git rebase --skip` |
| `git pull --rebase` | Pull com rebase (evita merge commit) | `git pull --rebase origin main` |

### Comandos do Rebase Interativo

| Ação | Abreviação | Descrição |
|------|------------|-----------|
| `pick` | `p` | Manter commit como está |
| `reword` | `r` | Alterar mensagem do commit |
| `edit` | `e` | Parar para editar o commit |
| `squash` | `s` | Fundir com commit anterior (mantém msgs) |
| `fixup` | `f` | Fundir descartando mensagem |
| `drop` | `d` | Remover commit |
| `exec` | `x` | Executar comando shell |

---

## Cherry-Pick

| Comando | Descrição | Exemplo |
|---------|-----------|---------|
| `git cherry-pick <hash>` | Aplicar commit específico | `git cherry-pick a1b2c3d` |
| `git cherry-pick <hash1>..<hash2>` | Aplicar range de commits | `git cherry-pick abc..def` |
| `git cherry-pick -n <hash>` | Aplicar sem commitar (staging) | `git cherry-pick -n a1b2c3d` |
| `git cherry-pick --continue` | Continuar após conflito | `git cherry-pick --continue` |
| `git cherry-pick --abort` | Cancelar cherry-pick | `git cherry-pick --abort` |

---

## Reflog

| Comando | Descrição | Exemplo |
|---------|-----------|---------|
| `git reflog` | Ver histórico completo de HEAD | `git reflog` |
| `git reflog show <branch>` | Reflog de branch específica | `git reflog show feature/auth` |
| `git checkout HEAD@{n}` | Ir para estado anterior | `git checkout HEAD@{3}` |
| `git reset --hard HEAD@{n}` | Restaurar estado anterior | `git reset --hard HEAD@{2}` |
| `git branch <name> HEAD@{n}` | Recriar branch deletada | `git branch recovered HEAD@{5}` |

> [!tip] Recuperar Commits Perdidos
> Se fez um reset acidental, `git reflog` mostra todos os estados do HEAD. Crie uma branch no hash desejado para recuperar o trabalho.

---

## Bisect

| Comando | Descrição | Exemplo |
|---------|-----------|---------|
| `git bisect start` | Iniciar busca binária | `git bisect start` |
| `git bisect bad` | Marcar commit atual como ruim | `git bisect bad` |
| `git bisect good <hash>` | Marcar commit como bom | `git bisect good v1.2.0` |
| `git bisect reset` | Finalizar bisect | `git bisect reset` |
| `git bisect run <script>` | Bisect automatizado | `git bisect run pytest tests/` |

```bash
# Workflow completo de bisect automatizado
git bisect start
git bisect bad HEAD
git bisect good v2.0.0
git bisect run bash -c "npm test 2>/dev/null | grep -q 'PASS'"
git bisect reset
```

---

## Aliases Úteis

```bash
# Adicionar ao ~/.gitconfig
[alias]
  # Log visual em grafo
  lg    = log --oneline --graph --decorate --all
  # Log compacto com autor e data
  ll    = log --oneline --decorate -20
  # Status curto
  s     = status -sb
  # Diff de staged
  ds    = diff --staged
  # Undo do último commit (mantém mudanças)
  undo  = reset --soft HEAD~1
  # Amend sem editar mensagem
  oops  = commit --amend --no-edit
  # Stash rápido
  save  = stash push -u -m
  # Limpar branches mergeadas
  clean-branches = "!git branch --merged main | grep -v 'main\\|\\*' | xargs git branch -d"
  # Ver quem mexeu em cada linha
  who   = blame -w -C -C -C
  # Listar aliases
  aliases = config --get-regexp alias
```

---

## Workflows Comuns

### Feature Branch Workflow

```bash
git switch main && git pull --rebase
git switch -c feature/JIRA-123-user-auth
# ... trabalho ...
git add -p                          # add interativo por hunk
git commit -m "feat: add JWT authentication"
git push -u origin feature/JIRA-123-user-auth
# abrir PR via gh pr create
```

### Hotfix em Produção

```bash
git switch main && git pull
git switch -c hotfix/fix-payment-bug
# ... fix ...
git commit -m "fix: correct payment rounding error"
git switch main && git merge --no-ff hotfix/fix-payment-bug
git tag -a v1.2.1 -m "Hotfix: payment rounding"
git push --follow-tags
```

### Sync de Fork

```bash
git remote add upstream https://github.com/original/repo.git
git fetch upstream
git switch main
git merge upstream/main
git push origin main
```

---

## Reset, Revert & Restore

| Comando | Descrição | Seguro em Produção |
|---------|-----------|-------------------|
| `git reset --soft HEAD~1` | Desfazer commit, manter stage | Sim (local) |
| `git reset --mixed HEAD~1` | Desfazer commit + stage | Sim (local) |
| `git reset --hard HEAD~1` | Descartar tudo do último commit | Cuidado |
| `git revert <hash>` | Criar commit que desfaz outro | Sim |
| `git restore <file>` | Descartar mudanças no working dir | Cuidado |
| `git restore --staged <file>` | Remover do stage (não descarta) | Sim |

---

> [!info] Ver também
> - Fluxos avançados de branching: [[git-advanced]]
> - Automação com Actions: [[github-actions]]
> - Scripts de automação: [[bash-snippets]]
> - Expressões regulares para filtros: [[regex-cheatsheet]]
