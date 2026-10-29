#!/usr/bin/env python3
"""Language-specific graphics: LZ77 4bpp assets <-> indexed PNG, via the vendored gbagfx.

  gfx.py export KEY [PNG]      vanilla asset -> PNG (default translation/ca/build/gfx/KEY.png)
  gfx.py export --all          every asset in gfx_assets.json
  gfx.py build KEY INC         translation/ca/gfx/KEY.png -> LZ77 include overriding the asset
  gfx.py roundtrip [KEY...]    asset -> PNG -> 4bpp -> LZ77 -> decompress, compared with the
                               vanilla tiles byte for byte (all assets if no KEY)

KEY is the asset's path under data/ without `.gfx.lz`, e.g. menus/game_over/text_prompt_spanish.
PNGs are 32 tiles (256 px) wide in VRAM order, indexed with the asset's 16-colour palette row.
Only pixel indices matter: keep the PNG's palette order when editing. Vanilla exports stay in
build/ and are never committed; commit only edited PNGs under translation/ca/gfx/.
"""
import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CA = ROOT / "translation" / "ca"
GBAGFX = CA / "build" / "gbagfx"
ASSETS = json.loads((CA / "tools" / "gfx_assets.json").read_text())
ASSETS.pop("_doc")
WIDTH_TILES = 32


def gbagfx(*args):
    r = subprocess.run([str(GBAGFX), *map(str, args)], capture_output=True, text=True)
    if r.returncode:
        sys.exit(f"error: gbagfx {' '.join(map(str, args))}: {r.stderr.strip()}")


def lz_path(key):
    return ROOT / "data" / f"{key}.gfx.lz"


def array_limit(key):
    """(symbol, max words or None) of the C array that includes the asset. An array declared
    unsized for LANG_CA (#ifdef LANG_CA ... [] #else ... [N] #endif) has no limit."""
    inc = f'"extracted/data/{key}.gfx.lz.inc"'
    for c in (ROOT / "src").rglob("*.c"):
        t = c.read_text(encoding="utf-8", errors="replace")
        if inc in t:
            m = re.search(r"#ifdef LANG_CA\s*\n\s*const u32 (\w+)\[\] = \{\s*\n#else[^\n]*\n[^\n]*\n#endif[^\n]*\n\s*#include "
                          + re.escape(inc), t)
            if m:
                return m.group(1), None
            m = re.search(r"(\w+)\s*\[(\w*)\]\s*=\s*\{\s*#include " + re.escape(inc), t)
            if m:
                return m.group(1), int(m.group(2), 0) if m.group(2) else None
    sys.exit(f"error: no C array includes {inc}")


def palette_row(key, out):
    a = ASSETS[key]
    pal = (ROOT / "data" / a["palette"]).read_bytes()
    row = pal[a["row"] * 32:(a["row"] + 1) * 32]
    if len(row) != 32:
        sys.exit(f"error: {a['palette']} has no row {a['row']}")
    out.write_bytes(row)


def decompress(key, tmp):
    raw = Path(tmp) / "vanilla.4bpp"
    gbagfx(lz_path(key), raw)
    return raw


def export(key, png, tmp):
    raw = decompress(key, tmp)
    pal = Path(tmp) / "row.gbapal"
    palette_row(key, pal)
    png.parent.mkdir(parents=True, exist_ok=True)
    gbagfx(raw, png, "-palette", pal, "-width", WIDTH_TILES)
    return raw.read_bytes()


def encode(png, num_tiles, tmp):
    """PNG -> (4bpp bytes, LZ77 bytes). Keeps at least num_tiles tiles, more if the PNG has
    non-empty tiles past them (trailing empty tiles are dropped)."""
    full = Path(tmp) / "full.4bpp"
    gbagfx(png, full)
    data = full.read_bytes()
    end = len(data)
    while end > num_tiles * 32 and not any(data[end - 32:end]):
        end -= 32
    tiles = Path(tmp) / "edited.4bpp"
    tiles.write_bytes(data[:end])
    lz = Path(tmp) / "edited.4bpp.lz"
    gbagfx(tiles, lz)
    best = lz77_optimal(data[:end])
    return data[:end], min(lz.read_bytes(), best, key=len)


def lz77_optimal(data, min_disp=2):
    """GBA LZ77 (type 0x10) with an optimal parse: the fewest bits for the given data, where
    gbagfx's greedy parse can come out a word too big for a fixed-size C array. Matches never
    point to the previous byte (min_disp 2), so the data can be decompressed straight to VRAM."""
    n = len(data)
    by_prefix, longest = {}, [(0, 0)] * n
    for i in range(n):
        best_len, best_disp = 0, 0
        if i + 3 <= n:
            for j in reversed(by_prefix.get(data[i:i + 3], [])):
                disp = i - j
                if disp > 4096:
                    break
                if disp < min_disp:
                    continue
                k = 3
                while k < 18 and i + k < n and data[j + k] == data[i + k]:
                    k += 1
                if k > best_len:
                    best_len, best_disp = k, disp
                    if k == 18:
                        break
        longest[i] = (best_len, best_disp)
        if i >= 2:
            by_prefix.setdefault(data[i - 2:i + 1], []).append(i - 2)
    cost, choice = [0] * (n + 1), [None] * n
    for i in range(n - 1, -1, -1):
        cost[i], choice[i] = 9 + cost[i + 1], (1, 0)
        length, disp = longest[i]
        for k in range(3, length + 1):
            if 17 + cost[i + k] < cost[i]:
                cost[i], choice[i] = 17 + cost[i + k], (k, disp)
    out = bytearray([0x10, n & 0xFF, (n >> 8) & 0xFF, (n >> 16) & 0xFF])
    i = 0
    while i < n:
        flag_at, flags = len(out), 0
        out.append(0)
        for bit in range(8):
            if i >= n:
                break
            k, disp = choice[i]
            if disp:
                flags |= 0x80 >> bit
                out += bytes([((k - 3) << 4) | ((disp - 1) >> 8), (disp - 1) & 0xFF])
            else:
                out.append(data[i])
            i += k
        out[flag_at] = flags
    return bytes(out)


def vanilla_tiles(key):
    with tempfile.TemporaryDirectory() as tmp:
        return len(decompress(key, tmp).read_bytes()) // 32


def check_limits(key, raw_len, lz_len):
    sym, words = array_limit(key)
    vram = ASSETS[key]["vram_max"]
    errors = []
    if raw_len > vram:
        errors.append(f"{raw_len} bytes of tiles, but only {vram} fit in VRAM before the next asset")
    if words is not None and (lz_len + 3) // 4 > words:
        errors.append(f"compressed to {(lz_len + 3) // 4} words, but {sym}[{words}] is fixed size: "
                      f"enlarge it in its .c and include/data/*.h declarations")
    return errors


def cmd_build(key, out):
    png = CA / "gfx" / f"{key}.png"
    with tempfile.TemporaryDirectory() as tmp:
        raw, lz = encode(png, vanilla_tiles(key), tmp)
    errors = check_limits(key, len(raw), len(lz))
    if errors:
        sys.exit(f"error: {png}: " + "; ".join(errors))
    lz += b"\0" * (-len(lz) % 4)
    words = [int.from_bytes(lz[i:i + 4], "little") for i in range(0, len(lz), 4)]
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    Path(out).write_text(",".join(f"{w}u" for w in words))


def cmd_roundtrip(keys):
    print(f"{'asset':58} {'tiles':>5} {'vanilla lz':>10} {'gbagfx lz':>9} {'C array':>9}  result")
    bad = 0
    for key in keys:
        with tempfile.TemporaryDirectory() as tmp:
            png = Path(tmp) / "asset.png"
            vanilla = export(key, png, tmp)
            raw, lz = encode(png, len(vanilla) // 32, tmp)
            back = Path(tmp) / "back.4bpp"
            (Path(tmp) / "back.lz").write_bytes(lz)
            gbagfx(Path(tmp) / "back.lz", back)
            same = back.read_bytes() == vanilla and raw == vanilla
        sym, words = array_limit(key)
        limit = f"[{words}]" if words is not None else "[]"
        fits = words is None or (len(lz) + 3) // 4 <= words
        ok = same and fits
        bad += not ok
        result = ("identical" if same else "DIFFERENT") + ("" if fits else ", TOO BIG for array")
        print(f"{key:58} {len(vanilla) // 32:5} {lz_path(key).stat().st_size:10} {len(lz):9} {limit:>9}  {result}")
    return bad


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    e = sub.add_parser("export")
    e.add_argument("key", nargs="?")
    e.add_argument("png", nargs="?")
    e.add_argument("--all", action="store_true")
    b = sub.add_parser("build")
    b.add_argument("key")
    b.add_argument("output")
    r = sub.add_parser("roundtrip")
    r.add_argument("keys", nargs="*")
    a = ap.parse_args()
    if a.cmd == "export":
        keys = sorted(ASSETS) if a.all else [a.key]
        for key in keys:
            png = Path(a.png) if a.png and not a.all else CA / "build" / "gfx" / f"{key}.png"
            with tempfile.TemporaryDirectory() as tmp:
                export(key, png, tmp)
            print(png.relative_to(ROOT) if png.is_relative_to(ROOT) else png)
    elif a.cmd == "build":
        cmd_build(a.key, a.output)
    else:
        sys.exit(1 if cmd_roundtrip(a.keys or sorted(ASSETS)) else 0)
