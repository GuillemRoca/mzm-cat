#!/usr/bin/env bash
# Puts a verified base ROM at mzm_<region>_baserom.gba in the repo root.
#
# usage: translation/ca/tools/get_baserom.sh [region]     (default: eu)
#
# Sources, first match wins:
#   1. mzm_<region>_baserom.gba already in the repo root (local builds)
#   2. $BASEROM_DIR/mzm_<region>_baserom.gba (CI: a checkout of a private ROM repository)
#   3. $BASEROM_<REGION>_URL, a .gba or a .zip holding exactly one .gba (CI: a private link)
# Whatever the source, its SHA1 must match mzm_<region>.sha1, or nothing is written.
# The ROM never leaves the repo root, which .gitignore already covers (*.gba).
set -euo pipefail

REGION=${1:-eu}
ROOT=$(cd "$(dirname "$0")/../../.." && pwd)
cd "$ROOT"

DEST=mzm_${REGION}_baserom.gba
SHA1FILE=mzm_${REGION}.sha1
[ -f "$SHA1FILE" ] || { echo "error: unknown region '$REGION' (no $SHA1FILE)" >&2; exit 1; }
EXPECTED=$(cut -d' ' -f1 "$SHA1FILE")
URL_VAR=BASEROM_$(echo "$REGION" | tr '[:lower:]' '[:upper:]')_URL
URL=${!URL_VAR:-}

verify() {
    local actual
    actual=$(sha1sum "$1" | cut -d' ' -f1)
    if [ "$actual" != "$EXPECTED" ]; then
        echo "error: $2 has SHA1 $actual, expected $EXPECTED (see $SHA1FILE)" >&2
        return 1
    fi
}

if [ -f "$DEST" ]; then
    verify "$DEST" "$DEST"
    echo "base ROM ok: $DEST (already present)"
    exit 0
fi

TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

if [ -n "${BASEROM_DIR:-}" ] && [ -f "$BASEROM_DIR/$DEST" ]; then
    cp "$BASEROM_DIR/$DEST" "$TMP/rom.gba"
    SOURCE="\$BASEROM_DIR/$DEST"
elif [ -n "$URL" ]; then
    # The URL is a secret: never echo it.
    curl -fsSL --retry 3 -o "$TMP/download" "$URL" || { echo "error: download from \$$URL_VAR failed" >&2; exit 1; }
    if [ "$(head -c 2 "$TMP/download")" = "PK" ]; then
        python3 - "$TMP/download" "$TMP/rom.gba" <<'PY'
import sys, zipfile
with zipfile.ZipFile(sys.argv[1]) as z:
    names = [n for n in z.namelist() if n.lower().endswith(".gba")]
    if len(names) != 1:
        sys.exit(f"error: expected exactly one .gba in the zip, found {len(names)}")
    with open(sys.argv[2], "wb") as out:
        out.write(z.read(names[0]))
PY
    else
        mv "$TMP/download" "$TMP/rom.gba"
    fi
    SOURCE="\$$URL_VAR"
else
    echo "error: no base ROM. Put it at $DEST, set BASEROM_DIR, or set $URL_VAR (see translation/ca/README.md)." >&2
    exit 1
fi

verify "$TMP/rom.gba" "the ROM from $SOURCE"
mv "$TMP/rom.gba" "$DEST"
echo "base ROM ok: $DEST (from $SOURCE)"
