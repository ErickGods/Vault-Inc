---
tags: [skill, ai-ml, mcp]
status: active
level: advanced
updated: 2026-04-05
created: 2026-04-05
aliases: [MCP, Model Context Protocol]
---

# MCP Servers Guide

## Overview

O **Model Context Protocol (MCP)** é um protocolo aberto criado pela Anthropic que padroniza como LLMs se conectam a fontes de dados e ferramentas externas. Funciona como um "USB para IA" — qualquer cliente MCP (Claude Desktop, [[claude-code]], IDEs) pode usar qualquer servidor MCP sem integração customizada.

A arquitetura é **cliente-servidor**: o host (aplicação com o LLM) atua como cliente MCP e conecta a múltiplos servidores MCP, cada um expondo capacidades específicas.

```
Host (Claude Code / Claude Desktop)
├── MCP Client
│   ├── → MCP Server: filesystem (tools: read_file, write_file)
│   ├── → MCP Server: github (tools: create_pr, list_issues)
│   ├── → MCP Server: postgres (tools: query, schema)
│   └── → MCP Server: custom-internal (tools: deploy, monitor)
```

> [!important] Segurança por Design
> Servidores MCP nunca se comunicam diretamente com o LLM. Todo contexto passa pelo host, que controla o que é exposto ao modelo. O servidor não sabe qual LLM está sendo usado.

Veja [[claude-code-superpowers]] para usar MCP com skills e [[claude-api]] para entender como o host integra as capacidades.

## Core Concepts

### Capabilities: Tools, Resources, Prompts, Sampling

**Tools** — funções que o LLM pode chamar (com side effects):
```
read_file, write_file, execute_query, send_email, create_issue
```

**Resources** — dados que o LLM pode ler (sem side effects, como GET):
```
file://path/to/file
github://repo/owner/name/README.md
postgres://db/schema/public
```

**Prompts** — templates de prompt reutilizáveis expostos pelo servidor:
```
/mcp-prompt code-review --file=src/auth.ts --style=security-focused
```

**Sampling** — o servidor pode solicitar que o LLM gere texto (servidor → LLM):
```python
# Servidor pode pedir ao LLM para processar dados
result = await session.create_message(
    messages=[{"role": "user", "content": "Summarize this log"}],
    max_tokens=500,
)
```

### Transport Layers

**stdio** — comunicação via stdin/stdout (processo local):

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/workspace"],
      "env": {}
    }
  }
}
```

**SSE/HTTP** — comunicação via HTTP Server-Sent Events (servidores remotos):

```json
{
  "mcpServers": {
    "remote-analytics": {
      "url": "https://analytics.company.com/mcp",
      "headers": {
        "Authorization": "Bearer ${ANALYTICS_TOKEN}"
      }
    }
  }
}
```

## Patterns

### Implementação em TypeScript SDK

```typescript
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

const server = new McpServer({
  name: "analytics-server",
  version: "1.0.0",
});

// Definir uma tool
server.tool(
  "query_metrics",
  "Query application metrics for a time range",
  {
    metric: z.string().describe("Metric name (e.g., 'api.latency', 'error.rate')"),
    start: z.string().datetime().describe("Start time ISO 8601"),
    end: z.string().datetime().describe("End time ISO 8601"),
    aggregation: z.enum(["avg", "max", "min", "sum", "p95", "p99"]).default("avg"),
  },
  async ({ metric, start, end, aggregation }) => {
    const data = await metricsDb.query({ metric, start, end, aggregation });
    return {
      content: [
        {
          type: "text",
          text: JSON.stringify(data, null, 2),
        },
      ],
    };
  }
);

// Definir um resource
server.resource(
  "schema",
  new ResourceTemplate("db://schema/{table}", { list: undefined }),
  async (uri, { table }) => {
    const schema = await db.getTableSchema(table);
    return {
      contents: [
        {
          uri: uri.href,
          mimeType: "application/json",
          text: JSON.stringify(schema),
        },
      ],
    };
  }
);

const transport = new StdioServerTransport();
await server.connect(transport);
```

### Implementação em Python SDK

```python
from mcp.server.fastmcp import FastMCP
from mcp.server.stdio import stdio_server

mcp = FastMCP("data-pipeline-server")

@mcp.tool()
async def run_pipeline(
    pipeline_name: str,
    parameters: dict,
    dry_run: bool = False,
) -> str:
    """Execute a data pipeline with given parameters.

    Args:
        pipeline_name: Name of the pipeline to run
        parameters: Pipeline-specific parameters
        dry_run: If True, validate without executing

    Returns:
        Execution result with status and logs
    """
    if dry_run:
        return await validate_pipeline(pipeline_name, parameters)

    result = await execute_pipeline(pipeline_name, parameters)
    return f"Pipeline {pipeline_name} completed. Status: {result.status}\n{result.logs}"

@mcp.resource("pipeline://config/{name}")
async def get_pipeline_config(name: str) -> str:
    """Get pipeline configuration as JSON."""
    config = await load_pipeline_config(name)
    return config.model_dump_json(indent=2)

@mcp.prompt()
def analyze_pipeline_failure(pipeline_name: str, error_log: str) -> str:
    """Generate a debugging prompt for pipeline failures."""
    return f"""Analyze this pipeline failure and suggest fixes:

Pipeline: {pipeline_name}
Error Log:
{error_log}

Please identify:
1. Root cause of the failure
2. Affected data or systems
3. Recommended fix
4. Prevention measures"""

if __name__ == "__main__":
    mcp.run(transport="stdio")
```

### Tool Definition com inputSchema Detalhado

```typescript
server.tool(
  "create_github_pr",
  "Create a pull request on GitHub",
  {
    owner: z.string().describe("Repository owner (user or org)"),
    repo: z.string().describe("Repository name"),
    title: z.string().min(1).max(256).describe("PR title"),
    body: z.string().describe("PR description in Markdown"),
    head: z.string().describe("Branch with changes"),
    base: z.string().default("main").describe("Target branch"),
    draft: z.boolean().default(false).describe("Create as draft PR"),
    reviewers: z.array(z.string()).optional().describe("GitHub usernames to request review"),
  },
  async (params) => {
    // Validação de segurança antes de chamar API
    if (!isAllowedRepo(params.owner, params.repo)) {
      return { content: [{ type: "text", text: "Error: Repository not in allowlist" }], isError: true };
    }

    const pr = await github.createPR(params);
    return {
      content: [{ type: "text", text: `PR created: ${pr.html_url}` }],
    };
  }
);
```

### Resource Templates para Coleções

```typescript
import { ResourceTemplate } from "@modelcontextprotocol/sdk/server/mcp.js";

// Template com parâmetros dinâmicos
server.resource(
  "logs",
  new ResourceTemplate("logs://{service}/{date}", {
    list: async () => ({
      resources: await getAvailableLogs(),
    }),
  }),
  async (uri, { service, date }) => {
    const logs = await fetchLogs(service, date);
    return {
      contents: [
        {
          uri: uri.href,
          mimeType: "text/plain",
          text: logs.join("\n"),
        },
      ],
    };
  }
);
```

### Security Considerations

**Input validation:**

```python
import re

@mcp.tool()
async def read_file(path: str) -> str:
    # Prevenir path traversal
    resolved = Path(ALLOWED_BASE_DIR / path).resolve()
    if not str(resolved).startswith(str(ALLOWED_BASE_DIR)):
        raise ValueError(f"Path traversal attempt detected: {path}")

    # Validar extensão
    if resolved.suffix not in ALLOWED_EXTENSIONS:
        raise ValueError(f"File type not allowed: {resolved.suffix}")

    return resolved.read_text()
```

**Sandboxing com Docker:**

```dockerfile
# Dockerfile para MCP server isolado
FROM python:3.12-slim
RUN useradd -m -u 1000 mcpuser
USER mcpuser
WORKDIR /home/mcpuser

COPY --chown=mcpuser requirements.txt .
RUN pip install --user -r requirements.txt

COPY --chown=mcpuser server.py .

# Sem acesso à rede exceto APIs específicas
ENTRYPOINT ["python", "server.py"]
```

### Ecosystem: Servidores Existentes

```bash
# Filesystem (leitura/escrita de arquivos)
npx @modelcontextprotocol/server-filesystem /path/to/workspace

# GitHub (issues, PRs, commits)
npx @modelcontextprotocol/server-github

# Slack (mensagens, canais)
npx @modelcontextprotocol/server-slack

# PostgreSQL (queries read-only)
npx @modelcontextprotocol/server-postgres postgresql://user:pass@host/db

# Puppeteer (automação de browser)
npx @modelcontextprotocol/server-puppeteer

# Brave Search (pesquisa na web)
npx @modelcontextprotocol/server-brave-search
```

### Configuração no Claude Code e Desktop

**Claude Code (`~/.claude/config.json` ou `.claude/config.json` no projeto):**

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "."],
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN}"
      }
    },
    "internal-api": {
      "command": "python",
      "args": ["/opt/mcp-servers/internal_api.py"],
      "env": {
        "API_BASE_URL": "https://api.internal.company.com",
        "API_KEY": "${INTERNAL_API_KEY}"
      }
    }
  }
}
```

**Claude Desktop (`claude_desktop_config.json`):**

```json
{
  "mcpServers": {
    "postgres": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres"],
      "env": {
        "POSTGRES_CONNECTION_STRING": "postgresql://..."
      }
    }
  }
}
```

## Gotchas

> [!warning] Tool Naming Conflicts
> Se dois servidores expõem tools com o mesmo nome, o comportamento é indefinido. Use prefixos no nome das tools: `github_create_pr` em vez de `create_pr`.

> [!bug] stdio e Logging
> Em servidores stdio, `print()` para stdout quebra o protocolo MCP. Use sempre `sys.stderr` para debug: `print("debug", file=sys.stderr)`.

> [!caution] Sampling Requer Permissão Explícita
> O capability de sampling (servidor chamar o LLM) deve ser habilitado explicitamente pelo host. Clientes podem negar esta capacidade por razões de segurança.

> [!tip] Desenvolvimento com Inspector
> Use `npx @modelcontextprotocol/inspector` para testar seu servidor MCP interativamente antes de integrar com Claude.

## Snippets

### Testar um Server MCP

```bash
# Inspecionar server localmente
npx @modelcontextprotocol/inspector python server.py

# Listar tools disponíveis
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | python server.py
```

### Erro Handling no Server

```typescript
server.tool("risky_operation", "...", schema, async (params) => {
  try {
    const result = await dangerousOperation(params);
    return { content: [{ type: "text", text: result }] };
  } catch (error) {
    return {
      content: [{ type: "text", text: `Operation failed: ${error.message}` }],
      isError: true,    // sinaliza ao LLM que houve erro
    };
  }
});
```

## References

- [MCP Specification](https://modelcontextprotocol.io/specification)
- [MCP SDK TypeScript](https://github.com/modelcontextprotocol/typescript-sdk)
- [MCP SDK Python](https://github.com/modelcontextprotocol/python-sdk)
- [MCP Servers Registry](https://github.com/modelcontextprotocol/servers)

## Related

- [[claude-code]] — cliente MCP primário
- [[claude-code-superpowers]] — combinar MCP com skills
- [[claude-api]] — entender como o host integra MCP
- [[typescript]] — SDK TypeScript para implementação
- [[python]] — SDK Python para implementação
