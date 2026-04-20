---
tags: [claude-code, core-features, permissions, security, safety]
status: active
level: intermediate
updated: 2026-04-19
created: 2026-04-19
---

# Permissões e Segurança — Claude Code

## Filosofia de Segurança do Claude Code

O Claude Code opera sob um princípio de "least privilege" aplicado ao contexto de IA: por padrão, qualquer ação com consequências irreversíveis ou de alto impacto requer aprovação explícita do usuário. O sistema de permissões é a implementação técnica deste princípio.

A segurança no Claude Code tem três camadas:

1. **Permissões por ferramenta**: O que o Claude pode executar sem pedir permissão
2. **Aprovação interativa**: Para ações não pre-aprovadas, Claude pede confirmação em tempo real
3. **Sandbox mode**: Modo de execução totalmente isolado para máxima segurança

O design reconhece que produtividade e segurança precisam coexistir: aprovações demais frustram o uso, aprovações de menos expõem ao risco. A configuração correta de permissões é o equilíbrio entre os dois.

---

## Modos de Permissão por Ferramenta

Cada ferramenta do Claude Code pode operar em três modos:

### ask (Padrão)

Claude pede permissão antes de executar. O usuário vê o comando/ação e escolhe aprovar ou negar.

```
Claude: Posso executar este comando?
  Bash: rm -rf /tmp/build-cache/
  [Aprovar] [Negar] [Aprovar Sempre]
```

### auto-accept (Permitido)

Claude executa sem pedir permissão. Usado para ferramentas de baixo risco que você confia que o Claude use livremente.

### deny (Negado)

Claude nunca pode executar esta ferramenta/comando, independente do contexto. A tentativa resulta em erro imediato.

---

## Configurando Permissões em settings.json

O sistema de permissões é configurado via `allow` e `deny` arrays no `settings.json`:

### Estrutura Básica

```json
{
  "permissions": {
    "allow": [
      "Bash(npm run test)",
      "Bash(npm run lint)",
      "Bash(git status)",
      "Bash(git log*)",
      "Read",
      "Glob",
      "Grep"
    ],
    "deny": [
      "Bash(git push --force*)",
      "Bash(rm -rf /*)",
      "Bash(sudo *)"
    ]
  }
}
```

### Sintaxe de Permissões

| Sintaxe | Significado |
|---------|-------------|
| `"Read"` | Permite a ferramenta Read sem restrição |
| `"Bash(npm run test)"` | Permite exatamente este comando Bash |
| `"Bash(npm run *)"` | Permite qualquer comando que comece com `npm run` |
| `"Bash(git *)"` | Permite qualquer comando git |
| `"mcp__[server]__[tool]"` | Permite ferramenta específica de MCP server |
| `"mcp__github__*"` | Permite todas as ferramentas do MCP server github |

> [!info] O matching usa glob patterns: `*` corresponde a qualquer string, mas não a `/`. Para match com slashes, use padrões mais específicos.

---

## settings.json Completo — Configuração de Produção

### Configuração Conservadora (Alta Segurança)

```json
{
  "model": "claude-sonnet-4-6",
  "permissions": {
    "allow": [
      "Read",
      "Glob",
      "Grep",
      "Bash(git status)",
      "Bash(git log*)",
      "Bash(git diff*)",
      "Bash(git branch*)",
      "Bash(npm run test*)",
      "Bash(npm run lint*)",
      "Bash(npm run build*)",
      "Bash(npm run dev*)",
      "Bash(npx tsc*)",
      "Bash(npx prisma generate)",
      "Bash(npx prisma migrate status)"
    ],
    "deny": [
      "Bash(git push*)",
      "Bash(git reset --hard*)",
      "Bash(git clean*)",
      "Bash(rm -rf*)",
      "Bash(sudo*)",
      "Bash(chmod*)",
      "Bash(chown*)",
      "Bash(curl * | bash)",
      "Bash(wget * | bash)",
      "Bash(npx prisma migrate dev*)",
      "Bash(npx prisma migrate reset*)",
      "Bash(npm install*)"
    ]
  }
}
```

### Configuração Balanceada (Desenvolvimento Diário)

```json
{
  "model": "claude-sonnet-4-6",
  "permissions": {
    "allow": [
      "Read",
      "Write",
      "Edit",
      "Glob",
      "Grep",
      "Bash(git status)",
      "Bash(git log*)",
      "Bash(git diff*)",
      "Bash(git add*)",
      "Bash(git commit*)",
      "Bash(git branch*)",
      "Bash(git checkout*)",
      "Bash(git stash*)",
      "Bash(npm run *)",
      "Bash(npx *)",
      "Bash(node *)",
      "Bash(ls*)",
      "Bash(pwd)",
      "Bash(echo*)",
      "Bash(cat*)",
      "Bash(grep*)",
      "Bash(find*)",
      "Bash(mkdir -p *)",
      "Bash(cp *)",
      "Bash(mv *)"
    ],
    "deny": [
      "Bash(git push --force*)",
      "Bash(git reset --hard*)",
      "Bash(rm -rf /*)",
      "Bash(sudo*)",
      "Bash(curl * | bash)",
      "Bash(wget * | bash)",
      "Bash(npx prisma migrate reset*)",
      "Bash(DROP *)",
      "Bash(TRUNCATE *)"
    ]
  }
}
```

---

## Aprovação Interativa

Quando o Claude tenta executar uma ação não pré-aprovada, aparece um prompt interativo:

```
Claude quer executar:
  git push origin main

[A] Aprovar uma vez
[S] Aprovar sempre (adicionar à allowlist)
[D] Negar
[E] Editar o comando antes de executar
```

### Comportamento do Claude ao Pedir Permissão

O Claude mostra:
1. A ferramenta que será usada
2. O comando/parâmetros exatos
3. O contexto (por que está pedindo fazer isso)

Você pode:
- **Aprovar uma vez**: Executa agora, pedirá novamente da próxima vez
- **Aprovar sempre**: Adiciona à allowlist automaticamente no settings.json
- **Negar**: Claude busca uma alternativa ou para e explica
- **Editar**: Você modifica o comando antes de aprovar

> [!tip] Use "Aprovar sempre" com cuidado. Cada vez que você faz isso, está modificando seu settings.json permanentemente. Revise periodicamente a lista de permissões para remover o que não é mais necessário.

---

## Sandbox Mode

O sandbox mode roda o Claude Code em um ambiente completamente isolado, sem acesso à internet, sem modificação de arquivos fora do projeto e com filesystem restrito.

### Ativar Sandbox

```bash
# Via flag CLI
claude --sandbox

# Via configuração permanente
# Em settings.json:
{
  "sandbox": true
}
```

### O que Sandbox Mode Restringe

| Recurso | Sem Sandbox | Com Sandbox |
|---------|-------------|-------------|
| Acesso à internet | Livre | Bloqueado |
| Escrita em arquivos | Qualquer arquivo | Apenas dentro do projeto |
| Execução de processos | Qualquer processo | Processos permitidos apenas |
| Acesso a secrets de sistema | Sim | Não |
| Instalação de pacotes | Sim | Não |

### Quando Usar Sandbox

- Ao testar prompts de usuários externos (código potencialmente malicioso)
- Em ambientes CI/CD onde o Claude não deve ter acesso à rede
- Ao trabalhar com dados sensíveis — sandbox garante que nada vaza
- Para revisar código de terceiros sem risco de execução acidental

> [!warning] Sandbox mode pode quebrar workflows que dependem de internet (npm install, API calls, etc.). Use apenas quando o isolamento é o objetivo.

---

## allowedTools e disallowedTools

Além do sistema de permissões por `allow`/`deny`, você pode configurar listas explícitas de ferramentas permitidas/negadas:

```json
{
  "allowedTools": [
    "Read",
    "Write",
    "Edit",
    "Bash",
    "Glob",
    "Grep"
  ],
  "disallowedTools": [
    "WebFetch",
    "WebSearch"
  ]
}
```

Diferença do `allow`/`deny`:
- `allowedTools`/`disallowedTools`: Controla quais *ferramentas* estão disponíveis (nível de ferramenta)
- `allow`/`deny` em `permissions`: Controla quais *invocações específicas* são pré-aprovadas (nível de comando)

Para um projeto sem acesso à internet:

```json
{
  "disallowedTools": ["WebFetch", "WebSearch"],
  "permissions": {
    "deny": [
      "Bash(curl*)",
      "Bash(wget*)",
      "Bash(fetch*)"
    ]
  }
}
```

---

## Permissões por Projeto vs Global

### Global (`~/.claude/settings.json`)

Aplica a todos os projetos. Use para permissões que você confia globalmente — ferramentas de leitura, comandos de listagem, ferramentas de desenvolvimento que você usa em todos os projetos.

```json
// ~/.claude/settings.json
{
  "permissions": {
    "allow": [
      "Read",
      "Glob",
      "Grep",
      "Bash(git status)",
      "Bash(git log*)",
      "Bash(git diff*)",
      "Bash(ls*)",
      "Bash(pwd)",
      "Bash(echo *)"
    ]
  }
}
```

### Local (`.claude/settings.json`)

Aplica apenas ao projeto atual. Permissões locais **complementam** as globais (não substituem). Use para comandos específicos do projeto.

```json
// .claude/settings.json (local ao projeto)
{
  "permissions": {
    "allow": [
      "Bash(npm run *)",
      "Bash(npx prisma *)",
      "Bash(docker-compose *)",
      "Bash(terraform plan)"
    ],
    "deny": [
      "Bash(terraform apply *)",
      "Bash(docker push *)"
    ]
  }
}
```

> [!info] Permissões locais de `deny` têm precedência sobre permissões globais de `allow`. Se você permitiu `Bash(git push*)` globalmente mas negou `Bash(git push --force*)` localmente, o force push é negado neste projeto.

---

## O que NUNCA Auto-Aprovar

Estas ações, independente do contexto, devem sempre requerer aprovação manual:

### Operações Git Destrutivas

```bash
# NUNCA auto-aprovar
git push --force *         # Sobrescreve histórico remoto
git push --force-with-lease *
git reset --hard *         # Descarta commits locais
git clean -fd *            # Remove arquivos não versionados
git rebase -i *            # Reescrita de histórico
```

### Operações de Sistema

```bash
# NUNCA auto-aprovar
rm -rf /*                  # Deleção recursiva de paths raiz
rm -rf ~/                  # Deleção do home
sudo *                     # Qualquer comando com sudo
chmod -R 777 *             # Permissões abertas recursivas
chown -R * /               # Mudança de ownership em raiz
```

### Deploy e Infraestrutura

```bash
# NUNCA auto-aprovar
terraform apply *          # Mudanças em infraestrutura real
kubectl delete *           # Deleção de recursos Kubernetes
aws ec2 terminate-instances *
helm uninstall *
docker system prune *      # Limpeza agressiva do Docker
```

### Banco de Dados

```bash
# NUNCA auto-aprovar
npx prisma migrate reset   # Drop completo do banco
DROP TABLE *               # SQL destrutivo
TRUNCATE *                 # Limpar tabelas
DELETE FROM * WHERE 1=1    # Deleção sem where
pg_dropcluster *           # Deleção de cluster PostgreSQL
```

### Instalação de Dependências em Produção

```bash
# NUNCA auto-aprovar em contexto de produção
npm install --save *       # Adiciona dependências permanentes
pip install *              # Instala pacotes Python
curl URL | bash            # Execução remota de scripts
wget URL -O - | sh         # Equivalente perigoso
```

---

## Configurações Seguras por Tipo de Projeto

### Projeto Frontend (Next.js/React)

```json
{
  "permissions": {
    "allow": [
      "Read", "Write", "Edit", "Glob", "Grep",
      "Bash(npm run dev)",
      "Bash(npm run build)",
      "Bash(npm run test*)",
      "Bash(npm run lint*)",
      "Bash(npm run storybook)",
      "Bash(npx tsc --noEmit)",
      "Bash(git *)",
      "Bash(ls*)", "Bash(pwd)"
    ],
    "deny": [
      "Bash(git push --force*)",
      "Bash(rm -rf*)",
      "Bash(npm install*)"
    ]
  }
}
```

### Projeto Backend (Node.js/API)

```json
{
  "permissions": {
    "allow": [
      "Read", "Write", "Edit", "Glob", "Grep",
      "Bash(npm run dev)",
      "Bash(npm run test*)",
      "Bash(npm run lint*)",
      "Bash(npx prisma generate)",
      "Bash(npx prisma migrate status)",
      "Bash(npx prisma studio)",
      "Bash(git *)",
      "Bash(ls*)", "Bash(pwd)", "Bash(cat*)"
    ],
    "deny": [
      "Bash(git push --force*)",
      "Bash(npx prisma migrate reset)",
      "Bash(npx prisma migrate dev*)",
      "Bash(rm -rf*)",
      "Bash(DROP *)",
      "Bash(TRUNCATE *)"
    ]
  }
}
```

### Projeto com Infra (Terraform/AWS)

```json
{
  "permissions": {
    "allow": [
      "Read", "Write", "Edit", "Glob", "Grep",
      "Bash(terraform fmt*)",
      "Bash(terraform validate)",
      "Bash(terraform plan*)",
      "Bash(terraform show*)",
      "Bash(terraform state list)",
      "Bash(aws * list*)",
      "Bash(aws * describe*)",
      "Bash(aws * get*)",
      "Bash(git *)",
      "Bash(ls*)", "Bash(pwd)"
    ],
    "deny": [
      "Bash(terraform apply*)",
      "Bash(terraform destroy*)",
      "Bash(terraform import*)",
      "Bash(terraform state rm*)",
      "Bash(aws * delete*)",
      "Bash(aws * terminate*)",
      "Bash(git push --force*)"
    ]
  }
}
```

---

## Auditoria de Permissões

### Verificar Permissões Atuais

```bash
# Ver permissões globais
cat ~/.claude/settings.json | jq '.permissions'

# Ver permissões locais do projeto
cat .claude/settings.json | jq '.permissions'
```

### Hook de Auditoria de Comandos Bash

Adicione ao settings.json para logar todos os comandos que o Claude executa:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "echo \"[$(date -u +%Y-%m-%dT%H:%M:%SZ)] $(echo $CLAUDE_TOOL_INPUT | jq -r '.command' | head -c 300)\" >> ~/.claude/audit.log"
          }
        ]
      }
    ]
  }
}
```

### Revisar o Log de Auditoria

```bash
# Ver últimas 50 ações
tail -50 ~/.claude/audit.log

# Buscar por ações suspeitas
grep -E "(rm|delete|drop|truncate|sudo|force)" ~/.claude/audit.log

# Ações das últimas 24h
grep "$(date -u +%Y-%m-%d)" ~/.claude/audit.log
```

---

## Boas Práticas de Segurança em Projetos

> [!warning] Nunca coloque secrets, tokens ou senhas em CLAUDE.md, skills ou commands. O Claude pode logar ou incluir esses valores em outputs. Use variáveis de ambiente e o sistema de secrets do projeto.

> [!tip] Comece sempre com permissões mínimas e expanda conforme a necessidade. É mais fácil adicionar permissões do que reparar danos causados por permissões excessivas.

> [!info] Em projetos de equipe, documente no CLAUDE.md quais permissões são necessárias e por quê. Isso ajuda novos membros a entender o nível de confiança configurado.

> [!warning] Revisite as permissões periodicamente. Permissões que foram aprovadas "uma vez" no início do projeto podem acumular no allow list sem revisão. Audite trimestralmente.

### Checklist de Segurança para Novos Projetos

```markdown
Antes de iniciar trabalho com Claude Code num projeto:

- [ ] Criado .claude/settings.json com permissões adequadas ao projeto
- [ ] Definido o que está no deny list (deploy, operações destrutivas)
- [ ] Revisado o allow list — cada item tem justificativa
- [ ] Secrets fora do CLAUDE.md (usar .env com .gitignore)
- [ ] Configurado hook de auditoria se projeto é crítico
- [ ] Testado que deny list funciona (tentou executar algo negado)
- [ ] Documentado as permissões no CLAUDE.md do projeto
```

---

## Resolução de Problemas Comuns

### "Claude não consegue executar X"

```bash
# Verificar se X está no deny list
cat .claude/settings.json | jq '.permissions.deny[]' | grep "X"
cat ~/.claude/settings.json | jq '.permissions.deny[]' | grep "X"

# Se estava negado por engano, remover do deny list e/ou adicionar ao allow list
```

### "Claude está pedindo permissão para tudo"

O allow list está vazio ou muito restrito. Adicione as ferramentas mais comuns:

```json
{
  "permissions": {
    "allow": [
      "Read", "Glob", "Grep",
      "Bash(git status)", "Bash(git log*)", "Bash(git diff*)",
      "Bash(ls*)", "Bash(pwd)", "Bash(cat*)"
    ]
  }
}
```

### "Claude executou algo que eu não queria"

1. Verifique o audit log: `tail -50 ~/.claude/audit.log`
2. Adicione o padrão ao deny list
3. Revise toda a allow list para garantir que não há outros padrões amplos demais

---

## Related

- [[hooks-system]] — Hooks PreToolUse como camada adicional de controle de permissões
- [[mcp-servers]] — Permissões para ferramentas MCP (`mcp__server__tool`)
- [[subagents]] — Permissões no contexto de subagentes (não herdam automaticamente)
- [[worktrees]] — Isolamento adicional via worktrees para trabalho de alto risco
- [[agent-teams]] — Permissões diferentes por tipo de agente especializado
- [[00-moc/claude-code-moc]] — Índice geral do Claude Code
