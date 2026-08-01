#!/usr/bin/env python3
"""Verifica a integridade dos wikilinks do vault."""

import os
import re
from collections import Counter

WIKILINK = re.compile(r"\[\[([^\[\]\n]+?)\]\]")
FENCE = re.compile(r"^\s*(`{3,}|~{3,})")
INDEXED_EXT = (".md", ".canvas")
SKIP_DIRS = (".git", ".obsidian", "__pycache__")
SKIP_PATHS = (".claude/worktrees",)
ALLOWLIST_PATHS = ("docs/superpowers",)
PLACEHOLDER = ("{{", "}}", "<%", "%>")


def _walk(root):
    for dirpath, dirnames, filenames in os.walk(root):
        rel = os.path.relpath(dirpath, root).replace(os.sep, "/")
        prefix = "" if rel == "." else rel + "/"
        dirnames[:] = [
            d for d in dirnames
            if d not in SKIP_DIRS and (prefix + d) not in SKIP_PATHS
        ]
        for name in filenames:
            yield dirpath, name


def index_targets(root):
    """Basenames alcancaveis por wikilink, com e sem extensao.

    O Obsidian resolve por basename, nao por caminho: mover um arquivo de
    pasta nao quebra o link; renomear quebra. A resolucao tambem ignora
    caixa, entao os alvos sao guardados em minusculas.
    """
    targets = set()
    for _, name in _walk(root):
        if name.endswith(INDEXED_EXT):
            targets.add(name.lower())
            targets.add(os.path.splitext(name)[0].lower())
    return targets


def ambiguous_targets(root):
    """Basenames alcancaveis por mais de um arquivo.

    Obsidian resolve wikilink por basename. Com uma casa por pasta,
    _house e _topics existem em varias — logo [[_house]] e ambiguo, e
    reportar 'resolvido' esconde isso.
    """
    seen = {}
    for dirpath, name in _walk(root):
        if not name.endswith(INDEXED_EXT):
            continue
        rel = os.path.relpath(os.path.join(dirpath, name), root).replace(os.sep, "/")
        seen.setdefault(os.path.splitext(name)[0].lower(), []).append(rel)
    return {k: sorted(v) for k, v in seen.items() if len(v) > 1}


def bare_links(root):
    """Alvos linkados SEM qualificador de caminho, e onde.

    [[pasta/nota]] escolhe o arquivo explicitamente; [[nota]] depende da
    resolucao por basename. Só o segundo sofre com ambiguidade, entao só
    ele deve entrar no relatorio.
    """
    bare = {}
    for dirpath, name in _walk(root):
        if not name.endswith(".md"):
            continue
        if is_allowlisted(root, dirpath):
            continue
        path = os.path.join(dirpath, name)
        with open(path, encoding="utf-8", errors="replace") as fh:
            text = fh.read()
        for raw in WIKILINK.findall(strip_fenced(text)):
            target = raw.split("|")[0].split("#")[0].strip().rstrip("\\").strip()
            if not target or "/" in target:
                continue
            rel = os.path.relpath(path, root).replace(os.sep, "/")
            bare.setdefault(_normalize(target).lower(), set()).add(rel)
    return bare


def ambiguous_bare_links(root):
    """Basename ambiguo linkado sem caminho, e sem candidato na propria pasta.

    Link nu para um irmao da mesma pasta resolve sem ambiguidade — o
    Obsidian prefere o diretorio do proprio arquivo. O caso perigoso e o
    link que cruza pastas: ali nao existe desempate e a escolha entre os
    candidatos e arbitraria.

    Um basename duplicado que ninguem linka de forma nua e inofensivo —
    reportar tudo viraria ruido e o relatorio seria ignorado.
    """
    ambiguous = ambiguous_targets(root)
    bare = bare_links(root)
    out = {}
    for target, files in ambiguous.items():
        if target not in bare:
            continue
        candidate_dirs = {os.path.dirname(f) for f in files}
        sources = sorted(
            s for s in bare[target] if os.path.dirname(s) not in candidate_dirs
        )
        if sources:
            out[target] = {"targets": files, "sources": sources}
    return out


def strip_fenced(text):
    """Remove blocos de codigo cercados.

    Sem isso, `[[ -d "$dir" ]]` do bash e lido como wikilink.

    Casa o marcador de abertura por caractere e comprimento: um bloco
    aberto com ~~~ nao fecha num ```, e um bloco de 4 crases contem
    blocos de 3 sem inverter.
    """
    out = []
    opener = None
    for line in text.splitlines():
        match = FENCE.match(line)
        if match:
            marker = match.group(1)
            if opener is None:
                opener = (marker[0], len(marker))
                continue
            if marker[0] == opener[0] and len(marker) >= opener[1]:
                opener = None
                continue
        if opener is None:
            out.append(line)
    return "\n".join(out)


def has_unclosed_fence(text):
    """True se o ultimo bloco cercado do texto nunca fechou.

    Um fence aberto e nao fechado engole o resto do arquivo em
    strip_fenced; isso e inevitavel sem adivinhar a intencao do autor,
    mas nao pode ser silencioso — quem chama deve avisar o usuario.
    """
    opener = None
    for line in text.splitlines():
        match = FENCE.match(line)
        if match:
            marker = match.group(1)
            if opener is None:
                opener = (marker[0], len(marker))
            elif marker[0] == opener[0] and len(marker) >= opener[1]:
                opener = None
    return opener is not None


def _clean(raw):
    """Reduz [[pasta/nota\\|apelido#secao]] ao basename 'nota'."""
    target = raw.split("|")[0].split("#")[0]
    target = target.strip().rstrip("\\").strip()
    return target.split("/")[-1]


def _is_placeholder(target):
    """Placeholder de template nunca e link real, em qualquer pasta.

    Substitui a antiga allowlist por pasta *templates, que cegava o
    verificador para 58 links reais — e deixou passar um link que a
    propria migracao quebrou dentro do payload de um template.

    Recebe o texto CRU do wikilink, nao o basename limpo: uma expressao
    templater pode conter barra (<% tp.date.now("YYYY/MM/DD") %>) e o
    _clean cortaria justamente o marcador que identifica o placeholder.
    """
    return any(p in target for p in PLACEHOLDER)


def extract_links(text):
    links = []
    for raw in WIKILINK.findall(strip_fenced(text)):
        if _is_placeholder(raw):
            continue
        target = _clean(raw)
        if target:
            links.append(target)
    return links


def _normalize(link):
    """Resolve so extensoes que o vault indexa; [[a.png]] nao vira [[a]]."""
    return os.path.splitext(link)[0] if link.lower().endswith(INDEXED_EXT) else link


def is_allowlisted(root, dirpath):
    """Pastas onde wikilink nao resolvido e esperado: specs e planos citam
    nomes de nota como exemplo, e o exemplo nao precisa existir.

    Puladas como FONTE; continuam indexadas como ALVO.
    """
    rel = os.path.relpath(dirpath, root).replace(os.sep, "/")
    return any(rel == a or rel.startswith(a + "/") for a in ALLOWLIST_PATHS)


def find_unresolved(root):
    """Conta ocorrencias de wikilink que nao resolvem para nenhum arquivo."""
    targets = index_targets(root)
    unresolved = Counter()
    for dirpath, name in _walk(root):
        if not name.endswith(".md"):
            continue
        if is_allowlisted(root, dirpath):
            continue
        with open(os.path.join(dirpath, name), encoding="utf-8", errors="replace") as fh:
            text = fh.read()
        for link in extract_links(text):
            if _normalize(link).lower() not in targets:
                unresolved[link] += 1
    return dict(unresolved)


def unclosed_fence_files(root):
    """Caminhos (relativos a root, varridos como fonte) cujo bloco cercado
    nunca fechou — a cauda do arquivo foi engolida por strip_fenced e
    links quebrados ali dentro nao aparecem em find_unresolved.
    """
    paths = []
    for dirpath, name in _walk(root):
        if not name.endswith(".md"):
            continue
        if is_allowlisted(root, dirpath):
            continue
        path = os.path.join(dirpath, name)
        with open(path, encoding="utf-8", errors="replace") as fh:
            text = fh.read()
        if has_unclosed_fence(text):
            paths.append(path)
    return paths


def _read_baseline(path):
    with open(path, encoding="utf-8") as fh:
        return {line.strip() for line in fh if line.strip()}


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Verifica wikilinks do vault.")
    parser.add_argument("root", nargs="?", default=".")
    parser.add_argument(
        "--baseline",
        metavar="ARQUIVO",
        help="Falha se surgir alvo nao resolvido ausente desta linha de base.",
    )
    parser.add_argument(
        "--write-baseline",
        metavar="ARQUIVO",
        help="Congela os alvos nao resolvidos atuais como nova linha de base.",
    )
    parser.add_argument(
        "--fail-on-ambiguous",
        action="store_true",
        help="Falha se um basename ambiguo for linkado sem caminho. "
             "Desligado por padrao: reporta agora, pode virar gate depois.",
    )
    args = parser.parse_args()

    unresolved = find_unresolved(args.root)
    total = sum(unresolved.values())

    for target, count in sorted(unresolved.items(), key=lambda kv: -kv[1]):
        print(f"{count:4d}  {target}")
    print(f"\nnao resolvidos: {len(unresolved)} distintos / {total} ocorrencias")

    unclosed = unclosed_fence_files(args.root)
    if unclosed:
        print(f"\nAVISO: {len(unclosed)} arquivo(s) com bloco cercado nao fechado"
              " (o resto do arquivo foi ignorado na verificacao):")
        for path in unclosed:
            print(f"  ! {path}")

    ambiguos = ambiguous_bare_links(args.root)
    if ambiguos:
        print(f"\nAMBIGUOS: {len(ambiguos)} basename(s) com mais de um arquivo"
              " e linkado(s) sem caminho — o Obsidian escolhe por conta dele:")
        for target in sorted(ambiguos):
            info = ambiguos[target]
            print(f"  ? {target}  ({len(info['targets'])} arquivos)")
            for t in info["targets"]:
                print(f"      alvo:  {t}")
            for s in info["sources"]:
                print(f"      linka: {s}")

    if args.write_baseline:
        with open(args.write_baseline, "w", encoding="utf-8") as fh:
            fh.write("\n".join(sorted(unresolved)) + "\n")
        print(f"linha de base gravada em {args.write_baseline}: {len(unresolved)} alvos")
        return 0

    if args.baseline:
        base = _read_baseline(args.baseline)
        novos = sorted(set(unresolved) - base)
        resolvidos = sorted(base - set(unresolved))
        if resolvidos:
            print(f"\nresolvidos desde a linha de base: {len(resolvidos)}")
            for t in resolvidos:
                print(f"  + {t}")
        if novos:
            print(f"\nFALHA: {len(novos)} alvo(s) quebrado(s) que nao existiam antes:")
            for t in novos:
                print(f"  - {t}")
            return 1
        print("\nOK: nenhum alvo novo quebrado")

    if ambiguos and args.fail_on_ambiguous:
        print(f"\nFALHA: {len(ambiguos)} basename ambiguo linkado sem caminho.")
        return 1
    if not ambiguos:
        print("OK: nenhum basename ambiguo linkado sem caminho")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
