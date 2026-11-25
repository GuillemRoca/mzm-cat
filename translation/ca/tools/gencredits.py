#!/usr/bin/env python3
"""Generates translation/ca/build/include/ca/credits.inc for LANG_CA=1: the EU sCredits with
the Catalan translators from translation/ca/credits.txt.

The input is the vanilla EU array (the `#else // !LANG_CA` branch around
`#include "ca/credits.inc"` in src/data/ending_and_gallery_data.c). A "CATALAN" block goes
right after the Italian translator, laid out like the other languages of the TRANSLATION
section. The credits scroll one row at a time (WHITE_BIG lines take 2 rows, the others 1) and
stop at the END line, so to keep them as long as vanilla, in time with the music, the rows
added are taken from the empty lines between the executive producer and the copyright, and
the entry count (the array has a fixed size) is restored by merging pairs of the empty lines
after the copyright, which are never seen.

usage: gencredits.py OUTPUT [--vanilla]   (--vanilla: reproduce vanilla, plumbing self-test)
"""
import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "src" / "data" / "ending_and_gallery_data.c"
CREDITS = ROOT / "translation" / "ca" / "credits.txt"

ENTRY_RE = re.compile(r'\[(\d+)\] = \{\s*\.type = CREDIT_LINE_TYPE_(\w+),\s*\.text = "((?:[^"\\]|\\.)*)"\s*\}')
HEADER_RE = re.compile(r"const struct CreditsEntry sCredits\[(\d+)\] = \{")
BIG = "WHITE_BIG"
BLUE_OK = re.compile(r"[A-Z .,&]+")          # the blue font: A-Z (lowercase shows as A-Z), . , &
NAME_OK = re.compile(r"[A-Za-z .,-]+")       # WHITE_BIG: letters, space, . , - (no accents)


def rows(entries):
    return sum(2 if t == BIG else 1 for t, _ in entries)


def vanilla():
    src = SRC.read_text(encoding="utf-8")
    m = re.search(r'#ifdef LANG_CA\n#include "ca/credits.inc"\n#else // !LANG_CA\n(.*?)\n#endif // LANG_CA', src, re.S)
    if not m:
        sys.exit(f"error: no LANG_CA block around the EU sCredits in {SRC}")
    block = m.group(1)
    size = int(HEADER_RE.search(block).group(1))
    entries = []
    for i, (n, t, text) in enumerate(ENTRY_RE.findall(block)):
        if int(n) != i:
            sys.exit(f"error: sCredits entry {n} out of order")
        entries.append((t, text))
    if len(entries) != size:
        sys.exit(f"error: parsed {len(entries)} sCredits entries, the array has {size}")
    return size, entries


def read_credits(path=CREDITS):
    heading, names = None, []
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        key, _, value = (s.strip() for s in line.partition("="))
        if key == "heading" and BLUE_OK.fullmatch(value):
            heading = value
        elif key == "name" and NAME_OK.fullmatch(value) and len(value) <= 30:
            names.append(value)
        else:
            sys.exit(f"{path}:{n}: error: expected 'heading = A-Z' or 'name = Name' (A-Z a-z . , -, 30 max)")
    if not heading or not names:
        sys.exit(f"{path}: error: needs a heading and at least one name")
    return heading, names


def blank(entry):
    return entry[1].strip() == "" and entry[0] in (BIG, "BLANK", "BLUE")


def catalan(entries, heading, names):
    out = list(entries)
    # After the Italian translator, as the Italian block follows the Spanish one:
    # name, 3 blank, heading, 2 blank, name(s)
    it = next(i for i, e in enumerate(out) if e == ("BLUE", "ITALIAN"))
    name_at = next(i for i in range(it + 1, len(out)) if out[i][0] == BIG and out[i][1])
    block = [("BLANK", "")] * 3 + [("BLUE", heading)] + [("BLANK", "")] * 2
    for k, name in enumerate(names):
        block += ([("BLANK", "")] if k else []) + [(BIG, name)]
    out[name_at + 1:name_at + 1] = block
    added_rows, added_entries = rows(block), len(block)

    # Take the rows back from the empty lines between the executive producer and the copyright
    start = next(i for i, e in enumerate(out) if e == (BIG, "Iwata Satoru")) + 1
    end = next(i for i, e in enumerate(out) if e[0] == "ALL_RIGHTS")
    need = added_rows
    i = end - 1
    while need > 0 and i >= start:
        if blank(out[i]) and out[i][0] == BIG and need >= 2:
            del out[i]
            need -= 2
        elif blank(out[i]) and out[i][0] == BIG and need == 1:
            out[i] = ("BLANK", "")
            need -= 1
        i -= 1
    if need:
        sys.exit("error: not enough empty lines before the copyright for the Catalan credit")

    # Restore the entry count by merging pairs of blank lines after the copyright
    extra = len(out) - len(entries)
    j = next(i for i, e in enumerate(out) if e[0] == "RESERVED") + 1
    while extra > 0:
        if out[j][0] == "END":
            sys.exit("error: not enough blank lines after the copyright")
        if out[j] == ("BLANK", "") and out[j + 1] == ("BLANK", ""):
            out[j:j + 2] = [(BIG, "")]
            extra -= 1
        j += 1
    assert len(out) == len(entries) and rows(out) == rows(entries), "credits length changed"
    assert out[-1][0] == "END"
    return out, added_entries


def emit(size, entries):
    lines = [f"// Generated by translation/ca/tools/gencredits.py from {SRC.relative_to(ROOT)} and",
             "// translation/ca/credits.txt. Do not edit.",
             f"const struct CreditsEntry sCredits[{size}] = {{"]
    for i, (t, text) in enumerate(entries):
        lines += [f"    [{i}] = {{", f"        .type = CREDIT_LINE_TYPE_{t},", f'        .text = "{text}"',
                  "    }," if i < len(entries) - 1 else "    }"]
    lines.append("};")
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--vanilla", action="store_true")
    a = ap.parse_args()
    size, entries = vanilla()
    if not a.vanilla:
        entries, _ = catalan(entries, *read_credits())
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(emit(size, entries), encoding="utf-8")


if __name__ == "__main__":
    main()
