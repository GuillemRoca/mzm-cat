#!/usr/bin/env python3
"""Composes the Catalan game over title, "FI DE LA / PARTIDA", from the vanilla "GAME OVER".

  gfx_game_over_title.py [OUT.png]   (needs data/ extracted)
                                     OUT.png: translation/ca/screens/game_over_title.png

The title is its own background layer (BG1): 128 tiles at the end of
menus/game_over/text_and_background, placed by menus/game_over/text.tt, and shared by every
language. Its letters are 31 px tall with a one-colour-per-row gradient (colours 4 to 9, which
GameOverUpdateLettersPalette animates), a bevel (1 on left and top edges, 2 on right and bottom
ones), a ring (3) and an outline (15); diagonals have a 2 in each step of the ring.

A, E and R are the vanilla letters as they are. The others are cut from them: F, L and I from
the E (its stem, with or without its bars), D from the O with a full-height stem, P from the R
without its leg and with the bowl's lower corner cut like its upper one, T from a bar over a
stem. Each new letter is drawn from its shape: a pixel whose surroundings (3 px each way) are
the same shape as in the vanilla letter keeps the vanilla pixel, the rest follow the rules
above. Letters are 2 px apart, as in vanilla, and words 13 px.

The whole title doesn't fit one line (285 px), so it is two lines of the vanilla size, centred,
between the top of the screen and the prompt (which starts at y = 83). OUT.png is the layer as
it shows on screen, 256 x 80; tools/gengameover.py cuts it into tiles and a tilemap for the
build. Only the German slot (Catalan) shows it: see translation/ca/include/ca/game_over.h.
"""
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gfx  # noqa: E402

ROOT = gfx.ROOT
DATA = ROOT / "data" / "menus" / "game_over"
OUT = gfx.CA / "screens" / "game_over_title.png"

CATALAN = ["FI DE LA", "PARTIDA"]
TOPS = [9, 41]                    # y of each line's outline; lines are 31 px tall
SCREEN_CENTRE = 120
LETTER_GAP, WORD_GAP = 2, 13      # between letter shapes
WIDTH, HEIGHT = 256, 80           # the layer, down to the prompt
VANILLA_ROWS = range(32, 64)      # where text.tt shows GAME OVER
VANILLA_LETTERS = ["G", "A", "M", "E1", "O", "V", "E", "R"]

SHAPE = {1, 2, 4, 5, 6, 7, 8, 9}  # bevel and gradient
RING2, RING, OUTLINE = 2, 3, 15
BANDS = [None, None, None, 9, 9, 8, 8, 7, 7, 6, 6, 6, 5, 5, 4, 4, 4, 5, 5, 6, 6, 6, 7, 7, 8, 8, 9, 9]
NEAR = 3                          # a pixel keeps its vanilla colour if the shape matches this far


def vanilla_title():
    """{(x, y): colour} of the vanilla title, y from the top of its line."""
    tiles = gfx.lz77_decompress((DATA / "text_and_background.gfx.lz").read_bytes())
    tilemap = gfx.lz77_decompress((DATA / "text.tt").read_bytes())
    px = {}
    for cell in range(len(tilemap) // 2):
        entry = int.from_bytes(tilemap[2 * cell:2 * cell + 2], "little")
        cx, cy = cell % 32 * 8, cell // 32 * 8
        if not entry or cy not in VANILLA_ROWS:
            continue
        if entry >> 10:
            sys.exit("error: the vanilla title has flipped or recoloured tiles")
        tile = tiles[entry * 32:entry * 32 + 32]
        for i in range(64):
            v = tile[i // 2] >> 4 if i & 1 else tile[i // 2] & 0xF
            if v:
                px[(cx + i % 8, cy - VANILLA_ROWS[0] + i // 8)] = v
    return px


def stair_notches(shape):
    """Pixels outside the shape in the inner corner of a step, on stairs of two steps or more:
    the ring is 2 there."""
    corners = {}
    for (x, y) in shape:
        for sx in (-1, 1):
            for sy in (-1, 1):
                n = (x + sx, y)
                if (n not in shape and (n[0], y + sy) in shape and (n[0], y - sy) not in shape
                        and (n[0] + sx, y) not in shape):
                    corners[n] = (-sx, sy)                     # towards the shape
    return {(x, y) for (x, y), (hx, vy) in corners.items()
            if (x - hx, y + vy) in corners or (x + hx, y - vy) in corners}


def vanilla_shape(px):
    """The letters' shapes: bevel and gradient pixels, less the 2s that are steps of the ring."""
    shape = {p for p, v in px.items() if v in SHAPE}

    def step(x, y):
        left, right = (x - 1, y) not in shape, (x + 1, y) not in shape
        up, down = (x, y - 1) not in shape, (x, y + 1) not in shape
        if px[(x, y)] != 2 or left == right or up == down:
            return False
        sx, sy = (-1 if left else 1), (-1 if up else 1)
        return any(px.get(d) == 2 and d in shape for d in ((x + sx, y - sy), (x - sx, y + sy)))
    return shape - {p for p in shape if step(*p)}


def draw(shape):
    """{(x, y): colour} of a shape, by the rules of the vanilla letters."""
    notches = stair_notches(shape)

    def out(x, y):
        return (x, y) not in shape

    def corner(x, y):                                          # outside, and not a step
        return out(x, y) and (x, y) not in notches
    px = {}
    for (x, y) in shape:
        left, right, up, down = out(x - 1, y), out(x + 1, y), out(x, y - 1), out(x, y + 1)
        if right:
            v = 2
        elif left and up:
            v = 2 if (x - 1, y + 1) in notches else 1        # the top of a cut corner
        elif left and down:
            v = 2 if (x - 1, y - 1) in notches else 1
        elif left or up:
            v = 1
        elif down:
            v = 2
        elif corner(x - 1, y + 1):                             # inner corners: the stem's bevel
            v = 1
        elif corner(x + 1, y - 1) or corner(x + 1, y + 1):
            v = 2
        else:
            v = BANDS[y]
        px[(x, y)] = v
    ring = {(x + dx, y + dy) for (x, y) in shape for dx in (-1, 0, 1) for dy in (-1, 0, 1)} - shape
    for p in ring:
        px[p] = RING2 if p in notches else RING
    for (x, y) in list(px):
        for d in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            px.setdefault(d, OUTLINE)
    return px


def rect(x0, x1, y0, y1):
    return {(x, y) for x in range(x0, x1 + 1) for y in range(y0, y1 + 1)}


def glyphs(title, shape):
    """{letter: {(x, y): colour}}, x from the letter shape's first column."""
    columns = sorted({x for x, _ in shape})
    starts = [x for x in columns if x - 1 not in columns]
    ends = [x for x in columns if x + 1 not in columns]
    if len(starts) != len(VANILLA_LETTERS):
        sys.exit(f"error: {len(starts)} letters in the vanilla title, expected GAME OVER")
    vanilla = {name: ({(x - a, y) for (x, y) in shape if a <= x <= b}, a)
               for name, a, b in zip(VANILLA_LETTERS, starts, ends)}
    a, e, o, r = (vanilla[n][0] for n in "AEOR")
    stem = rect(0, 6, 2, 28)
    if not stem <= e or not stem <= r or not rect(0, 6, 7, 23) <= o:
        sys.exit("error: the vanilla E, R and O don't have the stem the new letters are built on")
    new = {  # letter: (shape, the vanilla letter it is cut from)
        "A": (a, "A"),
        "E": (e, "E"),
        "R": (r, "R"),
        "F": ({p for p in e if p[0] <= 6 or p[1] <= 18}, "E"),                # no lower bar
        "L": ({p for p in e if p[0] <= 6 or p[1] >= 22}, "E"),                # only the lower bar
        "I": (stem, "E"),
        "D": (o | stem, "O"),                                                 # square on the left
        # the bowl closes at row 18, its lower right corner cut like the upper one (rows 2 to 6)
        "P": ({p for p in r if p[1] <= 13} | stem
              | {(x, y) for y in range(14, 19) for x in range(8, 34 - y)}, "R"),
        "T": (rect(0, 16, 2, 8) | rect(5, 11, 2, 28), "E"),
    }
    out = {}
    for letter, (new_shape, source) in new.items():
        src_shape, src_x = vanilla[source]
        px = draw(new_shape)
        for (x, y), v in px.items():
            same = all(((x + dx, y + dy) in new_shape) == ((x + dx, y + dy) in src_shape)
                       for dx in range(-NEAR, NEAR + 1) for dy in range(-NEAR, NEAR + 1))
            drawn = title.get((src_x + x, y))
            # the letter as drawn; around it only its ring's 2s and 3s (never a neighbour's ring)
            if same and ((x, y) in new_shape and drawn in SHAPE
                         or v in (RING, RING2) and drawn in (RING, RING2)):
                px[(x, y)] = drawn
        out[letter] = (px, max(x for x, _ in new_shape) + 1)
    return out


def set_line(letters, text):
    """({(x, y): colour}, width) of a line, x from its first letter shape's first column."""
    rank = {OUTLINE: 0, RING: 1, RING2: 2}     # where rings meet, the pixel nearer a letter wins
    out, pen = {}, 0
    for ch in text:
        if ch == " ":
            pen += WORD_GAP - LETTER_GAP
            continue
        if ch not in letters:
            sys.exit(f"error: no title letter for {ch!r}")
        px, width = letters[ch]
        for (x, y), v in px.items():
            p = (pen + x, y)
            if p not in out or rank.get(v, 3) > rank.get(out[p], 3):
                out[p] = v
        pen += width + LETTER_GAP
    return out, pen - LETTER_GAP


def palette():
    pal = (DATA / "palette.pal").read_bytes()[:32]             # row 0
    rgb = []
    for i in range(0, 32, 2):
        v = int.from_bytes(pal[i:i + 2], "little")
        rgb += [(v & 31) * 255 // 31, (v >> 5 & 31) * 255 // 31, (v >> 10 & 31) * 255 // 31]
    return rgb


def main(out_png):
    title = vanilla_title()
    letters = glyphs(title, vanilla_shape(title))
    img = Image.new("P", (WIDTH, HEIGHT), 0)
    img.putpalette(palette())
    for text, top in zip(CATALAN, TOPS):
        px, width = set_line(letters, text)
        left = round(SCREEN_CENTRE - width / 2)
        for (x, y), v in px.items():
            img.putpixel((left + x, top + y), v)
        print(f"{text!r}: x = {left}..{left + width - 1} ({width} px), y = {top}..{top + 30}")
    out_png.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_png)
    print(out_png.relative_to(ROOT) if out_png.is_relative_to(ROOT) else out_png)


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else OUT)
