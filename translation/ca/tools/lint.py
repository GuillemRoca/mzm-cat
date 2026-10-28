#!/usr/bin/env python3
"""Lints translation/ca/text/*.txt against the vanilla EU text in src/data/text_data.c.

  lint.py [--release] [--json OUT] [--text-dir DIR]

Errors (exit 1):
  - malformed lines, duplicate IDs, IDs that aren't in the Spanish pointer table
  - characters missing from charmap.txt, unknown {CODES}
  - control codes (COLOR, INDENT, DELAY, buttons and other named codes) that differ from the
    Spanish original, in order; or a different number of lines (\\n) where the box is fixed
  - a line that crosses 224 px (the game would wrap it and, in banners, lose the rest)
Warnings (exit 1 with --release):
  - stale centring GAPs (fix with gap.py fix), a different number of GAPs on a line, or a
    different FileScreen GAP value (those are Yes/No positions)
  - a FileScreen line wider than any shipped language's (the pop-up may be narrower)
  - text identical to the Spanish original (copied by mistake?)
TODO (never fail): · used while font/glyphs/0357.png doesn't exist yet.
Untranslated IDs show in English; --release fails if any remain.
"""
import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import catext  # noqa: E402
import gap  # noqa: E402

FIXED_LINES = {"message", "location", "story", "file_screen"}
LOOKALIKES = {"’": "'", "‘": "'", "“": "”", "–": "-", "—": "-", "€": "(not in the font)"}


def control_codes(text):
    return [m.group(0) for m in catext.CODE_RE.finditer(text) if m.group(1) != "GAP"]


def gaps_per_line(text):
    return [re.findall(r"\{GAP\((\d+)\)\}", l) for l in text.split("\\n")]


class Report:
    def __init__(self):
        self.items = []

    def add(self, level, path, line, idx, msg):
        self.items.append({"level": level, "file": str(path), "line": line, "id": idx, "message": msg})

    def count(self, level):
        return sum(1 for i in self.items if i["level"] == level)


def lint(text_dir=catext.CA / "text", middot_glyph=catext.CA / "font" / "glyphs" / "0357.png"):
    rep = Report()
    strings, tables = catext.vanilla_text()
    w = catext.widths(catalan=True)
    identical = catext.identical_ids()
    middot_fixed = Path(middot_glyph).exists()
    progress = {}
    for category in catext.CATEGORIES:
        spanish = catext.table(tables, "Spanish", category)
        english = dict(catext.table(tables, "English", category))
        others = [dict(catext.table(tables, l, category)) for l in catext.LANGUAGES]
        if [i for i, _ in spanish] != [i for i, _ in catext.table(tables, "English", category)]:
            rep.add("error", catext.TEXT_DATA, 0, category, "Spanish and English pointer tables differ")
        try:
            entries, path = catext.read_translation(category, text_dir)
        except ValueError as e:
            rep.add("error", text_dir / catext.CATEGORIES[category][1], 0, None, str(e))
            entries, path = {}, text_dir / catext.CATEGORIES[category][1]
        rel = path.relative_to(catext.ROOT) if path.is_relative_to(catext.ROOT) else path
        known = {i for i, _ in spanish}
        for idx in sorted(set(entries) - known):
            rep.add("error", rel, entries[idx][1], idx, "not in the Spanish pointer table (extra string)")
        done = 0
        for idx, sym in spanish:
            if idx not in entries:
                continue
            text, n = entries[idx]
            es, en = strings[sym], strings[english[idx]]
            if text != en or idx in identical:
                done += 1
            err = lambda msg: rep.add("error", rel, n, idx, msg)  # noqa: E731
            warn = lambda msg: rep.add("warning", rel, n, idx, msg)  # noqa: E731
            try:
                catext.tokens(text)
            except KeyError as e:
                msg = str(e).strip('"')
                bad = next((c for c in text if c in LOOKALIKES), None)
                err(msg + (f"; use {LOOKALIKES[bad]} instead of {bad}" if bad and repr(bad) in msg else ""))
                continue
            if "·" in text and not middot_fixed:
                rep.add("todo", rel, n, idx, "uses · before font/glyphs/0357.png exists")
            if control_codes(text) != control_codes(es):
                err(f"control codes {control_codes(text)} differ from the Spanish {control_codes(es)}")
            ca_lines, es_lines = text.split("\\n"), es.split("\\n")
            if category in FIXED_LINES and len(ca_lines) != len(es_lines):
                err(f"{len(ca_lines)} lines, the Spanish has {len(es_lines)} (the box is fixed)")
            for ln, line in enumerate(catext.split_lines(text), 1):
                lay = catext.line_layout(line, w)
                if lay["overflow"]:
                    err(f"line {ln} is {lay['pen_end']} px, over the {catext.LINE_LIMIT} px limit")
                elif category == "file_screen":
                    widest = max((catext.line_layout(l, w)["pen_end"]
                                  for o in others if idx in o
                                  for k, l in enumerate(catext.split_lines(strings[o[idx]]), 1) if k == ln),
                                 default=0)
                    if lay["pen_end"] > widest:
                        warn(f"line {ln} is {lay['pen_end']} px, wider than any shipped language ({widest} px)")
            ca_gaps, es_gaps = gaps_per_line(text), gaps_per_line(es)
            for ln, (cg, eg) in enumerate(zip(ca_gaps, es_gaps), 1):
                if len(cg) != len(eg):
                    warn(f"line {ln} has {len(cg)} GAPs, the Spanish has {len(eg)}")
                elif category == "file_screen" and cg != eg:
                    warn(f"line {ln} GAPs {cg} differ from the Spanish {eg} (Yes/No positions)")
            for line, old, new in gap.recompute(category, idx, text, w)[1]:
                warn(f"line {line}: stale GAP({old}), should be GAP({new}) (gap.py fix)")
            if text == es and idx not in identical:
                warn("identical to the Spanish original")
        progress[category] = (done, len(spanish))
    return rep, progress


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--release", action="store_true", help="also fail on warnings and untranslated text")
    ap.add_argument("--json", help="write the report as JSON")
    ap.add_argument("--text-dir", type=Path, default=catext.CA / "text")
    a = ap.parse_args()
    rep, progress = lint(a.text_dir)
    for i in rep.items:
        print(f"{i['file']}:{i['line']}: {i['level']}: {i['id']}: {i['message']}")
    print("\ntranslated:")
    total_done = total = 0
    for category, (done, n) in progress.items():
        total_done += done
        total += n
        print(f"  {category:12} {done:3}/{n:<3} {100 * done / n:5.1f}%")
    print(f"  {'total':12} {total_done:3}/{total:<3} {100 * total_done / total:5.1f}%")
    errors, warnings, todos = rep.count("error"), rep.count("warning"), rep.count("todo")
    print(f"\n{errors} errors, {warnings} warnings, {todos} TODOs")
    if a.json:
        Path(a.json).write_text(json.dumps({"items": rep.items, "progress": {
            c: {"translated": d, "total": n} for c, (d, n) in progress.items()}}, indent=2, ensure_ascii=False))
    failed = errors or (a.release and (warnings or total_done < total))
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
