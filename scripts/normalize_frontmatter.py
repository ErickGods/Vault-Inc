#!/usr/bin/env python3
"""Normaliza o frontmatter das notas de uma casa para o formato canonico.

Consolida `complexity` e `context` em `level` + `domain`, injeta `house`,
e fixa a ordem das chaves. Preserva o corpo e o estilo YAML original de
cada valor — o vault mistura listas inline (`tags: [a, b]`) com listas em
bloco (`tags:` seguido de `- item`), e reescrever o estilo geraria um diff
enorme sem ganho.
"""

import os
import re

KEY = re.compile(r"^([A-Za-z_][\w-]*):")

CANONICAL = ["tags", "aliases", "house", "domain", "level", "status", "created", "updated"]
DROP = ("complexity", "context")

LEVEL_MAP = {
    "basic": "intro",
    "beginner": "intro",
    "intro": "intro",
    "intermediate": "intermediate",
    "advanced": "advanced",
}
DEFAULT_LEVEL = "intermediate"
DEFAULT_STATUS = "active"


def derive_domain(rel_path):
    """`finance/02-investments/equities/a.md` -> `investments/equities`.

    Descarta o nome da casa, o arquivo, e o prefixo numerico de cada pasta.
    """
    parts = rel_path.replace(os.sep, "/").split("/")[1:-1]
    return "/".join(re.sub(r"^\d+-", "", p) for p in parts)


def parse_frontmatter(text):
    """Separa o frontmatter em blocos `(chave, linhas)` e devolve o corpo.

    Agrupa por chave sem interpretar o valor, entao lista inline e lista em
    bloco atravessam intactas.
    """
    if not text.startswith("---"):
        return [], text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return [], text

    blocks = []
    for line in parts[1].strip("\n").splitlines():
        match = KEY.match(line)
        if match:
            blocks.append((match.group(1), [line]))
        elif blocks:
            blocks[-1][1].append(line)
    return blocks, parts[2]


def _value(block_lines):
    return block_lines[0].split(":", 1)[1].strip()


def normalize_note(text, house, domain, updated):
    """Devolve a nota com frontmatter canonico e corpo intacto."""
    blocks, body = parse_frontmatter(text)
    original = dict(blocks)

    level = DEFAULT_LEVEL
    if "level" in original:
        level = LEVEL_MAP.get(_value(original["level"]).lower(), DEFAULT_LEVEL)
    elif "complexity" in original:
        level = LEVEL_MAP.get(_value(original["complexity"]).lower(), DEFAULT_LEVEL)

    forced = {
        "house": [f"house: {house}"],
        "domain": [f"domain: {domain}"],
        "level": [f"level: {level}"],
        "status": original.get("status", [f"status: {DEFAULT_STATUS}"]),
        "updated": [f"updated: {updated}"],
    }

    out = []
    for key in CANONICAL:
        if key in forced:
            out.extend(forced[key])
        elif key in original:
            out.extend(original[key])

    seen = set(CANONICAL) | set(DROP)
    for key, lines in blocks:
        if key not in seen:
            out.extend(lines)
            seen.add(key)

    if not body.startswith("\n"):
        body = "\n" + body
    return "---\n" + "\n".join(out) + "\n---" + body


def _iter_notes(root, house_dir, skip):
    for dirpath, dirnames, filenames in os.walk(os.path.join(root, house_dir)):
        rel_dir = os.path.relpath(dirpath, root).replace(os.sep, "/")
        if any(rel_dir == s or rel_dir.startswith(s + "/") for s in skip):
            continue
        for name in sorted(filenames):
            if name.endswith(".md") and name != "README.md":
                yield os.path.join(dirpath, name)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Normaliza frontmatter de uma casa.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--house", required=True)
    parser.add_argument("--dir", required=True)
    parser.add_argument(
        "--skip",
        action="append",
        default=[],
        help="caminho relativo a ignorar; repetivel",
    )
    parser.add_argument("--updated", required=True)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    changed = 0
    total = 0
    for path in _iter_notes(args.root, args.dir, args.skip):
        total += 1
        rel = os.path.relpath(path, args.root).replace(os.sep, "/")
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
        new = normalize_note(text, args.house, derive_domain(rel), args.updated)
        if new == text:
            continue
        changed += 1
        if args.apply:
            with open(path, "w", encoding="utf-8", newline="") as fh:
                fh.write(new)
        else:
            print(f"  {rel}  -> domain: {derive_domain(rel)}")

    verbo = "normalizadas" if args.apply else "a normalizar"
    print(f"{changed} de {total} notas {verbo}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
