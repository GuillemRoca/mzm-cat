#!/usr/bin/env python3
"""Composes the Catalan title screen menu: "JUGA" and "Idioma".

  gfx_title_menu.py OUT_DIR   (needs data/ extracted and build/gbagfx)

menus/title_screen/spanish_menu_top and _bottom are the upper and lower halves (8 rows each)
of the two menu labels, each centred on its own column: the first at x = 47.5, the second at
x = 127.5 (the same in all five EU languages). "Idioma" is the same word in Catalan and stays.
"JUGAR" becomes "JUGA": the Spanish letters are 7 columns each, starting with a shared outline
column (x = 30, 37, 44, 51, 58) and closed by one more (x = 65, the same as each letter's
first), so dropping the R keeps x = 30..58, and the label is moved to stay centred.
The compressed halves must fit their fixed-size C arrays (the bottom one has no word to
spare), so the label goes to the most centred column whose graphics still fit: x = 35, centre
49 (x = 33 and 34, centres 47 and 48, compress one word too big).
Writes OUT_DIR/spanish_menu_top.png and OUT_DIR/spanish_menu_bottom.png.
"""
import argparse
import sys
import tempfile
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gfx  # noqa: E402

KEYS = ("menus/title_screen/spanish_menu_top", "menus/title_screen/spanish_menu_bottom")
LABEL = (30, 66)        # JUGAR, closing column included
KEEP = (30, 59)         # JUGA: up to the A's closing column
CENTRE = 47.5


def compose(images, x0):
    width = KEEP[1] - KEEP[0]
    out = {}
    for key, im in images.items():
        new = im.copy()
        for x in range(*LABEL):
            for y in range(im.height):
                new.putpixel((x, y), 0)
        for dx in range(width):
            for y in range(im.height):
                new.putpixel((x0 + dx, y), im.getpixel((KEEP[0] + dx, y)))
        out[key] = new
    return out


def fits(composed, tmp):
    for key, im in composed.items():
        png = Path(tmp) / "try.png"
        im.save(png)
        raw, lz = gfx.encode(png, gfx.vanilla_tiles(key), tmp)
        if gfx.check_limits(key, len(raw), len(lz)):
            return False
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out_dir")
    a = ap.parse_args()
    out = Path(a.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    width = KEEP[1] - KEEP[0]
    with tempfile.TemporaryDirectory() as tmp:
        images = {}
        for key in KEYS:
            png = Path(tmp) / "in.png"
            gfx.export(key, png, tmp)
            images[key] = Image.open(png)
            images[key].load()
        # most centred first
        for x0 in sorted(range(LABEL[0], LABEL[1] - width + 1), key=lambda x: abs(x + (width - 1) / 2 - CENTRE)):
            composed = compose(images, x0)
            if fits(composed, tmp):
                break
        else:
            sys.exit("error: JUGA doesn't fit the C arrays at any position")
    for key, im in composed.items():
        im.save(out / f"{key.rsplit('/', 1)[1]}.png")
    print(f"JUGA: x={x0}..{x0 + width - 1} (centre {x0 + (width - 1) / 2}, vanilla labels {CENTRE})")


if __name__ == "__main__":
    main()
