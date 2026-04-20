---
tags: [claude-code, core-features, worktrees, git, isolamento]
status: active
level: intermediate
updated: 2026-04-19
created: 2026-04-19
---

# Worktrees — Isolamento com Git Worktrees

## O que são Git Worktrees

Um git worktree é um checkout adicional do mesmo repositório em um diretório diferente. Em termos simples: você tem um repositório Git, e pode ter múltiplos diretórios de trabalho ("working trees") apontando para o mesmo repositório, cada um numa branch diferente.

O repositório original é chamado de "main worktree" ou "linked worktree principal". Qualquer checkout adicional é um "linked worktree". Todos compartilham o mesmo histórico Git, os mesmos objetos (commits, blobs, trees) e os mesmos refs — mas cada um tem seu próprio working directory, seu próprio index (staging area) e sua própria branch ativa.

```
Repositório Git
│
├── /workspace/meu-projeto/          (main worktree — branch: main)
│   ├── src/
│   ├── .git/                        (diretório Git completo)
│   └── ...
│
├── /workspace/meu-projeto-feature-auth/   (linked worktree — branch: feature/auth)
│   ├── src/
│   ├── .git → ../meu-projeto/.git   (symlink, compartilha o .git)
│   └── ...
│
└── /workspace/meu-projeto-fix-payment/    (linked worktree — branch: fix/payment)
    ├── src/
    ├── .git → ../meu-projeto/.git   (symlink)
    └── ...
```

---

## Por que o Claude Code Usa Worktrees

O uso de worktrees pelo Claude Code resolve o problema de isolamento em tarefas paralelas. Sem worktrees:

**Problema:** Dois subagentes trabalhando no mesmo diretório podem criar conflitos de arquivo. Agente A edita `src/auth.ts` enquanto Agente B também modifica `src/auth.ts` para um propósito diferente. Ambos sobrescrevem as mudanças um do outro.

**Solução:** Cada subagente recebe seu próprio worktree (= diretório de trabalho isolado, numa branch própria). As mudanças de cada agente ficam no seu worktree isolado até o merge deliberado.

> [!info] A analogia com o mundo do desenvolvimento humano: worktrees são como ter vários desenvolvedores trabalhando em branches diferentes ao mesmo tempo, cada um no seu ambiente, sem se atrapalhar. O merge acontece quando o trabalho está pronto.

---

## Como Claude Code Usa Worktrees para Isolamento

Quando o Agent tool é chamado com `isolation: "worktree"`, o Claude Code:

1. Cria automaticamente uma nova branch a partir da branch atual
2. Cria um linked worktree em um diretório temporário
3. Inicia o subagente com o working directory apontando para esse worktree
4. Quando o subagente termina, o orquestrador pode fazer merge ou cherry-pick das mudanças

```
Orquestrador (main worktree: /workspace/projeto — branch: main)
│
├── Despacha Subagente A com isolation: "worktree"
│   └── Subagente A trabalha em /workspace/projeto-agent-a-xyz (branch: agent/a-xyz)
│
└── Despacha Subagente B com isolation: "worktree"
    └── Subagente B trabalha em /workspace/projeto-agent-b-abc (branch: agent/b-abc)

[Ambos trabalham em paralelo sem se atrapalhar]

Orquestrador faz merge:
git merge agent/a-xyz
git merge agent/b-abc
```

---

## Setup Manual de Worktrees

### Criar um Worktree

```bash
# Criar worktree com nova branch (mais comum)
git worktree add ../meu-projeto-feature feature/nova-funcionalidade

# Criar worktree a partir de branch existente
git worktree add ../meu-projeto-hotfix hotfix/critical-bug

# Criar worktree a partir de commit específico (detached HEAD)
git worktree add ../meu-projeto-review abc1234

# Criar worktree com branch nova a partir de origin
git worktree add -b feature/oauth2 ../meu-projeto-oauth2 origin/main
```

### Verificar Worktrees Ativos

```bash
git worktree list
```

Output:
```
/workspace/meu-projeto             abc1234 [main]
/workspace/meu-projeto-auth        def5678 [feature/auth]
/workspace/meu-projeto-payment     ghi9012 [fix/payment]
```

### Mover para um Worktree e Trabalhar

```bash
cd /workspace/meu-projeto-auth
# Trabalhe normalmente — git status, git add, git commit, etc.
git add src/auth/oauth.ts
git commit -m "feat(auth): implementa OAuth2 com Google"
```

### Fazer Merge de um Worktree no Principal

```bash
# Voltar para o worktree principal
cd /workspace/meu-projeto

# Merge da feature
git merge feature/auth

# Ou, se quiser manter histórico linear
git rebase feature/auth

# Ou cherry-pick de commits específicos
git cherry-pick abc123 def456
```

### Remover um Worktree

```bash
# Remover o worktree (mantém a branch)
git worktree remove /workspace/meu-projeto-auth

# Remover forçado (mesmo com mudanças não commitadas)
git worktree remove --force /workspace/meu-projeto-auth

# Limpar referências a worktrees deletados manualmente
git worktree prune
```

---

## Workflow Completo com Worktrees

### Cenário: Implementar 3 features em paralelo

```bash
# Branch principal: main
# Criar 3 worktrees para trabalho paralelo

git worktree add -b feature/notifications ../projeto-notifications main
git worktree add -b feature/payments ../projeto-payments main
git worktree add -b feature/analytics ../projeto-analytics main

# Verificar
git worktree list
# /workspace/projeto                 a1b2c3d [main]
# /workspace/projeto-notifications   a1b2c3d [feature/notifications]
# /workspace/projeto-payments        a1b2c3d [feature/payments]
# /workspace/projeto-analytics       a1b2c3d [feature/analytics]

# Trabalhar em cada um (pode ser em parallel com subagentes)
# Cada worktree evolui independentemente

# Após conclusão, merge seletivo
cd /workspace/projeto           # volta ao principal
git merge feature/notifications # primeiro, sem conflitos
git merge feature/payments      # resolver conflitos se houver
git merge feature/analytics     # resolver conflitos se houver

# Limpar
git worktree remove /workspace/projeto-notifications
git worktree remove /workspace/projeto-payments
git worktree remove /workspace/projeto-analytics

# Deletar branches se não precisar mais
git branch -d feature/notifications feature/payments feature/analytics
```

---

## EnterWorktree / ExitWorktree Tools

Claude Code disponibiliza duas ferramentas específicas para navegação entre worktrees durante uma sessão:

### EnterWorktree

Muda o contexto de trabalho do Claude para um worktree específico. Após chamar EnterWorktree, todas as operações de arquivo (Read, Write, Edit, Bash) passam a ocorrer no contexto do worktree destino.

```
// Parâmetros da ferramenta EnterWorktree:
{
  "worktree_path": "/workspace/projeto-feature-auth"
}
```

Após EnterWorktree:
- `pwd` retorna o path do worktree destino
- Operações de arquivo são relativas ao novo worktree
- O estado Git (git status, git log) reflete a branch do worktree destino

### ExitWorktree

Retorna ao worktree de origem (o worktree em que o agente iniciou a sessão).

```
// Sem parâmetros necessários — retorna ao worktree original
{}
```

### Exemplo de Uso

```
Orquestrador em /workspace/projeto (branch: main)

1. Cria feature branch:
   Bash: git worktree add -b feature/cache ../projeto-cache main

2. Entra no worktree:
   EnterWorktree: /workspace/projeto-cache

3. Implementa a feature (todas as operações ocorrem em projeto-cache):
   Read, Write, Edit, Bash...

4. Commita no worktree:
   Bash: git add . && git commit -m "feat(cache): implementa Redis cache layer"

5. Sai do worktree:
   ExitWorktree

6. Faz merge no main:
   Bash: git merge feature/cache

7. Limpa:
   Bash: git worktree remove /workspace/projeto-cache
```

---

## Worktrees e Subagentes

A combinação mais poderosa: múltiplos subagentes com `isolation: "worktree"`, cada um em seu próprio worktree, rodando em background.

```
Orquestrador:
1. Despacha 3 subagentes em background, cada um com isolation: "worktree"

   Subagente A (worktree: agent-branch-1):
   "Implemente o sistema de cache Redis para as queries de usuários.
    Faça commit de todas as mudanças antes de terminar."

   Subagente B (worktree: agent-branch-2):
   "Implemente o sistema de notificações por email usando SendGrid.
    Faça commit de todas as mudanças antes de terminar."

   Subagente C (worktree: agent-branch-3):
   "Implemente o dashboard de analytics com os novos eventos.
    Faça commit de todas as mudanças antes de terminar."

2. Aguarda todos terminarem

3. Revisa os resultados de cada branch

4. Faz merge seletivo:
   git merge agent-branch-1  # cache
   git merge agent-branch-2  # notificações
   git merge agent-branch-3  # analytics
   # Resolve conflitos se houver

5. Testa o resultado final
```

---

## Quando Usar Worktrees vs Não Usar

### Use Worktrees Quando

| Situação | Por quê Worktrees |
|----------|------------------|
| Múltiplos subagentes em paralelo | Evita conflitos de arquivo |
| Features longas que precisam maturar | Mantém main limpo |
| Hotfix enquanto feature branch está ativa | Não interfere no trabalho em progresso |
| Experimentação que pode ser descartada | Worktrees podem ser removidos sem merge |
| Code review de PR de outra pessoa | Checkout limpo sem afetar seu trabalho |
| Comparar versões diferentes do código | Dois worktrees = dois terminais simultâneos |

### Não Precisa de Worktrees Quando

| Situação | Por quê Não |
|----------|------------|
| Task simples de 1-2 arquivos | Overhead desnecessário |
| Agente único sem paralelismo | Não há conflitos a evitar |
| Mudanças globais (refatoração de naming) | Mais simples direto na branch |
| Hotfix pequeno em produção | Simples checkout direto |
| Exploração/prototipagem rápida | Worktree é overhead desnecessário |

---

## Gotchas e Limitações

> [!warning] Uma branch só pode estar ativa em um worktree por vez. Você não pode ter `feature/auth` em dois worktrees simultaneamente. Cada branch = no máximo um worktree.

> [!warning] Arquivos não versionados (`.gitignore`d) NÃO são copiados para o worktree. O `.env` local não existe no novo worktree. Configure isso antes de rodar o subagente.

> [!info] Worktrees compartilham o mesmo `.git` — o que significa que `git fetch`, `git remote add` e outros comandos que afetam o repositório afetam todos os worktrees simultaneamente. Isso é um feature, não um bug.

> [!warning] `npm install` em um worktree cria um `node_modules` separado naquele worktree. Em projetos grandes com muitas dependências, múltiplos worktrees = múltiplos node_modules = muito espaço em disco.

> [!tip] Para evitar duplicar `node_modules`, considere configurar o projeto para usar um `node_modules` compartilhado via symlink, ou use pnpm (que já compartilha o store globalmente).

---

## Worktrees na Prática: Desenvolvimento de Feature Complexa

### Cenário Real

Feature: "Implementar pagamentos com Stripe"
- Envolve: schema de banco, backend, frontend, testes, documentação
- Estimativa: 2-3 dias de trabalho
- Risco: muitos arquivos modificados, possibilidade de quebrar coisas

### Setup

```bash
# Criar worktree dedicado para a feature
git worktree add -b feature/stripe-integration ../projeto-stripe main

# Entrar no worktree
cd /workspace/projeto-stripe

# Configurar .env (não versionado, precisa ser criado manualmente)
cp .env.example .env
echo "STRIPE_SECRET_KEY=sk_test_..." >> .env

# Instalar dependências (se houver novas)
npm install stripe @stripe/stripe-js

# Trabalhar...
```

### Durante o Desenvolvimento

```bash
# Commits frequentes no worktree (não afetam main)
git add src/payments/stripe.service.ts
git commit -m "feat(payments): adiciona cliente Stripe"

git add src/payments/stripe.routes.ts
git commit -m "feat(payments): adiciona endpoints de checkout"

# Ver status do seu trabalho
git log --oneline main..HEAD
# abc123 feat(payments): adiciona endpoints de checkout
# def456 feat(payments): adiciona cliente Stripe
```

### Finalização e Merge

```bash
# Voltar ao main
cd /workspace/projeto

# Atualizar main (outros commits podem ter chegado)
git pull origin main

# Merge
git merge feature/stripe-integration

# Se houver conflitos, resolver e commitar
git add .
git commit -m "merge: integra feature/stripe-integration"

# Limpar
git worktree remove /workspace/projeto-stripe
git branch -d feature/stripe-integration
```

---

## Configuração de Node.js com Múltiplos Worktrees

Para evitar o problema de `node_modules` duplicados:

```bash
# Opção 1: Usar pnpm (já compartilha store globalmente)
npm install -g pnpm
pnpm install  # Em cada worktree, links simbólicos ao store central

# Opção 2: Symlink manual (não recomendado — pode causar problemas)
cd /workspace/projeto-feature
ln -s /workspace/projeto/node_modules ./node_modules

# Opção 3: Turborepo (para monorepos)
# Turborepo cache funciona bem com worktrees
```

---

## Related

- [[subagents]] — Worktrees são o mecanismo de isolamento para subagentes
- [[agent-teams]] — Times de agentes se beneficiam de worktrees para paralelismo
- [[permissions-and-safety]] — Permissões no contexto de worktrees isolados
- [[hooks-system]] — Hooks podem detectar mudanças de worktree e agir
- [[00-moc/claude-code-moc]] — Índice geral do Claude Code
