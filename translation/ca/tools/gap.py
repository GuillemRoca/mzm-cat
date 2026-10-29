#!/usr/bin/env python3
"""Recomputes the centring {GAP(n)} at the start of each line, as the EU text was laid out.

  gap.py check      list Catalan lines whose GAP is stale (exit 1 if any)
  gap.py fix        rewrite the stale GAPs in translation/ca/text/*.txt
  gap.py vanilla    recompute every vanilla EU line (all five languages) and report each
                    difference: the rules must reproduce the shipped GAPs

Rules (reverse-engineered from all EU languages; text.c only advances the pen by GAP):
  message, location   GAP = round_half_even((220 - w) / 2) on every line
  story               GAP = floor((224 - w) / 2) on lines that start with a GAP, except in
                      STORY_TEXT_PLANET_ZEBES, whose GAP(8) margins and GAP(138) are fixed
  file_screen         GAPs are positions (Yes/No columns), never recomputed, except the
                      "Best Time" labels: GAP = floor((96 - w) / 2)
  description         no GAPs
w is the sum of the line's glyph widths. GAPs and INDENTs after the leading GAP are layout
the translator chose (e.g. the extra GAP(8) in the Spanish save prompt) and are not counted.
"""
import argparse
import math
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import catext  # noqa: E402

FIXED = {"STORY_TEXT_PLANET_ZEBES"}
CENTRED_FILE_SCREEN = {"FILE_SCREEN_TEXT_BEST_TIME", "FILE_SCREEN_TEXT_BEST_TIME_100"}
LEAD_GAP = re.compile(r"^\{GAP\((\d+)\)\}")


def rule(category, idx):
    if category in ("message", "location"):
        return lambda w: round((220 - w) / 2)  # Python rounds half to even
    if category == "story" and idx not in FIXED:
        return lambda w: math.floor((224 - w) / 2)
    if category == "file_screen" and idx in CENTRED_FILE_SCREEN:
        return lambda w: math.floor((96 - w) / 2)
    return None


def recompute(category, idx, text, w):
    """Returns (new text, [(line number, old gap, new gap)])."""
    f = rule(category, idx)
    if f is None:
        return text, []
    lines, changes = text.split("\\n"), []
    for n, line in enumerate(lines):
        m = LEAD_GAP.match(line)
        if not m:
            if category not in ("message", "location"):
                continue
            # Every banner line is centred: give a missing lead GAP a value to fix.
            line = lines[n] = "{GAP(0)}" + line
            m = LEAD_GAP.match(line)
        glyphs = catext.line_layout(line, w)["glyph_width"]
        new = max(0, f(glyphs))  # an overflowing line is the linter's error, not a negative GAP
        old = int(m.group(1))
        if new != old:
            changes.append((n + 1, old, new))
            lines[n] = f"{{GAP({new})}}" + line[m.end():]
    return "\\n".join(lines), changes


def cmd_vanilla():
    strings, tables = catext.vanilla_text()
    w = catext.widths(catalan=False)
    total = diffs = 0
    for category in catext.CATEGORIES:
        for lang in catext.LANGUAGES:
            for idx, sym in catext.table(tables, lang, category):
                text = strings[sym]
                if rule(category, idx) is None:
                    continue
                total += sum(1 for l in text.split("\\n") if LEAD_GAP.match(l))
                _, changes = recompute(category, idx, text, w)
                for line, old, new in changes:
                    diffs += 1
                    print(f"{lang} {idx} line {line}: shipped GAP({old}), rules give GAP({new})")
    print(f"{total - diffs}/{total} recomputed vanilla GAPs match the shipped ones")
    return diffs


def cmd_check(fix):
    w = catext.widths(catalan=True)
    stale = 0
    for category in catext.CATEGORIES:
        entries, path = catext.read_translation(category)
        if not entries:
            continue
        text_lines = path.read_text(encoding="utf-8").split("\n")
        for idx, (text, lineno) in entries.items():
            new, changes = recompute(category, idx, text, w)
            for line, old, g in changes:
                stale += 1
                print(f"{path.relative_to(catext.ROOT)}:{lineno}: {idx} line {line}: GAP({old}) -> GAP({g})")
            if changes and fix:
                text_lines[lineno - 1] = text_lines[lineno - 1].replace(f'"{text}"', f'"{new}"', 1)
        if fix:
            path.write_text("\n".join(text_lines), encoding="utf-8")
    if fix and stale:
        print(f"fixed {stale} GAPs")
    return stale


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["check", "fix", "vanilla"])
    a = ap.parse_args()
    if a.cmd == "vanilla":
        sys.exit(1 if cmd_vanilla() else 0)
    stale = cmd_check(a.cmd == "fix")
    sys.exit(1 if stale and a.cmd == "check" else 0)
