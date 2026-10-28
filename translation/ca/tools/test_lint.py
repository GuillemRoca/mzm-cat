"""Tests for lint.py and gap.py. Run: python3 -m unittest translation/ca/tools/test_lint.py
Reads the vanilla text from src/data/text_data.c (no ROM needed)."""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import catext  # noqa: E402
import gap  # noqa: E402
import gencredits  # noqa: E402
import lint  # noqa: E402

GOOD_LONG_BEAM = 'MESSAGE_LONG_BEAM = "{GAP(88)}{COLOR(5)}Raig llarg\\n{GAP(110)}"'


class LintTest(unittest.TestCase):
    def run_lint(self, files, middot_glyph=True):
        with tempfile.TemporaryDirectory() as tmp:
            for category, (_, name) in catext.CATEGORIES.items():
                (Path(tmp) / name).write_text("\n".join(files.get(category, [])) + "\n", encoding="utf-8")
            glyph = catext.CA / "font" / "glyphs" / "0357.png" if middot_glyph else Path(tmp) / "none.png"
            identical = Path(tmp) / "identical.txt"
            identical.write_text("\n".join(files.get("identical", [])) + "\n")
            rep, progress = lint.lint(Path(tmp), glyph, identical)
        return [(i["level"], i["id"], i["message"]) for i in rep.items], progress

    def assertOnly(self, items, level, fragment):
        self.assertEqual(len(items), 1, items)
        self.assertEqual(items[0][0], level, items)
        self.assertIn(fragment, items[0][2])

    def test_empty_translation_is_clean(self):
        items, progress = self.run_lint({})
        self.assertEqual(items, [])
        self.assertEqual(progress["message"], (0, 39))
        self.assertEqual(sum(n for _, n in progress.values()), 127)

    def test_good_entry(self):
        items, progress = self.run_lint({"message": [GOOD_LONG_BEAM]})
        self.assertEqual(items, [])
        self.assertEqual(progress["message"], (1, 39))

    def test_character_not_in_charmap(self):
        items, _ = self.run_lint({"message": ['MESSAGE_LONG_BEAM = "{GAP(88)}{COLOR(5)}Raig €\\n{GAP(110)}"']})
        self.assertEqual(items[0][0], "error")
        self.assertIn("not in charmap", items[0][2])

    def test_control_code_mismatch(self):
        items, _ = self.run_lint({"message": ['MESSAGE_LONG_BEAM = "{GAP(88)}Raig llarg\\n{GAP(110)}"']})
        self.assertOnly(items, "error", "control codes")

    def test_button_glyph_counts_as_control_code(self):
        es = 'DESCRIPTION_TEXT_BOMBS = "Col·loca-les amb {A_button} en morfosfera."'
        items, _ = self.run_lint({"description": [es]})
        self.assertOnly(items, "error", "control codes")

    def test_line_count_mismatch(self):
        items, _ = self.run_lint({"message": ['MESSAGE_LONG_BEAM = "{GAP(88)}{COLOR(5)}Raig llarg"']})
        self.assertOnly(items, "error", "lines")

    def test_overflow(self):
        long = "{GAP(0)}{COLOR(5)}" + "Molt llarg " * 30
        items, _ = self.run_lint({"message": [f'MESSAGE_LONG_BEAM = "{long}\\n{{GAP(110)}}"']})
        self.assertTrue(any(l == "error" and "over the 224 px" in m for l, _, m in items), items)

    def test_stale_gap(self):
        items, _ = self.run_lint({"message": ['MESSAGE_LONG_BEAM = "{GAP(86)}{COLOR(5)}Raig llarg\\n{GAP(110)}"']})
        self.assertOnly(items, "warning", "stale GAP(86), should be GAP(88)")

    def test_unknown_id(self):
        items, _ = self.run_lint({"message": ['MESSAGE_LASER_BEAM = "{GAP(88)}Làser\\n{GAP(110)}"']})
        self.assertOnly(items, "error", "extra string")

    def test_duplicate_id(self):
        items, _ = self.run_lint({"message": [GOOD_LONG_BEAM, GOOD_LONG_BEAM]})
        self.assertOnly(items, "error", "defined twice")

    def test_ascii_quote_rejected(self):
        items, _ = self.run_lint({"message": ['MESSAGE_LONG_BEAM = "{GAP(88)}{COLOR(5)}"Raig"\\n{GAP(110)}"']})
        self.assertOnly(items, "error", "quotes")

    def test_identical_to_spanish(self):
        es = 'LT_BRINSTAR = "{GAP(86)}BRINSTAR"'
        items, progress = self.run_lint({"location": [es]})
        self.assertOnly(items, "warning", "identical to the Spanish")

    def test_identical_list_silences_spanish_match(self):
        items, progress = self.run_lint({"location": ['LT_BRINSTAR = "{GAP(86)}BRINSTAR"'],
                                         "identical": ["LT_BRINSTAR  # area name"]})
        self.assertEqual(items, [])
        self.assertEqual(progress["location"], (1, 26))

    def test_middot_todo_only_without_glyph(self):
        line = 'MESSAGE_LONG_BEAM = "{GAP(90)}{COLOR(5)}Col·lecció\\n{GAP(110)}"'
        items, _ = self.run_lint({"message": [line]})
        self.assertEqual(items, [])
        items, _ = self.run_lint({"message": [line]}, middot_glyph=False)
        self.assertEqual([l for l, _, _ in items], ["todo"])

    def test_lookalike_hint(self):
        items, _ = self.run_lint({"message": ['MESSAGE_WAVE_BEAM = "{GAP(80)}{COLOR(5)}Raig d’ones\\n{GAP(110)}"']})
        self.assertOnly(items, "error", "use ' instead of ’")

    def test_overflow_does_not_suggest_negative_gap(self):
        long = "{GAP(0)}" + "Evacueu immediatament la zona! " * 3
        items, _ = self.run_lint({"message": [f'MESSAGE_ZEBES_ESCAPE = "{long}\\n{{GAP(56)}}Evacueu immediatament!"']})
        self.assertFalse(any("GAP(-" in m for _, _, m in items), items)

    def test_gap_layout_of_english_or_spanish(self):
        centred = 'MESSAGE_SAVE_PROMPT = "{GAP(88)}Guardar？\\n{GAP(99)}{INDENT(64)}Sí{INDENT(160)}No"'
        items, _ = self.run_lint({"message": [centred]})
        self.assertEqual(items, [])
        extra = 'MESSAGE_LONG_BEAM = "{GAP(88)}{GAP(8)}{COLOR(5)}Raig llarg\\n{GAP(110)}"'
        items, _ = self.run_lint({"message": [extra]})
        self.assertTrue(any("2 GAPs" in m for _, _, m in items), items)

    def test_file_screen_gap_positions(self):
        line = 'FILE_SCREEN_TEXT_COPY_CONFIRM = "Vols sobreescriure\\naquest fitxer？\\n{GAP(30)}Sí{GAP(34)}No"'
        items, _ = self.run_lint({"file_screen": [line]})
        self.assertOnly(items, "warning", "Yes/No positions")


class GapTest(unittest.TestCase):
    def test_vanilla_reproduced(self):
        self.assertEqual(gap.cmd_vanilla(), 0)

    def test_half_even(self):
        w = catext.widths(catalan=False)
        # "Missile Tank acquired." is 99 px: (220 - 99) / 2 = 60.5 -> 60
        _, changes = gap.recompute("message", "MESSAGE_MISSILE_TANK_ACQUIRED",
                                   "{GAP(1)}{COLOR(5)}Missile Tank acquired.", w)
        self.assertEqual(changes, [(1, 1, 60)])

    def test_planet_zebes_is_fixed(self):
        w = catext.widths(catalan=False)
        text = "{GAP(8)}Línia\\n{GAP(138)}-Samus Aran-"
        self.assertEqual(gap.recompute("story", "STORY_TEXT_PLANET_ZEBES", text, w), (text, []))


class CreditsTest(unittest.TestCase):
    def test_same_length_after_italian(self):
        _, vanilla = gencredits.vanilla()
        for names in (["Guillem Roca"], ["Guillem Roca", "Second Person"]):
            out, _ = gencredits.catalan(vanilla, "CATALAN", names)
            self.assertEqual((len(out), gencredits.rows(out)), (len(vanilla), gencredits.rows(vanilla)))
            at = out.index(("BLUE", "CATALAN"))
            self.assertEqual(out[at - 4], ("WHITE_BIG", "Massimo Maietti"))
            self.assertEqual(out[at + 3], ("WHITE_BIG", names[0]))
            # the copyright still has the same blank rows below it before END
            tail = out[out.index(("RESERVED", "")) + 1:]
            self.assertEqual(gencredits.rows(tail), gencredits.rows(vanilla[vanilla.index(("RESERVED", "")) + 1:]))


if __name__ == "__main__":
    unittest.main()
