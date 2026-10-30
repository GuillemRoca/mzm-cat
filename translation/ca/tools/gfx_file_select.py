#!/usr/bin/env python3
"""Composes the Catalan file select graphics from the glyphs of the five vanilla EU sheets.

  gfx_file_select.py OUT_DIR   (needs data/ extracted and build/gbagfx)

Three assets under menus/file_select/, each a sheet of labels in fixed tile slots (placed by
menu.tt and options.tt; slots below as (band, first column, last column + 1)):
  large_text       16-px font, a colour per label: the screen title (centred), OPCIONS,
                   COPIA, ESBORRA (outline 5-8, fill in the label's colours).
  options_text     the options list, 16-px font (fill 4, outline 1).
  difficulty_text  8-px font (fill 1, outline 6) under each file: FÀCIL, NORMAL, DIFÍCIL and
                   C.RELLOTGE for TIMEATTACK (its narrow letters; R, L, O, G and the full stop
                   drawn in DRAWN, as CONTRARELLOTGE can't fit 40 px).
Letters are cut where two columns without fill meet (outlines touch in all three fonts).
Glyphs are cut from the labels of all five languages (texts in VANILLA), the Spanish sheet is
the base, and each Catalan label replaces its slot, aligned like the vanilla labels. Letters
no sheet has are made from others: the title's L is drawn from the title E (DRAWN), and È and
À take the É and Á accents mirrored.
Writes OUT_DIR/<asset>_spanish.png.
"""
import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
GBAGFX = ROOT / "translation" / "ca" / "build" / "gbagfx"
LANGS = ["english", "german", "french", "italian", "spanish"]

# asset: palette row, band height, rows of the letter body (relative to the band, used to cut
# letters), the indices that aren't fill (background and outline), slots
ASSETS = {
    "large_text": dict(row=0, band=16, body=range(3, 14), outline={0, 5, 6, 7, 8}, slots={
        "title": (0, 0, 160), "options": (0, 160, 256), "copy": (1, 0, 80), "erase": (1, 80, 168)}),
    "options_text": dict(row=0, band=16, body=range(4, 13), outline={0, 1}, slots={
        "sound": (0, 0, 40), "sound_test": (0, 40, 128), "ta_records": (0, 128, 256),
        "gallery": (1, 0, 128), "fusion_link": (1, 128, 256),
        "fusion_gallery": (2, 0, 128), "original": (2, 128, 256)}),
    "difficulty_text": dict(row=5, band=8, body=range(2, 8), outline={0, 6}, slots={
        "easy": (0, 0, 40), "normal": (0, 40, 80), "hard": (0, 80, 120), "time_attack": (0, 120, 160)}),
}
VANILLA = {
    "large_text": {
        "title": ["SAMUS DATA", "SAMUS' DATEN", "DONNEES DE SAMUS", "DATI DI SAMUS", "DATOS DE SAMUS"],
        "options": ["OPTIONS", "OPTIONEN", "OPTIONS", "OPZIONI", "OPCIONES"],
        "copy": ["COPY", "KOPIEREN", "COPIER", "COPIA", "COPIAR"],
        "erase": ["ERASE", "LÖSCHEN", "EFFACER", "CANCELLA", "BORRAR"]},
    "options_text": {
        "sound": ["SOUND", "SOUND", "SON", "SUONO", "SONIDO"],
        "sound_test": ["SOUND TEST", "SOUND TEST", "TEST SON", "TEST SUONO", "PRUEBA DE SONIDO"],
        "ta_records": ["TIME ATTACK RECORDS", "TIME ATTACK-REKORDE", "RECORDS CONTRE-LA-MONTRE",
                       "RECORD PROVA A TEMPO", "RÉCORDS DE RETO DE TIEMPO"],
        "gallery": ["GALLERY", "GALERIE", "GALERIE", "GALLERIA", "GALERÍA"],
        "fusion_link": ["METROID FUSION LINK", "METROID FUSION LINK", "METROID FUSION LINK",
                        "LINK CON METROID FUSION", "CONEXIÓN CON METROID FUSION"],
        "fusion_gallery": ["METROID FUSION GALLERY", "METROID FUSION-GALERIE", "GALERIE METROID FUSION",
                           "GALLERIA METROID FUSION", "GALERÍA DE METROID FUSION"],
        "original": ["ORIGINAL METROID", "ORIGINAL METROID", "JEU ORIGINAL METROID",
                     "METROID ORIGINALE", "METROID ORIGINAL"]},
    "difficulty_text": {
        "easy": ["EASY", "LEICHT", "FACILE", "FACILE", "FÁCIL"],
        "normal": ["NORMAL", "NORMAL", "NORMAL", "NORMALE", "NORMAL"],
        "hard": ["HARD", "SCHWER", "DIFFICILE", "DIFFICILE", "DIFÍCIL"],
        "time_attack": ["TIMEATTACK"] * 5},
}
CATALAN = {
    "large_text": {"title": "DADES DE LA SAMUS", "options": "OPCIONS", "copy": "COPIA", "erase": "ESBORRA"},
    "options_text": {"sound": "SO", "sound_test": "PROVA DE SO", "ta_records": "RÈCORDS CONTRARELLOTGE",
                     "gallery": "GALERIA", "fusion_link": "CONNEXIÓ A METROID FUSION",
                     "fusion_gallery": "GALERIA DE METROID FUSION"},   # METROID ORIGINAL as in Spanish
    "difficulty_text": {"easy": "FÀCIL", "time_attack": "C.RELLOTGE"},  # NORMAL, DIFÍCIL as in Spanish
}
# Glyphs made from others: (asset, char) -> (source char, how)
DERIVED = {("options_text", "È"): ("É", "mirror accent"), ("difficulty_text", "À"): ("Á", "mirror accent")}
# Drawn glyphs: {(asset, char): rows of the band, '.' = background}. The title font is two
# rows taller than the other large labels and shaded row by row, so its L (no title has one)
# is the title E without its top and middle bars.
DRAWN = {
    ("large_text", "L"): [
        "5667.....",
        "6448.....",
        "6338.....",
        "6338.....",
        "6228.....",
        "6228.....",
        "6118.....",
        "6228.....",
        "6228.....",
        "6338.....",
        "633766667",
        "644444448",
        "788888888",
        ".........",
        ".........",
        "........."],
    # TIMEATTACK's narrow letters (fill 1 on outline 6, 2-3 columns wide): the ones
    # C.RELLOTGE needs and it doesn't have
    ("difficulty_text", "R"): [".....", "66666", "61166", "61616", "61166", "61616", "61616", "66666"],
    ("difficulty_text", "L"): ["....", "6666", "6166", "6166", "6166", "6166", "6116", "6666"],
    ("difficulty_text", "O"): [".....", "66666", "61116", "61616", "61616", "61616", "61116", "66666"],
    ("difficulty_text", "G"): [".....", "66666", "61116", "61666", "61616", "61616", "61116", "66666"],
    ("difficulty_text", "."): ["...", "...", "...", "...", "...", "666", "616", "666"],
}


def load(asset, lang, tmp):
    """The vanilla sheet of an asset, by default data/menus/file_select/<asset>_<lang>.gfx.lz
    with palette.pal (other tools reuse this module with "dir", "name" and "palette")."""
    a = ASSETS[asset]
    d = a.get("dir", "menus/file_select")
    raw, png, pal = (Path(tmp) / f"{asset}_{lang}.{e}" for e in ("4bpp", "png", "gbapal"))
    pal.write_bytes((ROOT / "data" / d / a.get("palette", "palette.pal")).read_bytes()[a["row"] * 32:(a["row"] + 1) * 32])
    subprocess.run([GBAGFX, ROOT / f"data/{d}/{a.get('name', asset)}_{lang}.gfx.lz", raw], check=True)
    subprocess.run([GBAGFX, raw, png, "-palette", pal, "-width", "32"], check=True)
    im = Image.open(png)
    im.load()
    return im


def letters(im, asset, slot):
    """Column spans of the letters in a slot, outline and accents included: the connected
    shapes of fill pixels, merged when they overlap in x (accents), widened by the outline
    column on each side. In the options and difficulty fonts neighbours share that column, so
    their spans overlap by one."""
    a = ASSETS[asset]
    band, x0, x1 = a["slots"][slot]
    top = band * a["band"]
    def px(x, y):
        return im.getpixel((x, top + y)) if 0 <= x < im.width else a.get("bg", 0)
    fill = {(x, y) for x in range(x0, x1) for y in range(a["band"]) if px(x, y) not in a["outline"]}
    shapes = []
    while fill:
        stack, xs = [fill.pop()], []
        while stack:
            cx, cy = stack.pop()
            xs.append(cx)
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    q = (cx + dx, cy + dy)
                    if q in fill:
                        fill.remove(q)
                        stack.append(q)
        shapes.append([min(xs), max(xs) + 1])
    shapes.sort()
    merged = []
    for s, e in shapes:
        if merged and s < merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], e)
        else:
            merged.append([s, e])
    def ink(x):
        return any(px(x, y) != a.get("bg", 0) for y in range(a["band"]))
    return [[s - 1 if ink(s - 1) else s, e + 1 if ink(e) else e] for s, e in merged]


def cut(im, asset, slot, span):
    a = ASSETS[asset]
    top = ASSETS[asset]["slots"][slot][0] * a["band"]
    return [{y: im.getpixel((x, top + y)) for y in range(a["band"]) if im.getpixel((x, top + y)) != a.get("bg", 0)}
            for x in range(*span)]


def harvest(images, asset):
    """{(slot, char): glyph}, {slot: (letter gap, word gap)}."""
    glyphs, spacing = {}, {}
    for slot, texts in VANILLA[asset].items():
        lg, wg = [], []
        # the Spanish sheet first: its letters are the ones the rest of each label keeps
        for lang, text in sorted(zip(LANGS, texts), key=lambda lt: lt[0] != "spanish"):
            spans = letters(images[lang], asset, slot)
            chars = text.replace(" ", "")
            if len(spans) != len(chars):
                sys.exit(f"error: {asset} {lang} {slot}: {len(spans)} letters for {text!r}")
            k = 0
            for w in text.split(" "):
                lg += [spans[k + i + 1][0] - spans[k + i][1] for i in range(len(w) - 1)]
                k += len(w)
                if k < len(spans):
                    wg.append(spans[k][0] - spans[k - 1][1])
            for span, ch in zip(spans, chars):
                glyphs.setdefault((slot, ch), cut(images[lang], asset, slot, span))
        spacing[slot] = (min(lg), min(wg) if wg else None)
    return glyphs, spacing


def mirror_accent(glyph, body_top):
    rows_above = {y for col in glyph for y in col if y < body_top}
    out = [dict((y, v) for y, v in col.items() if y >= body_top) for col in glyph]
    for x, col in enumerate(glyph):
        for y, v in col.items():
            if y in rows_above:
                out[len(glyph) - 1 - x][y] = v
    return out


def recolour(glyph, src_slot, dst_slot, glyphs):
    """Recolour a glyph from one label's colours to another's, row by row, from the letters
    both labels have."""
    table = {}
    for (slot, ch), g in glyphs.items():
        if slot == src_slot and (dst_slot, ch) in glyphs and len(glyphs[(dst_slot, ch)]) == len(g):
            for c_src, c_dst in zip(g, glyphs[(dst_slot, ch)]):
                for y, v in c_src.items():
                    if y in c_dst:
                        table.setdefault((y, v), c_dst[y])
    return [{y: table.get((y, v), v) for y, v in col.items()} for col in glyph]


def glyph_for(asset, slot, ch, glyphs):
    if (slot, ch) in glyphs:
        return glyphs[(slot, ch)]
    if (asset, ch) in DRAWN:
        rows = DRAWN[(asset, ch)]
        return [{y: int(r[x], 16) for y, r in enumerate(rows) if r[x] != "."} for x in range(len(rows[0]))]
    if (asset, ch) in DERIVED:
        src, _ = DERIVED[(asset, ch)]
        g = next((g for (s, c), g in glyphs.items() if c == src), None)
        if g is not None:
            return mirror_accent(g, ASSETS[asset]["body"][0])
    # another label of the same font, recoloured to this label's colours
    for (s, c), g in glyphs.items():
        if c == ch:
            return recolour(g, s, slot, glyphs)
    sys.exit(f"error: no {asset} glyph for {ch!r}")


def compose(asset, images, glyphs, spacing):
    a = ASSETS[asset]
    img = images["spanish"].copy()
    for slot, text in CATALAN[asset].items():
        band, x0, x1 = a["slots"][slot]
        top = band * a["band"]
        lg, wg = spacing[slot]
        if wg is None:
            wg = max((w for _, w in spacing.values() if w is not None), default=0)
        cols = []
        def put(glyph, gap):
            start = len(cols) + gap
            for k, col in enumerate(glyph):
                if start + k < len(cols):
                    cols[start + k] = {**cols[start + k], **col}   # shared outline column
                else:
                    cols.extend([{}] * (start + k - len(cols)))
                    cols.append(dict(col))
        for i, word in enumerate(text.split(" ")):
            for j, ch in enumerate(word):
                put(glyph_for(asset, slot, ch, glyphs), wg if i and not j else lg if j else 0)
        if len(cols) > x1 - x0:
            sys.exit(f"error: {asset} {slot} {text!r} is {len(cols)} px, the slot has {x1 - x0}")
        spans = letters(images["spanish"], asset, slot)
        if asset == "large_text" and slot == "title":
            # centred like every language's title
            left = round((x0 + x1) / 2 - len(cols) / 2)
        elif "left" in a:
            left = a["left"]                           # one margin for all the lines
        else:
            left = spans[0][0]                         # where the Spanish label starts
            left = min(left, x1 - len(cols))
        for x in range(x0, x1):
            for y in range(a["band"]):
                img.putpixel((x, top + y), a.get("bg", 0))
        for dx, col in enumerate(cols):
            for y, v in col.items():
                img.putpixel((left + dx, top + y), v)
        print(f"{asset:15} {slot:14} {text!r}: x={left}..{left + len(cols) - 1} in {x0}..{x1 - 1}")
    return img


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out_dir")
    a = ap.parse_args()
    out = Path(a.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    for asset in ASSETS:
        with tempfile.TemporaryDirectory() as tmp:
            images = {lang: load(asset, lang, tmp) for lang in LANGS}
        glyphs, spacing = harvest(images, asset)
        compose(asset, images, glyphs, spacing).save(out / f"{asset}_spanish.png")


if __name__ == "__main__":
    main()
