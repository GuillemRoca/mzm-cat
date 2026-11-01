#!/usr/bin/env python3
"""Adds the letters the Catalan intro text needs to intro/text_and_ship.

  gfx_intro.py OUT_PNG   (needs data/ extracted and build/gbagfx)

The intro types its text with 8x16 sprites from this sheet (tiles n and n + 0x20), shared by
every language and by the Tourian escape (its ship). È, À and the apostrophe are drawn in cells
no frame of either scene uses (genintro.NEW), so the other languages don't change:
  È, À   the sheet's E and A with a grave accent in the black band above the letter
  '      a tick on the box's background
Writes OUT_PNG (translation/ca/gfx/intro/text_and_ship.png).
"""
import argparse
import sys
import tempfile
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import genintro  # noqa: E402
import gfx  # noqa: E402

KEY = "intro/text_and_ship"
# grave accent (col, row, colour index): rows 2-4, down to the box's top line (row 4) so it
# sits on the letter (row 5 up)
GRAVE = [(2, 2, 0xB), (3, 2, 0xF), (4, 2, 0x8), (3, 3, 0xC), (4, 3, 0xF), (5, 3, 0xE),
         (4, 4, 0x9), (5, 4, 0xF), (6, 4, 0xB)]
# the box's background, rows 4-15 (top line, scanlines, bottom line); rows 0-3 are black
BOX = {4: 0x2, 5: 0x4, 15: 0x4, **{y: 0x3 if y % 2 == 0 else 0x5 for y in range(6, 15)}}
APOSTROPHE = [(3, 5, 0xC), (4, 5, 0xF), (3, 6, 0xC), (4, 6, 0xF), (3, 7, 0x8), (4, 7, 0xE),
              (2, 8, 0x9), (3, 8, 0x8)]


def cell(tile):
    """Top-left pixel of an 8x16 cell (tiles n and n + 0x20)."""
    return (tile % 32) * 8, (tile // 32) * 8


def copy_cell(img, src, dst):
    sx, sy = cell(src)
    dx, dy = cell(dst)
    for y in range(16):
        for x in range(8):
            img.putpixel((dx + x, dy + y), img.getpixel((sx + x, sy + y)))


def draw(img, tile, pixels):
    x0, y0 = cell(tile)
    for x, y, v in pixels:
        img.putpixel((x0 + x, y0 + y), v)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    a = ap.parse_args()
    out = Path(a.out)
    with tempfile.TemporaryDirectory() as tmp:
        png = Path(tmp) / "vanilla.png"
        gfx.export(KEY, png, tmp)
        img = Image.open(png)
        img.load()
    x0, y0 = cell(genintro.PAD)
    if any(img.getpixel((x0 + x, y0 + y)) for x in range(8) for y in range(16)):
        sys.exit(f"error: cell {genintro.PAD:#x}, genintro's invisible PAD, isn't blank")
    for ch, base in (("È", "E"), ("À", "A")):
        tile = genintro.NEW[ch]
        copy_cell(img, genintro.LETTERS[base], tile)
        x0, y0 = cell(tile)
        for x in range(8):
            for y in range(4):
                img.putpixel((x0 + x, y0 + y), 0x1)
        draw(img, tile, GRAVE)
    tile = genintro.NEW["'"]
    draw(img, tile, [(x, y, 0x1) for x in range(8) for y in range(4)])
    draw(img, tile, [(x, y, v) for x in range(8) for y, v in BOX.items()])
    draw(img, tile, APOSTROPHE)
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out)
    print(f"{out}: È, À and ' in cells {', '.join(hex(t) for t in genintro.NEW.values())}")


if __name__ == "__main__":
    main()
