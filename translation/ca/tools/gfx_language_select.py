#!/usr/bin/env python3
"""Composes the language selector with "Català" in the Spanish slot.

  gfx_language_select.py OUT.png [--grave a|b]   (needs data/ extracted and build/gbagfx)

menus/language_select/background.gfx.lz starts with a 256x16 strip of the five labels (top
tiles 0x00-0x1F, bottom 0x20-0x3F), each left-aligned in its range: English, Deutsch,
Français, Italiano, Español (x 208-256, tiles 0x1A-0x1F and 0x3A-0x3F, which only the Spanish
label uses). The font is outlined: background F, outline 1, fill 4, capitals on rows 4-12,
x-height 7-11, accents on rows 3-5 like the ñ tilde. Each lowercase glyph is a 7-px cell with
its own outline columns, so cells cut from a vanilla label set side by side with the vanilla
spacing. "a", "t" and "l" come from "Italiano"; C and the grave accent are drawn in DRAWN.
The tilemap is unchanged: "Català" (38 px) fits the Spanish label's 6 tiles.
"""
import argparse
import sys
import tempfile
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gfx  # noqa: E402

KEY = "menus/language_select/background"
BG = 0xF
SPANISH = (208, 256)
ITALIANO = 160
# Cells cut from "Italiano" (x offsets in its range): a, then "tal" in one piece, so the l's
# serif overhanging the a stays as vanilla draws it.
CUTS = {"a": (13, 20), "tal": (7, 23)}

# Drawn glyphs: rows 3-12, '.' = background.
C = ["........",
     "..111111",
     ".1144441",
     "11411111",
     "141.....",
     "141.....",
     "141.....",
     "11411111",
     ".1144441",
     "..111111"]   # stair corners like the D of "Deutsch", mirrored
GRAVE = {
    "a": [".1111..", ".144111", ".114411"],   # 2-px stroke stepping down to the right
    "b": [".111...", ".1411..", ".11411."],   # 1-px stroke
}  # rows 3-5, over an "a" cell, like the ñ tilde


def drawn(rows, top):
    return [{y: int(r[x], 16) for y, r in enumerate(rows, top) if r[x] != "."}
            for x in range(len(rows[0]))]


def cut(im, x0, x1, top=0):
    return [{y: im.getpixel((x, y)) for y in range(top, 16) if im.getpixel((x, y)) != BG}
            for x in range(x0, x1)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--grave", choices=sorted(GRAVE), default="a")
    a = ap.parse_args()
    with tempfile.TemporaryDirectory() as tmp:
        png = Path(tmp) / "bg.png"
        gfx.export(KEY, png, tmp)
        im = Image.open(png)
        im.load()

    # rows 6+ only for a lone "a": its last column carries the outline of the l's serif
    cells = {k: cut(im, ITALIANO + s, ITALIANO + e, 6 if k == "a" else 0) for k, (s, e) in CUTS.items()}
    a_grave = [dict(col) for col in cells["a"]]
    for col, extra in zip(a_grave, drawn(GRAVE[a.grave], 3)):
        col.update(extra)
    cols = drawn(C, 3) + cells["a"] + cells["tal"] + a_grave
    x0, x1 = SPANISH
    if len(cols) > x1 - x0:
        sys.exit(f"error: 'Català' is {len(cols)} px, the label has {x1 - x0}")

    out = im.copy()
    for x in range(x0, x1):
        for y in range(16):
            out.putpixel((x, y), BG)
    for dx, col in enumerate(cols):
        for y, v in col.items():
            out.putpixel((x0 + dx, y), v)
    out.save(a.out)
    print(f"'Català': x={x0}..{x0 + len(cols)} ({len(cols)} px)")


if __name__ == "__main__":
    main()
