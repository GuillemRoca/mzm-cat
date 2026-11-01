#!/usr/bin/env python3
"""Generates the Catalan typed text of the intro for LANG_CA=1:

  genintro.py OUT [--vanilla]    ca/intro_text.inc: sCaIntro<Part>TextOam, Actions and Cursor,
                                 and sCaIntroStartX/Y (--vanilla: nothing, for the self-test)

The intro types three texts letter by letter with sprites from intro/text_and_ship (shared by
every language): EMERGENCY ORDER, EXTERMINATE ALL METROID..., AND DEFEAT THE MECHANICAL...
Other languages show subtitles under the English. In the Spanish slot, translation/ca/include/
ca/intro.h makes src/intro.c type these Catalan texts instead, without subtitles, like English.

Each text is a frame of 8x16 sprites, one per cell, and a list of actions (one per typing step)
that reveals the cells. Every word sits in a box: a cell before it holds its left edge (LEAD),
a cell after it its right edge (TRAIL); a space between words is one cell with both edges, and
punctuation cells carry the right edge. The rules are checked by rebuilding the vanilla English
data from its text before anything is written.

A typing cursor follows the letters from a start the code sets, and the code's new-line step
sends it back to a fixed column. To centre every Catalan line, ca/intro.h places the cursor
itself: at the start of each text (sCaIntroStartX/Y), and on the frame each later line's first
step moves it (sCaIntro<Part>Cursor). Those lines start with an ordinary step, so the code
doesn't move the cursor back. The text block sits half a line higher per extra line, with its
middle where the English block's is.
"""
import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
INTRO_C = ROOT / "src" / "data" / "intro_data.c"

PARTS = ["EmergencyOrder", "ExterminateAll", "DefeatThe"]
ENGLISH = {
    "EmergencyOrder": ["EMERGENCY ORDER"],
    "ExterminateAll": ["EXTERMINATE ALL METROID", "ORGANISMS ON PLANET ZEBES..."],
    "DefeatThe": ["AND DEFEAT THE MECHANICAL", "LIFE-FORM, MOTHER BRAIN."],
}
# The approved story subtitles (text/story.txt), in capitals, broken to fit the screen
CATALAN = {
    "EmergencyOrder": ["ORDRE D'EMERGÈNCIA"],
    "ExterminateAll": ["EXTERMINAR TOTS ELS", "ORGANISMES METROIDES DEL", "PLANETA ZEBES..."],
    "DefeatThe": ["I DERROTAR LA FORMA", "DE VIDA MECÀNICA,", "MOTHER BRAIN."],
}

ALPHABET = "ABCDEFGHILMNOPRSTVXYZ"            # tiles 0x4 to 0x18
LETTERS = {c: 0x4 + i for i, c in enumerate(ALPHABET)}
# drawn by gfx_intro.py in cells no frame of the sheet uses
NEW = {"È": 0x5a, "À": 0x5b, "'": 0x5c}
LETTERS.update(NEW)
LEAD, TRAIL, SPACE = 0x3, 0x1c, 0x1d
COMMA, HYPHEN, PERIOD = 0x5d, 0x5e, 0x5f      # each with the right edge of its word
ELLIPSIS = [0x1e, 0x1f, 0x1f]                 # the first dot with the right edge
GAPS = {LEAD, SPACE}                          # a step after these is a SPACE action (no sound)
LINE_HEIGHT = 24                              # IntroProcessText's new line
SCREEN_HALF_W, SCREEN_H, OAM_Y = 120, 160, 128


def cells(line):
    out = [LEAD]
    i = 0
    while i < len(line):
        c = line[i]
        if c in LETTERS:
            out.append(LETTERS[c])
        elif c == " ":
            out.append(SPACE if line[i - 1] in LETTERS else LEAD)
        elif line.startswith("...", i):
            out += ELLIPSIS
            i += 2
        elif c in ",.-":
            out.append({",": COMMA, ".": PERIOD, "-": HYPHEN}[c])
        else:
            sys.exit(f"error: {c!r} in {line!r} has no intro glyph")
        i += 1
    if line[-1] in LETTERS:
        out.append(TRAIL)
    return out


def layout(lines, x_first, x_next, y_first, centre=False):
    """(frame entries [(x, y, tile)], actions, cursor). x and y are relative to the sprite origin
    (screen x 120, y 128). Without centre, the vanilla layout: lines start at x_first, then
    x_next. With centre, every line is centred, and each later line starts with a
    SKIP_CHARACTER (the same two cells as the code's NEW_LINE, without the move back to its
    column); cursor gives, for each action, 0 or where ca/intro.h puts the cursor (y << 8 | x on
    screen, the first letter's cell)."""
    entries, actions, cursor = [], ["START"], [0]
    for k, line in enumerate(lines):
        c = cells(line)
        last = k == len(lines) - 1
        x0 = -4 * len(c) if centre else x_first if k == 0 else x_next
        y = y_first + k * LINE_HEIGHT
        if x0 < -SCREEN_HALF_W or x0 + 8 * len(c) > SCREEN_HALF_W or OAM_Y + y + 16 > SCREEN_H:
            sys.exit(f"error: {line!r} doesn't fit the screen ({len(c)} cells from x = {x0})")
        entries += [(x0 + 8 * i, y, t) for i, t in enumerate(c)]
        if k:                                           # the line's LEAD and first letter
            actions.append("SKIP_CHARACTER" if centre else "NEW_LINE")
            cursor.append((OAM_Y + y + LINE_HEIGHT) << 8 | (SCREEN_HALF_W + x0 + 8) if centre else 0)
        # the line's last cell is revealed with the one before it when it closes the word box
        # (lines that go on; the vanilla last lines end on a lone SKIP)
        pair = not last or c[-1] == TRAIL
        singles = range(2, len(c) - 2 if pair else len(c) - 1)
        actions += ["SPACE" if c[j - 1] in GAPS else "NONE" for j in singles]
        actions.append("SKIP_CHARACTER")
        cursor += [0] * (len(singles) + 1)
    actions.append("COUNT")
    cursor.append(0)
    return entries, actions, cursor


def vanilla(src):
    """{part: (entries, actions, x_first, x_next, y_first)} of the vanilla data."""
    out = {}
    for part in PARTS:
        frame = re.search(rf"sIntro{part}TextOam\[.*?\n\}};", src, re.S).group(0)
        entries = [(int(x), int(y), int(t, 16)) for x, y, t in re.findall(
            r"OAM_ENTRY\((-?\d+), (-?\d+), OAM_DIMS_8x16, OAM_NO_FLIP, (0x[0-9a-f]+), 1, 0\)", frame)]
        acts = re.search(rf"sIntro{part}Actions\[.*?\n\}};", src, re.S).group(0)
        actions = re.findall(r"INTRO_TEXT_ACTION_(\w+)", acts)
        ys = sorted({y for _, y, _ in entries})
        x_next = min(x for x, y, _ in entries if y == ys[1]) if len(ys) > 1 else None
        out[part] = (entries, actions, entries[0][0], x_next, ys[0])
    return out


def generate(src):
    v = vanilla(src)
    for part in PARTS:                       # the rules must rebuild the English data
        entries, actions, x_first, x_next, y_first = v[part]
        if layout(ENGLISH[part], x_first, x_next, y_first)[:2] != (entries, actions):
            sys.exit(f"error: genintro.py's rules don't rebuild the vanilla {part} data")
    text, starts = [], []
    for part in PARTS:
        _, _, x_first, x_next, y_first = v[part]
        # the block's middle where the English block's is: half a line up per extra line
        y_first -= LINE_HEIGHT * (len(CATALAN[part]) - len(ENGLISH[part])) // 2
        entries, actions, cursor = layout(CATALAN[part], x_first, x_next, y_first, centre=True)
        # the cursor starts on the first letter, a cell after the first line's LEAD
        starts.append((SCREEN_HALF_W + entries[0][0] + 8, OAM_Y + y_first + LINE_HEIGHT))
        oam = ",\n".join(f"    OAM_ENTRY({x}, {y}, OAM_DIMS_8x16, OAM_NO_FLIP, {t:#x}, 1, 0)" for x, y, t in entries)
        acts = ",\n".join(f"    INTRO_TEXT_ACTION_{a}" for a in actions)
        cur = ", ".join(f"{c:#x}" if c else "0" for c in cursor)
        text.append(f"// {' / '.join(CATALAN[part])}\n"
                    f"const u16 sCaIntro{part}TextOam[OAM_DATA_SIZE({len(entries)})] = {{\n"
                    f"    {len(entries)},\n{oam}\n}};\n\n"
                    f"const IntroTextAction sCaIntro{part}Actions[{len(actions)}] = {{\n{acts}\n}};\n\n"
                    f"// per action: where the cursor goes at a line's first step (y << 8 | x), or 0\n"
                    f"const u16 sCaIntro{part}Cursor[{len(cursor)}] = {{ {cur} }};\n")
    xs, ys = (", ".join(str(s[i]) for s in starts) for i in (0, 1))
    text.append(f"// the cursor's start for each text ({', '.join(PARTS)}), set by ca/intro.h\n"
                f"const u16 sCaIntroStartX[{len(PARTS)}] = {{ {xs} }};\n"
                f"const u16 sCaIntroStartY[{len(PARTS)}] = {{ {ys} }};\n")
    return "\n".join(text)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--vanilla", action="store_true")
    a = ap.parse_args()
    text = "" if a.vanilla else generate(INTRO_C.read_text(encoding="utf-8"))
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(f"// Generated by translation/ca/tools/genintro.py. Do not edit.\n{text}", encoding="utf-8")


if __name__ == "__main__":
    main()
