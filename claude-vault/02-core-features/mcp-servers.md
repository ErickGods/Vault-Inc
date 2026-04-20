---
tags: [claude-code, core-features, mcp, model-context-protocol]
status: active
level: intermediate
updated: 2026-04-19
created: 2026-04-19
---

# MCP Servers — Model Context Protocol

## O que é o Model Context Protocol

O Model Context Protocol (MCP) é um protocolo aberto criado pela Anthropic que define como modelos de linguagem se comunicam com ferramentas externas. É a camada de integração que permite ao Claude Code interagir com sistemas externos: bancos de dados, APIs, sistemas de arquivos especializados, IDEs, browsers e qualquer outro serviço.

A analogia mais útil: MCP é para Claude o que LSP (Language Server Protocol) é para editores de código. Assim como LSP permite que qualquer editor use qualquer language server para obter completions, diagnostics e refactoring, o MCP permite que Claude use qualquer MCP server para obter ferramentas, resources e prompts especializados.

Antes do MCP, cada integração era custom e tight-coupled. Com MCP, a interface é padronizada: qualquer servidor que implementa o protocolo pode ser usado por qualquer cliente MCP (Claude Code, Claude Desktop, outros agentes).

---

## Arquitetura do MCP

```
┌─────────────────────────────────────────┐
│           Claude Code (Cliente MCP)      │
│                                         │
│  ┌─────────────────────────────────┐    │
│  │         MCP Client              │    │
│  │   - Mantém conexões ativas      │    │
│  │   - Descobre tools disponíveis  │    │
│  │   - Roteia chamadas             │    │
│  └───────────┬─────────────────────┘    │
└──────────────┼──────────────────────────┘
               │ JSON-RPC 2.0
    ┌──────────┼──────────┐
    │          │          │
    ▼          ▼          ▼
┌───────┐ ┌───────┐ ┌───────┐
│ MCP   │ │ MCP   │ │ MCP   │
│Server │ │Server │ │Server │
│(stdio)│ │(SSE)  │ │(stdio)│
└───────┘ └───────┘ └───────┘
```

O Claude Code atua como **cliente MCP** e se conecta a um ou mais **MCP servers**. Cada server expõe um conjunto de capabilities (tools, resources, prompts) que o Claude pode usar durante sua sessão.

---

## Tipos de MCP Servers

### stdio (Standard Input/Output) — Servidores Locais

O servidor roda como processo filho, comunicando via stdin/stdout. É o tipo mais comum para ferramentas locais.

Características:
- Roda no mesmo machine que o Claude Code
- Sem networking — comunicação via pipes do OS
- Lifecycle gerenciado pelo Claude Code (Claude inicia e termina o processo)
- Acesso direto ao sistema de arquivos local
- Latência mínima (sem overhead de rede)

Casos de uso:
- Ferramentas de filesystem (ler/escrever arquivos especializados)
- Integração com banco de dados local
- Execução de scripts e CLIs
- Integrações com ferramentas de desenvolvimento local (Git, npm, etc.)

### SSE (Server-Sent Events) — Servidores Remotos

O servidor roda remotamente e se comunica via HTTP/SSE. Ideal para serviços compartilhados em equipe ou integrações com APIs externas.

Características:
- Pode ser compartilhado por múltiplos usuários/projetos
- Deployment independente do Claude Code
- Pode ser escalado e gerenciado separadamente
- Acessa recursos de rede e APIs externas
- Latência maior que stdio, mas aceitável para operações assíncronas

Casos de uso:
- Integração com Jira, Linear, Notion
- Acesso a bancos de dados compartilhados de equipe
- Serviços de análise e métricas
- APIs internas da empresa

---

## Como Registrar um MCP Server no Claude Code

### No settings.json

```json
{
  "mcpServers": {
    "meu-servidor-local": {
      "type": "stdio",
      "command": "node",
      "args": ["/absolute/path/to/server/index.js"],
      "env": {
        "DATABASE_URL": "postgresql://localhost:5432/mydb",
        "API_KEY": "sk-..."
      }
    },
    "servidor-python": {
      "type": "stdio",
      "command": "python",
      "args": ["-m", "meu_mcp_server"],
      "cwd": "/home/user/meu-projeto"
    },
    "servidor-remoto": {
      "type": "sse",
      "url": "https://mcp.minhaempresa.com/mcp",
      "headers": {
        "Authorization": "Bearer ${MCP_TOKEN}"
      }
    },
    "filesystem": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/workspace"]
    }
  }
}
```

### Via CLI

```bash
# Adicionar MCP server via comando
claude mcp add meu-servidor --command "node /path/to/server.js"

# Listar MCP servers registrados
claude mcp list

# Remover MCP server
claude mcp remove meu-servidor

# Verificar status de um servidor
claude mcp status meu-servidor
```

### Escopo do Registro

| Arquivo | Escopo | Prioridade |
|---------|--------|------------|
| `~/.claude/settings.json` | Global — todos os projetos | Menor |
| `.claude/settings.json` | Local — apenas este projeto | Maior |

---

## Protocolo de Comunicação (JSON-RPC 2.0)

MCP usa JSON-RPC 2.0 como protocolo de transporte. A comunicação segue o padrão request/response:

### Handshake de Inicialização

```json
// Cliente → Servidor: Initialize
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": {
    "protocolVersion": "2024-11-05",
    "capabilities": {
      "roots": { "listChanged": true },
      "sampling": {}
    },
    "clientInfo": {
      "name": "claude-code",
      "version": "1.0.0"
    }
  }
}

// Servidor → Cliente: InitializeResult
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "protocolVersion": "2024-11-05",
    "capabilities": {
      "tools": { "listChanged": true },
      "resources": { "subscribe": true, "listChanged": true }
    },
    "serverInfo": {
      "name": "meu-servidor",
      "version": "1.0.0"
    }
  }
}
```

### Chamada de Tool

```json
// Cliente → Servidor: CallTool
{
  "jsonrpc": "2.0",
  "id": 42,
  "method": "tools/call",
  "params": {
    "name": "buscar_usuario",
    "arguments": {
      "id": "usr_123",
      "include_orders": true
    }
  }
}

// Servidor → Cliente: ToolResult
{
  "jsonrpc": "2.0",
  "id": 42,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\"id\": \"usr_123\", \"nome\": \"João\", \"email\": \"joao@example.com\"}"
      }
    ],
    "isError": false
  }
}
```

---

## Tools, Resources e Prompts no MCP

MCP define três tipos de capability que um servidor pode expor:

### Tools (Ferramentas)

Funções executáveis que o Claude pode chamar. São o equivalente às built-in tools do Claude Code (Bash, Read, Write), mas implementadas no servidor MCP.

```typescript
{
  name: "criar_ticket",
  description: "Cria um novo ticket no Jira com título, descrição, prioridade e assignee",
  inputSchema: {
    type: "object",
    properties: {
      titulo: { type: "string", description: "Título do ticket" },
      descricao: { type: "string", description: "Descrição detalhada" },
      prioridade: { 
        type: "string", 
        enum: ["LOW", "MEDIUM", "HIGH", "CRITICAL"],
        description: "Prioridade do ticket"
      },
      assignee: { type: "string", description: "Username do responsável" }
    },
    required: ["titulo", "descricao"]
  }
}
```

### Resources (Recursos)

Dados estáticos ou dinâmicos que o Claude pode ler. Similar a arquivos, mas servidos pelo MCP server. Resources têm uma URI e um mime type.

```typescript
{
  uri: "jira://projeto/VAULT/backlog",
  name: "Backlog do projeto VAULT",
  mimeType: "application/json",
  description: "Lista de todos os tickets no backlog do projeto VAULT"
}
```

### Prompts (Templates)

Templates de prompt reutilizáveis com argumentos. Permitem que o servidor exponha prompts especializados que o Claude pode usar.

```typescript
{
  name: "analise_ticket",
  description: "Analisa um ticket do Jira e sugere implementação",
  arguments: [
    {
      name: "ticket_id",
      description: "ID do ticket (ex: VAULT-123)",
      required: true
    }
  ]
}
```

---

## Criando um MCP Server em TypeScript

### Setup do Projeto

```bash
mkdir meu-mcp-server && cd meu-mcp-server
npm init -y
npm install @modelcontextprotocol/sdk zod
npm install -D typescript @types/node tsx
```

### `tsconfig.json`

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "Node16",
    "moduleResolution": "Node16",
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true
  }
}
```

### `src/index.ts` — Servidor Mínimo Completo

```typescript
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  Tool,
} from "@modelcontextprotocol/sdk/types.js";
import { z } from "zod";

// ─── Definição das ferramentas ───────────────────────────────────────────────

const TOOLS: Tool[] = [
  {
    name: "buscar_produto",
    description:
      "Busca informações de um produto no catálogo interno por ID ou nome",
    inputSchema: {
      type: "object",
      properties: {
        query: {
          type: "string",
          description: "ID do produto (ex: PROD-001) ou termo de busca",
        },
        limit: {
          type: "number",
          description: "Número máximo de resultados (padrão: 10)",
          default: 10,
        },
      },
      required: ["query"],
    },
  },
  {
    name: "atualizar_estoque",
    description: "Atualiza a quantidade em estoque de um produto",
    inputSchema: {
      type: "object",
      properties: {
        produto_id: {
          type: "string",
          description: "ID único do produto",
        },
        quantidade: {
          type: "number",
          description: "Nova quantidade em estoque",
        },
        motivo: {
          type: "string",
          description: "Motivo da atualização (para auditoria)",
        },
      },
      required: ["produto_id", "quantidade", "motivo"],
    },
  },
];

// ─── Schemas Zod para validação de input ────────────────────────────────────

const BuscarProdutoInput = z.object({
  query: z.string().min(1),
  limit: z.number().int().positive().default(10),
});

const AtualizarEstoqueInput = z.object({
  produto_id: z.string(),
  quantidade: z.number().int().min(0),
  motivo: z.string().min(1),
});

// ─── Implementação dos handlers ──────────────────────────────────────────────

async function buscarProduto(args: z.infer<typeof BuscarProdutoInput>) {
  // Aqui você conectaria ao seu banco de dados real
  // Exemplo com dados mock:
  const produtos = [
    { id: "PROD-001", nome: "Notebook Pro", preco: 4999.99, estoque: 15 },
    { id: "PROD-002", nome: "Mouse Ergonômico", preco: 299.99, estoque: 87 },
  ];

  const resultado = produtos.filter(
    (p) =>
      p.id.toLowerCase().includes(args.query.toLowerCase()) ||
      p.nome.toLowerCase().includes(args.query.toLowerCase())
  );

  return resultado.slice(0, args.limit);
}

async function atualizarEstoque(
  args: z.infer<typeof AtualizarEstoqueInput>
) {
  // Aqui você faria a atualização no banco de dados
  console.error(
    `[AUDIT] Estoque atualizado: ${args.produto_id} → ${args.quantidade} (${args.motivo})`
  );

  return {
    sucesso: true,
    produto_id: args.produto_id,
    quantidade_anterior: 15, // Buscaria do banco
    quantidade_nova: args.quantidade,
    timestamp: new Date().toISOString(),
  };
}

// ─── Configuração do servidor ────────────────────────────────────────────────

const server = new Server(
  {
    name: "catalogo-server",
    version: "1.0.0",
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// Handler: listar ferramentas disponíveis
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return { tools: TOOLS };
});

// Handler: executar uma ferramenta
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    switch (name) {
      case "buscar_produto": {
        const validatedArgs = BuscarProdutoInput.parse(args);
        const resultado = await buscarProduto(validatedArgs);
        return {
          content: [
            {
              type: "text",
              text: JSON.stringify(resultado, null, 2),
            },
          ],
        };
      }

      case "atualizar_estoque": {
        const validatedArgs = AtualizarEstoqueInput.parse(args);
        const resultado = await atualizarEstoque(validatedArgs);
        return {
          content: [
            {
              type: "text",
              text: JSON.stringify(resultado, null, 2),
            },
          ],
        };
      }

      default:
        throw new Error(`Ferramenta desconhecida: ${name}`);
    }
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    return {
      content: [{ type: "text", text: `Erro: ${message}` }],
      isError: true,
    };
  }
});

// ─── Start ───────────────────────────────────────────────────────────────────

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("Catálogo MCP Server iniciado");
}

main().catch((error) => {
  console.error("Erro fatal:", error);
  process.exit(1);
});
```

### Registrando no Claude Code

```json
{
  "mcpServers": {
    "catalogo": {
      "type": "stdio",
      "command": "node",
      "args": ["/absolute/path/to/meu-mcp-server/dist/index.js"],
      "env": {
        "DATABASE_URL": "postgresql://localhost:5432/catalogo"
      }
    }
  }
}
```

---

## Criando um MCP Server em Python

### Setup

```bash
pip install mcp
```

### `server.py` — Servidor Mínimo

```python
import asyncio
import json
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types

app = Server("meu-server-python")

@app.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="consultar_cep",
            description="Consulta informações de endereço a partir de um CEP brasileiro",
            inputSchema={
                "type": "object",
                "properties": {
                    "cep": {
                        "type": "string",
                        "description": "CEP no formato 00000-000 ou 00000000"
                    }
                },
                "required": ["cep"]
            }
        ),
        types.Tool(
            name="calcular_frete",
            description="Calcula o frete entre dois CEPs com base no peso e dimensões",
            inputSchema={
                "type": "object",
                "properties": {
                    "cep_origem": {"type": "string"},
                    "cep_destino": {"type": "string"},
                    "peso_kg": {"type": "number"},
                    "servico": {
                        "type": "string",
                        "enum": ["PAC", "SEDEX", "SEDEX_10"],
                        "default": "PAC"
                    }
                },
                "required": ["cep_origem", "cep_destino", "peso_kg"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    if name == "consultar_cep":
        cep = arguments["cep"].replace("-", "")
        # Aqui você chamaria uma API real de CEP
        resultado = {
            "cep": cep,
            "logradouro": "Rua Exemplo",
            "bairro": "Centro",
            "cidade": "São Paulo",
            "uf": "SP"
        }
        return [types.TextContent(type="text", text=json.dumps(resultado, ensure_ascii=False))]

    elif name == "calcular_frete":
        # Implementação real chamaria API dos Correios
        resultado = {
            "servico": arguments.get("servico", "PAC"),
            "prazo_dias": 5,
            "valor": 25.90,
            "cep_origem": arguments["cep_origem"],
            "cep_destino": arguments["cep_destino"]
        }
        return [types.TextContent(type="text", text=json.dumps(resultado, ensure_ascii=False))]

    else:
        raise ValueError(f"Ferramenta desconhecida: {name}")

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
```

---

## MCP Servers Úteis (Prontos para Usar)

### Oficiais da Anthropic / MCP Ecosystem

| Server | Package | Propósito |
|--------|---------|-----------|
| Filesystem | `@modelcontextprotocol/server-filesystem` | Acesso a diretórios específicos |
| GitHub | `@modelcontextprotocol/server-github` | Issues, PRs, código |
| PostgreSQL | `@modelcontextprotocol/server-postgres` | Query e schema de banco |
| SQLite | `@modelcontextprotocol/server-sqlite` | Banco de dados local |
| Brave Search | `@modelcontextprotocol/server-brave-search` | Busca na web |
| Puppeteer | `@modelcontextprotocol/server-puppeteer` | Automação de browser |
| Slack | `@modelcontextprotocol/server-slack` | Mensagens e canais |

### Exemplo de uso do Filesystem MCP

```json
{
  "mcpServers": {
    "filesystem": {
      "type": "stdio",
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "/Users/erick/workspace",
        "/Users/erick/documents"
      ]
    }
  }
}
```

---

## Segurança em MCP Servers

> [!warning] MCP servers têm acesso aos recursos que você configurar. Um servidor comprometido ou mal-implementado pode vazar dados sensíveis ou executar operações destrutivas.

### O que Expor

- Operações de leitura em dados não-sensíveis
- APIs internas com autenticação própria
- Ferramentas de consulta (SELECT, GET)
- Metadados e estatísticas

### O que NÃO Expor via MCP

- Credenciais ou secrets (nem como output)
- Operações destrutivas sem confirmação
- Acesso direto a tabelas de produção sem camada de negócio
- Sistemas de autenticação (não exponha o sistema de auth via MCP)

### Boas Práticas de Segurança

```typescript
// ✓ BOM: Validar e sanitizar todos os inputs
const validatedArgs = InputSchema.parse(args);

// ✓ BOM: Usar prepared statements / ORMs
const user = await db.user.findUnique({ where: { id: validatedArgs.id } });

// ✓ BOM: Logar operações sensíveis
console.error(`[AUDIT] Operação: ${name} por sessão ${sessionId}`);

// ✓ BOM: Retornar apenas campos necessários
return { id: user.id, nome: user.nome }; // não retornar senha, tokens

// ✗ RUIM: Executar queries brutas com input do usuário
const result = await db.query(`SELECT * FROM users WHERE id = ${args.id}`);

// ✗ RUIM: Expor stack traces
catch (error) { return { error: error.stack }; } // Não faça isso
```

---

## Debugging de MCP Servers

### Flag --mcp-debug

```bash
# Ativa logs verbose de comunicação MCP
claude --mcp-debug

# Ver todas as mensagens JSON-RPC trocadas
```

### Logs do Servidor

Servidores MCP devem escrever logs em `stderr` (não `stdout`, que é reservado para o protocolo):

```typescript
// Correto — vai para stderr, não interfere no protocolo
console.error("[DEBUG] Processando request:", name);

// ERRADO — vai para stdout e corrompe o protocolo JSON-RPC
console.log("Processando...");
```

### Testar o Servidor Manualmente

```bash
# Testar handshake básico
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}' | node dist/index.js

# Listar tools disponíveis
echo '{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}' | node dist/index.js
```

---

## Related

- [[hooks-system]] — Hooks para automatizar ações quando Claude usa ferramentas MCP
- [[subagents]] — Subagentes podem usar MCP servers especializados
- [[permissions-and-safety]] — Configurar permissões para tools MCP (allowedTools)
- [[agent-teams]] — Times de agentes com MCP servers dedicados por especialidade
- [[00-moc/claude-code-moc]] — Índice geral do Claude Code
