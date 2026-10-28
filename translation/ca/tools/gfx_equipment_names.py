#!/usr/bin/env python3
"""Composes the Catalan status-screen equipment names from the glyphs of the vanilla EU sheets.

  gfx_equipment_names.py OUT.png   (needs data/ extracted and build/gbagfx)

menus/pause_screen/equipment_names_*.gfx.lz is a sheet of 160 tiles. Each name has a fixed run
of tiles, the same in every language (src/data/menus/pause_screen: status_screen.tt and
status_screen_background.tt place them), listed in HEADINGS and ITEMS as (first tile, tiles).
Two fonts:
  headings  dark outlined letters on the green bars (ink 1/4/5/7 on 8, rows 2-6; the ENERGY
            bar is one row lower). Letters touch, so glyphs are cut by hand in HEADING_GLYPHS
            from known vanilla headings.
  items     white-blue letters on the blue bars (ink 6 on C/D, rows 2-6, accents on row 1),
            a background column between letters, so glyphs are cut automatically from the
            vanilla item names in ITEM_TEXT.
The Spanish sheet is the base. Names that stay as in Spanish are left untouched; the others are
erased and set left-aligned at column 0, as in vanilla, and must leave the bar's last column
(its end) free. The unknown-item placeholders are not touched.
"""
import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
GBAGFX = ROOT / "translation" / "ca" / "build" / "gbagfx"
LANGS = ["english", "spanish", "italian"]

HEADINGS = {"energy": (0x00, 6), "beam": (0x06, 5), "missile": (0x0B, 6), "bomb": (0x11, 5),
            "suit": (0x16, 6), "misc": (0x1C, 6), "gun": (0x22, 5)}
ITEMS = {"long": (0x36, 5), "charge": (0x3B, 5), "ice": (0x40, 5), "wave": (0x45, 5),
         "plasma": (0x4A, 5), "missile_normal": (0x4F, 5), "super": (0x54, 5),
         "bomb_normal": (0x59, 5), "power": (0x60, 4), "varia": (0x64, 5), "gravity": (0x69, 7),
         "morph": (0x70, 7), "grip": (0x77, 7), "speed": (0x80, 7), "hijump": (0x87, 6),
         "screw": (0x8D, 7), "space": (0x94, 7), "pistol": (0x9B, 5)}

# Vanilla item names, to cut glyphs from
ITEM_TEXT = {
    "english": {"long": "LONG", "charge": "CHARGE", "ice": "ICE", "wave": "WAVE", "plasma": "PLASMA",
                "missile_normal": "NORMAL", "super": "SUPER", "power": "POWER", "varia": "VARIA",
                "gravity": "GRAVITY", "morph": "MORPH BALL", "grip": "POWER GRIP",
                "speed": "SPEED BOOSTER", "hijump": "HI-JUMP", "screw": "SCREW ATTACK",
                "space": "SPACE JUMP", "pistol": "PISTOL"},
    "spanish": {"long": "LARGO", "charge": "RECARGA", "ice": "HIELO", "wave": "ONDAS",
                "super": "SÚPER", "power": "ENERGÍA", "varia": "CLIMÁTICO",
                "gravity": "GRAVITATORIO", "morph": "MORFOSFERA", "grip": "AGARRE",
                "speed": "ACELERACIÓN", "hijump": "SUPERSALTO", "space": "SALTO ESPACIAL"},
    "italian": {"gravity": "GRAVITÀ"},
}

CATALAN_HEADINGS = {"energy": "ENERGIA", "beam": "RAIG", "missile": "MÍSSIL", "suit": "VESTIT",
                    "misc": "ALTRES", "gun": "ARMA"}       # BOMBA as in Spanish
CATALAN_ITEMS = {"long": "LLARG", "charge": "CÀRREGA", "ice": "GEL", "wave": "ONES",
                 "power": "ENERGIA", "varia": "CLIMÀTIC", "gravity": "GRAVITATORI",
                 "grip": "ARRAPADA", "speed": "ACCELERACIÓ", "hijump": "SUPERSALT",
                 "screw": "ATAC ESPIRAL", "space": "SALT ESPACIAL", "pistol": "PISTOLA"}
# PLASMA, NORMAL (x2), SÚPER, MORFOSFERA as in Spanish

# What each bar says on screen in English and Spanish (for translations.csv), in order
SHOWN = {
    "energy": ("ENERGY", "ENERGÍA"), "beam": ("BEAM", "RAYO"), "long": ("LONG", "LARGO"),
    "charge": ("CHARGE", "RECARGA"), "ice": ("ICE", "HIELO"), "wave": ("WAVE", "ONDAS"),
    "plasma": ("PLASMA", "PLASMA"), "missile": ("MISSILE", "MISIL"),
    "missile_normal": ("NORMAL", "NORMAL"), "super": ("SUPER", "SÚPER"), "bomb": ("BOMB", "BOMBA"),
    "bomb_normal": ("NORMAL", "NORMAL"), "power": ("POWER", "ENERGÍA"), "suit": ("SUIT", "TRAJE"),
    "varia": ("VARIA", "CLIMÁTICO"), "gravity": ("GRAVITY", "GRAVITATORIO"),
    "misc": ("MISC.", "OTROS"), "morph": ("MORPH BALL", "MORFOSFERA"),
    "grip": ("POWER GRIP", "AGARRE"), "speed": ("SPEED BOOSTER", "ACELERACIÓN"),
    "hijump": ("HI-JUMP", "SUPERSALTO"), "screw": ("SCREW ATTACK", "S. EN BARRENA"),
    "space": ("SPACE JUMP", "SALTO ESPACIAL"), "gun": ("GUN", "PISTOLA"), "pistol": ("PISTOL", "LÁSER"),
}


def catalan(key):
    """What the Catalan bar says: our text, or the Spanish where it is kept."""
    return CATALAN_HEADINGS.get(key) or CATALAN_ITEMS.get(key) or SHOWN[key][1]


# Heading glyphs: (language, heading, first column, width) of a vanilla heading. Rows 2-6 of
# the bar (ENERGY: 3-7). "Í" is the Spanish ENERGÍA one: accent on the row above a short I.
HEADING_GLYPHS = {
    "R": ("italian", "beam", 0, 7), "A": ("italian", "beam", 7, 7), "G": ("italian", "beam", 14, 7),
    "I": ("english", "missile", 9, 3), "M": ("english", "missile", 0, 9),
    "S": ("english", "missile", 12, 7), "L": ("english", "missile", 29, 7),
    "E": ("english", "beam", 7, 7), "V": ("italian", "misc", 0, 7), "T": ("italian", "suit", 0, 7),
    "Í": ("spanish", "energy", 37, 3),
}

HEAD_BG, ITEM_BG = 8, {1: 0xE, 2: 0xC, 3: 0xD, 4: 0xD, 5: 0xD, 6: 0xD}


def load(lang, tmp):
    raw, png, pal = Path(tmp) / f"{lang}.4bpp", Path(tmp) / f"{lang}.png", Path(tmp) / "p.gbapal"
    pal.write_bytes((ROOT / "data/menus/pause_screen/3fcef0.pal").read_bytes()[6 * 32:7 * 32])
    subprocess.run([GBAGFX, ROOT / f"data/menus/pause_screen/equipment_names_{lang}.gfx.lz", raw], check=True)
    subprocess.run([GBAGFX, raw, png, "-palette", pal, "-width", "32"], check=True)
    im = Image.open(png)
    im.load()
    return im


class Slot:
    """A name's run of tiles, addressed as one strip of 8 * tiles columns."""
    def __init__(self, im, first, tiles):
        self.im, self.first, self.w = im, first, tiles * 8

    def xy(self, x, y):
        t = self.first + x // 8
        return (t % 32) * 8 + x % 8, (t // 32) * 8 + y

    def get(self, x, y):
        return self.im.getpixel(self.xy(x, y))

    def put(self, x, y, v):
        self.im.putpixel(self.xy(x, y), v)


def item_glyphs(images):
    """{char: [{row: value}]} cut from the vanilla item names, the word gap and the letter
    pairs that vanilla sets with no gap (kerned, like LT). Letters are
    the connected ink shapes of rows 2-6 (some pairs, like LT, touch columns without a gap);
    an accent (ink on row 1, anti-alias 7 on row 2) goes with the letter below it."""
    glyphs, gaps, kerned = {}, [], set()
    for lang, names in ITEM_TEXT.items():
        for key, text in names.items():
            s = Slot(images[lang], *ITEMS[key])
            ink = {(x, y) for x in range(s.w - 1) for y in range(2, 7) if s.get(x, y) == 6}
            spans = []
            while ink:
                stack, comp = [ink.pop()], set()
                while stack:
                    p = stack.pop()
                    comp.add(p)
                    for dx in (-1, 0, 1):
                        for dy in (-1, 0, 1):
                            q = (p[0] + dx, p[1] + dy)
                            if q in ink:
                                ink.remove(q)
                                stack.append(q)
                spans.append([min(x for x, _ in comp), max(x for x, _ in comp)])
            spans.sort()
            merged = []
            for a, b in spans:                          # parts of one letter overlap in x
                if merged and a <= merged[-1][1]:
                    merged[-1][1] = max(merged[-1][1], b)
                else:
                    merged.append([a, b])
            letters = text.replace(" ", "")
            if len(merged) != len(letters):
                sys.exit(f"error: {lang} {key}: {len(merged)} glyphs for {text!r}")
            k = 0
            for w in text.split(" ")[:-1]:
                k += len(w)
                gaps.append(merged[k][0] - merged[k - 1][1] - 1)
            k = 0
            for w in text.split(" "):
                for i in range(len(w) - 1):
                    if merged[k + i + 1][0] - merged[k + i][1] - 1 == 0:
                        kerned.add(w[i:i + 2])
                k += len(w)
            accents = [x for x in range(s.w - 1) if s.get(x, 1) == 6 or s.get(x, 2) == 7]
            for (a, b), ch in zip(merged, letters):
                xs = [x for x in accents if a - 1 <= x <= b + 1]
                lo, hi = min([a] + xs), max([b] + xs)
                cols = []
                for x in range(lo, hi + 1):
                    col = {y: 6 for y in range(2, 7) if a <= x <= b and s.get(x, y) == 6}
                    if x in xs:
                        col.update({y: s.get(x, y) for y in (1, 2) if s.get(x, y) in (6, 7)})
                    cols.append(col)
                glyphs.setdefault(ch, cols)
    return glyphs, max(gaps), kerned


def heading_glyphs(images):
    glyphs = {}
    for ch, (lang, key, x0, w) in HEADING_GLYPHS.items():
        s = Slot(images[lang], *HEADINGS[key])
        dy = 1 if key == "energy" else 0             # ENERGY's letters sit one row lower
        top = 1 if ch == "Í" else 2
        glyphs[ch] = [{y - dy: s.get(x, y) for y in range(top + dy, 7 + dy) if s.get(x, y) != HEAD_BG}
                      for x in range(x0, x0 + w)]
    return glyphs


def set_items(img, glyphs, gap, kerned):
    for key, text in CATALAN_ITEMS.items():
        s = Slot(img, *ITEMS[key])
        cols = []
        for i, word in enumerate(text.split(" ")):
            if i:
                cols += [{}] * gap
            for j, ch in enumerate(word):
                if ch not in glyphs:
                    sys.exit(f"error: no item glyph for {ch!r}")
                if j and word[j - 1:j + 1] not in kerned:
                    cols.append({})                    # one background column between letters
                cols += glyphs[ch]
        if len(cols) > s.w - 1:                         # up to the column before the bar's end
            sys.exit(f"error: {text!r} is {len(cols)} px, the {key} bar fits {s.w - 1}")
        for x in range(s.w - 1):                        # erase, keep the bar's end column
            for y, bg in ITEM_BG.items():
                s.put(x, y, bg)
        for x, col in enumerate(cols):
            for y, v in col.items():
                s.put(x, y, v)
        print(f"item    {key:15} {text!r}: {len(cols)}/{s.w - 1} px")


def set_headings(img, images, glyphs):
    for key, text in CATALAN_HEADINGS.items():
        s = Slot(img, *HEADINGS[key])
        if key == "energy":                             # the Italian bar already says ENERGIA
            src = Slot(images["italian"], *HEADINGS[key])
            for x in range(s.w):
                for y in range(8):
                    s.put(x, y, src.get(x, y))
            print(f"heading {key:15} {text!r}: the Italian bar")
            continue
        cols = []
        for ch in text:
            if ch not in glyphs:
                sys.exit(f"error: no heading glyph for {ch!r}")
            cols += glyphs[ch]
        if len(cols) > s.w - 2:
            sys.exit(f"error: {text!r} is {len(cols)} px, the {key} bar fits {s.w - 2}")
        for x in range(s.w):
            for y in range(2, 7):
                s.put(x, y, HEAD_BG)
        for x, col in enumerate(cols):
            for y, v in col.items():
                s.put(x, y, v)
        print(f"heading {key:15} {text!r}: {len(cols)}/{s.w - 2} px")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    a = ap.parse_args()
    with tempfile.TemporaryDirectory() as tmp:
        images = {lang: load(lang, tmp) for lang in LANGS}
    ig, gap, kerned = item_glyphs(images)
    hg = heading_glyphs(images)
    img = images["spanish"].copy()
    set_headings(img, images, hg)
    set_items(img, ig, gap, kerned)
    img.save(a.out)


if __name__ == "__main__":
    main()
