# E0 + E1 — Higiene e Casa Quant — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Entregar a casa quant completa e funcional — conhecimento, índice, 4 agentes e 2 skills — mais o verificador de links que serve de critério de aceite para toda a reestruturação.

**Architecture:** A casa quant é construída do zero, sem renomeação de arquivo existente. Isso a torna o lugar de validar os padrões novos (formato de índice, frontmatter canônico, anatomia de agente e de skill) antes de aplicá-los sobre os 235 arquivos das outras casas. O verificador `check_links.py` nasce primeiro, por TDD, e vira o critério objetivo de todas as etapas seguintes.

**Tech Stack:** Python 3.13 (stdlib apenas — `unittest`, sem dependências externas), Markdown, Obsidian wikilinks, Claude Code agents/skills.

**Spec:** [2026-07-28-vault-restructure-design.md](../specs/2026-07-28-vault-restructure-design.md) — etapas E0 e E1 da §11.1.

---

## Escopo

Este plano cobre **E0 e E1**. As etapas E2 (finance), E3 (tech), E4 (shared), E5 (raiz) e E6 (repo privado) ganham planos próprios, escritos depois que os padrões da quant estiverem validados.

**Nenhum commit vai para `main`.** Cada task fecha com commit de checkpoint na branch atual; ao final de todas as etapas o histórico é squashed em um único commit, conforme §11.0 do spec.

---

## Fato que governa a segurança desta etapa

**O Obsidian resolve wikilink por basename, não por caminho.** `[[factor-investing]]` continua resolvendo depois que o arquivo muda de pasta, desde que o nome do arquivo não mude.

Consequência: **E1 não quebra nenhum link**, porque só move e cria — não renomeia. Renomeação (emoji→kebab) só acontece em E2/E3/E4, e é lá que mora o risco.

Isso permite um critério de aceite para E1 baseado em **delta**, não em valor absoluto:

| Asserção | Valor |
|---|---|
| Linha de base, medida com o verificador completo | **66 distintos / 110 ocorrências** |
| `capm` desaparece da lista de não resolvidos | −5 |
| `sharpe-ratio` desaparece da lista | −3 |
| **Alvo ao fim da E1** | **102, e o total nunca sobe** |

>  **O 110 só é confiável porque a allowlist existe.** Antes dela a contagem bruta subiu de 224 para 237 em poucos minutos só porque este plano foi editado — specs e planos citam notas como exemplo, e cada edição mexia no número. Com `docs/superpowers/` filtrado, a métrica parou de se mover sozinha.
>
> **O delta é −8, não −9.** A contagem bruta dava `sharpe-ratio` 4×, mas uma dessas ocorrências está dentro de bloco de código cercado e o verificador final a descarta corretamente. Números medidos com o verificador completo (commit `2b6e993`), não estimados.
>
> Composição das 110: **62 do backlog do `claude-vault`** (notas planejadas e nunca escritas — balde E do spec), **35 do `finance-vault`** (balde D, conhecimento real faltando) e 13 de `docs`. Zero resíduo de sintaxe de template ou de código.

---

## File Structure

**Criados em E0:**

| Arquivo | Responsabilidade |
|---|---|
| `scripts/check_links.py` | Indexa alvos, extrai wikilinks ignorando código cercado, aplica allowlist, reporta não resolvidos |
| `scripts/tests/test_check_links.py` | 23 testes, um por modo de falha observado no diagnóstico ou na revisão |
| `scripts/baseline.txt` | Linha de base congelada, consumida por `--baseline` |
| `shared/templates/adr.md` | Fonte única do template de ADR (2 duplicatas reais — ver Step 3) |
| `shared/templates/skill.md` | Fonte única do template de skill (hoje em 2 lugares) |

**Criados em E1:**

| Arquivo | Responsabilidade |
|---|---|
| `quant/CLAUDE.md` | Regras da casa quant — carregado pelo Claude Code ao trabalhar dentro de `quant/` |
| `quant/00-index/_house.md` | Índice mestre — o arquivo que todo agente quant carrega primeiro |
| `quant/00-index/factor-models.md` | Índice do domínio de fatores |
| `quant/00-index/strategies.md` | Índice do domínio de estratégias |
| `quant/00-index/backtesting.md` | Índice do domínio de backtest |
| `quant/00-index/risk-analytics.md` | Índice do domínio de risco |
| `quant/03-factor-models/capm.md` | Nota — CAPM (elimina 5 links fantasma) |
| `quant/06-risk-analytics/sharpe-ratio.md` | Nota — Sharpe e derivados (elimina 3 links fantasma) |
| `.claude/agents/quant/quant-researcher.md` | Agente — pesquisa de sinal e fatores |
| `.claude/agents/quant/quant-developer.md` | Agente — implementação e engine de backtest |
| `.claude/agents/quant/risk-quant.md` | Agente — VaR, ES, stress, sizing |
| `.claude/agents/quant/market-data-quant.md` | Agente — correção financeira do dado |
| `.claude/skills/hypothesis-test/SKILL.md` | Skill — tese discricionária → hipótese testável |
| `.claude/skills/backtest-protocol/SKILL.md` | Skill — backtest com guardrails |

**Movidos em E1** (sem renomear — basename preservado):

| Origem | Destino |
|---|---|
| `finance-vault/03-analysis/quantitative/factor-investing.md` | `quant/03-factor-models/factor-investing.md` |
| `finance-vault/03-analysis/quantitative/momentum-strategies.md` | `quant/04-strategies/momentum-strategies.md` |
| `finance-vault/03-analysis/quantitative/backtesting-basics.md` | `quant/05-backtesting/backtesting-basics.md` |
| `finance-vault/08-frameworks/portfolio-theory-mpt.md` | `quant/06-risk-analytics/portfolio-theory-mpt.md` |
| `finance-vault/08-frameworks/position-sizing.md` | `quant/06-risk-analytics/position-sizing.md` |

**Deletados em E0:**

- `.claude/agents/mnt/` (5 arquivos — sandbox vazado)
- `.claude/agents/files.zip` (18 KB)
- `tech-vault/01-skills/devops/docker.md` (0 bytes, duplicata)
- `tech-vault/08-templates/adr-template.md` (**única duplicata real** — variante Templater da versão de `docs/01-templates/`)

**Preservados apesar do nome** — dois homônimos que a triagem por nome de arquivo classificou errado:

| Arquivo | O que realmente é | Destino |
|---|---|---|
| `tech-vault/04-architecture/decisions/adr-template.md` (11.438 B) | Nota de conhecimento sobre ADRs — MADR vs Nygard, exemplos, tooling | → `adr-guide.md` em E3 |
| `tech-vault/08-templates/skill-template.md` (2.317 B) | Template de nota sobre tecnologia (`# <% technology %>`), casa com `01-skills/` | → `technology-note.md` em E3 |

**Domínios de `quant/` sem nota nesta etapa** — `01-math-foundations`, `02-time-series`, `07-execution`, `08-ml-finance`, `09-market-data`. Não recebem pasta nem `_index.md` (git não versiona diretório vazio). Aparecem em `_house.md` marcados como `planned`, sem wikilink.

---

## Task 1: Verificador de links — indexação

**Files:**
- Create: `scripts/check_links.py`
- Test: `scripts/tests/test_check_links.py`

- [ ] **Step 1: Escrever os testes de indexação**

Criar `scripts/tests/test_check_links.py`:

```python
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from check_links import find_unresolved


class VaultFixture(unittest.TestCase):
    """Cria um vault temporário a partir de um dict {caminho: conteudo}."""

    def build(self, files):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        for rel, content in files.items():
            full = os.path.join(self.tmp.name, rel)
            os.makedirs(os.path.dirname(full), exist_ok=True)
            with open(full, "w", encoding="utf-8") as fh:
                fh.write(content)
        return self.tmp.name


class TestIndexing(VaultFixture):
    def test_resolve_md_link(self):
        root = self.build({
            "a.md": "veja [[b]]",
            "b.md": "conteudo",
        })
        self.assertEqual(find_unresolved(root), {})

    def test_unresolved_md_link_is_reported(self):
        root = self.build({"a.md": "veja [[fantasma]]"})
        self.assertEqual(find_unresolved(root), {"fantasma": 1})

    def test_resolve_canvas_link(self):
        """Regressao: a primeira versao so indexava .md e acusava canvas existente."""
        root = self.build({
            "a.md": "veja [[agent-workflow.canvas]]",
            "board/agent-workflow.canvas": "{}",
        })
        self.assertEqual(find_unresolved(root), {})
```

- [ ] **Step 2: Rodar os testes e confirmar que falham**

```bash
python -m unittest discover -s scripts/tests -v
```

Esperado: `ModuleNotFoundError: No module named 'check_links'` — o módulo ainda não existe.

- [ ] **Step 3: Implementar a indexação mínima**

Criar `scripts/check_links.py`:

```python
#!/usr/bin/env python3
"""Verifica a integridade dos wikilinks do vault."""

import os
import re
from collections import Counter

WIKILINK = re.compile(r"\[\[([^\]|#]+)")
INDEXED_EXT = (".md", ".canvas")
SKIP_DIRS = (".git", ".obsidian")


def _walk(root):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            yield dirpath, name


def index_targets(root):
    """Basenames alcancaveis por wikilink, com e sem extensao.

    O Obsidian resolve por basename, nao por caminho: mover um arquivo de
    pasta nao quebra o link; renomear quebra.
    """
    targets = set()
    for _, name in _walk(root):
        if name.endswith(INDEXED_EXT):
            targets.add(name)
            targets.add(os.path.splitext(name)[0])
    return targets


def extract_links(text):
    return [m.strip().split("/")[-1] for m in WIKILINK.findall(text)]


def find_unresolved(root):
    """Conta ocorrencias de wikilink que nao resolvem para nenhum arquivo."""
    targets = index_targets(root)
    unresolved = Counter()
    for dirpath, name in _walk(root):
        if not name.endswith(".md"):
            continue
        with open(os.path.join(dirpath, name), encoding="utf-8") as fh:
            text = fh.read()
        for link in extract_links(text):
            if link not in targets and os.path.splitext(link)[0] not in targets:
                unresolved[link] += 1
    return dict(unresolved)
```

- [ ] **Step 4: Rodar os testes e confirmar que passam**

```bash
python -m unittest discover -s scripts/tests -v
```

Esperado: `Ran 3 tests` / `OK`

- [ ] **Step 5: Commit de checkpoint**

```bash
git add scripts/check_links.py scripts/tests/test_check_links.py
git commit -m "checkpoint(e0): indexacao de alvos do verificador de links"
```

### Correções aplicadas após revisão de código

A revisão do commit inicial encontrou dois falsos negativos — a direção perigosa, em que a contagem parece boa com o vault quebrado. Aplicadas no mesmo passo, com teste de regressão para cada uma.

- [ ] **Step 6: `SKIP_DIRS` exclui `.claude` e `__pycache__`**

```python
SKIP_DIRS = (".git", ".obsidian", ".claude", "__pycache__")
```

O repositório principal contém `.claude/worktrees/<nome>/`, uma cópia completa do vault. Indexada, ela mascara renomeações: o link real quebra, a cópia obsoleta ainda resolve, e a contagem não se move.

- [ ] **Step 7: Normalizar apenas extensões indexadas**

```python
def _normalize(link):
    """Resolve so extensoes que o vault indexa; [[a.png]] nao vira [[a]]."""
    return os.path.splitext(link)[0] if link.endswith(INDEXED_EXT) else link
```

e em `find_unresolved`, uma única checagem: `if _normalize(link) not in targets:`.

Antes, com `architecture.md` presente, `[[architecture.png]]` era reportado como resolvido — e está quebrado no Obsidian.

- [ ] **Step 8: `rstrip("\\")` e descarte de alvo vazio**

```python
def extract_links(text):
    links = []
    for raw in WIKILINK.findall(text):
        target = raw.strip().rstrip("\\").strip().split("/")[-1]
        if target:
            links.append(target)
    return links
```

`\|` é escape obrigatório dentro de célula de tabela. Sem o `rstrip`, os 21 links de tabela do vault viram falso positivo — **todos com alvo existente**. O `if target` descarta o `[[ ]]` vazio.

- [ ] **Step 9: Leitura tolerante a byte inválido**

```python
with open(os.path.join(dirpath, name), encoding="utf-8", errors="replace") as fh:
```

O verificador é portão de aceite de 6 etapas; não pode morrer num arquivo.

- [ ] **Step 10: Quatro testes de regressão**

```python
    def test_all_link_forms_resolve_to_same_target(self):
        root = self.build({
            "a.md": "[[b]] [[sub/b]] [[b|apelido]] [[b#secao]] [[sub/b|apelido]]",
            "sub/b.md": "conteudo",
        })
        self.assertEqual(find_unresolved(root), {})

    def test_counts_every_occurrence(self):
        root = self.build({"a.md": "[[x]] [[x]]", "b.md": "[[x]]"})
        self.assertEqual(find_unresolved(root), {"x": 3})

    def test_escaped_pipe_in_table_resolves(self):
        root = self.build({
            "a.md": "| col | [[b\\|apelido]] |",
            "b.md": "conteudo",
        })
        self.assertEqual(find_unresolved(root), {})

    def test_unindexed_extension_is_not_resolved(self):
        root = self.build({
            "a.md": "veja [[diagrama.png]]",
            "diagrama.md": "conteudo",
        })
        self.assertEqual(find_unresolved(root), {"diagrama.png": 1})
```

Os dois primeiros travam `split("/")[-1]` e a classe `[^\]|#]+` **antes** de a Task 2 reescrever o regex — sem eles, um desvio de dezenas de links passaria com a suíte verde.

Esperado: `Ran 7 tests` / `OK`.

```bash
git commit -m "fix(e0): falsos negativos de indexacao e falso positivo de pipe escapado"
```

---

## Task 2: Verificador — ignorar código cercado

Balde A do spec: `[[ ]]` de teste bash dentro de blocos de código não são links.

> **Medido em 2026-07-29:** das ocorrências não resolvidas, **80 estão dentro de blocos cercados**, 11 dentro de crase simples inline e 150 em prosa. Uma revisão de código afirmou que apenas 2 estavam em fences; a medição refuta isso e esta task segue como projetada. O tratamento de crase inline fica de fora — 11 ocorrências não justificam a complexidade de um parser de inline code, e nenhuma delas é falso positivo estrutural.

**Files:**
- Modify: `scripts/check_links.py`
- Modify: `scripts/tests/test_check_links.py`

- [ ] **Step 1: Escrever o teste que falha**

Acrescentar a `scripts/tests/test_check_links.py`:

```python
class TestFencedCode(VaultFixture):
    def test_ignores_bash_test_brackets_in_fenced_block(self):
        root = self.build({
            "hooks.md": (
                "Exemplo de hook:\n\n"
                "```bash\n"
                'if [[ -d "$dir" ]]; then\n'
                '  echo "$code -eq 124"\n'
                "fi\n"
                "```\n"
            ),
        })
        self.assertEqual(find_unresolved(root), {})

    def test_link_after_fenced_block_still_counts(self):
        root = self.build({
            "a.md": "```bash\n[[ -z \"$pid\" ]]\n```\n\nveja [[fantasma]]",
        })
        self.assertEqual(find_unresolved(root), {"fantasma": 1})

    def test_tilde_fence_also_ignored(self):
        root = self.build({
            "a.md": "~~~sh\n[[ -n \"$line\" ]]\n~~~\n",
        })
        self.assertEqual(find_unresolved(root), {})
```

- [ ] **Step 2: Rodar e confirmar que falha**

```bash
python -m unittest discover -s scripts/tests -v
```

Esperado: `test_ignores_bash_test_brackets_in_fenced_block` FALHA com algo como
`AssertionError: {' -d "$dir" ': 1, ...} != {}`

- [ ] **Step 3: Implementar o descarte de blocos cercados**

Em `scripts/check_links.py`, acrescentar após `WIKILINK`:

```python
FENCE = re.compile(r"^\s*(```|~~~)")
```

E acrescentar a função `strip_fenced`, chamando-a em `extract_links`:

```python
def strip_fenced(text):
    """Remove blocos de codigo cercados.

    Sem isso, `[[ -d "$dir" ]]` do bash e lido como wikilink.
    """
    out = []
    in_fence = False
    for line in text.splitlines():
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        if not in_fence:
            out.append(line)
    return "\n".join(out)


def extract_links(text):
    return [m.strip().split("/")[-1] for m in WIKILINK.findall(strip_fenced(text))]
```

- [ ] **Step 4: Rodar e confirmar que passam**

```bash
python -m unittest discover -s scripts/tests -v
```

Esperado: `Ran 10 tests` / `OK`

- [ ] **Step 5: Commit de checkpoint**

```bash
git add scripts/check_links.py scripts/tests/test_check_links.py
git commit -m "checkpoint(e0): verificador ignora wikilink dentro de codigo cercado"
```

---

## Task 3: Verificador — allowlist e CLI com baseline

Balde B do spec: 27 ocorrências são sintaxe legítima de template (`{{moc-relacionado}}`, `<% tp.date.now(...) %>`) dentro de `shared/templates/`.

**Files:**
- Modify: `scripts/check_links.py`
- Modify: `scripts/tests/test_check_links.py`
- Create: `scripts/baseline.txt`

- [ ] **Step 1: Escrever o teste que falha**

Acrescentar a `scripts/tests/test_check_links.py`:

```python
class TestAllowlist(VaultFixture):
    def test_template_dir_is_skipped(self):
        root = self.build({
            "shared/templates/note.md": "MOC: [[{{moc-relacionado}}]]",
        })
        self.assertEqual(find_unresolved(root), {})

    def test_placeholder_outside_template_dir_is_reported(self):
        root = self.build({
            "finance/nota.md": "MOC: [[{{moc-relacionado}}]]",
        })
        self.assertEqual(find_unresolved(root), {"{{moc-relacionado}}": 1})

    def test_plans_and_specs_are_skipped_as_sources(self):
        """Spec cita nota como exemplo; isso nao e link quebrado do vault."""
        root = self.build({
            "docs/superpowers/specs/design.md": "criar [[nota-que-nao-existe]]",
        })
        self.assertEqual(find_unresolved(root), {})

    def test_allowlisted_dir_is_still_indexed_as_target(self):
        """Template e alvo valido de link, mesmo nao sendo varrido como fonte."""
        root = self.build({
            "shared/templates/note.md": "template",
            "finance/nota.md": "baseado em [[note]]",
        })
        self.assertEqual(find_unresolved(root), {})
```

O último teste trava uma assimetria que é fácil de quebrar por engano: pastas da allowlist **não são varridas como fonte**, mas **continuam sendo indexadas como alvo** — notas legitimamente linkam `[[note-template]]`. `index_targets` percorre tudo; só `find_unresolved` filtra.

- [ ] **Step 2: Rodar e confirmar que falha**

```bash
python -m unittest discover -s scripts/tests -v
```

Esperado: `test_template_dir_is_skipped` FALHA com
`AssertionError: {'{{moc-relacionado}}': 1} != {}`

- [ ] **Step 3: Implementar allowlist e CLI**

Em `scripts/check_links.py`, acrescentar após `SKIP_DIRS`:

```python
ALLOWLIST_PATHS = ("docs/superpowers",)
TEMPLATE_DIR_SUFFIX = "templates"
```

> **Duas regras, e a distinção importa.**
>
> `docs/superpowers/` é **caminho fixo**: specs e planos citam notas como exemplo ilustrativo — este próprio plano contém `[[dcf-valuation]]` e `[[capm]]` em prosa. Medido: **91 das 237 ocorrências (38%) vinham daí**, a maior fonte isolada. Pior, o número se mexe a cada edição de plano, o que o torna inútil como linha de base.
>
> Templates casam por **nome de pasta**, não por caminho. A primeira versão deste plano listava `shared/templates` — que **não existe** (nasce na Task 4), enquanto as pastas reais são `docs/01-templates/`, `finance-vault/11-templates/` e `tech-vault/08-templates/`. E duas delas ainda vão ser renomeadas em E2/E3. Uma lista de caminhos literais precisaria de edição a cada fase, e uma entrada obsoleta para de filtrar em silêncio. A regra de sufixo sobrevive a todas as renomeações sem manutenção.

Acrescentar o predicado e usá-lo no laço de `find_unresolved`:

```python
def is_allowlisted(root, dirpath):
    """Pastas onde wikilink nao resolvido e esperado.

    Duas regras distintas:
    - caminho fixo: specs e planos citam notas como exemplo
    - qualquer pasta cujo nome termine em "templates": placeholders
      {{...}} e <% templater %>. Casa 01-templates, 08-templates,
      11-templates e templates — sobrevive as renomeacoes de E2/E3.

    Puladas como FONTE; continuam indexadas como ALVO.
    """
    rel = os.path.relpath(dirpath, root).replace(os.sep, "/")
    if any(rel == a or rel.startswith(a + "/") for a in ALLOWLIST_PATHS):
        return True
    return any(seg.endswith(TEMPLATE_DIR_SUFFIX) for seg in rel.split("/"))
```

Dentro de `find_unresolved`, logo após `if not name.endswith(".md"): continue`:

```python
        if is_allowlisted(root, dirpath):
            continue
```

E acrescentar o CLI ao final do arquivo:

```python
def main():
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="Verifica wikilinks do vault.")
    parser.add_argument("root", nargs="?", default=".")
    parser.add_argument(
        "--baseline",
        type=int,
        default=None,
        help="Falha se o total de nao resolvidos exceder este numero.",
    )
    args = parser.parse_args()

    unresolved = find_unresolved(args.root)
    total = sum(unresolved.values())

    for target, count in sorted(unresolved.items(), key=lambda kv: -kv[1]):
        print(f"{count:4d}  {target}")
    print(f"\nnao resolvidos: {len(unresolved)} distintos / {total} ocorrencias")

    if args.baseline is not None and total > args.baseline:
        print(f"FALHA: {total} excede a linha de base de {args.baseline}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Rodar e confirmar que passam**

```bash
python -m unittest discover -s scripts/tests -v
```

Esperado: `Ran 23 tests` / `OK`

- [ ] **Step 5: Commit de checkpoint**

```bash
git add scripts/check_links.py scripts/tests/test_check_links.py
git commit -m "checkpoint(e0): allowlist de templates e CLI com --baseline"
```

---

## Task 4: Higiene e linha de base

**Files:**
- Delete: `.claude/agents/mnt/`, `.claude/agents/files.zip`, `tech-vault/01-skills/devops/docker.md`
- Create: `shared/templates/adr.md`, `shared/templates/skill.md`, `scripts/baseline.txt`
- Delete: os 5 templates duplicados

- [ ] **Step 1: Registrar a linha de base antes de qualquer mudança**

```bash
python scripts/check_links.py . | tail -1
```

Esperado: `nao resolvidos: 98 distintos / 155 ocorrencias` (medido em 2026-07-29).

Se o número divergir, **use o medido** — ele é a linha de base real. Anote-o; os deltas dos passos seguintes são relativos a ele.

- [ ] **Step 2: Apagar o lixo**

```bash
git rm -r --quiet .claude/agents/mnt .claude/agents/files.zip tech-vault/01-skills/devops/docker.md
```

- [ ] **Step 3: Consolidar os templates de ADR**

> **Atenção — os três arquivos chamados `adr-template.md` não são duplicatas.** Conferido por estrutura de seções:
>
> | Arquivo | Tamanho | O que é |
> |---|---|---|
> | `docs/01-templates/adr-template.md` | 3.200 B | Template real, placeholders `{{NNNN}}`, mais seções de guia (*Quando Criar um ADR*, *Lifecycle*) |
> | `tech-vault/08-templates/adr-template.md` | 2.529 B | Mesmo template, sintaxe Templater `<% adrNumber %>`, sem as seções de guia |
> | `tech-vault/04-architecture/decisions/adr-template.md` | 11.438 B | **Não é template.** É nota de conhecimento sobre ADRs — MADR vs Nygard, exemplos completos, tooling (`log4brains`, `adr-tools`) |
>
> Só os dois primeiros se consolidam. **O terceiro é conteúdo e não pode ser apagado** — ele é renomeado para `adr-guide.md` na etapa E3, junto do resto da casa tech. Nesta etapa, deixe-o intacto.

Manter a versão de `docs/01-templates/` (é a mais completa) e apagar a de `tech-vault/08-templates/`:

```bash
mkdir -p shared/templates
git mv docs/01-templates/adr-template.md shared/templates/adr.md
git rm --quiet tech-vault/08-templates/adr-template.md
```

- [ ] **Step 3b: Mover o template de skill — sem apagar o homônimo**

> **Atenção — os dois `skill-template.md` também não são duplicatas.** Conferido por estrutura:
>
> | Arquivo | O que é |
> |---|---|
> | `docs/01-templates/skill-template.md` | Template de **Skill do Claude Code** — variantes rígida e flexível, checklist obrigatório, formato de output, gotchas |
> | `tech-vault/08-templates/skill-template.md` | Template de **nota sobre uma tecnologia** — `# <% technology %>`, Overview, Core Concepts, Patterns, Snippets, References |
>
> No segundo, "skill" significa *habilidade técnica*, casando com `tech-vault/01-skills/` (Python, Docker, PostgreSQL). **Não apagar.** Ele é renomeado para `technology-note.md` em E3, junto do resto da casa tech.

```bash
git mv docs/01-templates/skill-template.md shared/templates/skill.md
```

**Resultado do Step 3 + 3b:** de cinco arquivos suspeitos pelo nome, **apenas um era duplicata de verdade** — a variante Templater do ADR. Os outros dois homônimos são conteúdo distinto e ficam onde estão até suas etapas.

- [ ] **Step 4: Congelar a linha de base**

```bash
python -B scripts/check_links.py . --write-baseline scripts/baseline.txt | tail -1
```

`baseline.txt` é a **lista ordenada dos alvos** não resolvidos, um por linha — não um número.

> **Por que conjunto e não soma.** A versão anterior deste plano congelava um inteiro e o portão falhava se o total subisse. Isso permite compensação: uma fase apaga um arquivo do backlog com 2 links mortos e quebra 1 link real — total cai de 2 para 1, portão passa, vault quebrado. Com 62 das 110 ocorrências vindo do backlog do `claude-vault`, que as fases vão consolidar, havia um orçamento de 62 ocorrências para mascarar quebra real.
>
> A regra correta é: **falha se surgir qualquer alvo que não estava na linha de base**, independente de totais. Resolver links continua sendo progresso livre; quebrar links é sempre detectado.

Confirmar que o portão funciona nos dois sentidos:

```bash
python -B scripts/check_links.py . --baseline scripts/baseline.txt > /dev/null; echo "sem mudanca: $?"
printf 'so-um-alvo\n' > /tmp/base-falso.txt
python -B scripts/check_links.py . --baseline /tmp/base-falso.txt > /dev/null; echo "com alvos novos: $?"
```

Esperado: `0` e depois `1`.

- [ ] **Step 5: Rodar os testes e commitar**

```bash
python -m unittest discover -s scripts/tests -v
git add -A
git commit -m "checkpoint(e0): higiene do repo e linha de base do verificador"
```

---

## Task 5: Esqueleto da casa quant

**Files:**
- Create: `quant/CLAUDE.md`

- [ ] **Step 1: Escrever `quant/CLAUDE.md`**

```markdown
# Casa Quant — Vault Inc

## Mandato

A casa quant traduz em duas direções, e é a única que faz isso:

- **← finance:** tese discricionária → hipótese testável (universo, período, fator, critério de rejeição)
- **→ tech:** hipótese validada → código que roda (engine de backtest, pipeline, execução)

Toda entrega desta casa é uma dessas duas traduções, ou a evidência que sustenta uma delas.

## Como alcançar o conhecimento

Carregue `quant/00-index/_house.md` primeiro. Ele lista os domínios e o que cada um
cobre. Escolha o domínio, carregue o `_index.md` dele, e leia apenas as notas que a
tarefa exige. Nunca varra o vault com Glob às cegas.

## Padrões obrigatórios

- **Nenhum resultado sem período, universo e critério de rejeição declarados.** Backtest
  sem isso não é evidência, é anedota.
- **Custos de transação sempre.** Estratégia bruta de custo não é resultado.
- **Viés de sobrevivência tratado e declarado.** Se o dado não é point-in-time, diga.
- **Sharpe reportado com o número de tentativas.** Ver [[sharpe-ratio]] — Sharpe de uma
  estratégia escolhida entre 200 testadas não é o mesmo de uma testada uma vez.
- **Cenário de falha explícito:** em que regime esta estratégia perde dinheiro?

## Fronteira com a casa tech

`market-data-quant` cuida da **correção financeira** do dado — point-in-time, ajuste de
proventos, sobrevivência, splits, corporate actions. **Especifica.**

`data-engineer` (tech) cuida do **transporte** — ingestão, orquestração, storage, SLA,
custo. **Constrói.**

Quando a fronteira ficar ambígua, abra um Cross-Desk Request em vez de decidir sozinho.

## Entregáveis

Vão para o repositório privado, nunca para este:

- Backtests: `reports/quant/<estrategia>-<YYYY-MM-DD>.md`
- Risk reports: `reports/risk/<portfolio>-<YYYY-MM-DD>.md`
- Cross-Desk Requests: `cross-desk/<YYYY-MM-DD>-<from>-<to>.md`

Conhecimento durável que sair de um estudo **sobe para este vault** como nota nova, e o
índice do domínio ganha uma linha.
```

- [ ] **Step 2: Verificar que não introduziu link quebrado**

```bash
python scripts/check_links.py . | grep "sharpe-ratio"
```

Esperado: `sharpe-ratio` ainda aparece como não resolvido (a nota nasce na Task 7). Isso é esperado nesta task.

- [ ] **Step 3: Commit de checkpoint**

```bash
git add quant/CLAUDE.md
git commit -m "checkpoint(e1): mandato e padroes da casa quant"
```

---

## Task 6: Migrar as 5 notas existentes

Move apenas — sem renomear. Basename preservado, portanto nenhum wikilink quebra.

**Files:**
- Move: 5 arquivos de `finance-vault/` para `quant/`

- [ ] **Step 1: Registrar o número antes**

```bash
python scripts/check_links.py . | tail -1
```

Anote o total de ocorrências.

- [ ] **Step 2: Mover os arquivos**

```bash
mkdir -p quant/03-factor-models quant/04-strategies quant/05-backtesting quant/06-risk-analytics
git mv finance-vault/03-analysis/quantitative/factor-investing.md      quant/03-factor-models/
git mv finance-vault/03-analysis/quantitative/momentum-strategies.md   quant/04-strategies/
git mv finance-vault/03-analysis/quantitative/backtesting-basics.md    quant/05-backtesting/
git mv finance-vault/08-frameworks/portfolio-theory-mpt.md             quant/06-risk-analytics/
git mv finance-vault/08-frameworks/position-sizing.md                  quant/06-risk-analytics/
```

- [ ] **Step 3: Confirmar que `03-analysis/quantitative/` ficou vazio**

```bash
ls finance-vault/03-analysis/quantitative/ 2>&1
```

Esperado: diretório vazio ou inexistente. Se sobrou arquivo, ele não estava no spec — parar e reportar.

- [ ] **Step 4: Confirmar que o total não mudou**

```bash
python scripts/check_links.py . | tail -1
```

Esperado: **exatamente o mesmo número do Step 1.** Mover preserva basename, logo preserva link. Qualquer variação significa que um `git mv` renomeou algo — reverter com `git reset --hard` e refazer.

- [ ] **Step 5: Atualizar o frontmatter das 5 notas para o padrão canônico**

Em cada uma das 5 notas, o bloco de frontmatter passa a ter estes campos, preservando `tags`, `aliases`, `created` e `updated` que já existirem. Remover `complexity` e `context` se presentes; consolidar em `level`.

`quant/03-factor-models/factor-investing.md`:
```yaml
house: quant
domain: factor-models
level: intermediate
status: active
```

`quant/04-strategies/momentum-strategies.md`:
```yaml
house: quant
domain: strategies
level: intermediate
status: active
```

`quant/05-backtesting/backtesting-basics.md`:
```yaml
house: quant
domain: backtesting
level: intro
status: active
```

`quant/06-risk-analytics/portfolio-theory-mpt.md`:
```yaml
house: quant
domain: risk-analytics
level: intermediate
status: active
```

`quant/06-risk-analytics/position-sizing.md`:
```yaml
house: quant
domain: risk-analytics
level: intermediate
status: active
```

Definir `updated: 2026-07-29` em todas as cinco.

- [ ] **Step 6: Commit de checkpoint**

```bash
git add -A
git commit -m "checkpoint(e1): migrar 5 notas quantitativas para a casa quant"
```

---

## Task 7: Criar `capm.md` e `sharpe-ratio.md`

Estas duas notas eliminam 8 links fantasma (`capm` ×5, `sharpe-ratio` ×3) do balde D do spec.

**Files:**
- Create: `quant/03-factor-models/capm.md`
- Create: `quant/06-risk-analytics/sharpe-ratio.md`

- [ ] **Step 1: Escrever `quant/03-factor-models/capm.md`**

Frontmatter exato:

```yaml
---
tags: [quant, factor-models, capm, asset-pricing]
aliases: [CAPM, Capital Asset Pricing Model, modelo de precificação de ativos]
house: quant
domain: factor-models
level: intermediate
status: active
created: 2026-07-29
updated: 2026-07-29
---
```

Seções obrigatórias e o que cada uma precisa conter:

1. **`# CAPM — Capital Asset Pricing Model`** — uma frase dizendo o que o modelo afirma.
2. **`## A equação`** — `E(Ri) = Rf + βi · (E(Rm) − Rf)`, com cada termo definido em uma linha: `Rf` (taxa livre de risco), `βi` (sensibilidade ao mercado), `E(Rm) − Rf` (prêmio de risco de mercado).
3. **`## Beta`** — definição como `Cov(Ri, Rm) / Var(Rm)`; o que significa beta 1, <1 e >1; e a advertência de que beta estimado por janela histórica é instável.
4. **`## O que o modelo assume`** — listar explicitamente: mercado eficiente, investidores racionais e avessos a risco, ausência de custos e impostos, possibilidade de emprestar e tomar emprestado à taxa livre de risco, expectativas homogêneas.
5. **`## Limitações`** — nomear as três críticas empíricas: (a) **crítica de Roll** — a carteira de mercado é inobservável, logo o modelo não é testável; (b) beta explica pouco do retorno de corte transversal; (c) anomalias de **size** e **value** que motivaram Fama-French. Ligar a [[factor-investing]].
6. **`## No contexto brasileiro`** — qual proxy usar para `Rf` (Selic ou NTN-B), qual para `E(Rm)` (Ibovespa), e o problema de amostra curta e alta rotatividade do índice.
7. **`## Onde a casa usa`** — custo de capital próprio no WACC, e comparação de retorno ajustado ao risco junto de [[sharpe-ratio]].

**Regra de link:** só usar `[[...]]` para alvos que existem ao fim desta task — `factor-investing`, `sharpe-ratio`, `portfolio-theory-mpt`. Não linkar `wacc` (nasce em E2).

- [ ] **Step 2: Escrever `quant/06-risk-analytics/sharpe-ratio.md`**

Frontmatter exato:

```yaml
---
tags: [quant, risk-analytics, performance, sharpe]
aliases: [Sharpe Ratio, índice de Sharpe, IS]
house: quant
domain: risk-analytics
level: intermediate
status: active
created: 2026-07-29
updated: 2026-07-29
---
```

Seções obrigatórias:

1. **`# Sharpe Ratio`** — o que mede em uma frase: excesso de retorno por unidade de volatilidade.
2. **`## A fórmula`** — `S = (Rp − Rf) / σp`, com cada termo definido, e a regra de anualização `S_anual = S_periodo · √n` com a ressalva de que ela assume retornos i.i.d.
3. **`## Deflated Sharpe`** — a razão de existir: Sharpe de uma estratégia escolhida entre N testadas é enviesado para cima. Explicar que o ajuste penaliza pelo número de tentativas e pela não-normalidade dos retornos. Esta seção é o que a skill `backtest-protocol` cita.
4. **`## Quando o Sharpe mente`** — três casos nomeados: (a) retornos assimétricos ou de cauda gorda, onde desvio-padrão subestima o risco — típico de estratégias vendidas em volatilidade; (b) séries com autocorrelação, que subestimam σ; (c) períodos curtos, onde o erro-padrão do próprio Sharpe é grande.
5. **`## Alternativas`** — **Sortino** (penaliza só o desvio negativo), **Calmar** (retorno sobre drawdown máximo). Uma linha dizendo quando cada uma é preferível.
6. **`## Referência de leitura`** — que Sharpe isolado nunca é critério de aprovação nesta casa; ver os padrões em `quant/CLAUDE.md`.

**Regra de link:** só linkar `position-sizing` e `portfolio-theory-mpt`.

- [ ] **Step 3: Verificar a queda exata**

```bash
python scripts/check_links.py . | grep -E "^\s+[0-9]+\s+(capm|sharpe-ratio)$"
```

Esperado: **nenhuma saída.** Os dois alvos deixaram de estar entre os não resolvidos.

```bash
python scripts/check_links.py . | tail -1
```

Esperado: total caiu em **8 ocorrências** em relação à Task 6 (`capm` ×5 + `sharpe-ratio` ×3), de 110 para 102. Se caiu menos, um dos arquivos ficou com nome errado; se subiu, uma das notas novas linkou alvo inexistente — rodar `python scripts/check_links.py .` e ler a lista.

A asserção do Step 3 anterior (os dois alvos sumirem da lista) é a que vale se o delta divergir por conta de linha de base diferente.

- [ ] **Step 4: Commit de checkpoint**

```bash
git add quant/03-factor-models/capm.md quant/06-risk-analytics/sharpe-ratio.md
git commit -m "checkpoint(e1): notas capm e sharpe-ratio"
```

---

## Task 8: Índices da casa quant

Este é o artefato mais importante do plano — é o formato que E2, E3 e E4 vão replicar sobre 235 arquivos. Errar aqui custa a migração inteira.

**Files:**
- Create: `quant/00-index/_house.md`
- Create: `quant/00-index/factor-models.md`
- Create: `quant/00-index/strategies.md`
- Create: `quant/00-index/backtesting.md`
- Create: `quant/00-index/risk-analytics.md`

- [ ] **Step 1: Escrever os 4 índices de domínio**

`quant/00-index/factor-models.md`:

```markdown
---
house: quant
domain: factor-models
type: index
updated: 2026-07-29
---

# Índice — Modelos de Fatores

| Nota | O que responde | Nível |
|---|---|---|
| [[capm]] | Precificar retorno esperado por exposição ao mercado, e por que o modelo falha empiricamente | intermediate |
| [[factor-investing]] | Quais fatores são remunerados e como construir exposição a eles | intermediate |
```

`quant/00-index/strategies.md`:

```markdown
---
house: quant
domain: strategies
type: index
updated: 2026-07-29
---

# Índice — Estratégias

| Nota | O que responde | Nível |
|---|---|---|
| [[momentum-strategies]] | Construir e testar sinal de momentum, e em que regime ele quebra | intermediate |
```

`quant/00-index/backtesting.md`:

```markdown
---
house: quant
domain: backtesting
type: index
updated: 2026-07-29
---

# Índice — Backtesting

| Nota | O que responde | Nível |
|---|---|---|
| [[backtesting-basics]] | Montar um backtest honesto e os vieses que o invalidam | intro |
```

`quant/00-index/risk-analytics.md`:

```markdown
---
house: quant
domain: risk-analytics
type: index
updated: 2026-07-29
---

# Índice — Risco e Performance

| Nota | O que responde | Nível |
|---|---|---|
| [[sharpe-ratio]] | Medir retorno ajustado ao risco, e os três casos em que a medida mente | intermediate |
| [[portfolio-theory-mpt]] | Combinar ativos na fronteira eficiente e o que a teoria assume | intermediate |
| [[position-sizing]] | Dimensionar posição em função de convicção e risco | intermediate |
```

- [ ] **Step 2: Escrever `quant/00-index/_house.md`**

```markdown
---
house: quant
type: house-index
updated: 2026-07-29
---

# Casa Quant — Índice Mestre

Este é o primeiro arquivo que um agente quant carrega. Escolha o domínio,
abra o índice dele, e leia apenas as notas que a tarefa exigir.

## Domínios ativos

| Domínio | Índice | Cobre |
|---|---|---|
| Modelos de fatores | [[factor-models]] | CAPM, fatores remunerados, construção de exposição |
| Estratégias | [[strategies]] | Momentum e sinais direcionais |
| Backtesting | [[backtesting]] | Metodologia e vieses que invalidam resultado |
| Risco e performance | [[risk-analytics]] | Sharpe, fronteira eficiente, dimensionamento |

## Domínios planejados

Sem nota escrita ainda. Não têm índice e não devem ser referenciados por agente.

| Domínio | Vai cobrir | Status |
|---|---|---|
| Fundamentos matemáticos | Probabilidade, álgebra linear, cálculo estocástico, otimização | planned |
| Séries temporais | Estacionariedade, cointegração, GARCH, regime switching | planned |
| Execução | Microestrutura, slippage, impacto de mercado, TCA | planned |
| ML em finanças | Features, walk-forward, overfitting | planned |
| Dados de mercado | Point-in-time, corporate actions, vendors, B3 vs US | planned |

## Regra de manutenção

Nota nova exige **uma linha** no índice do domínio. Nenhum prompt de agente é
editado. Se um domínio planejado receber sua primeira nota, crie o `_index.md`
dele e mova a linha da tabela de planejados para a de ativos.
```

- [ ] **Step 3: Verificar que todo link do índice resolve**

```bash
python scripts/check_links.py . | grep -E "factor-models|strategies|backtesting|risk-analytics|capm|sharpe-ratio|position-sizing|portfolio-theory-mpt|momentum-strategies|factor-investing"
```

Esperado: **nenhuma saída.** Todos os alvos citados nos índices existem.

- [ ] **Step 4: Verificar o total da E1**

```bash
python scripts/check_links.py . | tail -1
```

Esperado: 102 ocorrências — 8 abaixo da linha de base de 110. Nenhum link novo quebrado.

- [ ] **Step 5: Commit de checkpoint**

```bash
git add quant/00-index/
git commit -m "checkpoint(e1): indices da casa quant"
```

---

## Task 9: Os 4 agentes da casa quant

**Files:**
- Create: `.claude/agents/quant/quant-researcher.md`
- Create: `.claude/agents/quant/quant-developer.md`
- Create: `.claude/agents/quant/risk-quant.md`
- Create: `.claude/agents/quant/market-data-quant.md`

Todos os quatro seguem a mesma anatomia: frontmatter com `name`/`description`/`tools`, seção **Identidade**, **Como alcançar o conhecimento** (o caminho de 3 saltos), **Responsabilidades**, **Padrões obrigatórios**, **O que você NÃO faz**.

- [ ] **Step 1: Criar `quant-researcher.md`**

```markdown
---
name: quant-researcher
description: Pesquisa quantitativa da Vault Inc. Invoque para transformar uma tese em hipótese testável, desenhar estudo de fator, avaliar se um sinal é remunerado e interpretar resultado de backtest.
tools: [Read, Write, Edit, Glob, Grep, Bash]
---

# Quant Researcher

## Identidade

Você é o Quant Researcher da Vault Inc. Seu trabalho é decidir se uma ideia
sobrevive ao contato com os dados. Você é a primeira linha de defesa da casa
contra tese bonita e falsa.

Sua postura padrão é o ceticismo: a hipótese nula é que o sinal não existe.
O ônus da prova é de quem afirma.

## Como alcançar o conhecimento

1. Carregue `quant/00-index/_house.md`
2. Escolha o domínio e carregue o `_index.md` dele
3. Leia apenas as notas que a tarefa exigir

Nunca varra o vault com Glob às cegas.

## Responsabilidades

1. **Traduzir tese em hipótese** — receber uma afirmação discricionária e devolver
   universo, período, definição operacional do sinal e critério de rejeição
   declarados antes de qualquer teste.
2. **Desenhar o estudo** — escolher o método, justificar a escolha, declarar o que
   invalidaria o resultado.
3. **Interpretar** — separar o que o dado mostra do que você gostaria que ele
   mostrasse.

## Padrões obrigatórios

- **Critério de rejeição antes do teste.** Definir o que faria você abandonar a
  hipótese depois de ver o resultado é como se engana honestamente.
- **Declarar quantas variações foram testadas.** Ver [[sharpe-ratio]] — a seção de
  deflated Sharpe existe por isso.
- **Nunca reportar resultado sem período, universo e custos.**
- **Cenário de falha explícito:** em que regime este sinal para de funcionar?

## O que você NÃO faz

- Não implementa a engine de backtest em produção — isso é `quant-developer`
- Não constrói pipeline de dados — isso é `market-data-quant` (especifica) com
  `data-engineer` (constrói)
- Não faz recomendação de compra ou venda a cliente — isso é a casa financeira
- Não decide alocação de portfólio de cliente — isso é `private-banker`
```

- [ ] **Step 2: Criar `quant-developer.md`**

```markdown
---
name: quant-developer
description: Desenvolvimento quantitativo da Vault Inc. Invoque para implementar estratégia em código, construir ou estender engine de backtest, otimizar cálculo numérico e transformar hipótese validada em sistema executável.
tools: [Read, Write, Edit, MultiEdit, Bash, Glob, Grep]
---

# Quant Developer

## Identidade

Você é o Quant Developer da Vault Inc. Você transforma hipótese validada em código
que roda, e é responsável por garantir que o código faz exatamente o que a
especificação diz — nem mais, nem menos.

Seu inimigo é o look-ahead bias introduzido por acidente na implementação. Um
backtest que usa informação do futuro é pior que nenhum backtest, porque parece
resultado.

## Como alcançar o conhecimento

1. Carregue `quant/00-index/_house.md`
2. Escolha o domínio e carregue o `_index.md` dele
3. Leia apenas as notas que a tarefa exigir

## Responsabilidades

1. **Implementar a estratégia** conforme a especificação do `quant-researcher`,
   sem otimizar parâmetro por conta própria.
2. **Engine de backtest** — garantir que a ordem temporal é respeitada em cada
   ponto do pipeline.
3. **Custos e fricções** — modelar corretagem, spread e impacto. Backtest bruto
   de custo não é entregável.
4. **Reprodutibilidade** — semente fixa, versão de dado registrada, mesmo input
   produz mesmo output.

## Padrões obrigatórios

- **Teste de look-ahead em toda feature nova:** deslocar o sinal um período para
  trás deve degradar o resultado. Se não degradar, há vazamento.
- **Nenhum parâmetro mágico sem justificativa** rastreável à especificação.
- **Separar dados de treino, validação e teste** antes de olhar qualquer resultado.
- Ver [[backtesting-basics]] para os vieses que invalidam resultado.

## O que você NÃO faz

- Não decide se a hipótese é boa — isso é `quant-researcher`
- Não provisiona infraestrutura, container ou CI — isso é `devops` na casa tech
- Não define política de risco — isso é `risk-quant`
```

- [ ] **Step 3: Criar `risk-quant.md`**

```markdown
---
name: risk-quant
description: Risco quantitativo da Vault Inc. Invoque para calcular VaR e Expected Shortfall, rodar stress testing, definir limites de mandato, dimensionar posição e avaliar risco de cauda de um portfólio.
tools: [Read, Write, Edit, Bash, Glob, Grep]
---

# Risk Quant

## Identidade

Você é o Risk Quant da Vault Inc. Seu trabalho é responder quanto se pode perder,
com que probabilidade, e em que cenário — antes que a perda aconteça.

Você é estruturalmente pessimista. Quando a estimativa é incerta, você erra para
o lado conservador e diz que errou para esse lado.

## Como alcançar o conhecimento

1. Carregue `quant/00-index/_house.md`
2. Escolha o domínio e carregue o `_index.md` dele
3. Leia apenas as notas que a tarefa exigir

## Responsabilidades

1. **Medidas de risco** — VaR e Expected Shortfall, sempre com horizonte e nível
   de confiança declarados.
2. **Stress testing** — cenários históricos nomeados (2008, março de 2020, maio
   de 2017 no Brasil) e cenários hipotéticos.
3. **Limites** — traduzir mandato em limite operacional por posição, setor e fator.
4. **Dimensionamento** — ver [[position-sizing]].

## Padrões obrigatórios

- **VaR nunca é reportado sozinho.** Ele não diz nada sobre a cauda além do corte;
  sempre acompanhar de Expected Shortfall.
- **Declarar o método** — histórico, paramétrico ou Monte Carlo — e por que ele
  foi escolhido.
- **Declarar a janela** de estimação e a sensibilidade do resultado a ela.
- **Correlação não é estável.** Toda análise que depende de correlação precisa de
  um cenário onde ela vai a 1.
- Ver [[sharpe-ratio]] para por que volatilidade sozinha subestima risco de cauda.

## O que você NÃO faz

- Não faz suitability nem KYC — isso é `compliance-officer` na casa financeira
- Não decide alocação de cliente — isso é `private-banker`
- Não pesquisa sinal novo — isso é `quant-researcher`
```

- [ ] **Step 4: Criar `market-data-quant.md`**

```markdown
---
name: market-data-quant
description: Dados de mercado da Vault Inc. Invoque para especificar requisitos de dado financeiro, auditar qualidade de série histórica, tratar corporate actions e garantir correção point-in-time.
tools: [Read, Write, Edit, Bash, Glob, Grep]
---

# Market Data Quant

## Identidade

Você é o Market Data Quant da Vault Inc. Você é responsável pela **correção
financeira** do dado — não pelo transporte dele.

Seu trabalho existe porque quase todo backtest ruim é ruim por causa do dado, não
do modelo. Preço não ajustado por provento, universo com viés de sobrevivência e
fundamento sem data de divulgação são as três causas mais comuns.

## Como alcançar o conhecimento

1. Carregue `quant/00-index/_house.md`
2. Escolha o domínio e carregue o `_index.md` dele
3. Leia apenas as notas que a tarefa exigir

## Responsabilidades

1. **Point-in-time** — garantir que cada dado esteja disponível na data em que o
   backtest o consome. Fundamento tem data de divulgação, não só data de referência.
2. **Corporate actions** — splits, grupamentos, proventos, JCP, bonificações,
   incorporações. Especificar o tratamento de cada um.
3. **Viés de sobrevivência** — o universo precisa incluir o que foi deslistado.
4. **Especificação para a casa tech** — traduzir requisito financeiro em requisito
   técnico que `data-engineer` possa construir.

## Padrões obrigatórios

- **Toda série entregue vem com:** fonte, janela, tratamento de proventos, política
  de valor faltante e se é point-in-time ou não.
- **Nunca silenciar valor faltante.** Preencher para a frente é decisão que muda
  resultado; se fizer, declare.
- **B3 e mercado americano têm convenções diferentes** de ajuste e de calendário.
  Nunca aplicar a de um no outro sem verificar.

## Fronteira com `data-engineer` (casa tech)

Você **especifica**: o que o dado precisa ser para estar financeiramente correto.

`data-engineer` **constrói**: ingestão, orquestração, storage, SLA e custo.

Quando a fronteira ficar ambígua, abra um Cross-Desk Request em vez de decidir
sozinho.

## O que você NÃO faz

- Não constrói pipeline nem escolhe tecnologia de storage — isso é `data-engineer`
- Não pesquisa sinal — isso é `quant-researcher`
- Não negocia contrato com vendor
```

- [ ] **Step 5: Verificar que os agentes não quebraram nada**

```bash
python scripts/check_links.py . | tail -1
```

Esperado: mesmo total da Task 8. Os agentes só linkam `sharpe-ratio`, `position-sizing` e `backtesting-basics`, que existem.

- [ ] **Step 6: Commit de checkpoint**

```bash
git add .claude/agents/quant/
git commit -m "checkpoint(e1): quatro agentes da casa quant"
```

---

## Task 10: As 2 skills da casa quant

**Files:**
- Create: `.claude/skills/hypothesis-test/SKILL.md`
- Create: `.claude/skills/backtest-protocol/SKILL.md`

- [ ] **Step 1: Criar `hypothesis-test/SKILL.md`**

```markdown
---
name: hypothesis-test
description: Use ao transformar uma tese de investimento discricionária em hipótese testável — define universo, período, sinal operacional e critério de rejeição antes de qualquer teste. Invoque quando alguém disser "será que funciona" sobre um padrão de mercado.
---

# Hipótese Testável

Skill rígida. Os passos são sequenciais e nenhum é opcional.

## Antes de começar

Leia `quant/00-index/_house.md`. Se a tese envolve um fator, leia [[capm]] e
[[factor-investing]] antes de continuar.

**Pare se:** a tese não puder ser escrita como afirmação falsificável. "WEGE3 é uma
empresa de qualidade" não é hipótese. "Empresas com ROIC acima de 15% por 5 anos
consecutivos superam o índice em 12 meses" é.

## Passos

1. **Escreva a hipótese nula.** Comece pelo que você tentaria provar se quisesse
   que a ideia fosse falsa.

2. **Defina o universo.** Quais ativos, com que critério de entrada e saída. Inclua
   deslistados — universo só com sobreviventes já contamina o resultado.

3. **Defina o período.** Data de início, fim e por quê. Declare quantos ciclos
   econômicos ele cobre. Período que começa depois de 2016 no Brasil não viu recessão.

4. **Operacionalize o sinal.** Escreva a regra em termos que não admitam
   interpretação: qual dado, qual transformação, qual limiar, qual frequência de
   rebalanceamento.

5. **Declare o critério de rejeição AGORA.** Antes de ver qualquer resultado, escreva
   o número que faria você abandonar a hipótese. Este passo é o que separa pesquisa
   de racionalização.

6. **Declare o que já foi testado.** Quantas variações desta ideia você já tentou.
   Alimenta o deflated Sharpe — ver [[sharpe-ratio]].

7. **Aponte o cenário de falha.** Em que regime de mercado este sinal deveria parar
   de funcionar? Se você não consegue imaginar um, a hipótese provavelmente está
   mal formulada.

## Critérios de saída

- [ ] Hipótese escrita de forma falsificável
- [ ] Universo declarado, incluindo tratamento de deslistados
- [ ] Período declarado com número de ciclos coberto
- [ ] Regra do sinal sem ambiguidade
- [ ] Critério de rejeição escrito **antes** de qualquer teste
- [ ] Número de variações já testadas registrado
- [ ] Cenário de falha nomeado

## Entregável

Vai para o repositório privado: `cross-desk/<YYYY-MM-DD>-hypothesis-<slug>.md`
```

- [ ] **Step 2: Criar `backtest-protocol/SKILL.md`**

```markdown
---
name: backtest-protocol
description: Use ao rodar ou revisar um backtest de estratégia — aplica os guardrails contra viés de sobrevivência, look-ahead, custos omitidos e Sharpe inflado por múltiplas tentativas. Invoque antes de tratar qualquer resultado de backtest como evidência.
---

# Protocolo de Backtest

Skill rígida. Um backtest que pula qualquer passo não é evidência e não deve ser
reportado como tal.

## Antes de começar

Leia [[backtesting-basics]]. É obrigatório existir uma hipótese formulada pela skill
`hypothesis-test`, com critério de rejeição escrito. **Se não existir, pare** — rodar
backtest sem critério de rejeição prévio produz racionalização, não resultado.

## Passos

1. **Audite o dado antes do modelo.** Confirme com `market-data-quant`: a série é
   point-in-time? Proventos ajustados? Deslistados presentes? Se qualquer resposta
   for não, registre como limitação declarada.

2. **Teste de look-ahead.** Desloque o sinal um período para trás. O resultado
   **precisa** piorar. Se não piorar, há vazamento de informação futura — pare e
   encontre a causa.

3. **Rode fora da amostra.** Separe treino, validação e teste antes de olhar
   qualquer número. Nunca ajuste parâmetro olhando o conjunto de teste.

4. **Aplique custos.** Corretagem, spread e impacto de mercado, com premissa
   declarada para cada um. Estratégia de alta rotatividade morre aqui — e é bom
   que morra no backtest e não no capital.

5. **Calcule o Sharpe e depois o deflated Sharpe.** Use o número de variações
   registrado no passo 6 da `hypothesis-test`. Ver [[sharpe-ratio]] para o porquê.

6. **Reporte o drawdown máximo e a duração dele.** Perda de 40% que leva 3 anos
   para recuperar é inviável na prática mesmo com Sharpe bom.

7. **Confronte com o critério de rejeição.** Compare o resultado com o número
   escrito antes do teste. Se rejeitou, o entregável é a rejeição — e isso é um
   resultado válido e valioso.

8. **Nomeie o regime de falha.** Identifique o pior subperíodo e explique o que
   estava acontecendo no mercado.

## Critérios de saída

- [ ] Qualidade do dado auditada e limitações declaradas
- [ ] Teste de look-ahead executado e resultado registrado
- [ ] Separação treino/validação/teste respeitada
- [ ] Custos aplicados com premissas explícitas
- [ ] Deflated Sharpe reportado junto do Sharpe bruto
- [ ] Drawdown máximo e duração de recuperação reportados
- [ ] Confronto com o critério de rejeição prévio
- [ ] Regime de falha nomeado

## Nunca

- Reportar Sharpe sem o número de variações testadas
- Otimizar parâmetro no conjunto de teste
- Omitir o pior subperíodo do relatório
- Apresentar backtest bruto de custo como resultado

## Entregável

Vai para o repositório privado: `reports/quant/<estrategia>-<YYYY-MM-DD>.md`
```

- [ ] **Step 3: Verificar**

```bash
python scripts/check_links.py . | tail -1
```

Esperado: mesmo total da Task 9.

- [ ] **Step 4: Commit de checkpoint**

```bash
git add .claude/skills/hypothesis-test/ .claude/skills/backtest-protocol/
git commit -m "checkpoint(e1): skills hypothesis-test e backtest-protocol"
```

---

## Task 11: Verificação final da E1

**Files:** nenhum criado — só verificação.

- [ ] **Step 1: Rodar a suíte de testes do verificador**

```bash
python -m unittest discover -s scripts/tests -v
```

Esperado: `Ran 23 tests` / `OK`

- [ ] **Step 2: Confirmar a queda de 8 ocorrências**

```bash
cat scripts/baseline.txt
python scripts/check_links.py . | tail -1
```

Esperado: `110` na baseline e `102` agora (`capm` ×5 + `sharpe-ratio` ×3).

- [ ] **Step 3: Confirmar que `capm` e `sharpe-ratio` sumiram da lista**

```bash
python scripts/check_links.py . | grep -cE "^\s+[0-9]+\s+(capm|sharpe-ratio)$"
```

Esperado: `0`

- [ ] **Step 4: Confirmar que os 4 agentes são descobríveis**

```bash
ls .claude/agents/quant/
```

Esperado: `market-data-quant.md  quant-developer.md  quant-researcher.md  risk-quant.md`

- [ ] **Step 5: Confirmar que as skills têm o layout correto**

```bash
ls .claude/skills/hypothesis-test/ .claude/skills/backtest-protocol/
```

Esperado: `SKILL.md` em cada uma. Skill é diretório, não arquivo solto.

- [ ] **Step 6: Confirmar que toda nota da quant está em um índice**

```bash
for f in $(find quant -name "*.md" -not -path "quant/00-index/*"); do
  b=$(basename "$f" .md)
  grep -rq "\[\[$b\]\]" quant/00-index/ || echo "ORFA: $f"
done
```

Esperado: **nenhuma saída.** Toda nota aparece em algum índice.

- [ ] **Step 7: Commit final da etapa**

```bash
git add -A
git commit -m "checkpoint(e1): verificacao final da casa quant"
```

---

## Estado ao fim deste plano

| Item | Antes | Depois |
|---|---|---|
| Casas estruturadas | 0 | 1 (quant) |
| Agentes quant | 0 | 4 |
| Skills operacionais | 0 | 2 |
| Verificador de links | não existe | 23 testes, portão por conjunto de alvos |
| Links não resolvidos | 110 (baseline) | 102 (baseline − 8) |
| Lixo no repo | `mnt/`, `files.zip`, `docker.md` vazio, 2 templates duplicados | removido |

**Não commitado em `main`.** Todos os commits são checkpoints na branch de trabalho, para squash ao fim de E6 conforme §11.0 do spec.

## Próximo plano

`2026-XX-XX-e2-casa-finance.md` — a etapa de risco alto, com a renomeação emoji→kebab de `finance-vault/`. Só deve ser escrito depois que o formato de índice desta etapa for validado na prática, porque é ele que será replicado sobre ~90 arquivos.
