#!/usr/bin/env python3
"""Lints translation/ca/text/*.txt against the vanilla EU text in src/data/text_data.c.

  lint.py [--release] [--json OUT] [--text-dir DIR]

Errors (exit 1):
  - malformed lines, duplicate IDs, IDs that aren't in the Spanish pointer table
  - characters missing from charmap.txt, unknown {CODES}
  - control codes (COLOR, INDENT, DELAY, buttons and other named codes) that differ from the
    Spanish original, in order; or a different number of lines (\\n) where the box is fixed
    (story screens: more lines than any shipped language uses for that text)
  - a line that crosses 224 px (the game would wrap it and, in banners, lose the rest)
Warnings (exit 1 with --release):
  - stale centring GAPs (fix with gap.py fix), a number of GAPs on a line that matches neither
    the Spanish nor the English, or a
    different FileScreen GAP value (those are Yes/No positions)
  - a FileScreen line wider than any shipped line drawn into the same text area (pop-ups have
    four, from sFileScreenMessagesInfo; other FileScreen texts: that text's widest line); a story
    line wider than the widest line any shipped language uses for that text
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

FIXED_LINES = {"message", "location", "file_screen"}
# Story screens have room for more lines and differ between languages (German and English use
# 7 and 8 where the Spanish uses 6): bounded by the shipped languages instead.
SHIPPED_BOUNDS = {"story"}
LOOKALIKES = {"’": "'", "‘": "'", "“": "”", "–": "-", "—": "-", "€": "(not in the font)"}


_FILE_SCREEN_REGIONS = None


def file_screen_regions():
    """{FileScreen ID: {text area}} from sFileScreenMessagesInfo: the file select draws each
    pop-up into one of four VRAM text areas (the same text can use several)."""
    global _FILE_SCREEN_REGIONS
    if _FILE_SCREEN_REGIONS is None:
        src = (catext.ROOT / "src/data/menus/file_select_data.c").read_text(encoding="utf-8")
        block = re.search(r"sFileScreenMessagesInfo\[[^]]*\]\[3\] = \{(.*?)\n\};", src, re.S).group(1)
        _FILE_SCREEN_REGIONS = {}
        for idx, area in re.findall(r"\{\s*(FILE_SCREEN_TEXT_\w+),\s*(\d+),\s*\d+\s*\}", block):
            _FILE_SCREEN_REGIONS.setdefault(idx, set()).add(int(area))
    return _FILE_SCREEN_REGIONS


def file_screen_bound(idx, strings, others, w):
    """(px, description) a FileScreen line may take: the widest line any shipped language draws
    into the same text area (the narrowest of its areas), or, for texts drawn elsewhere, the
    widest line of that text in any shipped language."""
    regions = file_screen_regions()
    def widest(ids):
        return max((catext.line_layout(l, w)["pen_end"] for o in others for i in ids if i in o
                    for l in catext.split_lines(strings[o[i]])), default=0)
    if idx in regions:
        bounds = [(widest([i for i, a in regions.items() if area in a]), area) for area in regions[idx]]
        px, area = min(bounds)
        return px, f"in text area {area}"
    return widest([idx]), "of this text"


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


def lint(text_dir=catext.CA / "text", middot_glyph=catext.CA / "font" / "glyphs" / "0357.png",
         identical_path=catext.CA / "identical.txt"):
    rep = Report()
    strings, tables = catext.vanilla_text()
    w = catext.widths(catalan=True)
    identical = catext.identical_ids(Path(identical_path))
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
            if category in SHIPPED_BOUNDS:
                most = max(len(strings[o[idx]].split("\\n")) for o in others if idx in o)
                if len(ca_lines) > most:
                    err(f"{len(ca_lines)} lines, no shipped language uses more than {most}")
                widest_any = max(catext.line_layout(l, w)["pen_end"] for o in others if idx in o
                                 for l in catext.split_lines(strings[o[idx]]))
            for ln, line in enumerate(catext.split_lines(text), 1):
                lay = catext.line_layout(line, w)
                if lay["overflow"]:
                    err(f"line {ln} is {lay['pen_end']} px, over the {catext.LINE_LIMIT} px limit")
                elif category in SHIPPED_BOUNDS and lay["pen_end"] > widest_any:
                    warn(f"line {ln} is {lay['pen_end']} px, wider than any shipped language ({widest_any} px)")
                elif category == "file_screen":
                    widest, where = file_screen_bound(idx, strings, others, w)
                    if lay["pen_end"] > widest:
                        warn(f"line {ln} is {lay['pen_end']} px, wider than any shipped line {where} ({widest} px)")
            ca_gaps, es_gaps, en_gaps = gaps_per_line(text), gaps_per_line(es), gaps_per_line(en)
            for ln, (cg, eg) in enumerate(zip(ca_gaps, es_gaps), 1):
                # Either vanilla layout is fine (e.g. the save prompt centred like the English)
                eng = en_gaps[ln - 1] if ln <= len(en_gaps) else eg
                if len(cg) != len(eg) and len(cg) != len(eng):
                    warn(f"line {ln} has {len(cg)} GAPs, the Spanish has {len(eg)} and the English {len(eng)}")
                elif category == "file_screen" and cg != eg and gap.rule(category, idx) is None:
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
