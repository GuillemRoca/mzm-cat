#!/usr/bin/env python3
"""Composes the Catalan game over prompt from the glyphs of the five vanilla EU prompts.

  gfx_game_over.py OUT.png        (needs data/ extracted and the gbagfx in build/)

The prompt (menus/game_over/text_prompt_*.gfx.lz) is three 16-px lines of an outlined font:
the question in red, the two options in blue. Each glyph's fill is cut out of a vanilla line
whose text is known, with one outline column on each side, and the Catalan lines are set with
the vanilla spacing. Options are left-aligned, and the options block plus the Samus helmet
(~24 px to the left) is centred on screen, as in vanilla. Prints the helmet X for
translation/ca/include/ca/layout.h: in every EU language it is the options' left edge + 2 px.
"""
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
GBAGFX = ROOT / "translation" / "ca" / "build" / "gbagfx"

CATALAN = ["TORNAR A PROVAR?", "SÍ (CONTINUA)", "NO (SURT)"]
VANILLA = {
    "spanish": ["¿VOLVERAINTENTARLO?", "SÍ(CONTINUAR)", "NO(SALIR)"],
    "italian": ["VUOIRIPROVARE?", "SÍ(RITORNAALGIOCO)", None],
    "english": ["TRYAGAIN?", None, "NO(TOTITLESCREEN)"],
    "german": ["ERNEUTERVERSUCH?", "JA(ZUMSPIEL)", "NEIN(ZUMTITEL)"],
    "french": ["RÉESSAYER?", "OUI(REJOUER)", "NON(QUITTERLEJEU)"],
}  # None: lines whose glyphs touch too much to segment by fill
OUTLINE = {5, 6, 10, 11}
WIDTH, LINE_H, VISIBLE = 256, 16, 232  # columns past 232 hold a katakana label, off screen
HELMET_W, SCREEN_CENTRE = 24, 120


def load(lang, tmp):
    raw, png, pal = Path(tmp) / f"{lang}.4bpp", Path(tmp) / f"{lang}.png", Path(tmp) / "row2.gbapal"
    pal.write_bytes((ROOT / "data/menus/game_over/palette.pal").read_bytes()[2 * 32:3 * 32])
    subprocess.run([GBAGFX, ROOT / f"data/menus/game_over/text_prompt_{lang}.gfx.lz", raw], check=True)
    subprocess.run([GBAGFX, raw, png, "-palette", pal, "-width", "32"], check=True)
    return Image.open(png)


def fill_segments(im, line):
    y0 = line * LINE_H
    fill = [any(im.getpixel((x, y)) not in OUTLINE | {0} for y in range(y0, y0 + LINE_H)) for x in range(VISIBLE)]
    segs, x = [], 0
    while x < VISIBLE:
        if fill[x]:
            s = x
            while x < VISIBLE and fill[x]:
                x += 1
            segs.append((s, x))
        else:
            x += 1
    return segs


def atlas(images):
    """{(colour, char): glyph columns}, colour 0 = red (question), 1 = blue (options);
    plus the most common letter spacing (fill to fill) and word spacing."""
    glyphs, letter_gaps, word_gaps = {}, Counter(), Counter()
    for lang, lines in VANILLA.items():
        for line, text in enumerate(lines):
            if text is None:
                continue
            segs = fill_segments(images[lang], line)
            if len(segs) != len(text):
                sys.exit(f"error: {lang} line {line}: {len(segs)} glyphs for {text!r}")
            for (s, e), ch in zip(segs, text):
                cols = [[images[lang].getpixel((x, y)) for y in range(line * LINE_H, (line + 1) * LINE_H)]
                        for x in range(s - 1, e + 1)]
                glyphs.setdefault((min(line, 1), ch), cols)
            for (_, e), (s, _) in zip(segs, segs[1:]):
                (letter_gaps if s - e <= 4 else word_gaps)[s - e] += 1
    return glyphs, letter_gaps.most_common(1)[0][0], word_gaps.most_common(1)[0][0]


def set_line(glyphs, colour, text, letter_gap, word_gap):
    """Columns of a composed line; fill of each glyph starts letter_gap after the previous."""
    out, pen, pending_space = {}, 1, False
    for ch in text:
        if ch == " ":
            pending_space = True
            continue
        cols = glyphs.get((colour, ch))
        if cols is None:
            sys.exit(f"error: no {'red' if colour == 0 else 'blue'} glyph for {ch!r}")
        if out:
            pen += word_gap if pending_space else letter_gap
        pending_space = False
        for i, col in enumerate(cols):
            x = pen - 1 + i
            prev = out.get(x, [0] * LINE_H)
            out[x] = [c if c else p for c, p in zip(col, prev)]
        pen += len(cols) - 2  # fill width
    left, right = min(out), max(out) + 1
    return [out.get(x, [0] * LINE_H) for x in range(left, right)]


def main(out_png):
    with tempfile.TemporaryDirectory() as tmp:
        images = {lang: load(lang, tmp) for lang in VANILLA}
        base = load("spanish", tmp)
    glyphs, letter_gap, word_gap = atlas(images)
    lines = [set_line(glyphs, min(i, 1), t, letter_gap, word_gap) for i, t in enumerate(CATALAN)]

    img = Image.new("P", (WIDTH, 3 * LINE_H), 0)
    img.putpalette(base.getpalette())
    widest = max(len(lines[1]), len(lines[2]))
    options_left = round(SCREEN_CENTRE - (widest - HELMET_W) / 2)
    lefts = [round(SCREEN_CENTRE - len(lines[0]) / 2), options_left, options_left]
    for i, (cols, left) in enumerate(zip(lines, lefts)):
        for dx, col in enumerate(cols):
            for dy, v in enumerate(col):
                if v:
                    img.putpixel((left + dx, i * LINE_H + dy), v)
    img.save(out_png)
    # +1: the glyph cut includes one outline column left of the fill; vanilla measures the fill
    helmet = options_left + 1 + 2
    print(f"{out_png}: lines at x={lefts}, widths={[len(c) for c in lines]}")
    print(f"helmet X = {helmet} px = {helmet * 4} sub-pixels (vanilla Spanish: 82 px)")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "game_over_ca.png")
