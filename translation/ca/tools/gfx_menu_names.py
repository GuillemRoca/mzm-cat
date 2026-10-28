#!/usr/bin/env python3
"""Composes the Catalan pause-screen menu names from the glyphs of the five vanilla EU sheets.

  gfx_menu_names.py OUT.png [--accent a|b|c]   (needs data/ extracted and build/gbagfx)

menus/pause_screen/menu_names_*.gfx.lz is one 8-px row of 22 tiles: the top bar with the L tab
(Easy Sleep) and the R tab (status screen) in tiles 0-9, then two copies of the area-change
label (tiles 10-15 and 16-21). Two 5-px fonts: the tabs (rows 3-7, ink B/C on 3) and the label
(rows 0-5, ink 3/4/5 on 2). Glyphs are cut from vanilla labels whose text is known; the
Spanish sheet is the base, with its text erased and the Catalan set in. Tab labels are centred
like vanilla, the area label left-aligned. Letters no sheet has are drawn in DRAWN:
  Ò (tabs): an accented capital, like German Ä in the label font (accent on top, 4-row body);
  V (label): in the style of the label font's A and N.
"""
import argparse
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
GBAGFX = ROOT / "translation" / "ca" / "build" / "gbagfx"

CATALAN = {"L": "REPÒS", "R": "ESTAT", "area": "CANVIA ZONA"}

TABS = {"english": ("SLEEP", "STATUS"), "german": ("STANDBY", "STATUS"), "french": ("VEILLE", "STATUT"),
        "italian": ("RIPOSO", "STATO"), "spanish": (None, "ESTADO")}  # "SALVAP.": the dot merges
AREA = {"english": "CHANGEAREAS", "german": "BEREICHÄNDERN", "french": "CHANGERZONES",
        "italian": "CAMBIAAREA", "spanish": "CAMBIARZONA"}

# font: (rows, background index, ink indices, x ranges of the labels in the sheet)
FONTS = {
    "tab": (range(3, 8), 3, {0xB, 0xC}, {"L": (6, 34), "R": (46, 74)}),
    "area": (range(0, 6), 2, {3, 4, 5}, {"area": (80, 128), "area2": (128, 176)}),
}
TAB_CENTRES = {"L": 20, "R": 60}  # centre of the vanilla tab labels (all languages)
AREA_LEFT = 1                     # vanilla area labels start 1 px into their box

# Drawn glyphs: 8 rows each (the sheet row), '.' = background.
ACCENTED_O = {
    "a": ["...", "...", "...", "B..", "CBC", "B.B", "B.B", "CBC"],   # accent dot right above
    "b": ["...", "...", ".B.", "...", "CBC", "B.B", "B.B", "CBC"],   # accent in the highlight row
    "c": ["...", "...", "B..", ".B.", "CBC", "B.B", "B.B", "CBC"],   # 2-px grave stroke
}
DRAWN_AREA = {
    "V": ["...", "3.4", "3.4", "3.4", "3.4", ".4.", "...", "..."],  # letters use rows 1-5
}


def load(lang, tmp):
    raw, png, pal = Path(tmp) / f"{lang}.4bpp", Path(tmp) / f"{lang}.png", Path(tmp) / "p.gbapal"
    pal.write_bytes((ROOT / "data/menus/pause_screen/3fcef0.pal").read_bytes()[6 * 32:7 * 32])
    subprocess.run([GBAGFX, ROOT / f"data/menus/pause_screen/menu_names_{lang}.gfx.lz", raw], check=True)
    subprocess.run([GBAGFX, raw, png, "-palette", pal, "-width", "32"], check=True)
    return Image.open(png)


def segments(im, x0, x1, rows, bg):
    ink = [any(im.getpixel((x, y)) != bg for y in rows) for x in range(x0, x1)]
    out, x = [], 0
    while x < len(ink):
        if ink[x]:
            s = x
            while x < len(ink) and ink[x]:
                x += 1
            out.append((x0 + s, x0 + x))
        else:
            x += 1
    return out


def harvest(images):
    """{(font, char): [column of 8 pixels]} and the letter/word gaps of each font."""
    glyphs, gaps = {}, {"tab": Counter(), "area": Counter()}
    for lang, im in images.items():
        jobs = [("tab", "L", TABS[lang][0]), ("tab", "R", TABS[lang][1]), ("area", "area", AREA[lang])]
        for font, label, text in jobs:
            if text is None:
                continue
            rows, bg, _, ranges = FONTS[font]
            segs = segments(im, *ranges[label], rows, bg)
            if len(segs) != len(text):
                sys.exit(f"error: {lang} {label}: {len(segs)} glyphs for {text!r}")
            for (s, e), ch in zip(segs, text):
                cols = [[im.getpixel((x, y)) if y in rows else bg for y in range(8)] for x in range(s, e)]
                glyphs.setdefault((font, ch), cols)
            for (_, e), (s, _) in zip(segs, segs[1:]):
                gaps[font][s - e] += 1
    for font, table in (("tab", {"Ò": None}), ("area", DRAWN_AREA)):
        for ch, rows in table.items():
            if rows is None:
                continue
            glyphs[(font, ch)] = drawn(rows, FONTS[font][1])
    letter = {f: min(c) for f, c in gaps.items()}
    word = {f: max(c) for f, c in gaps.items()}
    return glyphs, letter, word


def drawn(rows, bg):
    return [[int(r[x], 16) if r[x] != "." else bg for r in rows] for x in range(len(rows[0]))]


def set_text(glyphs, font, text, letter, word):
    cols, pending = [], False
    for ch in text:
        if ch == " ":
            pending = True
            continue
        g = glyphs.get((font, ch))
        if g is None:
            sys.exit(f"error: no {font} glyph for {ch!r}")
        if cols:
            cols += [None] * (word[font] if pending else letter[font])
        pending = False
        cols += g
    return cols


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--accent", choices=sorted(ACCENTED_O), default="c")
    a = ap.parse_args()
    with tempfile.TemporaryDirectory() as tmp:
        images = {lang: load(lang, tmp) for lang in TABS}
    glyphs, letter, word = harvest(images)
    glyphs[("tab", "Ò")] = drawn(ACCENTED_O[a.accent], FONTS["tab"][1])

    img = images["spanish"].copy()
    # Erase the Spanish text (tab ink in rows 3-7; label ink in rows 0-5), keep the frames
    for font, (rows, bg, ink, ranges) in FONTS.items():
        for x0, x1 in ranges.values():
            for x in range(x0, x1):
                for y in rows:
                    if img.getpixel((x, y)) in ink:
                        img.putpixel((x, y), bg)
        # the tab highlight row (2) may carry an accent: restore it from the frame first
    placements = {}
    for label, (x0, x1) in FONTS["tab"][3].items():
        cols = set_text(glyphs, "tab", CATALAN[label], letter, word)
        left = round(TAB_CENTRES[label] - len(cols) / 2)
        placements[label] = (left, cols)
    for label, (x0, x1) in FONTS["area"][3].items():
        cols = set_text(glyphs, "area", CATALAN["area"], letter, word)
        if len(cols) > x1 - x0 - AREA_LEFT:
            sys.exit(f"error: {CATALAN['area']!r} is {len(cols)} px, the box has {x1 - x0 - AREA_LEFT}")
        placements[label] = (x0 + AREA_LEFT, cols)
    for label, (left, cols) in placements.items():
        font = "tab" if label in ("L", "R") else "area"
        bg = FONTS[font][1]
        for dx, col in enumerate(cols):
            if col is None:
                continue
            for y, v in enumerate(col):
                if v != bg and (font == "tab" and y >= 2 or font == "area" and y <= 5):
                    img.putpixel((left + dx, y), v)
    img.save(a.out)
    for label, (left, cols) in placements.items():
        print(f"{label:5} {CATALAN['area' if label.startswith('area') else label]!r}: x={left}..{left + len(cols)}")


if __name__ == "__main__":
    main()
