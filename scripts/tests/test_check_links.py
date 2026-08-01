import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from check_links import (
    find_unresolved,
    _read_baseline,
    ambiguous_targets,
    ambiguous_bare_links,
)


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


class TestAllowlist(VaultFixture):
    def test_placeholder_in_template_dir_is_skipped(self):
        root = self.build({
            "shared/templates/note.md": "MOC: [[{{moc-relacionado}}]]",
        })
        self.assertEqual(find_unresolved(root), {})

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

    def test_placeholder_in_every_numbered_template_dir_is_skipped(self):
        """01-templates, 08-templates, 11-templates — o placeholder e que
        isenta, nao o nome da pasta, entao a renomeacao e irrelevante."""
        for path in ("docs/01-templates", "finance-vault/11-templates",
                     "tech-vault/08-templates", "finance/11-templates"):
            root = self.build({f"{path}/t.md": "MOC: [[{{moc-relacionado}}]]"})
            self.assertEqual(find_unresolved(root), {}, path)

    def test_templater_syntax_is_skipped(self):
        root = self.build({
            "tech-vault/08-templates/weekly.md":
                '[[weekly-review-<% tp.date.now("YYYY-MM-DD", -7) %>]]',
        })
        self.assertEqual(find_unresolved(root), {})

    def test_templater_expression_with_slash_is_still_skipped(self):
        """_clean cortaria em '/' e perderia o '<%'; a deteccao roda no cru."""
        root = self.build({
            "tech-vault/08-templates/diario.md":
                '[[diario-<% tp.date.now("YYYY/MM/DD") %>]]',
        })
        self.assertEqual(find_unresolved(root), {})

    def test_no_directory_name_heuristic_remains(self):
        """Nenhum nome de pasta isenta nada: so placeholder e docs/superpowers."""
        root = self.build({
            "tech/template-design-notes/a.md": "veja [[fantasma]]",
        })
        self.assertEqual(find_unresolved(root), {"fantasma": 1})


class TestFencePairing(VaultFixture):
    def test_broken_link_after_mispaired_fence_is_still_reported(self):
        """FN guard: ``` dentro de bloco ~~~ nao pode engolir o resto do arquivo."""
        root = self.build({"a.md": "~~~text\n```\n~~~\n\nveja [[fantasma]]\n"})
        self.assertEqual(find_unresolved(root), {"fantasma": 1})

    def test_four_backtick_block_contains_three_backtick_block(self):
        root = self.build({
            "a.md": "````markdown\n```bash\n[[ -d \"$d\" ]]\n```\n````\n\nveja [[fantasma]]\n",
        })
        self.assertEqual(find_unresolved(root), {"fantasma": 1})


class TestWikilinkSyntax(VaultFixture):
    def test_unclosed_bracket_does_not_swallow_following_links(self):
        """Caso real: docs/03-workflows tem o texto literal 'buscar `[[` sem match'."""
        root = self.build({
            "a.md": "buscar `[[` sem match\n\n- veja [[fantasma]]\n",
            "b.md": "conteudo",
        })
        self.assertEqual(find_unresolved(root), {"fantasma": 1})

    def test_alias_and_heading_are_stripped(self):
        root = self.build({
            "a.md": "[[b#secao|apelido]] [[sub/b#outra]]",
            "sub/b.md": "conteudo",
            "b.md": "conteudo",
        })
        self.assertEqual(find_unresolved(root), {})


class TestCaseInsensitive(VaultFixture):
    def test_link_resolves_ignoring_case(self):
        root = self.build({"a.md": "[[factor-investing]]", "Factor-Investing.md": "x"})
        self.assertEqual(find_unresolved(root), {})


class TestBaselineGate(VaultFixture):
    def test_new_broken_target_is_detected_even_when_total_drops(self):
        """O bug que motivou trocar soma por conjunto."""
        root = self.build({"a.md": "[[capm]]"})
        base = os.path.join(root, "base.txt")
        with open(base, "w", encoding="utf-8") as fh:
            fh.write("falta-1\nfalta-2\n")
        novos = set(find_unresolved(root)) - _read_baseline(base)
        self.assertEqual(novos, {"capm"})


class TestClaudeDirectory(VaultFixture):
    def test_agent_definitions_are_scanned_as_sources(self):
        """Agente que cita nota inexistente tem de ser pego."""
        root = self.build({
            ".claude/agents/quant/researcher.md": "consulte [[nota-que-nao-existe]]",
        })
        self.assertEqual(find_unresolved(root), {"nota-que-nao-existe": 1})

    def test_agent_link_to_real_note_resolves(self):
        root = self.build({
            ".claude/agents/quant/researcher.md": "ver [[sharpe-ratio]]",
            "quant/06-risk-analytics/sharpe-ratio.md": "conteudo",
        })
        self.assertEqual(find_unresolved(root), {})

    def test_worktree_copy_does_not_mask_a_broken_link(self):
        """Regressao C1: a copia do vault sob .claude/worktrees nao pode
        servir de alvo, senao um rename quebrado passa despercebido."""
        root = self.build({
            "index.md": "ver [[momentum-strategies]]",
            ".claude/worktrees/copia/quant/momentum-strategies.md": "copia obsoleta",
        })
        self.assertEqual(find_unresolved(root), {"momentum-strategies": 1})

    def test_worktree_copy_is_not_scanned_as_source(self):
        root = self.build({
            ".claude/worktrees/copia/nota.md": "ver [[fantasma]]",
        })
        self.assertEqual(find_unresolved(root), {})


class TestAmbiguity(VaultFixture):
    def test_same_basename_in_two_houses_is_reported(self):
        root = self.build({
            "finance/00-index/_house.md": "a",
            "quant/00-index/_house.md": "b",
        })
        self.assertEqual(
            ambiguous_targets(root),
            {"_house": ["finance/00-index/_house.md", "quant/00-index/_house.md"]},
        )

    def test_unique_basenames_are_not_reported(self):
        root = self.build({"a.md": "x", "sub/b.md": "y"})
        self.assertEqual(ambiguous_targets(root), {})


class TestPlaceholders(VaultFixture):
    def test_placeholder_link_is_skipped_anywhere(self):
        root = self.build({
            "finance/nota.md": "MOC: [[{{moc-relacionado}}]]",
            "docs/01-templates/t.md": "ADR: [[adr-{{NNNN}}]]",
            "tech/08-templates/w.md": "prox: [[weekly-<% tp.date.now() %>]]",
        })
        self.assertEqual(find_unresolved(root), {})

    def test_real_broken_link_in_template_dir_is_now_reported(self):
        """A regra antiga cegava a pasta inteira; um template que linka
        arquivo renomeado passa a nascer com link quebrado."""
        root = self.build({
            "docs/01-templates/equity.md": "veja [[investments-moc]]",
        })
        self.assertEqual(find_unresolved(root), {"investments-moc": 1})

    def test_superpowers_allowlist_still_applies(self):
        root = self.build({
            "docs/superpowers/specs/design.md": "exemplo: [[nota-que-nao-existe]]",
        })
        self.assertEqual(find_unresolved(root), {})


class TestAmbiguityPrecision(VaultFixture):
    def test_same_folder_bare_link_is_not_flagged(self):
        root = self.build({
            "finance/00-index/_house.md": "a",
            "quant/00-index/_house.md": "b",
            "finance/00-index/accounting.md": "ver [[_house]]",
        })
        self.assertEqual(ambiguous_bare_links(root), {})

    def test_cross_folder_bare_link_is_flagged(self):
        root = self.build({
            "finance/00-index/_house.md": "a",
            "quant/00-index/_house.md": "b",
            "claude/home.md": "ver [[_house]]",
        })
        result = ambiguous_bare_links(root)
        self.assertIn("_house", result)
        self.assertEqual(result["_house"]["sources"], ["claude/home.md"])

    def test_qualified_link_is_never_flagged(self):
        root = self.build({
            "finance/00-index/_house.md": "a",
            "quant/00-index/_house.md": "b",
            "claude/home.md": "ver [[finance/00-index/_house]]",
        })
        self.assertEqual(ambiguous_bare_links(root), {})


if __name__ == "__main__":
    unittest.main()
