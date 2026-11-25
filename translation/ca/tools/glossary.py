#!/usr/bin/env python3
"""Imports AM2R-cat terms into translation/ca/glossary.md.

  glossary.py import FILE [--dry-run]

FILE is the AM2R-cat glossary (gitignored, e.g. translation/ca/reference/am2r-glossary.csv):
CSV, TSV or a Markdown table, with a header row naming an English column ("English",
"Anglès", "EN") and a Catalan column ("Catalan", "Català", "CA"). Rows are matched on the
English term, ignoring case and anything in parentheses.

- PROPOSED term found in AM2R-cat: becomes APPROVED with the AM2R-cat Catalan.
- APPROVED term that AM2R-cat translates differently: reported, never changed (your
  approvals win; settle it by hand).
- AM2R-cat terms not in the glossary are listed, to add if MZM uses them.
"""
import argparse
import csv
import re
import sys
from pathlib import Path

GLOSSARY = Path(__file__).resolve().parents[1] / "glossary.md"
EN_HEADERS = {"english", "anglès", "angles", "en"}
CA_HEADERS = {"catalan", "català", "catala", "ca"}


def key(term):
    return re.sub(r"\s+", " ", re.sub(r"\(.*?\)", "", term)).strip().lower()


def read_reference(path):
    text = path.read_text(encoding="utf-8-sig")
    if path.suffix.lower() == ".md":
        rows = [[c.strip() for c in l.strip().strip("|").split("|")]
                for l in text.splitlines() if l.strip().startswith("|") and not re.match(r"^\|[\s:|-]+\|$", l.strip())]
    else:
        dialect = "excel-tab" if path.suffix.lower() == ".tsv" or "\t" in text.splitlines()[0] else "excel"
        rows = list(csv.reader(text.splitlines(), dialect=dialect))
    if not rows:
        sys.exit(f"error: {path} is empty")
    header = [h.strip().lower() for h in rows[0]]
    try:
        en = next(i for i, h in enumerate(header) if h in EN_HEADERS)
        ca = next(i for i, h in enumerate(header) if h in CA_HEADERS)
    except StopIteration:
        sys.exit(f"error: {path}: header needs an English and a Catalan column, found {rows[0]}")
    return {key(r[en]): r[ca].strip() for r in rows[1:] if len(r) > max(en, ca) and r[en].strip() and r[ca].strip()}


def import_terms(ref, lines):
    """Returns (new lines, approved, conflicts, matched keys)."""
    approved, conflicts, matched, out = [], [], set(), []
    for line in lines:
        cells = [c.strip() for c in line.strip().strip("|").split("|")] if line.startswith("| ") else None
        if not cells or len(cells) != 5 or cells[3] not in ("APPROVED", "PROPOSED"):
            out.append(line)
            continue
        english, spanish, catalan, status, notes = cells
        k = key(english)
        if k not in ref:
            out.append(line)
            continue
        matched.add(k)
        am2r = ref[k]
        if status == "APPROVED":
            if am2r != catalan:
                conflicts.append((english, catalan, am2r))
            out.append(line)
            continue
        approved.append((english, am2r))
        notes = f"From AM2R-cat. {notes}".strip()
        out.append(f"| {english} | {spanish} | {am2r} | APPROVED | {notes} |")
    return out, approved, conflicts, matched


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["import"])
    ap.add_argument("file", type=Path)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    ref = read_reference(a.file)
    lines = GLOSSARY.read_text(encoding="utf-8").split("\n")
    out, approved, conflicts, matched = import_terms(ref, lines)
    for english, ca in approved:
        print(f"approved: {english} -> {ca}")
    for english, ours, am2r in conflicts:
        print(f"CONFLICT: {english}: glossary has '{ours}', AM2R-cat has '{am2r}' (left as is)")
    unused = sorted(set(ref) - matched)
    if unused:
        print(f"{len(unused)} AM2R-cat terms not in the glossary: {', '.join(unused)}")
    if not a.dry_run:
        GLOSSARY.write_text("\n".join(out), encoding="utf-8")
    print(f"{len(approved)} approved, {len(conflicts)} conflicts{' (dry run)' if a.dry_run else ''}")


if __name__ == "__main__":
    main()
