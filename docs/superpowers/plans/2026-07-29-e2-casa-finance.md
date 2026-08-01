# E2 — Casa Finance — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Migrar as 78 notas do `finance-vault/` para a casa `finance/` no formato validado em E1, escrever as 9 notas de conhecimento que faltam, e religar os agentes da casa ao índice.

**Architecture:** Três estágios com tipos de risco separados. **A** move e renomeia (risco de quebrar link, mitigado por plan/apply com hash). **B** escreve conhecimento novo (risco de conteúdo, não de estrutura). **C** religa agentes e skills, que só então podem citar tudo que existe. Misturar renomeação com escrita de conteúdo no mesmo estágio confunde dois tipos de falha que exigem verificações diferentes.

**Tech Stack:** Python 3.13 (stdlib apenas — `unittest`), Markdown, Obsidian wikilinks, Claude Code agents/skills.

**Spec:** [2026-07-28-vault-restructure-design.md](../specs/2026-07-28-vault-restructure-design.md) — etapa E2 da §11.1.
**Plano anterior:** [2026-07-29-e0-e1-casa-quant.md](2026-07-29-e0-e1-casa-quant.md) — E0 e E1, concluídas.

---

## Estado de partida, medido

| Métrica | Valor |
|---|---|
| Notas em `finance-vault/` | **78** |
| Arquivos com emoji no nome | **6** — todos em `00-MOC/` |
| Arquivos com espaço no nome | **0** |
| Links a reescrever nos 6 MOCs | **21** (27 cru → 23 sem blocos cercados → 21 sem o registro histórico) |
| Linha de base do verificador | **63 alvos / 101 ocorrências** |
| Notas de finance faltando (balde D) | **9 notas / 27 ocorrências** |

### Correção de risco em relação ao spec

O spec §11.1 classifica E2 como risco **alto** e fala em renomeação em massa. Medido, isso está errado: **são 6 renomeações, não ~90.**

O que reduz o risco é a regra do basename — mover `finance-vault/` para `finance/` preserva todos os nomes de arquivo e portanto **não quebra link nenhum**. Só os 6 MOCs com emoji mudam de nome de arquivo, e eles concentram 23 links de entrada.

Isso não torna E2 trivial: 23 links reescritos à mão erram. Mas move o risco de "90 renomeações" para "6 renomeações com 23 referências", que é auditável por revisão humana antes de aplicar — e é exatamente o que o plan/apply do Estágio A entrega.

> **O número é 23, não 27.** O 27 saiu de uma sonda que não descartava blocos de código cercados. Quatro das ocorrências estão dentro de fence — três num plano antigo em `docs/superpowers/` e uma em `docs/01-templates/equity-research-template.md`. Distribuição por alvo, medida pelo dry-run: `Home` 10, `Investments-MOC` 6, `Analysis-MOC` 4, `Accounting-MOC` 1, `Macroeconomics-MOC` 1, `Personal-Finance-MOC` 1.
>
> `docs/superpowers/` é **excluído da reescrita** — o spec cita `🗺️ Home.md` como exemplo da convenção divergente que estamos corrigindo, e reescrevê-lo apagaria o próprio registro diagnóstico. Pastas `*templates` continuam sendo reescritas: template que linka arquivo renomeado passa a emitir link quebrado.

### Padrão emprestado: plan/apply com hash

Vem do projeto `AgriciDaniel/claude-obsidian` (MIT), que não serve para adotar aqui — `init` só monta vault novo, Windows nativo não é suportado, e o `wiki-mode` dele impõe LYT/PARA/Zettelkasten, conflitando com o desenho validado em E1. Mas um mecanismo dele resolve exatamente o problema desta etapa:

> "Pin `--generated-at` and `--operation-id`, review the JSON operation, and pass that exact hash with `--apply`. Filesystem or generated-bundle drift fails before a vault write."

Adaptado: o script emite um plano JSON com todos os moves e todas as reescritas de link, hasheia, e o `--apply` só executa se receber aquele hash **e** se o plano regenerado bater. Se qualquer arquivo mudou entre planejar e aplicar, aborta antes de escrever.

Isso converte "espero que o mapeamento esteja certo" em "revisei o mapeamento exato e o apply está preso a ele".

---

## Estágio A — Migração estrutural

### Task A1: `migrate_house.py` — plano determinístico

**Files:**
- Create: `scripts/migrate_house.py`
- Test: `scripts/tests/test_migrate_house.py`

- [ ] **Step 1: Escrever os testes do plano**

Criar `scripts/tests/test_migrate_house.py`:

```python
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from migrate_house import build_plan, plan_hash, read_map


class MigrationFixture(unittest.TestCase):
    def build(self, files):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        for rel, content in files.items():
            full = os.path.join(self.tmp.name, rel)
            os.makedirs(os.path.dirname(full), exist_ok=True)
            with open(full, "w", encoding="utf-8") as fh:
                fh.write(content)
        return self.tmp.name

    def write_map(self, root, pairs):
        path = os.path.join(root, "map.tsv")
        with open(path, "w", encoding="utf-8") as fh:
            for old, new in pairs:
                fh.write(f"{old}\t{new}\n")
        return path


class TestPlan(MigrationFixture):
    def test_plan_lists_moves_and_rewrites(self):
        root = self.build({
            "old/home.md": "raiz",
            "nota.md": "veja [[home]]",
        })
        mapping = read_map(self.write_map(root, [("old/home.md", "new/_house.md")]))
        plan = build_plan(root, mapping)
        self.assertEqual(plan["moves"], [{"from": "old/home.md", "to": "new/_house.md"}])
        self.assertEqual(
            plan["rewrites"],
            [{"file": "nota.md", "old": "home", "new": "_house", "count": 1}],
        )

    def test_plan_is_deterministic(self):
        root = self.build({
            "old/home.md": "raiz",
            "a.md": "[[home]]",
            "b.md": "[[home]] e [[home]]",
        })
        mapping = read_map(self.write_map(root, [("old/home.md", "new/_house.md")]))
        first = plan_hash(build_plan(root, mapping))
        second = plan_hash(build_plan(root, mapping))
        self.assertEqual(first, second)

    def test_hash_changes_when_a_source_file_changes(self):
        root = self.build({"old/home.md": "raiz", "a.md": "[[home]]"})
        mapping = read_map(self.write_map(root, [("old/home.md", "new/_house.md")]))
        before = plan_hash(build_plan(root, mapping))
        with open(os.path.join(root, "a.md"), "a", encoding="utf-8") as fh:
            fh.write("\nmais um [[home]]\n")
        after = plan_hash(build_plan(root, mapping))
        self.assertNotEqual(before, after)

    def test_missing_source_file_is_reported(self):
        root = self.build({"a.md": "texto"})
        mapping = read_map(self.write_map(root, [("nao/existe.md", "novo.md")]))
        plan = build_plan(root, mapping)
        self.assertEqual(plan["errors"], ["origem inexistente: nao/existe.md"])
```

- [ ] **Step 2: Rodar e confirmar que falham**

```bash
python -B -m unittest discover -s scripts/tests -v 2>&1 | tail -5
```

Esperado: `ModuleNotFoundError: No module named 'migrate_house'`.

- [ ] **Step 3: Implementar o plano**

Criar `scripts/migrate_house.py`:

```python
#!/usr/bin/env python3
"""Move arquivos de uma casa e reescreve os wikilinks, com plan/apply.

O plano e hasheado. O --apply so executa se receber aquele hash e se o
plano regenerado bater — se qualquer arquivo mudou no intervalo, aborta
antes de escrever.
"""

import hashlib
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from check_links import WIKILINK, _walk, _clean, strip_fenced


def read_map(path):
    """Le o TSV old_path<TAB>new_path, ignorando linhas vazias e comentarios."""
    pairs = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.rstrip("\n")
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            old, new = line.split("\t")
            pairs.append((old.strip(), new.strip()))
    return pairs


def build_plan(root, mapping):
    """Monta o plano: moves, reescritas de link e erros detectados."""
    moves, errors = [], []
    rename = {}
    for old, new in mapping:
        if not os.path.isfile(os.path.join(root, old)):
            errors.append(f"origem inexistente: {old}")
            continue
        if os.path.exists(os.path.join(root, new)):
            errors.append(f"destino ja existe: {new}")
            continue
        moves.append({"from": old, "to": new})
        old_base = os.path.splitext(os.path.basename(old))[0]
        new_base = os.path.splitext(os.path.basename(new))[0]
        if old_base != new_base:
            rename[old_base] = new_base

    rewrites = []
    for dirpath, name in _walk(root):
        if not name.endswith(".md"):
            continue
        rel = os.path.relpath(os.path.join(dirpath, name), root).replace(os.sep, "/")
        with open(os.path.join(dirpath, name), encoding="utf-8", errors="replace") as fh:
            text = fh.read()
        counts = {}
        for raw in WIKILINK.findall(strip_fenced(text)):
            target = _clean(raw)
            if target in rename:
                counts[target] = counts.get(target, 0) + 1
        for target in sorted(counts):
            rewrites.append({
                "file": rel,
                "old": target,
                "new": rename[target],
                "count": counts[target],
            })

    return {"moves": moves, "rewrites": rewrites, "errors": errors}


def plan_hash(plan):
    canonical = json.dumps(plan, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
```

- [ ] **Step 4: Rodar e confirmar que passam**

```bash
python -B -m unittest discover -s scripts/tests 2>&1 | tail -3
```

Esperado: `Ran 31 tests` / `OK` (27 do verificador + 4 novos).

- [ ] **Step 5: Commit**

```bash
git add scripts/migrate_house.py scripts/tests/test_migrate_house.py
git commit -m "checkpoint(e2): plano deterministico de migracao de casa"
```

---

### Task A2: `migrate_house.py` — apply preso ao hash

**Files:**
- Modify: `scripts/migrate_house.py`
- Modify: `scripts/tests/test_migrate_house.py`

- [ ] **Step 1: Escrever os testes do apply**

Acrescentar a `scripts/tests/test_migrate_house.py`:

```python
from migrate_house import apply_plan


class TestApply(MigrationFixture):
    def test_apply_moves_file_and_rewrites_link(self):
        root = self.build({
            "old/home.md": "raiz",
            "nota.md": "veja [[home]] agora",
        })
        mapping = read_map(self.write_map(root, [("old/home.md", "new/_house.md")]))
        plan = build_plan(root, mapping)
        apply_plan(root, plan, plan_hash(plan), mapping)
        self.assertTrue(os.path.isfile(os.path.join(root, "new/_house.md")))
        self.assertFalse(os.path.exists(os.path.join(root, "old/home.md")))
        with open(os.path.join(root, "nota.md"), encoding="utf-8") as fh:
            self.assertEqual(fh.read(), "veja [[_house]] agora")

    def test_apply_refuses_wrong_hash(self):
        root = self.build({"old/home.md": "raiz", "nota.md": "[[home]]"})
        mapping = read_map(self.write_map(root, [("old/home.md", "new/_house.md")]))
        plan = build_plan(root, mapping)
        with self.assertRaises(SystemExit):
            apply_plan(root, plan, "0" * 64, mapping)
        self.assertTrue(os.path.isfile(os.path.join(root, "old/home.md")))

    def test_apply_refuses_when_filesystem_drifted(self):
        """O plano foi revisado; alguem editou um arquivo; o apply aborta."""
        root = self.build({"old/home.md": "raiz", "nota.md": "[[home]]"})
        mapping = read_map(self.write_map(root, [("old/home.md", "new/_house.md")]))
        plan = build_plan(root, mapping)
        approved = plan_hash(plan)
        with open(os.path.join(root, "nota.md"), "a", encoding="utf-8") as fh:
            fh.write("\noutro [[home]]\n")
        with self.assertRaises(SystemExit):
            apply_plan(root, plan, approved, mapping)
        self.assertTrue(os.path.isfile(os.path.join(root, "old/home.md")))

    def test_apply_preserves_alias_and_heading(self):
        root = self.build({
            "old/home.md": "raiz",
            "nota.md": "[[home|Início]] e [[home#Seção]]",
        })
        mapping = read_map(self.write_map(root, [("old/home.md", "new/_house.md")]))
        plan = build_plan(root, mapping)
        apply_plan(root, plan, plan_hash(plan), mapping)
        with open(os.path.join(root, "nota.md"), encoding="utf-8") as fh:
            self.assertEqual(fh.read(), "[[_house|Início]] e [[_house#Seção]]")

    def test_apply_preserves_escaped_pipe_in_table(self):
        """Em tabela o pipe vem escapado; apagar a barra quebra a tabela."""
        root = self.build({
            "old/home.md": "raiz",
            "t.md": "| [[home\\|Início]] |",
        })
        mapping = read_map(self.write_map(root, [("old/home.md", "new/_house.md")]))
        plan = build_plan(root, mapping)
        apply_plan(root, plan, plan_hash(plan), mapping)
        with open(os.path.join(root, "t.md"), encoding="utf-8") as fh:
            self.assertEqual(fh.read(), "| [[_house\\|Início]] |")

    def test_apply_refuses_plan_with_errors(self):
        root = self.build({"a.md": "texto"})
        mapping = read_map(self.write_map(root, [("nao/existe.md", "novo.md")]))
        plan = build_plan(root, mapping)
        with self.assertRaises(SystemExit):
            apply_plan(root, plan, plan_hash(plan), mapping)
```

- [ ] **Step 2: Rodar e confirmar que falham**

```bash
python -B -m unittest discover -s scripts/tests -v 2>&1 | tail -5
```

Esperado: `ImportError: cannot import name 'apply_plan'`.

- [ ] **Step 3: Implementar o apply e a CLI**

Acrescentar a `scripts/migrate_house.py`:

```python
def _rewrite_text(text, rename):
    """Troca o alvo dentro de [[...]], preservando alias, heading e barra escapada."""
    def repl(match):
        raw = match.group(1)
        target = _clean(raw)
        if target not in rename:
            return match.group(0)
        return "[[" + raw.replace(target, rename[target], 1) + "]]"

    return re.sub(r"\[\[([^\[\]\n]+?)\]\]", repl, text)


def apply_plan(root, plan, approved_sha256, mapping):
    """Executa o plano, mas so se ele estiver intacto e aprovado."""
    if plan["errors"]:
        for err in plan["errors"]:
            print(f"ERRO: {err}", file=sys.stderr)
        raise SystemExit(1)

    if plan_hash(plan) != approved_sha256:
        print("ERRO: hash aprovado nao corresponde ao plano.", file=sys.stderr)
        raise SystemExit(1)

    fresh = build_plan(root, mapping)
    if plan_hash(fresh) != approved_sha256:
        print(
            "ERRO: o repositorio mudou desde a geracao do plano. "
            "Regere, revise e aprove de novo.",
            file=sys.stderr,
        )
        raise SystemExit(1)

    rename = {}
    for move in plan["moves"]:
        old_base = os.path.splitext(os.path.basename(move["from"]))[0]
        new_base = os.path.splitext(os.path.basename(move["to"]))[0]
        if old_base != new_base:
            rename[old_base] = new_base

    for move in plan["moves"]:
        src = os.path.join(root, move["from"])
        dst = os.path.join(root, move["to"])
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        os.replace(src, dst)

    touched = sorted({r["file"] for r in plan["rewrites"]})
    for rel in touched:
        path = os.path.join(root, rel)
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
        with open(path, "w", encoding="utf-8", newline="") as fh:
            fh.write(_rewrite_text(text, rename))

    print(f"aplicado: {len(plan['moves'])} moves, {len(touched)} arquivos reescritos")
    return 0


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Migra uma casa do vault.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--map", required=True, help="TSV old_path<TAB>new_path")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--approved-plan-sha256")
    args = parser.parse_args()

    mapping = read_map(args.map)
    plan = build_plan(args.root, mapping)
    digest = plan_hash(plan)

    if not args.apply:
        print(json.dumps(plan, indent=2, ensure_ascii=False, sort_keys=True))
        print(f"\napproved_plan_sha256: {digest}")
        if plan["errors"]:
            print(f"\n{len(plan['errors'])} erro(s) — corrija antes de aplicar.")
            return 1
        n_files = len({r["file"] for r in plan["rewrites"]})
        n_links = sum(r["count"] for r in plan["rewrites"])
        print(f"moves: {len(plan['moves'])}  "
              f"arquivos a reescrever: {n_files}  links a reescrever: {n_links}")
        return 0

    if not args.approved_plan_sha256:
        print("ERRO: --apply exige --approved-plan-sha256", file=sys.stderr)
        return 1
    return apply_plan(args.root, plan, args.approved_plan_sha256, mapping)


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Rodar e confirmar que passam**

```bash
python -B -m unittest discover -s scripts/tests 2>&1 | tail -3
```

Esperado: `Ran 37 tests` / `OK`.

- [ ] **Step 5: Commit**

```bash
git add scripts/migrate_house.py scripts/tests/test_migrate_house.py
git commit -m "checkpoint(e2): apply preso ao hash do plano aprovado"
```

---

### Task A3: Mover `finance-vault/` → `finance/`

Movimentação de pasta pura. Nenhum basename muda, portanto nenhum link quebra.

**Files:** 78 arquivos movidos, nenhum renomeado.

- [ ] **Step 1: Registrar o estado antes**

```bash
python -B scripts/check_links.py . | tail -1
```

Esperado: `63 distintos / 101 ocorrencias`.

- [ ] **Step 2: Mover, deixando de fora o que não pertence à casa**

```bash
git mv finance-vault finance
```

Não mova `finance/agents/` nem `finance/reports/` ainda — Task A7 trata os agentes e a E6 leva os reports para o repo privado. Eles ficam onde estão por enquanto.

- [ ] **Step 3: Confirmar contagem inalterada**

```bash
python -B scripts/check_links.py . | tail -1
python -B scripts/check_links.py . --baseline scripts/baseline.txt > /dev/null; echo "exit: $?"
```

Esperado: **exatamente** `63 distintos / 101 ocorrencias` e exit `0`. Qualquer variação significa que o `git mv` renomeou algo — reverter com `git reset --hard` e refazer.

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "checkpoint(e2): finance-vault passa a ser finance"
```

---

### Task A4: Renomear os 6 MOCs com emoji via plan/apply

Esta é a operação de risco da etapa: 6 renomeações concentrando **21 links a reescrever em 9 arquivos**.

Distribuição medida: `Home` 9, `Investments-MOC` 5, `Analysis-MOC` 4, `Accounting-MOC` 1, `Macroeconomics-MOC` 1, `Personal-Finance-MOC` 1.

**Files:**
- Create: `scripts/maps/e2-finance-mocs.tsv`
- Renames: 6 arquivos, 21 links reescritos em 9 arquivos

- [ ] **Step 1: Qualificar o `[[_topics]]` da casa quant**

`quant/00-index/_house.md` linka `[[_topics]]` sem caminho, e hoje `quant/00-index/_topics.md` é o único `_topics` do vault. No instante em que esta etapa criar `finance/00-index/_topics.md`, aquele link fica **ambíguo por basename**.

O Obsidian resolveria certo — prefere a pasta do próprio arquivo — mas o `check_links.py` resolve por basename puro, sem preferência de diretório. Qualificar é explícito e não depende de regra sutil de resolução:

```bash
grep -n "\[\[_topics\]\]" quant/00-index/_house.md
```

Troque por `[[quant/00-index/_topics|_topics]]`, preservando o texto visível. Confirme que o relatório de ambiguidade segue limpo:

```bash
python -B scripts/check_links.py . 2>&1 | tail -3
```

Esperado: `OK: nenhum basename ambiguo linkado sem caminho`.

- [ ] **Step 2: Corrigir dois links que apontam para a casa errada**

Antes de gerar o plano. Dois links dizem `[[tech-vault/00-moc/🗺️ Home|🖥️ Tech Home]]` — o prefixo de caminho aponta para tech, mas o basename é o arquivo do finance, e por isso resolvem acidentalmente para o lugar errado. Tech's home é `tech-vault/00-moc/home.md`.

```bash
grep -rn "tech-vault/00-moc/🗺️ Home" --include="*.md" . | grep -v docs/superpowers
```

Corrija cada um para `[[tech-vault/00-moc/home|🖥️ Tech Home]]`. É correção de conteúdo, não de migração — e se ficar para depois, a renomeação os transforma em link quebrado de verdade.

```bash
python -B scripts/check_links.py . --baseline scripts/baseline.txt > /dev/null; echo "exit: $?"
```
Exit `0`.

- [ ] **Step 3: Escrever o mapa**

Criar `scripts/maps/e2-finance-mocs.tsv` (separador é TAB literal, não espaços). **O emoji precisa ir como UTF-8 com o variation selector U+FE0F** — o nome real é `U+1F5FA` + `U+FE0F` + espaço. Sem o VS16 o script reporta `origem inexistente` silenciosamente:

```
finance/00-MOC/🗺️ Home.md	finance/00-index/_house.md
finance/00-MOC/🗺️ Analysis-MOC.md	finance/00-index/analysis.md
finance/00-MOC/🗺️ Investments-MOC.md	finance/00-index/investments.md
finance/00-MOC/🗺️ Accounting-MOC.md	finance/00-index/accounting.md
finance/00-MOC/🗺️ Macroeconomics-MOC.md	finance/00-index/macro.md
finance/00-MOC/🗺️ Personal-Finance-MOC.md	finance/00-index/personal-finance.md
```

- [ ] **Step 4: Gerar e REVISAR o plano**

```bash
python -B scripts/migrate_house.py --map scripts/maps/e2-finance-mocs.tsv > scripts/maps/e2-plan.json
tail -5 scripts/maps/e2-plan.json
```

Esperado no rodapé: `moves: 6`. Confirme o total de links contra o valor que o dry-run da Task A2 reportou — divergência significa que o mapa está errado ou que algo mudou desde então.

**Leia o plano antes de aplicar.** Confira especificamente:

```bash
grep -c '"file"' scripts/maps/e2-plan.json
grep '"errors"' -A3 scripts/maps/e2-plan.json
```

O array `errors` deve estar vazio. Se houver `origem inexistente`, o caminho no mapa está errado — provavelmente o emoji não foi copiado literalmente.

- [ ] **Step 5: Aplicar preso ao hash**

```bash
HASH=$(grep "approved_plan_sha256:" scripts/maps/e2-plan.json | awk '{print $2}')
echo "hash: $HASH"
python -B scripts/migrate_house.py --map scripts/maps/e2-finance-mocs.tsv \
  --apply --approved-plan-sha256 "$HASH"
```

Esperado: `aplicado: 6 moves, N arquivos reescritos`.

Se aparecer `o repositorio mudou desde a geracao do plano`, algum arquivo foi editado entre gerar e aplicar. Isso é o mecanismo funcionando — regere o plano, revise de novo, aplique.

- [ ] **Step 6: Verificar que nada quebrou**

```bash
python -B scripts/check_links.py . --baseline scripts/baseline.txt | tail -4; echo "exit: ${PIPESTATUS[0]}"
```

Esperado: exit `0`. Os alvos com emoji devem aparecer na lista de **resolvidos** (`+ 🗺️ Home` etc.) porque deixaram de ser citados, e nenhum alvo novo pode surgir.

```bash
find finance -name "*.md" | python -B -c "
import sys
maus = [l.strip() for l in sys.stdin if any(ord(c) > 127 for c in l.split('/')[-1])]
print('arquivos com emoji restantes:', len(maus))
for m in maus: print('  ', m)
"
```

Esperado: `0`.

```bash
grep -rn "🗺️" finance/ --include="*.md" | head
```

Esperado: nenhuma saída. Se sobrar, é wikilink apontando para nome antigo que o plano não pegou — investigar antes de commitar.

- [ ] **Step 7: Conferir o relatório de ambiguidade**

```bash
python -B scripts/check_links.py . 2>&1 | tail -8
```

`finance/00-index/_house.md` passa a existir junto de `quant/00-index/_house.md`, então `_house` fica **ambíguo por basename**. O relatório vai apontar. Isso é esperado e não bloqueia: os agentes alcançam o arquivo por caminho, via a coluna `Pasta`. O que não pode acontecer é algum arquivo linkar `[[_house]]` sem qualificar o caminho — se o relatório listar isso, corrija para `[[finance/00-index/_house]]`.

- [ ] **Step 8: Commit**

```bash
git add -A
git commit -m "checkpoint(e2): MOCs com emoji viram indices em kebab-case"
```

---

### Task A5: Frontmatter canônico nas 78 notas

Medido no `finance-vault`: 73 notas têm `complexity` e `context` (os campos que consolidam em `level` + `domain`), 45 têm `status`, 52 têm `updated`, 18 têm `created`.

**Files:** as 78 notas de `finance/`, só o bloco de frontmatter.

- [ ] **Step 1: Escrever os testes do normalizador**

Ele reescreve o frontmatter de 78 notas de uma vez. `--dry-run` ajuda, mas não substitui teste — um mapeamento errado de `complexity` corrompe as 78 silenciosamente.

Criar `scripts/tests/test_normalize_frontmatter.py`:

```python
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from normalize_frontmatter import normalize_note, derive_domain


class TestDeriveDomain(unittest.TestCase):
    def test_nested_path_becomes_slash_domain(self):
        self.assertEqual(derive_domain("finance/02-investments/equities/a.md"), "investments/equities")

    def test_flat_path_drops_numeric_prefix(self):
        self.assertEqual(derive_domain("finance/05-accounting/a.md"), "accounting")


class TestNormalize(unittest.TestCase):
    def test_complexity_becomes_level_and_is_removed(self):
        out = normalize_note(
            "---\ntags: [a]\ncomplexity: basic\ncontext: x\n---\n\n# T\n",
            house="finance", domain="accounting", updated="2026-07-29",
        )
        self.assertIn("level: intro", out)
        self.assertNotIn("complexity:", out)
        self.assertNotIn("context:", out)

    def test_preserves_tags_aliases_created(self):
        out = normalize_note(
            "---\ntags: [a, b]\naliases: [X]\ncreated: 2026-01-01\n---\n\ncorpo\n",
            house="finance", domain="markets", updated="2026-07-29",
        )
        self.assertIn("tags: [a, b]", out)
        self.assertIn("aliases: [X]", out)
        self.assertIn("created: 2026-01-01", out)

    def test_defaults_when_fields_absent(self):
        out = normalize_note(
            "---\ntags: []\n---\n\ncorpo\n",
            house="finance", domain="markets", updated="2026-07-29",
        )
        self.assertIn("level: intermediate", out)
        self.assertIn("status: active", out)
        self.assertIn("house: finance", out)

    def test_body_is_untouched(self):
        body = "\n# Titulo\n\nParagrafo com [[link]] e `codigo`.\n"
        out = normalize_note(
            "---\ntags: []\n---" + body,
            house="finance", domain="markets", updated="2026-07-29",
        )
        self.assertTrue(out.endswith(body))

    def test_note_without_frontmatter_gains_one(self):
        out = normalize_note("# Sem frontmatter\n", house="finance",
                             domain="markets", updated="2026-07-29")
        self.assertTrue(out.startswith("---\n"))
        self.assertIn("# Sem frontmatter", out)
```

- [ ] **Step 2: Rodar e confirmar que falham**

```bash
python -B -m unittest discover -s scripts/tests -v 2>&1 | tail -4
```

Esperado: `ModuleNotFoundError: No module named 'normalize_frontmatter'`.

- [ ] **Step 3: Escrever o normalizador**

Criar `scripts/normalize_frontmatter.py`, expondo `derive_domain(rel_path)` e `normalize_note(text, house, domain, updated)` além da CLI. Para cada nota:

- preserva `tags`, `aliases`, `created`, `title` se existirem
- adiciona `house: finance`
- deriva `domain` do caminho: `finance/02-investments/equities/x.md` → `domain: investments/equities`
- converte `complexity` em `level`, mapeando `basic`→`intro`, `beginner`→`intro`, e mantendo `intermediate`/`advanced`; se não houver `complexity`, usa `level: intermediate`
- **remove** `complexity` e `context`
- garante `status: active` se ausente
- define `updated: 2026-07-29`
- ordem final: `tags`, `aliases`, `house`, `domain`, `level`, `status`, `created`, `updated`

Rode com `--dry-run` primeiro, listando quantas notas mudam e quais campos são removidos, antes de aplicar.

- [ ] **Step 4: Aplicar e verificar**

```bash
python -B scripts/normalize_frontmatter.py --root . --house finance --dir finance --dry-run | tail -5
python -B scripts/normalize_frontmatter.py --root . --house finance --dir finance --apply
grep -rl -E "^(complexity|context):" finance/ --include="*.md"
```

O último comando não deve ter saída.

```bash
python -B -c "
import os, re, collections
c = collections.Counter()
for dp, dn, fn in os.walk('finance'):
    for f in fn:
        if not f.endswith('.md'): continue
        t = open(os.path.join(dp,f), encoding='utf-8', errors='replace').read()
        if not t.startswith('---'): c['<sem frontmatter>'] += 1; continue
        for k in re.findall(r'^(\w[\w-]*):', t.split('---',2)[1], re.M): c[k] += 1
print(dict(c))
"
```

`house` e `domain` devem contar 78 menos os arquivos que não são nota (os 2 agentes e o report). Reporte o número exato.

```bash
python -B scripts/check_links.py . --baseline scripts/baseline.txt > /dev/null; echo "exit: $?"
```
Esperado `0` — normalizar frontmatter não deve tocar link nenhum.

- [ ] **Step 5: Commit**

```bash
python -B -m unittest discover -s scripts/tests 2>&1 | tail -3
git add -A
git commit -m "checkpoint(e2): frontmatter canonico nas notas de finance"
```

Esperado: `Ran 43 tests` / `OK` (37 + 6 do normalizador).

---

### Task A6: Índices da casa finance

O formato é o validado em E1 e **não deve ser reinventado**. Leia antes: `quant/00-index/_house.md`, `quant/00-index/_topics.md` e `quant/00-index/risk-analytics.md`.

**Files:**
- Rewrite: `finance/00-index/_house.md`, `analysis.md`, `investments.md`, `accounting.md`, `macro.md`, `personal-finance.md` (vêm dos MOCs renomeados, com formato antigo)
- Create: `finance/00-index/fundamentals.md`, `psychology.md`, `frameworks.md`, `glossary.md`, `snippets.md`, `_topics.md`

Os 6 arquivos renomeados na Task A4 ainda têm conteúdo de MOC — prosa e listas de links. **A curadoria deles tem valor**: representa o que o autor agrupou. Use-a como fonte das linhas da tabela, mas adote o formato novo.

- [ ] **Step 1: Mapear domínio → pasta → notas**

```bash
for d in finance/0*/ finance/1*/; do
  n=$(find "$d" -name "*.md" | wc -l)
  echo "$n  $d"
done
```

Contagens medidas em 2026-07-29 (confirme; podem ter mudado):

| Domínio | Pasta | Notas |
|---|---|---|
| Fundamentos | `finance/01-fundamentals/` | 6 |
| Investimentos | `finance/02-investments/` | 16 |
| Análise | `finance/03-analysis/` | 11 |
| Finanças pessoais | `finance/04-personal-finance/` | 6 |
| Contabilidade | `finance/05-accounting/` | 5 |
| Mercados | `finance/06-markets/` | 5 |
| Psicologia | `finance/07-psychology/` | 4 |
| Frameworks | `finance/08-frameworks/` | 2 |
| Glossário | `finance/09-glossary/` | 4 |
| Snippets | `finance/10-snippets/` | 3 |

> **`investments` está com 16 linhas, no teto de 15–20 da §5 do spec.** Mantenha como um índice só nesta etapa, mas registre em `_house.md` na regra de manutenção que ele é o primeiro candidato a divisão — por subpasta (`equities`, `fixed-income`, `funds`, `derivatives`, `alternatives`) — quando ganhar a próxima nota.

- [ ] **Step 2: Escrever os índices de domínio**

Um `_index.md` por domínio, com frontmatter `house: finance`, `domain: <nome>`, `type: index`, `updated: 2026-07-29`, um H1 e a tabela `| Nota | O que responde | Nível |`.

**A coluna "O que responde" é o mecanismo inteiro.** Escreva cada linha como a pergunta que a nota responde ou o que o leitor consegue fazer depois de lê-la — não como o tópico dela. Leia cada nota; não derive do título. Ruim: `[[dcf-valuation]] | Explica DCF`. Bom: `[[dcf-valuation]] | Projetar FCF e descontar à WACC, e quando o método não se aplica`.

- [ ] **Step 3: Escrever `_house.md` no formato validado**

Precisa ter, na ordem: o parágrafo de instrução dos três saltos; o parágrafo **"Como abrir uma nota"** com a convenção `<pasta>/<nome>.md` e o aviso de que os prefixos numéricos não são deriváveis; a tabela **Domínios ativos** com as colunas `| Domínio | Índice | Pasta | Cobre |`; a seção **Temas transversais** apontando `[[_topics]]`; e a **Regra de manutenção** com a regra de uma linha por nota, o teto de 15–20 linhas, a nota sobre `investments` estar no teto, e o aviso de que `Nível` não é sinal de roteamento.

A coluna `Pasta` é obrigatória e foi a correção que salvou a E1 — sem ela o agente adivinha o caminho e cai numa varredura.

- [ ] **Step 4: Escrever `_topics.md`**

Formato `| Tema | Onde começar | Também tratado em |`.

**Critério de inclusão: dispersão entre domínios, não contagem de notas.** O teste é — existe um domínio que responde a pergunta sozinho? Se existe, o tema pertence ao índice daquele domínio.

**Confirme cada tema lendo o hit, não contando `grep`.** Na quant, três alegações derivadas de palavra-chave eram artefato: "survivorship em 6 notas" eram 4, porque um hit era citação de Van Tharp e outro era sobre overfitting.

Temas prováveis nesta casa, a confirmar: inflação e correção monetária, tributação brasileira, liquidez, risco de crédito, horizonte de investimento, vieses comportamentais. Não invente linha para tema que vive num único domínio.

- [ ] **Step 5: Verificar**

```bash
python -B scripts/check_links.py . --baseline scripts/baseline.txt | tail -4; echo "exit: ${PIPESTATUS[0]}"
```
Exit `0`. Só linke alvos que existem — as 9 notas do Estágio B **ainda não existem** e não podem ser linkadas aqui.

Todo caminho declarado tem de existir:
```bash
grep -o '`finance/[^`]*`' finance/00-index/_house.md | tr -d '`' | sort -u | while read p; do
  if [ -d "$p" ] || [ -f "$p" ]; then echo "OK    $p"; else echo "FALTA $p"; fi
done
```
Toda linha `OK`.

Nenhuma nota órfã de índice:
```bash
for f in $(find finance -name "*.md" -not -path "finance/00-index/*" -not -path "finance/11-templates/*" -not -path "finance/agents/*" -not -path "finance/reports/*"); do
  b=$(basename "$f" .md)
  grep -rq "\[\[$b" finance/00-index/ || echo "ORFA: $f"
done
```
Nenhuma saída.

- [ ] **Step 6: Commit**

```bash
git add finance/00-index
git commit -m "checkpoint(e2): indices da casa finance"
```

---

### Task A7: `finance/CLAUDE.md`

**Files:**
- Create: `finance/CLAUDE.md`
- Delete: `finance/agents/financial-research-house/CLAUDE.md` (conteúdo absorvido)

O `CLAUDE.md` antigo dos agentes tem material bom que precisa sobreviver: os padrões obrigatórios da casa (margem de segurança, disclosures, compliance CVM 30, risk warnings) e as regras de colaboração. Leia-o antes de escrever.

- [ ] **Step 1: Escrever `finance/CLAUDE.md`**

Espelhe a estrutura de `quant/CLAUDE.md` (leia primeiro). Precisa de:

- **Mandato** — research fundamentalista, wealth management e crédito; a casa que fala com o cliente.
- **Como alcançar o conhecimento** — os três saltos, apontando `finance/00-index/_house.md` e `_topics.md`.
- **Padrões obrigatórios** — toda recomendação de equity apoiada em valuation explícita com sensibilidade; disclosure de conflito de interesse e premissas-chave; cenário bear com perda máxima estimada; suitability e CVM 30; citação dos arquivos do vault que sustentam a tese.
- **Fronteira com a casa quant** — tese discricionária vira hipótese testável no `quant-researcher`; a casa finance não roda backtest nem produz evidência estatística por conta própria.
- **Entregáveis** — reports de equity em `reports/equity/<ticker>-<YYYY-MM-DD>.md`, IPS em `clients/<cliente>/IPS-<YYYY-MM-DD>.md`, ambos **no repo privado**.

- [ ] **Step 2: Remover o CLAUDE.md antigo e verificar**

```bash
git rm --quiet finance/agents/financial-research-house/CLAUDE.md
python -B scripts/check_links.py . --baseline scripts/baseline.txt > /dev/null; echo "exit: $?"
```
Exit `0`.

- [ ] **Step 3: Commit**

```bash
git add -A
git commit -m "checkpoint(e2): mandato e padroes da casa finance"
```

---

## Estágio B — As 9 notas que faltam

Escritas **depois** da migração estrutural, de propósito: renomear arquivo e escrever conhecimento novo são riscos de natureza diferente, com verificações diferentes. Misturados, uma falha fica ambígua.

Estas 9 notas eliminam 27 ocorrências do balde D e são todas citadas por notas que já existem.

| Nota | Ocorr. | Destino |
|---|---|---|
| `dcf-valuation` | 5 | `finance/03-analysis/fundamental/` |
| `moats` | 5 | `finance/03-analysis/fundamental/` |
| `selic-and-monetary-policy` | 5 | `finance/03-analysis/macro/` |
| `hedging-strategies` | 4 | `finance/02-investments/derivatives/` |
| `wacc` | 3 | `finance/03-analysis/fundamental/` |
| `roe-roic` | 2 | `finance/05-accounting/` |
| `gdp-and-growth` | 1 | `finance/03-analysis/macro/` |
| `jcp` | 1 | `finance/09-glossary/` |
| `order-book` | 1 | `finance/06-markets/` |

### Task B1: Valuation — `dcf-valuation`, `wacc`, `moats`

**Files:**
- Create: `finance/03-analysis/fundamental/dcf-valuation.md`, `wacc.md`, `moats.md`

Frontmatter para as três, ajustando `aliases`:

```yaml
---
tags: [finance, analysis, fundamental, valuation]
aliases: []
house: finance
domain: analysis/fundamental
level: advanced
status: active
created: 2026-07-29
updated: 2026-07-29
---
```

- [ ] **Step 1: `dcf-valuation.md`**

Aliases: `[DCF, Fluxo de Caixa Descontado, Discounted Cash Flow]`.

Seções obrigatórias:

1. `# DCF — Fluxo de Caixa Descontado` — uma frase sobre o que o método afirma.
2. `## A mecânica` — projeção de FCF explícito, desconto à WACC, valor terminal. A fórmula do valor presente e a do valor terminal por perpetuidade de Gordon.
3. `## FCF: qual usar` — FCFF vs FCFE, e a que taxa cada um se desconta (FCFF à WACC, FCFE ao custo de equity). Errar esse par é o erro mais comum e produz resultado silenciosamente errado.
4. `## Valor terminal` — que ele costuma ser 60–80% do valor total, e que `g` **não pode exceder o crescimento nominal do PIB de longo prazo**, sem exceção.
5. `## Sensibilidade obrigatória` — matriz WACC × g, e por que apresentar DCF com número único é enganoso: a dispersão é o resultado.
6. `## Quando NÃO se aplica` — bancos e seguradoras (a estrutura de capital é o negócio; use múltiplos de patrimônio ou dividendos), empresas pré-receita, cíclicas no pico. Ligar a `[[wacc]]`.
7. `## No Brasil` — inflação e o problema de projetar em nominal vs real, a volatilidade da taxa de desconto quando a Selic se move, e ligar a `[[selic-and-monetary-policy]]`.
8. `## Onde a casa usa` — a skill `dcf-valuation` executa; esta nota explica.

- [ ] **Step 2: `wacc.md`**

Aliases: `[WACC, Custo Médio Ponderado de Capital]`.

Seções: `# WACC`; `## A fórmula` (`WACC = E/V·Re + D/V·Rd·(1−T)`, cada termo definido); `## Custo de equity` (via CAPM, ligando a `[[capm]]` do vault quant); `## Custo de dívida` (por que é pós-imposto, e usar custo marginal e não histórico); `## Pesos` (a valor de mercado, nunca contábil); `## No Brasil` (proxy de `Rf`, prêmio de risco-país, e que a estrutura de capital brasileira tem dívida mais curta e mais caro rolar); `## Erros comuns` (usar beta de janela curta — ligar a `[[capm]]`; usar peso contábil; esquecer o benefício fiscal).

- [ ] **Step 3: `moats.md`**

Aliases: `[Moat, Vantagem Competitiva, Economic Moat]`.

Seções: `# Moats`; `## O que é` (vantagem que sustenta retorno acima do custo de capital por tempo longo — a definição operacional é ROIC persistentemente acima da WACC, ligando a `[[roe-roic]]` e `[[wacc]]`); `## As cinco fontes` (efeito de rede, custo de troca, vantagem de custo, ativo intangível, escala eficiente — uma linha de teste para cada); `## Como testar` (série de ROIC de 10 anos, estabilidade de market share, poder de preço acima da inflação); `## Como moats morrem` (tecnologia, regulação, mudança de comportamento); `## No Brasil` (concentração setorial, moats regulatórios em utilities e concessões, e por que barreira regulatória é frágil a ciclo político).

- [ ] **Step 4: Verificar**

```bash
python -B scripts/check_links.py . --baseline scripts/baseline.txt | tail -5; echo "exit: ${PIPESTATUS[0]}"
```

Exit `0`. **Só linke o que já existe** — nesta task, `wacc`, `moats`, `dcf-valuation`, `capm`, e as notas do finance que já existiam. `roe-roic` e `selic-and-monetary-policy` nascem nas tasks B2 e B3; se você quiser citá-las, faça isso **em texto simples** e converta em wikilink na Task B4.

- [ ] **Step 5: Commit**

```bash
git add finance/03-analysis/fundamental
git commit -m "checkpoint(e2): notas dcf-valuation, wacc e moats"
```

---

### Task B2: Macro e contabilidade — `selic-and-monetary-policy`, `gdp-and-growth`, `roe-roic`

**Files:**
- Create: `finance/03-analysis/macro/selic-and-monetary-policy.md`, `gdp-and-growth.md`
- Create: `finance/05-accounting/roe-roic.md`

- [ ] **Step 1: `selic-and-monetary-policy.md`**

`domain: analysis/macro`, `level: intermediate`, aliases `[Selic, Política Monetária, Copom]`.

Seções: `# Selic e política monetária`; `## O que a Selic é` (meta vs efetiva, e quem decide — Copom, 8 reuniões/ano); `## Mecanismo de transmissão` (juro → crédito → demanda → inflação, com a defasagem de 6 a 9 meses); `## Regime de metas` (a meta de inflação, a banda, e o que acontece quando estoura); `## Efeito nos ativos` (renda fixa: marcação a mercado e duration; equities: taxa de desconto e setores sensíveis a crédito; câmbio: diferencial de juros); `## Como ler o Copom` (o comunicado, a ata, e por que a expectativa importa mais que a decisão); `## Onde a casa usa` (proxy de `Rf` — ligar a `[[wacc]]`).

- [ ] **Step 2: `gdp-and-growth.md`**

`domain: analysis/macro`, `level: intro`, aliases `[PIB, GDP, Crescimento Econômico]`.

Seções: `# PIB e crescimento`; `## As três óticas` (produção, despesa, renda — e que devem fechar); `## Nominal vs real` (deflator, e por que comparar nominal entre anos é erro); `## No Brasil` (divulgação trimestral do IBGE, revisões, e a composição por setor); `## Por que importa para valuation` (é o teto do `g` de perpetuidade — ligar a `[[dcf-valuation]]`).

- [ ] **Step 3: `roe-roic.md`**

`domain: accounting`, `level: intermediate`, aliases `[ROE, ROIC, Retorno sobre Capital]`.

Seções: `# ROE e ROIC`; `## As fórmulas` (`ROE = Lucro Líquido / PL`, `ROIC = EBIT·(1−T) / Capital Investido`, com capital investido definido); `## Por que ROIC é superior para julgar o negócio` (ROE é inflável por alavancagem — o mesmo negócio com mais dívida mostra ROE maior sem ter melhorado); `## DuPont` (decompor ROE em margem × giro × alavancagem, e o que cada componente revela); `## ROIC vs WACC` (a comparação que define se a empresa cria ou destrói valor — ligar a `[[wacc]]` e `[[moats]]`); `## Armadilhas` (PL negativo, intangível de aquisição inflando capital investido, um único ano não é sinal).

- [ ] **Step 4: Verificar e commitar**

```bash
python -B scripts/check_links.py . --baseline scripts/baseline.txt > /dev/null; echo "exit: $?"
git add finance/03-analysis/macro finance/05-accounting
git commit -m "checkpoint(e2): notas selic, pib e roe-roic"
```

---

### Task B3: `hedging-strategies`, `jcp`, `order-book`

**Files:**
- Create: `finance/02-investments/derivatives/hedging-strategies.md`
- Create: `finance/09-glossary/jcp.md`
- Create: `finance/06-markets/order-book.md`

- [ ] **Step 1: `hedging-strategies.md`**

`domain: investments/derivatives`, `level: advanced`, aliases `[Hedge, Estratégias de Hedge, Hedging]`.

Seções: `# Estratégias de hedge`; `## O que hedge é e não é` (transferir risco a um custo, não eliminar risco de graça; hedge tem preço e o preço é o retorno esperado que você abre mão); `## Instrumentos na B3` (futuro de índice, futuro de dólar, opções, DI futuro — um caso de uso por instrumento); `## Hedge cambial` (para quem tem receita ou ativo em dólar, e o custo de carrego pelo diferencial de juros); `## Protective put e collar` (o custo do prêmio, e como o collar financia a proteção abrindo mão de upside); `## Razão de hedge` (por que 100% raramente é ótimo, e o risco de base quando o instrumento não casa com a exposição); `## Erros` (hedgear depois do evento, confundir hedge com especulação direcional, ignorar chamada de margem no hedge).

- [ ] **Step 2: `jcp.md`**

`domain: glossary`, `level: intro`, aliases `[JCP, Juros sobre Capital Próprio]`.

Seções: `# JCP — Juros sobre Capital Próprio`; `## O que é` (instrumento brasileiro de distribuição, dedutível para a empresa); `## Por que existe` (a dedutibilidade gera economia fiscal na empresa que o dividendo não gera); `## Tributação` (15% retido na fonte para o investidor, contra dividendo isento — e por que a comparação líquida é o que importa); `## Limites` (a base de cálculo pela TJLP sobre o PL, com teto); `## Efeito prático` (por que JCP bruto não é comparável a dividendo bruto, e o ajuste correto para comparar yield).

- [ ] **Step 3: `order-book.md`**

`domain: markets`, `level: intermediate`, aliases `[Book de Ofertas, Livro de Ordens, Order Book]`.

Seções: `# Book de ofertas`; `## Estrutura` (bid, ask, spread, profundidade por nível de preço); `## Tipos de ordem` (mercado, limitada, stop — e o que cada uma faz ao book); `## Prioridade` (preço, depois tempo); `## Spread e liquidez` (o spread como custo de transação real, e por que ele abre em estresse); `## Impacto de mercado` (por que ordem grande anda o preço, e a relação com % do volume diário); `## Na B3` (leilão de abertura e fechamento, circuit breaker, e a concentração de liquidez em poucos papéis).

- [ ] **Step 4: Verificar e commitar**

```bash
python -B scripts/check_links.py . --baseline scripts/baseline.txt > /dev/null; echo "exit: $?"
git add finance/02-investments finance/09-glossary finance/06-markets
git commit -m "checkpoint(e2): notas hedging, jcp e order-book"
```

---

### Task B4: Fechar os índices e o balde D

**Files:**
- Modify: os índices de domínio afetados, `finance/00-index/_topics.md`

- [ ] **Step 1: Acrescentar uma linha por nota nova ao índice do seu domínio**

Nove notas, nove linhas. `analysis.md` recebe cinco (`dcf-valuation`, `wacc`, `moats`, `selic-and-monetary-policy`, `gdp-and-growth`) — **confira se ela não cruza o teto de 15–20 linhas**; se cruzar, divida em `analysis-fundamental.md` e `analysis-macro.md`, atualizando `_house.md`.

- [ ] **Step 2: Converter as referências em texto simples em wikilink**

As tasks B1–B3 pediram menções em texto quando o alvo ainda não existia. Agora todos existem:

```bash
grep -rn "roe-roic\|selic-and-monetary-policy\|order-book\|hedging-strategies" finance/ --include="*.md" | grep -v "\[\[" | grep -v 00-index
```

Converta as menções relevantes em wikilink. Não force: só onde o link ajuda o leitor.

- [ ] **Step 3: Verificar a eliminação do balde D**

```bash
python -B scripts/check_links.py . | tail -1
python -B scripts/check_links.py . | grep -E "^\s+[0-9]+\s+(dcf-valuation|wacc|moats|selic-and-monetary-policy|gdp-and-growth|roe-roic|jcp|order-book|hedging-strategies)$"
```

O `grep` não deve ter saída. A contagem deve cair de 101 para **74 ocorrências** (−27) e de 63 para **54 alvos** (−9).

```bash
python -B scripts/check_links.py . --baseline scripts/baseline.txt | tail -12; echo "exit: ${PIPESTATUS[0]}"
```
Exit `0`, com as 9 aparecendo como resolvidas.

- [ ] **Step 4: Recongelar a linha de base e commitar**

```bash
python -B scripts/check_links.py . --write-baseline scripts/baseline.txt | tail -1
git add -A
git commit -m "checkpoint(e2): balde D eliminado, linha de base em 54 alvos"
```

---

## Estágio C — Agentes e skills

### Task C1: Os 6 agentes da casa finance

**Files:**
- Create: `.claude/agents/finance/equity-research-analyst.md` (reescrito de `finance/agents/financial-research-house/`)
- Create: `.claude/agents/finance/private-banker.md` (idem)
- Create: `.claude/agents/finance/credit-research-analyst.md`
- Create: `.claude/agents/finance/macro-strategist.md`
- Create: `.claude/agents/finance/pe-analyst.md`
- Create: `.claude/agents/finance/compliance-officer.md`
- Delete: `finance/agents/` inteiro

**O motivo de reescrever os dois existentes, e não copiar:** `equity-research-analyst.md` cita **23 arquivos do vault direto no prompt**. É exatamente a patologia que este projeto existe para eliminar — cada nota nova exigiria editar o agente à mão. As citações diretas saem e entra o bloco de roteamento de três saltos.

Leia antes: os quatro agentes em `.claude/agents/quant/` (anatomia e tom), e os dois antigos em `finance/agents/financial-research-house/` (o conteúdo de domínio que precisa sobreviver).

- [ ] **Step 1: Escrever os 6**

Cada um com frontmatter `name`, `description`, `tools`, e as seções `## Identidade`, `## Como alcançar o conhecimento`, `## Responsabilidades`, `## Padrões obrigatórios`, `## O que você NÃO faz`.

**A seção `## Como alcançar o conhecimento` tem de ser byte-idêntica nos seis**, adaptada da versão da quant trocando `quant/00-index/` por `finance/00-index/`. Inclui o parágrafo sobre `Related` mostrar o que foi linkado e o índice o que existe.

Responsabilidades por agente:

- **`equity-research-analyst`** — iniciação de cobertura, valuation por DCF e múltiplos, updates de resultado, recomendação Buy/Hold/Sell com margem de segurança explícita. NÃO roda backtest (é `quant-researcher`), NÃO decide alocação de cliente (é `private-banker`).
- **`private-banker`** — atendimento HNW/UHNW, IPS, alocação patrimonial, planejamento sucessório. Consulta equity e crédito antes de incluir ativo no IPS. NÃO faz research próprio, NÃO define limite de risco (é `risk-quant`).
- **`credit-research-analyst`** — crédito corporativo, debêntures, CRA/CRI, análise de covenants, rating interno. NÃO precifica equity.
- **`macro-strategist`** — cenário macro, asset allocation tática, calls de juros e câmbio. Alinha com `equity-research-analyst` antes de recomendação setorial grande.
- **`pe-analyst`** — due diligence, modelagem de LBO, screening de teses. NÃO opera mercado líquido.
- **`compliance-officer`** — suitability (CVM 30), KYC/AML, conflito de interesse. **Pode vetar entrega.** NÃO faz análise nem calcula risco de mercado (é `risk-quant`).

- [ ] **Step 2: Remover os antigos e verificar**

```bash
git rm -r --quiet finance/agents
for f in .claude/agents/finance/*.md; do
  awk '/^## Como alcançar o conhecimento/{flag=1;next}/^## /{flag=0}flag' "$f" | md5sum | cut -c1-12
done | sort -u | wc -l
```
Esperado `1` — os seis blocos idênticos.

```bash
python -B scripts/check_links.py . --baseline scripts/baseline.txt > /dev/null; echo "exit: $?"
```
Exit `0`.

- [ ] **Step 3: Commit**

```bash
git add -A
git commit -m "checkpoint(e2): seis agentes da casa finance religados ao indice"
```

---

### Task C2: Skills `equity-initiation` e `dcf-valuation`

**Files:**
- Create: `.claude/skills/equity-initiation/SKILL.md`
- Create: `.claude/skills/dcf-valuation/SKILL.md`

Leia antes `.claude/skills/backtest-protocol/SKILL.md` — é a skill rígida de referência.

- [ ] **Step 1: `dcf-valuation/SKILL.md`**

Rígida. `description` dizendo quando invocar: ao valuar empresa por fluxo de caixa descontado.

**Condição de parada no topo:** se a empresa for financeira (banco, seguradora), PARE — DCF não se aplica, a estrutura de capital é o negócio.

Passos: ler `[[dcf-valuation]]` e `[[wacc]]`; coletar 5 anos de demonstrativos registrando fonte e data; projetar FCF explícito 5–10 anos justificando cada premissa por escrito; casar FCF com taxa (FCFF→WACC, FCFE→custo de equity); calcular WACC com beta, prêmio-país e custo de dívida pós-imposto; valor terminal com `g ≤` crescimento nominal do PIB de longo prazo, sem exceção; **matriz de sensibilidade WACC × g obrigatória**; cenário bear com perda máxima estimada.

Seção `## Nunca`: apresentar DCF com número único; usar `g` acima do PIB nominal de longo prazo; descontar FCFE à WACC; omitir a sensibilidade.

Critérios de saída como checklist. Entregável no repo privado: `reports/equity/<ticker>-<YYYY-MM-DD>.md`.

- [ ] **Step 2: `equity-initiation/SKILL.md`**

Rígida. Produz o report de iniciação de cobertura — o primeiro entregável ponta a ponta da casa.

Passos: tese em uma frase falseável; negócio e como ganha dinheiro; setor e posição competitiva com teste de moat (`[[moats]]`); qualidade dos números (`[[roe-roic]]`, red flags contábeis); valuation por DCF (invocar a skill `dcf-valuation`) **e** por múltiplos, com a divergência entre os dois explicada; cenário bear com perda máxima; riscos nomeados, não genéricos; recomendação com preço-alvo, horizonte e margem de segurança explícita; disclosures de conflito de interesse e premissas-chave.

Seção `## Nunca`: recomendação sem valuation explícita; risco genérico ("risco de mercado"); omitir cenário bear; preço-alvo sem horizonte.

**Se a tese depender de um padrão quantitativo** ("empresas com X superam o índice"), abra um Cross-Desk Request para `quant-researcher` em vez de afirmar — a casa finance não produz evidência estatística.

- [ ] **Step 3: Verificar e commitar**

```bash
find .claude/skills -name SKILL.md | wc -l
python -B scripts/check_links.py . --baseline scripts/baseline.txt > /dev/null; echo "exit: $?"
git add .claude/skills/equity-initiation .claude/skills/dcf-valuation
git commit -m "checkpoint(e2): skills equity-initiation e dcf-valuation"
```

Esperado: `4` skills, exit `0`.

---

### Task C3: Teste de ponta a ponta com agente real

**Este é o critério de aceite que nenhuma verificação estática substitui.** Em E1 foi ele — e só ele — que revelou que o `_house.md` não permitia resolver wikilink em caminho: os links resolviam, não havia órfãs, a contagem não mudava, e o mecanismo estava quebrado.

**Files:** nenhum. Só verificação.

- [ ] **Step 1: Invocar o `equity-research-analyst` com uma pergunta real**

Peça uma iniciação de cobertura resumida de uma empresa brasileira, e **exija ao final um `## Rastro de navegação`**: em ordem, cada arquivo aberto e por quê, incluindo tentativas falhas, e se em algum momento usou Glob, Grep, `ls` ou `find` em vez dos índices — e o que levou a isso.

Diga explicitamente que um rastro honesto revelando um contorno vale mais que um rastro limpo.

- [ ] **Step 2: Avaliar o rastro contra três critérios**

| Critério | Falha se |
|---|---|
| **Resolveu caminho** | houve leitura falha ou o agente adivinhou pasta |
| **Não varreu** | usou Glob, Grep, `ls -R` ou `find` para localizar nota |
| **Filtrou** | leu 100% do corpus do domínio — com 78 notas, ao contrário de E1, o filtro agora é testável |

O terceiro critério é o que E1 **não conseguiu testar**: com 7 notas o agente leu todas, e o valor demonstrado do índice foi resolver caminho, não economizar contexto. Com 78 notas, se o agente ainda abre tudo, o mecanismo não está entregando o que justifica existir.

- [ ] **Step 3: Corrigir o que o rastro revelar, e repetir**

Toda correção estrutural que sair daqui vai também para o spec, porque E3 e E4 herdam o formato.

- [ ] **Step 4: Verificação final da E2**

```bash
python -B -m unittest discover -s scripts/tests 2>&1 | tail -3
python -B scripts/check_links.py . --baseline scripts/baseline.txt > /dev/null; echo "gate: $?"
python -B scripts/check_links.py . | tail -1
ls .claude/agents/finance/ | wc -l
find .claude/skills -name SKILL.md | wc -l
grep -rl "🗺️" finance/ --include="*.md" | wc -l
```

Esperado: testes OK, gate `0`, `54 distintos / 74 ocorrencias`, `6` agentes, `4` skills, `0` arquivos com emoji.

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "checkpoint(e2): verificacao final da casa finance"
```

---

## Estado ao fim deste plano

| Item | Antes | Depois |
|---|---|---|
| Casas estruturadas | 1 (quant) | 2 (quant, finance) |
| Agentes | 4 quant | 4 quant + 6 finance |
| Skills | 2 | 4 |
| Alvos quebrados | 63 | **54** |
| Ocorrências | 101 | **74** |
| Arquivos com emoji | 6 | 0 |
| Agentes citando nota por nome no prompt | 2 (23 arquivos) | 0 |

**Nenhum commit em `main`.** Checkpoints na branch, para squash ao fim de E6 conforme §11.0 do spec.

## Próximo plano

`2026-XX-XX-e3-casa-tech.md`. Herdará duas coisas que E2 produz: um formato de índice testado contra um corpus de 78 notas (não 7), e o `migrate_house.py` com plan/apply já exercitado num caso real. A E3 tem os mesmos 9 agentes genéricos a religar e o `adr-template.md` de 11 KB a renomear para `adr-guide.md`, mais o `skill-template.md` de tecnologia para `technology-note.md`.
