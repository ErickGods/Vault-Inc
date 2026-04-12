---
tags: [moc, home, tech-vault]
status: active
level: advanced
updated: 2026-04-05
aliases: [Tech Vault, Home]
created: 2026-04-05
---

# 🗺️ Tech Knowledge Vault

## Visão Geral

Este vault é o repositório central de conhecimento técnico para engenharia de software moderna. Aqui você encontra documentação estruturada, padrões arquiteturais, referências de ferramentas e guias práticos organizados por domínio. O objetivo é manter um segundo cérebro técnico que evolui junto com as tecnologias utilizadas nos projetos.

O vault cobre desde linguagens de programação e frameworks até infraestrutura, DevOps, inteligência artificial e engenharia de dados. Cada seção é mantida com status e nível de maturidade para facilitar a navegação e priorização do aprendizado.

> [!info] Como Navegar
> Use os MOCs (Maps of Content) abaixo como ponto de entrada para cada domínio. Cada MOC lista todos os arquivos da sua categoria com indicadores de status. O Dataview queries abaixo mostram uma visão dinâmica do vault.

---

## 🧭 Maps of Content

Navegue pelo vault através dos MOCs de cada domínio:

| MOC | Domínio | Arquivos |
|-----|---------|---------|
| [[engineering-moc\|🛠️ Engineering]] | Linguagens, frameworks e bancos de dados | 20+ |
| [[devops-moc\|⚙️ DevOps]] | CI/CD, containers, monitoramento e IaC | 13 |
| [[ai-ml-moc\|🤖 AI/ML]] | LLMs, agentes e frameworks de IA | 10 |
| [[architecture-moc\|🏗️ Architecture]] | Padrões, decisões e cloud services | 11 |
| [[data-engineering-moc\|📊 Data Engineering]] | Pipelines, streaming e transformação | 10 |
| [[infrastructure-moc\|🌐 Infrastructure]] | Redes, segurança e cloud | 11 |

---

## 📊 Dashboard — Recently Updated

Arquivos atualizados nos últimos 30 dias:

```dataview
TABLE status, level, updated
FROM "tech-vault"
WHERE updated >= date(today) - dur(30 days)
SORT updated DESC
LIMIT 15
```

---

## ⚡ Quick Access

As referências mais utilizadas no dia a dia:

### Snippets
- [[python-snippets]] — Padrões e receitas Python
- [[bash-snippets]] — Scripts e one-liners Bash
- [[docker-snippets]] — Comandos e Dockerfiles
- [[sql-snippets]] — Queries e otimizações SQL

### Cheatsheets
- [[git-cheatsheet]] — Comandos Git essenciais
- [[regex-cheatsheet]] — Expressões regulares
- [[big-o-notation]] — Complexidade de algoritmos

### Core Technologies
- [[docker]] — Containerização
- [[python]] — Linguagem principal
- [[postgresql]] — Banco de dados relacional

> [!tip] Dica de Produtividade
> Use `Ctrl+O` no Obsidian para abrir qualquer arquivo rapidamente. Os snippets são organizados por linguagem e têm tags específicas para busca rápida.

---

## 📈 Vault Statistics

### Skills por Status

```dataview
TABLE length(rows) AS "Count"
FROM "tech-vault"
WHERE status
GROUP BY status
```

### Skills por Nível

```dataview
TABLE length(rows) AS "Count"
FROM "tech-vault"
WHERE level
GROUP BY level
SORT length(rows) DESC
```

---

## 🗓️ Manutenção do Vault

> [!warning] Processo de Revisão
> Arquivos com status `draft` devem ser revisados e promovidos para `active` ou marcados como `deprecated` a cada 30 dias. Use o dashboard acima para identificar o que precisa de atenção.

### Convenções de Status
- ✅ **active** — Conteúdo revisado e confiável
- 🚧 **draft** — Em construção, pode estar incompleto
- ⚠️ **deprecated** — Tecnologia ou padrão obsoleto

### Convenções de Nível
- **beginner** — Conceitos introdutórios
- **intermediate** — Uso prático com exemplos
- **advanced** — Profundidade técnica, edge cases, otimizações

---

## 🔗 Links Externos Importantes

- [Obsidian Docs](https://help.obsidian.md)
- [Dataview Plugin Docs](https://blacksmithgu.github.io/obsidian-dataview/)
- [GitHub](https://github.com)
- [MDN Web Docs](https://developer.mozilla.org)

---

## 📅 Changelog

| Data | Mudança |
|------|---------|
| 2026-04-05 | Vault inicializado com estrutura completa |
| 2026-04-05 | MOCs criados para todos os 6 domínios |
| 2026-04-05 | Quick Access e dashboards configurados |

> [!example] Próximos Passos
> 1. Preencher os arquivos de skills com conteúdo técnico detalhado
> 2. Adicionar canvas para visualizações de arquitetura
> 3. Configurar templates para novos arquivos
> 4. Revisar e expandir os snippets existentes
