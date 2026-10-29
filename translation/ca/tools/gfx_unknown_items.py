#!/usr/bin/env python3
"""Composes the Catalan names of the three unknown items, as revealed on the status screen.

  gfx_unknown_items.py OUT.png   (needs data/ extracted and build/gbagfx)

menus/pause_screen/map_screen_unknown_items_names_*.gfx.lz is one 8-px row: an icon, then the
three names between divider columns (6), drawn as sprites over the placeholder bars of the
status screen while the fully powered suit reveals them. Same font as the status screen item
names: ink 3 on 5 (row 2: 4), rows 2-6. The Spanish names are cut into letters (connected ink
shapes, so touching pairs like LT come out apart) and reset as the Catalan names of the
equipment names graphic, left-aligned after the divider like vanilla, keeping the vanilla
kerning and word gap.
"""
import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
GBAGFX = ROOT / "translation" / "ca" / "build" / "gbagfx"

# name: (first text column, divider column after it, vanilla Spanish, vanilla English, Catalan).
# Dividers are at columns 6, 47, 103 and 159. PLASMA stays as in Spanish.
NAMES = {
    "plasma": (8, 47, "PLASMA", "PLASMA", None),
    "space_jump": (48, 103, "SALTOESPACIAL", "SPACE JUMP", "SALT ESPACIAL"),
    "gravity": (104, 159, "GRAVITATORIO", "GRAVITY", "GRAVITATORI"),
}
INK, BG = 3, {2: 4, 3: 5, 4: 5, 5: 5, 6: 5}


def load(lang, tmp):
    from PIL import Image
    raw, png, pal = Path(tmp) / f"{lang}.4bpp", Path(tmp) / f"{lang}.png", Path(tmp) / "p.gbapal"
    pal.write_bytes((ROOT / "data/menus/pause_screen/tank_icons.pal").read_bytes()[12 * 32:13 * 32])
    subprocess.run([GBAGFX, ROOT / f"data/menus/pause_screen/map_screen_unknown_items_names_{lang}.gfx.lz",
                    raw], check=True)
    subprocess.run([GBAGFX, raw, png, "-palette", pal, "-width", "32"], check=True)
    im = Image.open(png)
    im.load()
    return im


def letters(im, x0, x1):
    """Column spans of the letters between x0 and x1: connected ink shapes, merged when they
    overlap in x."""
    ink = {(x, y) for x in range(x0, x1) for y in range(2, 7) if im.getpixel((x, y)) == INK}
    spans = []
    while ink:
        stack, xs = [ink.pop()], []
        while stack:
            p = stack.pop()
            xs.append(p[0])
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    q = (p[0] + dx, p[1] + dy)
                    if q in ink:
                        ink.remove(q)
                        stack.append(q)
        spans.append([min(xs), max(xs)])
    spans.sort()
    merged = []
    for a, b in spans:
        if merged and a <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], b)
        else:
            merged.append([a, b])
    return merged


def harvest(images):
    glyphs, kerned, gaps = {}, set(), []
    for lang, idx in (("spanish", 2), ("english", 3)):
        im = images[lang]
        for x0, x1, *texts in NAMES.values():
            text = texts[idx - 2]
            spans = letters(im, x0, x1)
            chars = text.replace(" ", "")
            if len(spans) != len(chars):
                sys.exit(f"error: {lang}: {len(spans)} letters for {text!r}")
            k = 0
            for w in text.split(" "):
                for i in range(len(w) - 1):
                    if spans[k + i + 1][0] - spans[k + i][1] == 1:
                        kerned.add(w[i:i + 2])
                k += len(w)
                if k < len(spans):
                    gaps.append(spans[k][0] - spans[k - 1][1] - 1)
            for (a, b), ch in zip(spans, chars):
                glyphs.setdefault(ch, [{y: INK for y in range(2, 7) if im.getpixel((x, y)) == INK}
                                       for x in range(a, b + 1)])
    return glyphs, kerned, max(gaps)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    a = ap.parse_args()
    with tempfile.TemporaryDirectory() as tmp:
        images = {lang: load(lang, tmp) for lang in ("spanish", "english")}
    glyphs, kerned, gap = harvest(images)
    img = images["spanish"].copy()
    for key, (x0, x1, _, _, text) in NAMES.items():
        if text is None:
            continue
        cols = []
        for i, word in enumerate(text.split(" ")):
            if i:
                cols += [{}] * gap
            for j, ch in enumerate(word):
                if j and word[j - 1:j + 1] not in kerned:
                    cols.append({})
                cols += glyphs[ch]
        if len(cols) > x1 - x0:
            sys.exit(f"error: {text!r} is {len(cols)} px, the {key} name fits {x1 - x0}")
        for x in range(x0, x1):
            for y, bg in BG.items():
                img.putpixel((x, y), bg)
        for dx, col in enumerate(cols):
            for y, v in col.items():
                img.putpixel((x0 + dx, y), v)
        print(f"{key:11} {text!r}: {len(cols)}/{x1 - x0} px")
    img.save(a.out)


if __name__ == "__main__":
    main()
