# Vault Inc Library

Open-source knowledge base by **Vault Inc** covering **technology** and **finance** — built as an [Obsidian](https://obsidian.md) vault with AI-powered agents for financial research.

## Structure

```
Vault-Inc-Library/
├── tech-vault/          # Technology knowledge base
│   ├── 01-skills/       # Languages, frameworks, databases, tools
│   ├── 02-devops/       # CI/CD, containers, IaC, monitoring, networking
│   ├── 03-ai-ml/        # LLM patterns, AI frameworks, MCP, tools
│   ├── 04-architecture/ # Patterns, messaging, cloud services, ADRs
│   ├── 05-data-eng/     # Pipelines, streaming, storage, transformation
│   ├── 06-snippets/     # Ready-to-use code snippets
│   ├── 07-references/   # Cheatsheets (git, regex, Big-O)
│   └── 08-templates/    # Project, ADR, skill, weekly review templates
│
├── finance-vault/       # Finance & investments knowledge base
│   ├── 01-fundamentals/ # Core concepts (compound interest, risk, TVM)
│   ├── 02-investments/  # Equities, fixed income, funds, derivatives, alts
│   ├── 03-analysis/     # Fundamental, technical, quantitative, macro
│   ├── 04-personal/     # Budgeting, FIRE, tax optimization, insurance
│   ├── 05-accounting/   # Financial statements, ratios, red flags
│   ├── 06-markets/      # B3, US markets, cycles, participants
│   ├── 07-psychology/   # Behavioral finance, biases, risk tolerance
│   ├── 08-frameworks/   # MPT, position sizing, capital allocation
│   ├── 09-glossary/     # Financial terms (PT-BR and EN)
│   ├── 10-snippets/     # Python finance snippets, formulas
│   ├── 11-templates/    # Stock analysis, portfolio review, trade journal
│   └── agents/          # AI-powered financial research agents
│       └── financial-research-house/
│
└── docs/                # Project docs, canvas boards, plans
```

## Highlights

- **180+ interconnected notes** with Obsidian backlinks and MOCs (Maps of Content)
- **Financial Research House** — AI agents (built for [Claude Code](https://claude.com/claude-code)) that act as an equity research analyst and private banker, using the knowledge base as their source of truth
- **Bilingual content** — Portuguese (BR) primary, English technical terms preserved
- **Covers both Brazilian and US markets** — Tesouro Direto, B3, CDB/LCI/LCA alongside bonds, ETFs, and US market structure

## How to Use

### As an Obsidian vault

1. Clone this repo
2. Open the root folder (or `tech-vault/` / `finance-vault/` individually) in [Obsidian](https://obsidian.md)
3. Navigate using the MOC files in `00-moc/`

### With Claude Code agents

The `finance-vault/agents/financial-research-house/` contains agent definitions that can be installed in Claude Code:

```bash
# Copy to global agents directory
cp finance-vault/agents/financial-research-house/*.md ~/.claude/agents/
```

Then ask Claude to act as the Equity Research Analyst or Private Banker — they'll use the knowledge base to produce analysis.

## Topics Covered

### Tech Vault
Python, TypeScript, Rust | React, Next.js, FastAPI, Django | PostgreSQL, Redis, MongoDB, Supabase | Docker, Kubernetes, Terraform | GitHub Actions, ArgoCD | Kafka, RabbitMQ, NATS | RAG, prompt engineering, multi-agent systems | Clean architecture, event-driven, microservices

### Finance Vault
Valuation (DCF, multiples) | Graham, Buffett, Dalio frameworks | Options, futures, derivatives | Brazilian market (B3, Tesouro Direto, FIIs) | Factor investing, momentum strategies | Behavioral finance | FIRE movement | Portfolio theory (MPT)

## License

[MIT](LICENSE)

---

Built by [Vault Inc](https://github.com/ErickGods)
