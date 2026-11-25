#!/usr/bin/env python3
"""Tests for po.py: the export parses back to the same text, also after Poedit rewraps it."""
import re
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import po  # noqa: E402


def poedit_style(text, width=79):
    """Rewrap quoted strings at `width` columns on spaces, the way Poedit saves a file."""
    out = []
    for line in text.split("\n"):
        m = re.match(r'^((?:msgid|msgstr|msgctxt) )?(".*")$', line)
        if not m or len(line) <= width:
            out.append(line)
            continue
        body = m.group(2)[1:-1]
        if m.group(1):
            out.append(f'{m.group(1)}""')
        while len(body) + 2 > width:
            cut = body.rfind(" ", 0, width - 2)
            cut = width - 2 if cut <= 0 else cut + 1
            out.append(f'"{body[:cut]}"')
            body = body[cut:]
        out.append(f'"{body}"')
    return "\n".join(out)


class RoundTrip(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "ca.po"
            po.export(out)
            cls.text = out.read_text(encoding="utf-8")
        cls.entries = {idx: (en, ca) for _, idx, en, _, ca, _ in po.entries()}

    def check(self, parsed):
        got = {e["ctxt"]: e for e in parsed if e.get("ctxt")}
        self.assertEqual(set(got), set(self.entries))
        for idx, (en, ca) in self.entries.items():
            self.assertEqual(po.from_display(got[idx]["id"], idx), en, idx)
            self.assertEqual(po.from_display(got[idx]["str"], idx) if got[idx]["str"] else None, ca, idx)

    def test_export_parses_back(self):
        self.check(po.parse(self.text))

    def test_poedit_rewrapped(self):
        wrapped = poedit_style(self.text.replace('"X-Source-Language: en\\n"',
                                                 '"X-Source-Language: en\\n"\n"X-Generator: Poedit 3.4\\n"'))
        self.assertNotEqual(wrapped, self.text)
        self.check(po.parse(wrapped))

    def test_comment_and_fuzzy(self):
        text = self.text.replace('msgctxt "MESSAGE_LONG_BEAM"',
                                 '# check in game\n#, fuzzy\nmsgctxt "MESSAGE_LONG_BEAM"')
        e = next(e for e in po.parse(text) if e.get("ctxt") == "MESSAGE_LONG_BEAM")
        self.assertEqual(e["comments"], ["check in game"])
        self.assertTrue(e["fuzzy"])

    def test_rejects_straight_quote_and_backslash(self):
        with self.assertRaises(ValueError):
            po.from_display('Diu "hola"', "X")
        with self.assertRaises(ValueError):
            po.from_display("a\\nb", "X")
        self.assertEqual(po.from_display("a\nb", "X"), "a\\nb")


if __name__ == "__main__":
    unittest.main()
