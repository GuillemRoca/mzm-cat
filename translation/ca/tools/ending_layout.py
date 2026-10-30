#!/usr/bin/env python3
"""Layout of the Catalan sprite texts of the ending and of "Mission accomplished", from the
vanilla sprite (OAM) data of the five EU languages. Used by genending.py (the C data) and
gfx_ending.py (the graphics), so both agree.

Ending results screen (src/data/ending_and_gallery_data.c): each line is typed one letter
per sprite (sClearTime*/sCollecting*Oam_N: one 16x16 or 8x16 sprite of a letter of the
alphabet in ending/text_*), then shown whole (sFullLines*Oam_0 and _3: 32x16 sprites of the
line drawn in the same sheet, rows 0-1 and 2-3). The tables sEndingImageOam_ClearTime_Spanish
[15] and _Collecting_Spanish[19] have a fixed size, so the Catalan lines have as many letters.
"Mission accomplished" (src/data/chozodia_escape_data.c): one frame of 16 letter sprites from a
sheet shared by all languages; the Catalan line has 16 too.
Letter metrics (tile, size, y, advance) come from the vanilla lines whose text is known
(VANILLA); spaces add the vanilla word space.
"""
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
ENDING_C = ROOT / "src" / "data" / "ending_and_gallery_data.c"
CHOZODIA_C = ROOT / "src" / "data" / "chozodia_escape_data.c"

CATALAN = {"ClearTime": "TEMPS TOTAL DE JOC", "Collecting": "OBJECTES ACONSEGUITS",
           "MissionAccomplished": "MISSIÓ COMPLERTA!"}
# full line sprites: frame name, first tile of the line in the sheet
FULL_LINES = {"ClearTime": ("sFullLinesSpanishOam_0", 0x80), "Collecting": ("sFullLinesSpanishOam_3", 0xC0)}

VANILLA = {
    "sEndingImageOam_ClearTime_German": "BENÖTIGTE ZEIT",
    "sEndingImageOam_Collecting_German": "GEFUNDENE ITEMS",
    "sEndingImageOam_ClearTime_French": "DUREE DE LA MISSION",
    "sEndingImageOam_Collecting_French": "TAUX D'OBJETS COLLECTES",
    "sEndingImageOam_ClearTime_Italian": "TEMPO COMPLETAMENTO",
    "sEndingImageOam_YourRate_Italian": "PERCENTUALE",
    "sEndingImageOam_Collecting_Italian": "STRUMENTI RACCOLTI",
    "sEndingImageOam_ClearTime_Spanish": "TIEMPO INVERTIDO",
    "sEndingImageOam_Collecting_Spanish": "PORCENTAJE DE OBJETOS",
}
# (the English frame uses another set of letters, the Japanese release's)
MISSION_VANILLA = {
    "German": "MISSION ABGESCHLOSSEN!", "French": "MISSION RÉUSSIE!",
    "Italian": "MISSIONE COMPIUTA!", "Spanish": "¡MISIÓN CUMPLIDA!",
}
ENTRY_RE = re.compile(r"OAM_ENTRY\((-?\d+), (-?\d+), OAM_DIMS_(\w+), OAM_NO_FLIP, (0x[0-9a-f]+), (\d+), (\d+)\)")
WIDTH = {"8x16": 8, "16x16": 16, "32x16": 32, "8x8": 8, "16x8": 16, "32x8": 32}


def glyphs(text):
    """The sprite letters of a text: D' is one letter, spaces aren't letters."""
    out, i = [], 0
    while i < len(text):
        if text[i:i + 2] == "D'":
            out.append("D'")
            i += 2
        else:
            out.append(text[i])
            i += 1
    return out


def frames(src):
    """{frame name: [(x, y, dims, tile, palette, priority)]}."""
    return {m.group(1): [(int(e[0]), int(e[1]), e[2], int(e[3], 16), int(e[4]), int(e[5]))
                         for e in ENTRY_RE.findall(m.group(2))]
            for m in re.finditer(r"const u16 (s\w+)\[OAM_DATA_SIZE\(\d+\)\] = \{\s*\d+,(.*?)\};", src, re.S)}


def tables(src):
    """{table name: [frame name]} of the EndingImageOam tables."""
    return {m.group(1): re.findall(r"\.pFrame = (\w+)", m.group(2))
            for m in re.finditer(r"const struct EndingImageOam (\w+)\[\w+\] = \{(.*?)\n\};", src, re.S)}


def metrics(lines):
    """{letter: (tile, dims, dy, advance)} and the word space, from [(text, [(x, y, dims, tile)])]."""
    seen, adv, space = {}, {}, Counter()
    for text, ents in lines:
        letters = glyphs(text)
        assert len(letters) - letters.count(" ") == len(ents), (text, len(ents))
        k = 0
        prev = None
        for ch in letters:
            if ch == " ":
                prev = (prev[0], prev[1], True) if prev else None
                continue
            x, y, dims, tile = ents[k][:4]
            # "Mission accomplished" starts with a big M: the first letter has its own key
            seen.setdefault(("^" + ch) if k == 0 else ch, Counter())[(tile, dims, y)] += 1
            if prev:
                pch, px, after_space = prev
                if after_space:
                    space[x - px] += 1
                    space_from = pch
                    adv.setdefault(("space", pch), Counter())[x - px] += 1
                else:
                    adv.setdefault(pch, Counter())[x - px] += 1
            prev = (ch, x, False)
            k += 1
    out = {}
    for ch, c in seen.items():
        tile, dims, dy = c.most_common(1)[0][0]
        a = adv.get(ch.lstrip("^") if len(ch) > 1 and ch[0] == "^" else ch)
        out[ch] = (tile, dims, dy, a.most_common(1)[0][0] if a else WIDTH[dims] - 6)
    # the word space: the gap after a letter followed by a space, minus that letter's advance
    gaps = Counter()
    for key, c in adv.items():
        if isinstance(key, tuple) and key[1] in out:
            for gap, n in c.items():
                gaps[gap - out[key[1]][3]] += n
    return out, gaps.most_common(1)[0][0]


def lay(text, m, space):
    """[(letter, x)] relative to the line start, and the line's width in pixels."""
    out, x = [], 0
    for ch in glyphs(text):
        if ch == " ":
            x += space
            continue
        key = "^" + ch if not out and "^" + ch in m else ch
        out.append((key, x))
        x += m[ch][3]
    last = out[-1]
    return out, last[1] + WIDTH[m[last[0]][1]]


def ending():
    """{"ClearTime"/"Collecting": dict(letters=[(letter, x, y, dims, tile)], full=[(x, y, dims, tile)],
    start=x of the first letter)}; x relative to the sprite centre, as in the vanilla frames."""
    src = ENDING_C.read_text(encoding="utf-8")
    fr, tb = frames(src), tables(src)
    lines = [(text, [fr[f][0] for f in tb[name]]) for name, text in VANILLA.items()]
    m, space = metrics(lines)
    out = {}
    for key, text in CATALAN.items():
        if key not in FULL_LINES:
            continue
        laid, width = lay(text, m, space)
        start = -(width // 2)
        letters = [(ch, start + x, m[ch][2], m[ch][1], m[ch][0]) for ch, x in laid]
        name, base = FULL_LINES[key]
        y = fr[name][0][1]
        full, x = [], 0
        while x < width:
            dims = "32x16" if width - x > 16 else "16x16" if width - x > 8 else "8x16"
            full.append((start + x, y, dims, base + x // 8))
            x += WIDTH[dims]
        out[key] = dict(letters=letters, full=full, start=start, width=width, text=text)
    return out, m


def mission():
    """[(x, y, dims, tile)] of the Catalan "Mission accomplished" frame."""
    src = CHOZODIA_C.read_text(encoding="utf-8")
    fr = frames(src)
    lines = [(text, fr[f"sChozodiaEscapeOam_MissionAccomplished{lang}_Frame0"]) for lang, text in MISSION_VANILLA.items()]
    m, space = metrics(lines)
    laid, width = lay(CATALAN["MissionAccomplished"], m, space)
    start = -(width // 2)
    return [(start + x, m[ch][2], m[ch][1], m[ch][0]) for ch, x in laid], width


if __name__ == "__main__":
    e, _ = ending()
    for k, v in e.items():
        print(k, v["text"], "width", v["width"], "start", v["start"])
        print("  letters", v["letters"])
        print("  full", v["full"])
    print("mission", mission())
