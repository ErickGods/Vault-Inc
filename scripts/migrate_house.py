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

NO_REWRITE_PATHS = ("docs/superpowers",)


def _is_no_rewrite(root, dirpath):
    """Pastas que registram historico e nao devem ser reescritas.

    O spec cita nomes de arquivo antigos como exemplo do problema que a
    migracao corrige; reescreve-los apagaria o proprio registro.

    Deliberadamente mais estreito que check_links.is_allowlisted: pastas
    *templates continuam sendo reescritas, senao um template passaria a
    emitir link quebrado para o arquivo renomeado.
    """
    rel = os.path.relpath(dirpath, root).replace(os.sep, "/")
    return any(rel == p or rel.startswith(p + "/") for p in NO_REWRITE_PATHS)


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


def _rename_map(moves):
    """basename antigo -> basename novo, so para os que de fato mudam de nome."""
    rename = {}
    for move in moves:
        old_base = os.path.splitext(os.path.basename(move["from"]))[0]
        new_base = os.path.splitext(os.path.basename(move["to"]))[0]
        if old_base != new_base:
            rename[old_base] = new_base
    return rename


def _prune_empty_sources(root, moves):
    """Remove diretorios de origem que ficaram vazios apos os moves.

    os.replace move arquivos e nao poda a pasta. Git nao versiona
    diretorio vazio, entao o repo parece limpo enquanto o Obsidian
    mostra uma pasta orfa.

    Poda apenas o diretorio imediato de cada origem, e apenas se estiver
    completamente vazio — os.listdir enxerga tambem entradas ocultas.
    Nunca sobe para o pai e nunca toca a raiz: uma poda recursiva poderia
    apagar arvore que a migracao nem visitou.
    """
    pruned = []
    for rel in sorted({os.path.dirname(m["from"]) for m in moves}):
        if not rel:
            continue  # origem na raiz do vault: nao existe pasta a podar
        path = os.path.join(root, rel)
        if not os.path.isdir(path) or os.listdir(path):
            continue
        os.rmdir(path)
        pruned.append(rel)
    return pruned


def build_plan(root, mapping):
    """Monta o plano: moves, reescritas de link e erros detectados."""
    moves, errors = [], []
    for old, new in mapping:
        if not os.path.isfile(os.path.join(root, old)):
            errors.append(f"origem inexistente: {old}")
            continue
        if os.path.exists(os.path.join(root, new)):
            errors.append(f"destino ja existe: {new}")
            continue
        moves.append({"from": old, "to": new})

    rename = _rename_map(moves)
    rewrites = []
    for dirpath, name in _walk(root):
        if not name.endswith(".md"):
            continue
        if _is_no_rewrite(root, dirpath):
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

    rewrites.sort(key=lambda r: (r["file"], r["old"]))
    return {"moves": moves, "rewrites": rewrites, "errors": errors}


def plan_hash(plan):
    canonical = json.dumps(plan, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


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

    # Daqui pra baixo usa-se `fresh`, nunca o plano recebido: os dois tem o
    # mesmo hash, logo sao identicos — mas ler do plano recem-verificado
    # deixa isso obvio. Se alguem um dia estreitar a checagem de deriva,
    # o codigo continua operando sobre o estado que acabou de medir.
    rename = _rename_map(fresh["moves"])
    touched = sorted({r["file"] for r in fresh["rewrites"]})

    # Pre-voo: confere que tudo que sera lido ou movido existe, ANTES de
    # escrever qualquer coisa. Transforma um crash no meio da aplicacao —
    # que deixaria o vault meio migrado — numa recusa limpa que nao muda nada.
    for rel in touched:
        if not os.path.isfile(os.path.join(root, rel)):
            print(f"ERRO: alvo de reescrita ausente: {rel}", file=sys.stderr)
            raise SystemExit(1)
    for move in fresh["moves"]:
        if not os.path.isfile(os.path.join(root, move["from"])):
            print(f"ERRO: origem do move ausente: {move['from']}", file=sys.stderr)
            raise SystemExit(1)

    # Reescreve ANTES de mover. Um arquivo pode ser movido e reescrito ao
    # mesmo tempo — os 6 MOCs da casa finance linkam uns aos outros — e
    # reescrever depois de mover abriria o caminho antigo, que ja nao existe.
    # Nesta ordem nenhuma traducao de caminho e necessaria.
    #
    # A ordem tambem e melhor em falha parcial: se uma reescrita levantar no
    # meio, nenhum arquivo saiu do lugar e `git checkout .` restaura tudo.
    for rel in touched:
        path = os.path.join(root, rel)
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
        with open(path, "w", encoding="utf-8", newline="") as fh:
            fh.write(_rewrite_text(text, rename))

    for move in fresh["moves"]:
        dst = os.path.join(root, move["to"])
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        os.replace(os.path.join(root, move["from"]), dst)

    pruned = _prune_empty_sources(root, fresh["moves"])

    print(f"aplicado: {len(fresh['moves'])} moves, {len(touched)} arquivos reescritos")
    for rel in pruned:
        print(f"  pasta de origem vazia removida: {rel}")
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
