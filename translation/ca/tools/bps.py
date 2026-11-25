#!/usr/bin/env python3
"""BPS patches (byuu's format, as read by Flips, mGBA, Rom Patcher JS...).

  bps.py create SOURCE TARGET PATCH [--metadata TEXT]
  bps.py apply SOURCE PATCH OUTPUT

create emits SourceRead for unchanged bytes, SourceCopy for data that moved (the Catalan
text shifts everything after it), and TargetRead for new bytes. apply checks all three
CRC32s. Standard library only.
"""
import argparse
import sys
import zlib

MIN_MATCH = 8      # shorter matches are cheaper as literals
INDEX_STEP = 16    # source positions sampled for SourceCopy lookups
KEY = 32           # bytes hashed per sample; any match >= KEY + INDEX_STEP - 1 is found


def number(n):
    out = bytearray()
    while True:
        x = n & 0x7F
        n >>= 7
        if n == 0:
            out.append(0x80 | x)
            return out
        out.append(x)
        n -= 1


def common_prefix(a, ai, b, bi):
    """Length of the common prefix of a[ai:] and b[bi:]."""
    n, size = 0, 4096
    limit = min(len(a) - ai, len(b) - bi)
    while n < limit:
        step = min(size, limit - n)
        if a[ai + n:ai + n + step] == b[bi + n:bi + n + step]:
            n += step
            size *= 2
        elif step == 1:
            break
        else:
            size = max(1, step // 2)
    return n


def create(source, target, metadata=b""):
    index = {}
    for p in range(0, len(source) - KEY + 1, INDEX_STEP):
        index.setdefault(source[p:p + KEY], p)
    out = bytearray(b"BPS1") + number(len(source)) + number(len(target)) + number(len(metadata)) + metadata
    literal = bytearray()
    t = rel = 0  # rel: source relative offset for SourceCopy

    def flush():
        if literal:
            out.extend(number(((len(literal) - 1) << 2) | 1))
            out.extend(literal)
            literal.clear()

    while t < len(target):
        best, kind, src = 0, None, 0
        if t < len(source):
            best, kind = common_prefix(source, t, target, t), 0
        n = common_prefix(source, rel, target, t) if rel < len(source) else 0
        if n > best:
            best, kind, src = n, 2, rel
        if best < 64:
            for j in range(INDEX_STEP):
                p = index.get(target[t + j:t + j + KEY]) if t + j + KEY <= len(target) else None
                if p is not None and p >= j:
                    n = common_prefix(source, p - j, target, t)
                    if n > best:
                        best, kind, src = n, 2, p - j
                    break
        if best < MIN_MATCH:
            literal.append(target[t])
            t += 1
            continue
        flush()
        if kind == 0:
            out.extend(number(((best - 1) << 2) | 0))
        else:
            delta = src - rel
            out.extend(number(((best - 1) << 2) | 2))
            out.extend(number((abs(delta) << 1) | (delta < 0)))
            rel = src + best
        t += best
    flush()
    out += zlib.crc32(source).to_bytes(4, "little") + zlib.crc32(target).to_bytes(4, "little")
    out += zlib.crc32(out).to_bytes(4, "little")
    return bytes(out)


def apply(source, patch):
    if patch[:4] != b"BPS1":
        raise ValueError("not a BPS patch")
    if zlib.crc32(patch[:-4]) != int.from_bytes(patch[-4:], "little"):
        raise ValueError("patch CRC mismatch")
    if zlib.crc32(source) != int.from_bytes(patch[-12:-8], "little"):
        raise ValueError("source CRC mismatch: wrong base ROM")
    pos = 4

    def read_number():
        nonlocal pos
        data, shift = 0, 1
        while True:
            x = patch[pos]
            pos += 1
            data += (x & 0x7F) * shift
            if x & 0x80:
                return data
            shift <<= 7
            data += shift

    src_size, tgt_size, meta_size = read_number(), read_number(), read_number()
    pos += meta_size
    if src_size != len(source):
        raise ValueError("source size mismatch")
    target = bytearray()
    src_rel = tgt_rel = 0
    while pos < len(patch) - 12:
        data = read_number()
        cmd, length = data & 3, (data >> 2) + 1
        if cmd == 0:
            target += source[len(target):len(target) + length]
        elif cmd == 1:
            target += patch[pos:pos + length]
            pos += length
        else:
            d = read_number()
            delta = -(d >> 1) if d & 1 else d >> 1
            if cmd == 2:
                src_rel += delta
                target += source[src_rel:src_rel + length]
                src_rel += length
            else:
                tgt_rel += delta
                for _ in range(length):
                    target.append(target[tgt_rel])
                    tgt_rel += 1
    if len(target) != tgt_size or zlib.crc32(target) != int.from_bytes(patch[-8:-4], "little"):
        raise ValueError("target CRC mismatch")
    return bytes(target)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("create")
    c.add_argument("source")
    c.add_argument("target")
    c.add_argument("patch")
    c.add_argument("--metadata", default="")
    a_ = sub.add_parser("apply")
    a_.add_argument("source")
    a_.add_argument("patch")
    a_.add_argument("output")
    a = ap.parse_args()
    if a.cmd == "create":
        src, tgt = open(a.source, "rb").read(), open(a.target, "rb").read()
        patch = create(src, tgt, a.metadata.encode())
        open(a.patch, "wb").write(patch)
        if apply(src, patch) != tgt:
            sys.exit("error: patch does not reproduce the target")
        print(f"{a.patch}: {len(patch)} bytes")
    else:
        open(a.output, "wb").write(apply(open(a.source, "rb").read(), open(a.patch, "rb").read()))
