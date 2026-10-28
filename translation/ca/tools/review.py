#!/usr/bin/env python3
"""Writes translation/ca/translations.csv: every game string in English, Spanish and Catalan,
side by side, to compare during a playthrough.

  review.py            regenerate the CSV
  review.py --check    fail if the CSV is out of date (CI)

One row per text ID (all five categories of src/data/text_data.c, in pointer-table order), then
the strings drawn in graphics, and the Catalan credit. Control codes are dropped and button glyphs
shown as [A], [L], …; line breaks stay line breaks inside the cell. Columns: section, id,
where (on screen), english, spanish, catalan, status (translated / same as English /
untranslated), notes. The notes column is yours: regenerating keeps it, matched by section
and id.
"""
import argparse
import csv
import io
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import catext  # noqa: E402
import gencredits  # noqa: E402
import gfx_game_over  # noqa: E402
import gfx_menu_names  # noqa: E402

OUT = catext.CA / "translations.csv"
FIELDS = ["section", "id", "where", "english", "spanish", "catalan", "status", "notes"]
WHERE = {
    "message": "Message banner",
    "location": "Area / room banner",
    "description": "Pause screen, equipment description",
    "story": "Story text (intro, escapes, ending)",
    "file_screen": "File select",
}
BUTTONS = {"A_button": "[A]", "B_button": "[B]", "L_button": "[L]", "R_button": "[R]",
           "Select_button": "[SELECT]", "Start_button": "[START]", "Up_button": "[UP]",
           "Down_button": "[DOWN]", "Left_button": "[LEFT]", "Right_button": "[RIGHT]",
           "hundred_percent": "100%"}


def plain(text):
    """Game text without layout codes, as a reader sees it."""
    out = []
    for line in re.split(r"\\n", text.replace("{NEW_PAGE}", "\\n\\n")):
        line = re.sub(r"^(\{(GAP|INDENT|COLOR)\(\d+\)\})+", "", line)      # leading layout
        line = re.sub(r"\{(GAP|INDENT)\(\d+\)\}", "  ", line)              # gaps inside a line
        line = re.sub(r"\{(COLOR|DELAY)\(\d+\)\}", "", line)
        line = re.sub(r"\{(\w+)\}", lambda m: BUTTONS.get(m.group(1), ""), line)
        line = re.sub(r"\\(.)", r"\1", line)
        out.append(line.replace("？", "?").replace("！", "!").rstrip())
    return "\n".join(out).strip("\n")


def text_rows():
    strings, tables = catext.vanilla_text()
    same = catext.identical_ids()
    rows = []
    for category in catext.CATEGORIES:
        catalan, _ = catext.read_translation(category)
        english = dict(catext.table(tables, "English", category))
        spanish = dict(catext.table(tables, "Spanish", category))
        for idx, _sym in catext.table(tables, "English", category):
            en = plain(strings[english[idx]])
            ca = plain(catalan[idx][0]) if idx in catalan else ""
            if idx in catalan:
                status = "same as English" if ca == en and idx in same else "translated"
            else:
                status = "same as English" if idx in same else "untranslated"
            rows.append({"section": category, "id": idx, "where": WHERE[category], "english": en,
                         "spanish": plain(strings[spanish[idx]]) if idx in spanish else "",
                         "catalan": ca, "status": status})
    return rows


def graphic_rows():
    """Strings drawn in graphics (vanilla English and Spanish as on screen), and the credits."""
    menu = gfx_menu_names.CATALAN
    heading, names = gencredits.read_credits()
    g = [  # id, where, english, spanish, catalan, the PNG that draws it
        ("language_select", "Language selector, 5th entry", "(Spanish slot)", "Español", "Català",
         "menus/language_select/background"),
        ("game_over_prompt", "Game over screen", "TRY AGAIN?\nYES (RETURN TO GAME)\nNO (TO TITLE SCREEN)",
         "¿VOLVER A INTENTARLO?\nSÍ (CONTINUAR)\nNO (SALIR)", "\n".join(gfx_game_over.CATALAN),
         "menus/game_over/text_prompt_spanish"),
        ("pause_tab_l", "Pause screen, L tab (Easy Sleep)", "SLEEP", "SALVAP.", menu["L"],
         "menus/pause_screen/menu_names_spanish"),
        ("pause_tab_r", "Pause screen, R tab (status)", "STATUS", "ESTADO", menu["R"],
         "menus/pause_screen/menu_names_spanish"),
        ("pause_change_area", "Pause screen, map: change area", "CHANGE AREAS", "CAMBIAR ZONA", menu["area"],
         "menus/pause_screen/menu_names_spanish"),
    ]
    rows = [{"section": "graphics", "id": id_, "where": where, "english": en, "spanish": es, "catalan": ca,
             "status": "translated" if (catext.CA / "gfx" / f"{key}.png").exists() else "untranslated"}
            for id_, where, en, es, ca, key in g]
    rows.append({"section": "credits", "id": "translation", "where": "Staff credits, TRANSLATION section",
                 "english": "", "spanish": "", "catalan": "\n".join([heading] + names), "status": "translated"})
    return rows


def render(old_notes):
    buf = io.StringIO()
    w = csv.DictWriter(buf, FIELDS, lineterminator="\n")
    w.writeheader()
    for r in text_rows() + graphic_rows():
        r["notes"] = old_notes.get((r["section"], r["id"]), "")
        w.writerow(r)
    return buf.getvalue()


def read_notes(path=OUT):
    if not path.exists():
        return {}
    with path.open(encoding="utf-8", newline="") as f:
        return {(r["section"], r["id"]): r.get("notes", "") for r in csv.DictReader(f) if r.get("notes")}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    new = render(read_notes())
    old = OUT.read_text(encoding="utf-8") if OUT.exists() else ""
    if a.check:
        if new != old:
            sys.exit(f"error: {OUT.relative_to(catext.ROOT)} is out of date: run translation/ca/tools/review.py")
        print(f"{OUT.relative_to(catext.ROOT)} is up to date")
        return
    OUT.write_text(new, encoding="utf-8")
    print(f"wrote {OUT.relative_to(catext.ROOT)}")


if __name__ == "__main__":
    main()
