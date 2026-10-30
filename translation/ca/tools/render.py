#!/usr/bin/env python3
"""Offline preview of text lines as the game draws them (TextDrawCharacter, src/text.c).

  render.py OUT.png "line" ["line"...] [--vanilla] [--scale N] [--color N]

Uses the extracted EU font and widths, with the Catalan glyph and width overrides unless
--vanilla. Each glyph is ORed into 8-px tiles at the pen position. Its columns past the
current tile are drawn only when it spills (pen%8 + width > 8, with the EU +1 when it ends
on a tile boundary), so outline columns are clipped exactly as in the game. Lines are
224 px wide (the overflow limit); pixels past the limit are shown in red.
"""
import argparse
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import catext  # noqa: E402
import font as fontlib  # noqa: E402

from PIL import Image  # noqa: E402

SHADES = {0: (24, 24, 56), 1: (70, 70, 90), 2: (120, 120, 140), 3: (170, 170, 185)}
COLORS = {0: (255, 255, 255), 5: (255, 220, 60), 6: (255, 90, 90), 7: (120, 200, 255),
          8: (120, 255, 120), 9: (255, 160, 60), 10: (220, 140, 255)}


def load_font(vanilla):
    if vanilla:
        return fontlib.FONT.read_bytes()
    with tempfile.TemporaryDirectory() as tmp:
        inc = Path(tmp) / "font.inc"
        fontlib.cmd_build(inc)
        return bytes(int(v[:-1]) for v in inc.read_text().split(","))


def glyph_pixels(font, cid):
    """16 rows x 16 cols of 4-bit values (two tiles wide)."""
    px = [[0] * 16 for _ in range(16)]
    for half in (0, 1):
        for t in (0, 1):
            off = (cid + t) * 32 + half * 0x400
            for y in range(8):
                for xb in range(4):
                    b = font[off + y * 4 + xb]
                    px[half * 8 + y][t * 8 + xb * 2] = b & 0xF
                    px[half * 8 + y][t * 8 + xb * 2 + 1] = b >> 4
    return px


def draw_line(text, font, w, canvas, y0, default_color):
    pen, color = 0, default_color
    for kind, v, _ in catext.tokens(text):
        if kind == "gap":
            pen += v
            continue
        if kind == "indent":
            pen = v
            continue
        if kind == "color":
            color = v
            continue
        if kind != "char":
            continue
        width = w[v] if v < len(w) else 10
        if pen + width > catext.LINE_LIMIT:
            break  # the game moves this glyph to the next line
        drawn = width
        if pen + width < 224 and (pen + width) % 8 == 0 and width % 8 != 0:
            drawn += 1  # EU: let the outline column spill into the next tile
        s = pen % 8
        cols = 16 if width > 8 else 8
        visible = cols if s + drawn > cols else cols - s
        g = glyph_pixels(font, v)
        for y in range(16):
            for c in range(visible):
                val = g[y][c]
                if val:
                    x = pen + c
                    old = canvas.get((x, y0 + y), (0, color))[0]
                    canvas[(x, y0 + y)] = (old | val, color)
        pen += width
    return pen


def render(lines, out, vanilla=False, scale=3, color=0):
    font = load_font(vanilla)
    w = catext.widths(catalan=not vanilla)
    canvas = {}
    ends = [draw_line(line, font, w, canvas, i * 16, color) for i, line in enumerate(lines)]
    img = Image.new("RGB", (240, 16 * len(lines)), SHADES[0])
    for (x, y), (val, col) in canvas.items():
        if 0 <= x < 240:
            rgb = COLORS.get(col, (255, 255, 255)) if val & 4 else SHADES.get(val & 3, SHADES[3])
            img.putpixel((x, y), rgb if x < catext.LINE_LIMIT else (255, 0, 0))
    for y in range(img.height):
        img.putpixel((catext.LINE_LIMIT, y), (255, 0, 0))
    img = img.resize((img.width * scale, img.height * scale), Image.NEAREST)
    img.save(out)
    return ends


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("lines", nargs="+")
    ap.add_argument("--vanilla", action="store_true")
    ap.add_argument("--scale", type=int, default=3)
    ap.add_argument("--color", type=int, default=0)
    a = ap.parse_args()
    for line, end in zip(a.lines, render(a.lines, a.out, a.vanilla, a.scale, a.color)):
        print(f"{end:3} px  {line}")
