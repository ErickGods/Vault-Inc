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


class TestNoRewrite(MigrationFixture):
    def test_superpowers_docs_are_not_rewritten(self):
        """O spec cita nomes antigos como exemplo; reescrever apaga o registro."""
        root = self.build({
            "old/home.md": "raiz",
            "docs/superpowers/specs/design.md": "exemplo ruim: [[home]]",
            "nota.md": "veja [[home]]",
        })
        mapping = read_map(self.write_map(root, [("old/home.md", "new/_house.md")]))
        plan = build_plan(root, mapping)
        self.assertEqual([r["file"] for r in plan["rewrites"]], ["nota.md"])
        apply_plan(root, plan, plan_hash(plan), mapping)
        with open(os.path.join(root, "docs/superpowers/specs/design.md"), encoding="utf-8") as fh:
            self.assertIn("[[home]]", fh.read())

    def test_template_dirs_are_still_rewritten(self):
        """Template que linka arquivo renomeado passaria a gerar link quebrado."""
        root = self.build({
            "old/home.md": "raiz",
            "docs/01-templates/nota.md": "MOC: [[home]]",
        })
        mapping = read_map(self.write_map(root, [("old/home.md", "new/_house.md")]))
        plan = build_plan(root, mapping)
        self.assertEqual([r["file"] for r in plan["rewrites"]], ["docs/01-templates/nota.md"])


class TestMovedAndRewritten(MigrationFixture):
    def test_file_that_is_both_moved_and_rewritten(self):
        """Caso real da E2: os 6 MOCs linkam uns aos outros e todos sao movidos."""
        root = self.build({
            "old/home.md": "veja [[analysis]]",
            "old/analysis.md": "volte a [[home]]",
        })
        mapping = read_map(self.write_map(root, [
            ("old/home.md", "new/_house.md"),
            ("old/analysis.md", "new/analysis.md"),
        ]))
        plan = build_plan(root, mapping)
        apply_plan(root, plan, plan_hash(plan), mapping)
        with open(os.path.join(root, "new/analysis.md"), encoding="utf-8") as fh:
            self.assertEqual(fh.read(), "volte a [[_house]]")
        with open(os.path.join(root, "new/_house.md"), encoding="utf-8") as fh:
            self.assertEqual(fh.read(), "veja [[analysis]]")

    def test_mutual_links_among_three_moved_files(self):
        root = self.build({
            "m/a.md": "[[b]] e [[c]]",
            "m/b.md": "[[a]] e [[c]]",
            "m/c.md": "[[a]] e [[b]]",
        })
        mapping = read_map(self.write_map(root, [
            ("m/a.md", "i/_house.md"),
            ("m/b.md", "i/beta.md"),
            ("m/c.md", "i/gama.md"),
        ]))
        plan = build_plan(root, mapping)
        apply_plan(root, plan, plan_hash(plan), mapping)
        with open(os.path.join(root, "i/_house.md"), encoding="utf-8") as fh:
            self.assertEqual(fh.read(), "[[beta]] e [[gama]]")
        with open(os.path.join(root, "i/beta.md"), encoding="utf-8") as fh:
            self.assertEqual(fh.read(), "[[_house]] e [[gama]]")
        with open(os.path.join(root, "i/gama.md"), encoding="utf-8") as fh:
            self.assertEqual(fh.read(), "[[_house]] e [[beta]]")


class TestPruneEmptySource(MigrationFixture):
    def test_emptied_source_dir_is_removed(self):
        """os.replace move o arquivo e nao poda a pasta; git nao versiona
        diretorio vazio, entao o repo parece limpo e o Obsidian mostra
        uma pasta orfa."""
        root = self.build({"old/a.md": "x"})
        mapping = read_map(self.write_map(root, [("old/a.md", "new/a2.md")]))
        plan = build_plan(root, mapping)
        apply_plan(root, plan, plan_hash(plan), mapping)
        self.assertFalse(os.path.isdir(os.path.join(root, "old")))

    def test_source_dir_with_survivors_is_kept(self):
        root = self.build({"old/a.md": "x", "old/b.md": "y"})
        mapping = read_map(self.write_map(root, [("old/a.md", "new/a2.md")]))
        plan = build_plan(root, mapping)
        apply_plan(root, plan, plan_hash(plan), mapping)
        self.assertTrue(os.path.isfile(os.path.join(root, "old/b.md")))
        self.assertTrue(os.path.isdir(os.path.join(root, "old")))


if __name__ == "__main__":
    unittest.main()
