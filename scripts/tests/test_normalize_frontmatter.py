import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from normalize_frontmatter import derive_domain, normalize_note, parse_frontmatter


class TestDeriveDomain(unittest.TestCase):
    def test_nested_path_becomes_slash_domain(self):
        self.assertEqual(
            derive_domain("finance/02-investments/equities/a.md"), "investments/equities"
        )

    def test_flat_path_drops_numeric_prefix(self):
        self.assertEqual(derive_domain("finance/05-accounting/a.md"), "accounting")

    def test_windows_separator_is_handled(self):
        self.assertEqual(
            derive_domain(os.path.join("finance", "06-markets", "a.md")), "markets"
        )


class TestParse(unittest.TestCase):
    def test_inline_and_block_values_are_grouped_by_key(self):
        blocks, body = parse_frontmatter(
            "---\ntags: [a, b]\naliases:\n  - X\n  - Y\nstatus: active\n---\n\ncorpo\n"
        )
        self.assertEqual([k for k, _ in blocks], ["tags", "aliases", "status"])
        self.assertEqual(dict(blocks)["aliases"], ["aliases:", "  - X", "  - Y"])
        # o corpo comeca logo apos o `---` de fecho: quebra do delimitador
        # mais a linha em branco que separa do texto
        self.assertEqual(body, "\n\ncorpo\n")

    def test_note_without_frontmatter_returns_empty_blocks(self):
        blocks, body = parse_frontmatter("# Titulo\n\ntexto\n")
        self.assertEqual(blocks, [])
        self.assertEqual(body, "# Titulo\n\ntexto\n")


class TestNormalize(unittest.TestCase):
    def test_complexity_becomes_level_and_both_are_removed(self):
        out = normalize_note(
            "---\ntags: [a]\ncomplexity: basic\ncontext: global\n---\n\n# T\n",
            house="finance",
            domain="accounting",
            updated="2026-07-29",
        )
        self.assertIn("level: intro", out)
        self.assertNotIn("complexity:", out)
        self.assertNotIn("context:", out)

    def test_block_style_list_is_preserved_verbatim(self):
        out = normalize_note(
            "---\ntags:\n  - finance\n  - markets\ncomplexity: intermediate\n---\n\ncorpo\n",
            house="finance",
            domain="markets",
            updated="2026-07-29",
        )
        self.assertIn("tags:\n  - finance\n  - markets", out)

    def test_preserves_tags_aliases_created(self):
        out = normalize_note(
            "---\ntags: [a, b]\naliases: [X]\ncreated: 2026-01-01\n---\n\ncorpo\n",
            house="finance",
            domain="markets",
            updated="2026-07-29",
        )
        self.assertIn("tags: [a, b]", out)
        self.assertIn("aliases: [X]", out)
        self.assertIn("created: 2026-01-01", out)

    def test_defaults_when_fields_absent(self):
        out = normalize_note(
            "---\ntags: []\n---\n\ncorpo\n",
            house="finance",
            domain="markets",
            updated="2026-07-29",
        )
        self.assertIn("level: intermediate", out)
        self.assertIn("status: active", out)
        self.assertIn("house: finance", out)
        self.assertIn("domain: markets", out)

    def test_canonical_key_order(self):
        out = normalize_note(
            "---\nstatus: draft\ncomplexity: advanced\ntags: [a]\naliases: [X]\n---\n\ncorpo\n",
            house="finance",
            domain="analysis/fundamental",
            updated="2026-07-29",
        )
        keys = [
            ln.split(":")[0]
            for ln in out.split("---")[1].strip().splitlines()
            if ln and not ln.startswith(" ")
        ]
        self.assertEqual(
            keys, ["tags", "aliases", "house", "domain", "level", "status", "updated"]
        )

    def test_existing_status_is_preserved(self):
        out = normalize_note(
            "---\ntags: []\nstatus: draft\n---\n\ncorpo\n",
            house="finance",
            domain="markets",
            updated="2026-07-29",
        )
        self.assertIn("status: draft", out)

    def test_unknown_keys_are_kept_after_the_canonical_ones(self):
        out = normalize_note(
            "---\ntags: []\ntitle: Meu Titulo\n---\n\ncorpo\n",
            house="finance",
            domain="markets",
            updated="2026-07-29",
        )
        self.assertIn("title: Meu Titulo", out)
        self.assertLess(out.index("updated:"), out.index("title:"))

    def test_body_is_untouched(self):
        body = "\n# Titulo\n\nParagrafo com [[link]] e `codigo`.\n"
        out = normalize_note(
            "---\ntags: []\n---" + body,
            house="finance",
            domain="markets",
            updated="2026-07-29",
        )
        self.assertTrue(out.endswith(body))

    def test_note_without_frontmatter_gains_one(self):
        out = normalize_note(
            "# Sem frontmatter\n",
            house="finance",
            domain="markets",
            updated="2026-07-29",
        )
        self.assertTrue(out.startswith("---\n"))
        self.assertIn("house: finance", out)
        self.assertIn("# Sem frontmatter", out)

    def test_is_idempotent(self):
        once = normalize_note(
            "---\ntags: [a]\ncomplexity: basic\ncontext: global\n---\n\ncorpo\n",
            house="finance",
            domain="markets",
            updated="2026-07-29",
        )
        twice = normalize_note(
            once, house="finance", domain="markets", updated="2026-07-29"
        )
        self.assertEqual(once, twice)


if __name__ == "__main__":
    unittest.main()
