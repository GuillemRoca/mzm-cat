#!/usr/bin/env python3
"""Generates the Catalan ending sprites for LANG_CA=1, in the German slot:

  genending.py ending OUT [--vanilla]    ca/ending_oam.inc: the typed letters and whole lines
                                         of the ending results screen, and the new record box
  genending.py tables OUT [--vanilla]    ca/ending_tables.inc: the tables that type and show
                                         those sprites (sEndingImageOam_*_German)
  genending.py mission OUT [--vanilla]   ca/mission_accomplished.inc: the "Mission
                                         accomplished" frame
--vanilla reproduces the vanilla German blocks (plumbing self-test).

Each output replaces the German `#ifdef LANG_CA` block of src/data/ending_and_gallery_data.c
or src/data/chozodia_escape_data.c. The Catalan was laid out on the Spanish sprites (letter
counts, spawn delays, positions, the record box), so each output is the vanilla Spanish block
with the Catalan sprites, renamed to the German symbols; the Spanish data itself is untouched.
The German table sizes follow (translation/ca/include/ca/layout.h). The typed letters and the
two result lines come from ending_layout.py; the last line ("Fins a la propera missió!") from
the ink of translation/ca/gfx/ending/text_german.png (rows 8-9, and the 8x8 tiles of row 10
that hold descenders), drawn from the sheet's left edge by gfx_ending.py.
"""
import argparse
import re
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ending_layout as L  # noqa: E402

PNG = L.ROOT / "translation" / "ca" / "gfx" / "ending" / "text_german.png"
LAST_TILE, LAST_ROW = 0x180, 64          # the last line: rows 8-9 of the sheet, descenders in row 10


# Symbols of the Spanish template and the German symbols they become.
RENAMES = [
    (r"\bs(FullLines|ClearTime|Collecting)SpanishOam_", r"s\1GermanOam_"),
    (r"\bsEndingImageOam_NewRecordSpanish\b", "sEndingImageOam_NewRecordGerman"),
    (r"\bsEndingImageOam_(FullLines|ClearTime|Collecting)_Spanish\b", r"sEndingImageOam_\1_German"),
    (r"\bsChozodiaEscapeOam_MissionAccomplishedSpanish_Frame0\b", "sChozodiaEscapeOam_MissionAccomplishedGerman_Frame0"),
]


def block(src, inc):
    """The vanilla German code of the `#ifdef LANG_CA` block that includes `inc`."""
    m = re.search(r'#ifdef LANG_CA\n#include "' + re.escape(inc) + r'"\n#else // !LANG_CA\n(.*?)\n#endif // LANG_CA', src, re.S)
    if not m:
        sys.exit(f"error: no LANG_CA block for {inc}")
    if "German" not in m.group(1) or "Spanish" in m.group(1):
        sys.exit(f"error: the LANG_CA block for {inc} must be the German one")
    return m.group(1)


def template(src, first, last):
    """The vanilla Spanish code from the declaration of `first` to the end of `last`'s."""
    decl = r"^(?:static )?const [^\n=]*\b{}\["
    start = re.search(decl.format(first), src, re.M)
    end = start and re.compile(decl.format(last) + r".*?^\};", re.M | re.S).search(src, start.start())
    if not end or "#" in src[start.start():end.end()]:
        sys.exit(f"error: no vanilla block from {first} to {last}")
    return src[start.start():end.end()]


def to_german(text):
    for pat, new in RENAMES:
        text = re.sub(pat, new, text)
    if "Spanish" in text:
        sys.exit("error: a Spanish symbol is left in the German block: " + re.search(r"\w*Spanish\w*", text).group(0))
    return text


def entry(x, y, dims, tile, pal):
    return f"    OAM_ENTRY({x}, {y}, OAM_DIMS_{dims}, OAM_NO_FLIP, {tile:#x}, {pal}, 0)"


def frame(decl, entries):
    return "\n".join([f"{decl} = {{", f"    {len(entries)},", ",\n".join(entries), "};"])


def replace_frame(text, name, entries, static=True, size=None):
    pat = re.compile(r"(?:static )?const u16 " + name + r"\[OAM_DATA_SIZE\((\d+)\)\] = \{.*?\n\};", re.S)
    m = pat.search(text)
    if not m:
        sys.exit(f"error: no {name}")
    n = size if size is not None else len(entries)
    if size is not None and len(entries) != size:
        sys.exit(f"error: {name} needs {size} sprites, the Catalan has {len(entries)}")
    decl = ("static " if static else "") + f"const u16 {name}[OAM_DATA_SIZE({n})]"
    return text[:m.start()] + frame(decl, entries) + text[m.end():]


def last_line():
    """Sprites of the last line from the PNG: [(x, y, dims, tile)]."""
    im = Image.open(PNG)
    ink = [x for x in range(im.width) if any(im.getpixel((x, y)) for y in range(LAST_ROW, LAST_ROW + 16))]
    width = ink[-1] + 1
    if ink[0] != 0:
        sys.exit("error: the last line must start at the sheet's left edge")
    start = -(width // 2)
    out, x = [], 0
    while x < width:
        dims = "32x16" if width - x > 16 else "16x16" if width - x > 8 else "8x16"
        out.append((start + x, -16, dims, LAST_TILE + x // 8))
        x += L.WIDTH[dims]
    for col in range(32):
        if any(im.getpixel((col * 8 + dx, LAST_ROW + 16 + dy)) for dx in range(8) for dy in range(8)):
            out.append((start + col * 8, 0, "8x8", LAST_TILE + 0x40 + col))
    return out


def ending(vanilla):
    src = L.ENDING_C.read_text(encoding="utf-8")
    german = block(src, "ca/ending_oam.inc")
    if vanilla:
        return german
    text = template(src, "sFullLinesSpanishOam_0", "sEndingImageOam_NewRecordSpanish")
    layout, _ = L.ending()
    for key, (full, _) in L.FULL_LINES.items():
        line = layout[key]
        text = replace_frame(text, full, [entry(x, y, d, t, 0) for x, y, d, t in line["full"]])
        for k, (_, x, y, d, t) in enumerate(line["letters"]):
            text = replace_frame(text, f"s{key}SpanishOam_{k}", [entry(x, y, d, t, 0)], size=1)
        n = len(re.findall(rf"static const u16 s{key}SpanishOam_\d+\[", text))
        if n != len(line["letters"]):
            sys.exit(f"error: {key}: {len(line['letters'])} Catalan letters, the table has {n}")
    if PNG.exists():
        text = replace_frame(text, "sFullLinesSpanishOam_2", [entry(x, y, d, t, 1) for x, y, d, t in last_line()])
    return to_german(text)


def tables(vanilla):
    """The Spanish tables (their letter counts, spawn delays and positions), as the German."""
    src = L.ENDING_C.read_text(encoding="utf-8")
    german = block(src, "ca/ending_tables.inc")
    if vanilla:
        return german
    return to_german(template(src, "sEndingImageOam_FullLines_Spanish", "sEndingImageOam_Collecting_Spanish"))


def mission(vanilla):
    src = L.CHOZODIA_C.read_text(encoding="utf-8")
    german = block(src, "ca/mission_accomplished.inc")
    if vanilla:
        return german
    name = "sChozodiaEscapeOam_MissionAccomplishedSpanish_Frame0"
    entries, _ = L.mission()
    text = replace_frame(template(src, name, name), name,
                         [entry(x, y, d, t, 0) for x, y, d, t in entries], static=False, size=16)
    return to_german(text)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("what", choices=["ending", "tables", "mission"])
    ap.add_argument("out")
    ap.add_argument("--vanilla", action="store_true")
    a = ap.parse_args()
    text = {"ending": ending, "tables": tables, "mission": mission}[a.what](a.vanilla)
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(f"// Generated by translation/ca/tools/genending.py. Do not edit.\n{text}\n", encoding="utf-8")


if __name__ == "__main__":
    main()
