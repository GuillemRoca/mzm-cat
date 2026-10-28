"""Shared helpers for the Catalan text tools: vanilla text, widths, layout and the
translation files. Reference text is always read from the decomp source, never copied
into translation/ca.
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CA = ROOT / "translation" / "ca"
TEXT_DATA = ROOT / "src" / "data" / "text_data.c"
WIDTHS_SRC = ROOT / "src" / "data" / "menus" / "pause_screen_data.c"

sys.path.insert(0, str(ROOT / "tools"))
from preproc import CharMap  # noqa: E402

CATEGORIES = {
    # name: (pointer-table suffix, translation file)
    "message": ("Message", "message.txt"),
    "location": ("Location", "location.txt"),
    "description": ("Description", "description.txt"),
    "story": ("Story", "story.txt"),
    "file_screen": ("FileScreen", "file_screen.txt"),
}
LANGUAGES = ["English", "German", "French", "Italian", "Spanish"]

LINE_LIMIT = 224  # text.c: a glyph that would end past 224 px forces a new line
MAX_LINES = {"message": 2, "location": 1, "description": None, "story": None, "file_screen": 4}

_charmap = None


def charmap():
    global _charmap
    if _charmap is None:
        _charmap = CharMap.parse_charmap(str(ROOT / "charmap.txt"))
    return _charmap


# --- vanilla text --------------------------------------------------------------------

def vanilla_text(region="REGION_EU"):
    """Strings and pointer tables of text_data.c as built for `region` without LANG_CA.
    Returns (strings: {symbol: text}, tables: {table symbol: [(index name, symbol)]})."""
    src = TEXT_DATA.read_text(encoding="utf-8")
    src = re.sub(r"^\s*#include.*$", "", src, flags=re.M)
    out = subprocess.run(["cpp", "-P", "-w", "-D" + region], input=src,
                         capture_output=True, text=True, check=True).stdout
    strings = {m.group(1): m.group(2)
               for m in re.finditer(r'const u16 (s\w+)\[\] = INCTEXT\("(.*?)"\);', out)}
    tables = {m.group(1): re.findall(r"\[(\w+)\] = (\w+)", m.group(2))
              for m in re.finditer(r"const u16\* (s\w+TextPointers_\w+)\[[^\]]*\] = \{(.*?)\};", out, re.S)}
    return strings, tables


def table(tables, language, category):
    return tables[f"s{language}TextPointers_{CATEGORIES[category][0]}"]


# --- widths --------------------------------------------------------------------------

def vanilla_widths():
    """The EU half of sCharacterWidths, as compiled without LANG_CA."""
    src = WIDTHS_SRC.read_text(encoding="utf-8")
    i = src.index("const u8 sCharacterWidths[1184]")
    body = src[i:src.index("};", i)]
    eu = body.split("#ifdef REGION_EU", 1)[1].split("#else // !REGION_EU", 1)[0]
    if "#ifdef LANG_CA" in eu:
        eu = eu.split("#else // !LANG_CA", 1)[1].split("#endif // LANG_CA", 1)[0]
    vals = [int(x) for x in re.findall(r"\b\d+\b", eu)]
    if len(vals) != 1184:
        raise ValueError(f"expected 1184 EU widths, found {len(vals)}")
    return vals


def width_overrides(path=CA / "font" / "widths.txt"):
    """{char id: width} from font/widths.txt lines like `0357 2  # middle dot`."""
    over = {}
    if path.exists():
        for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            line = line.split("#", 1)[0].strip()
            if not line:
                continue
            m = re.fullmatch(r"([0-9A-Fa-f]{3,4})\s+(\d+)", line)
            if not m:
                raise ValueError(f"{path}:{n}: expected `HEXID WIDTH`")
            over[int(m.group(1), 16)] = int(m.group(2))
    return over


def widths(catalan=True):
    w = vanilla_widths()
    if catalan:
        for cid, v in width_overrides().items():
            w[cid] = v
    return w


# --- tokens and layout ---------------------------------------------------------------

CODE_RE = re.compile(r"\{(\w+)(?:\((\d+)\))?\}")


def tokens(text):
    """[(kind, value, raw)], kind in char/gap/indent/color/delay/nl/code (other named codes)."""
    cm = charmap()
    out, i = [], 0
    while i < len(text):
        c = text[i]
        if c == "{":
            j = text.index("}", i)
            raw = text[i:j + 1]
            m = CODE_RE.fullmatch(raw)
            if not m:
                raise KeyError(f"bad code {raw!r}")
            name, arg = m.group(1), m.group(2)
            if arg is not None:
                out.append((name.lower(), int(arg), raw))
            else:
                vals = cm.named_char_dict.get(name)
                if vals is None:
                    raise KeyError(f"unknown code {raw!r}")
                if len(vals) == 1 and vals[0] >= 0x8000:
                    out.append(("code", vals[0], raw))
                else:
                    for v in vals:
                        out.append(("char", v, raw))
            i = j + 1
        elif c == "\\":
            raw = text[i:i + 2]
            vals = cm.char_dict.get(raw)
            if vals is None:
                raise KeyError(f"unknown escape {raw!r}")
            out.append(("nl", vals[0], raw) if raw == "\\n" else ("char", vals[0], raw))
            i += 2
        else:
            vals = cm.char_dict.get(c)
            if vals is None:
                raise KeyError(f"character not in charmap.txt: {c!r} (U+{ord(c):04X})")
            for v in vals:
                out.append(("char", v, c))
            i += 1
    return out


def split_lines(text):
    """Split on \\n and {NEW_PAGE}; returns the raw text of each line."""
    return re.split(r"\\n|\{NEW_PAGE\}", text)


def line_layout(line_text, w):
    """Pen model of TextProcessCurrentMessage for one line.
    Returns dict: lead_gap (int or None), glyph_width (sum of glyph widths only), pen_end
    (final pen incl. GAP/INDENT), overflow (True if a glyph or GAP would cross 224 px)."""
    toks = tokens(line_text)
    lead = toks[0][1] if toks and toks[0][0] == "gap" else None
    pen = glyphs = 0
    overflow = False
    for kind, v, _ in toks:
        if kind == "gap":
            step = v
        elif kind == "char":
            step = w[v] if v < len(w) else 10  # TextGetCharacterWidth
            glyphs += step
        elif kind == "indent":
            pen = v
            continue
        else:
            continue
        if pen + step > LINE_LIMIT:
            overflow = True
        pen += step
    return {"lead_gap": lead, "glyph_width": glyphs, "pen_end": pen, "overflow": overflow}


# --- translation files ---------------------------------------------------------------

ENTRY_RE = re.compile(r'^([A-Z][A-Z0-9_]*)\s*=\s*"(.*)"\s*$')


def read_translation(category, base=CA / "text"):
    """{index name: (text, line number)} from text/<file>. Lines: `ID = "text"`; `#` comments."""
    path = base / CATEGORIES[category][1]
    entries = {}
    if not path.exists():
        return entries, path
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        m = ENTRY_RE.match(s)
        if not m:
            raise ValueError(f"{path}:{n}: expected ID = \"text\"")
        if m.group(1) in entries:
            raise ValueError(f"{path}:{n}: {m.group(1)} is defined twice")
        if '"' in m.group(2):
            raise ValueError(f"{path}:{n}: use ” (charmap 0x42) for quotes, not \"")
        entries[m.group(1)] = (m.group(2), n)
    return entries, path


def identical_ids(path=CA / "identical.txt"):
    """IDs whose Catalan text is meant to equal the English (counted as translated)."""
    if not path.exists():
        return set()
    return {l.split("#", 1)[0].strip() for l in path.read_text(encoding="utf-8").splitlines()} - {""}
