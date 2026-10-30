#!/usr/bin/env bash
# The Catalan build checks, run by CI (.github/workflows/catalan.yml) and the same way locally.
#
#   translation/ca/tools/ci.sh            usual checks; fails on lint errors
#   RELEASE=1 translation/ca/tools/ci.sh  also fails on lint warnings and untranslated text
#                                         (CI sets it on v* tags, which are releases)
#
# Needs the base ROM (see translation/ca/README.md), agbcc and arm-none-eabi binutils on PATH,
# libpng-dev for gbagfx, and libmgba-dev to check the patch with mGBA's own loader.
# Outputs in translation/ca/dist/: mzm-cat-<version>.bps, lint.txt, lint.json. No ROM is ever copied there.
set -euo pipefail

ROOT=$(cd "$(dirname "$0")/../../.." && pwd)
cd "$ROOT"
CA=translation/ca
JOBS=$(nproc)  # `make eu` would drop to -j1 (no jobserver in the sub-make), so call REGION=eu directly
DIST=$CA/dist
mkdir -p "$DIST"

step() { echo "::group::$*" 2>/dev/null || true; echo "== $*"; }
endstep() { echo "::endgroup::" 2>/dev/null || true; }

step "Base ROM"
"$CA/tools/get_baserom.sh" eu
[ -d data ] || make extract REGION=eu > /dev/null
endstep

step "Tool tests"
python3 -m unittest "$CA/tools/test_lint.py"
python3 "$CA/tools/gap.py" vanilla
make ca-tools > /dev/null
python3 "$CA/tools/gfx.py" roundtrip
endstep

step "Vanilla EU"
make REGION=eu -j"$JOBS" > /dev/null
sha1sum -c mzm_eu.sha1
VANILLA=$(cut -d' ' -f1 mzm_eu.sha1)
endstep

step "LANG_CA self-test (vanilla text through the Catalan plumbing)"
make REGION=eu LANG_CA=1 CA_SELFTEST=1 -j"$JOBS" > /dev/null
GOT=$(sha1sum mzm_eu_ca.gba | cut -d' ' -f1)
if [ "$GOT" != "$VANILLA" ]; then
    echo "error: self-test ROM is $GOT, vanilla EU is $VANILLA: the LANG_CA plumbing changes the ROM" >&2
    exit 1
fi
echo "mzm_eu_ca.gba (self-test) is byte-identical to vanilla EU"
endstep

step "Lint"
LINT_FLAGS=()
[ "${RELEASE:-0}" = 1 ] && LINT_FLAGS+=(--release)
set +e
python3 "$CA/tools/lint.py" --json "$DIST/lint.json" "${LINT_FLAGS[@]}" | tee "$DIST/lint.txt"
LINT=${PIPESTATUS[0]}
set -e
[ "$LINT" = 0 ] || { echo "error: lint failed" >&2; exit 1; }
python3 "$CA/tools/review.py" --check
endstep

step "Catalan EU"
make REGION=eu LANG_CA=1 -j"$JOBS" > /dev/null
sha1sum mzm_eu_ca.gba
endstep

step "Patch"
# The tag on a release commit (v1.0.0), else the last tag plus the commit (v1.0.0-3-gabc1234).
VERSION=$(git describe --tags --match 'v*' --always --dirty 2>/dev/null || echo dev)
rm -f "$DIST"/*.bps
PATCH="$DIST/mzm-cat-$VERSION.bps"
python3 "$CA/tools/bps.py" create mzm_eu_baserom.gba mzm_eu_ca.gba "$PATCH" \
    --metadata "Metroid: Zero Mission en catala $VERSION. Base: EU ROM, SHA1 $VANILLA."
if pkg-config --exists libmgba 2>/dev/null || [ -f /usr/include/mgba/core/core.h ]; then
    make ca-emu-tools > /dev/null
    "$CA/build/bpscheck" mzm_eu_baserom.gba "$PATCH" mzm_eu_ca.gba
else
    echo "warning: libmgba not installed, patch not checked with mGBA's loader"
fi
endstep

step "Preview patch (testing only, never released: see translation/ca/TESTING.md)"
make REGION=eu LANG_CA=1 CA_PREVIEW=1 -j"$JOBS" > /dev/null
PREVIEW="$DIST/mzm-cat-$VERSION-PREVIEW-TEST-ONLY.bps"
python3 "$CA/tools/bps.py" create mzm_eu_baserom.gba mzm_eu_ca_preview.gba "$PREVIEW" \
    --metadata "TEST BUILD, do not distribute. Metroid: Zero Mission en catala $VERSION preview."
if [ -x "$CA/build/bpscheck" ]; then
    "$CA/build/bpscheck" mzm_eu_baserom.gba "$PREVIEW" mzm_eu_ca_preview.gba
fi
ls -l "$DIST"
endstep
