#!/usr/bin/env python3
"""Composes the Catalan erase-save screens (A+B+Select at boot, then the confirmation).

  gfx_erase_sram.py OUT_DIR   (needs data/ extracted and build/gbagfx)

menus/erase_sram/question_* and confirm_* are two 16-px lines of a proportional font (fill 2,
outline 3, background F): the question on the left, the answers ("No" / "Sí", kept from the
Spanish) from x = 200. Uses the file select composer (gfx_file_select.py): letters are cut
from the five vanilla sheets by their fill shapes, and each Catalan line is set where the
Spanish line starts, with the vanilla spacing.
Writes OUT_DIR/question_spanish.png and OUT_DIR/confirm_spanish.png.
"""
import argparse
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gfx_file_select as fs  # noqa: E402

TEXT = (0, 196)          # the question; the answers start at x = 200
SCREEN = dict(dir="menus/erase_sram", palette="objects.pal", row=2, band=16, body=range(3, 14),
              bg=0xF, outline={0xF, 3}, slots={"line1": (0, *TEXT), "line2": (1, *TEXT)})

# the Spanish margins (its second question line starts a pixel right of the first's "¿")
LEFT = {"question": 8, "confirm": 0}
VANILLA = {
    "question": {
        "line1": ["Do you want to", "Alle gespeicherten", "Effacer toutes les", "Vuoi cancellare",
                  "¿Quieres borrar todos"],
        "line2": ["erase all saved data?", "Daten löschen?", "données sauvegardées?",
                  "tutti i dati salvati?", "los datos guardados?"]},
    "confirm": {
        "line1": ["Are you sure you want", "Wirklich alle gespeicher-", "Etes-vous sûr de",
                  "Saranno cancellati tutti", "¿Seguro que quieres"],
        "line2": ["to erase all saved data?", "ten Daten löschen?", "vouloir tout effacer?",
                  "i dati. Procedere?", "borrar todos los datos?"]},
}
CATALAN = {
    "question": {"line1": "Vols esborrar totes les", "line2": "dades guardades?"},
    "confirm": {"line1": "Segur que vols esborrar", "line2": "totes les dades?"},
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out_dir")
    a = ap.parse_args()
    out = Path(a.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    for name in VANILLA:
        fs.ASSETS[name] = dict(SCREEN, name=name, left=LEFT[name])
        fs.VANILLA[name] = VANILLA[name]
        fs.CATALAN[name] = CATALAN[name]
        with tempfile.TemporaryDirectory() as tmp:
            images = {lang: fs.load(name, lang, tmp) for lang in fs.LANGS}
        glyphs, spacing = fs.harvest(images, name)
        fs.compose(name, images, glyphs, spacing).save(out / f"{name}_spanish.png")


if __name__ == "__main__":
    main()
