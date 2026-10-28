# Metroid: Zero Mission en català

A Catalan fan translation built from this decompilation. Catalan replaces the Spanish slot
(`LANGUAGE_SPANISH`) of the EU build, and releases are `.bps` patches against the vanilla EU ROM
(SHA1 `0fd107445a42e6f3a3e5ce8c865f412583179903`, also in `mzm_eu.sha1`). Everything about the
translation lives under `translation/ca/`. The ROM is never committed or distributed.

## Layout

```
text/<category>.txt   the Catalan text: message, location, description, story, file_screen
font/glyphs/XXXX.png  edited glyphs (char ID in hex), drawn over the extracted EU font
font/widths.txt       sCharacterWidths overrides for those glyphs
gfx/<asset>.png       edited graphics; <asset> is the path under data/ without .gfx.lz
identical.txt         IDs whose Catalan is meant to equal the English
glossary.md           terminology (APPROVED / PROPOSED), STYLE.md, notes/translator-notes.md
RELEASE_CHECKLIST.md  what a release needs
VERSION               version in the patch name
ca.mk                 the LANG_CA build, included from the top-level Makefile
include/ca/layout.h   per-language layout constants
credits.txt           the Catalan translators, added to the staff credits
translations.csv      every string in English, Spanish and Catalan, for playtesting (generated)
tools/                generators, linter, GAP tool, graphics and font tools, CI
reference/            your private references (e.g. am2r-glossary.csv); gitignored
build/, dist/         generated files and CI outputs; gitignored
```

Upstream files touched: `Makefile` (one `include`); `#ifdef LANG_CA` wraps around vanilla code
in `src/data/text_data.c`, the EU half of `sCharacterWidths` in
`src/data/menus/pause_screen_data.c`, the Spanish helmet position in
`src/data/menus/game_over_data.c` and the EU `sCredits` in
`src/data/ending_and_gallery_data.c`; the `CA_PREVIEW` hook in `src/in_game.c`; and
`.github/workflows/catalan.yml`.

## Building

```sh
make extract REGION=eu                       # once, from your base ROM (below)
make eu                                      # vanilla: still matches mzm_eu.sha1
make eu LANG_CA=1                            # mzm_eu_ca.gba, Catalan in the Spanish slot
make eu LANG_CA=1 CA_SELFTEST=1              # plumbing self-test: byte-identical to vanilla
translation/ca/tools/ci.sh                   # everything CI runs, plus the .bps in dist/
```

Switching between these is safe: objects that depend on the mode are rebuilt automatically.
Tools need python3, cpp, libpng-dev (gbagfx) and, for the emulator tools, libmgba-dev.

## Translating text

Each `text/<category>.txt` line is `ID = "text"`, with the IDs of the Spanish pointer tables in
`src/data/text_data.c` and the same codes and escapes (`{COLOR(5)}`, `{A_button}`, `\n`). IDs left
out show in English, so the game always builds.

```sh
python3 translation/ca/tools/gap.py fix      # recompute the centring GAPs
python3 translation/ca/tools/lint.py         # check everything (--release: also completeness)
python3 translation/ca/tools/render.py out.png "{GAP(88)}{COLOR(5)}Raig llarg"   # quick preview
python3 translation/ca/tools/review.py       # refresh translations.csv (CI checks it is current)
```

`translations.csv` lists every string side by side (English, Spanish, Catalan, where it shows,
status) for checking during a playthrough. Write your remarks in its `notes` column:
regenerating keeps them.

The linter compares each entry with the Spanish original: control codes, line count, and width
(no line may pass 224 px). `gap.py vanilla` shows the GAP rules reproduce all 545 shipped GAPs.

## Graphics and font

```sh
make ca-tools                                            # builds the vendored gbagfx
python3 translation/ca/tools/gfx.py export --all         # vanilla assets -> build/gfx/*.png
cp translation/ca/build/gfx/menus/game_over/text_prompt_spanish.png \
   translation/ca/gfx/menus/game_over/                   # then edit it
python3 translation/ca/tools/font.py export 357 g.png    # a glyph, to edit
```

Keep each PNG's palette and indices; the build re-encodes the PNG and refuses graphics that
overflow their VRAM space or a fixed-size C array. Never commit the vanilla exports in `build/`.
`gfx_assets.json` records each asset's palette row and VRAM limit.

## Testing in the emulator

See `TESTING.md` for playtesting in mGBA, with the preview build that shows every message.

`make ca-emu-tools` builds `build/gbashot` (headless mGBA: scripted input, screenshots, save
states) and `build/bpscheck` (checks a patch with mGBA's own loader).

## Base ROM

Every build starts from your own EU dump. `tools/get_baserom.sh` puts it at `mzm_eu_baserom.gba`
in the repo root, and only after its SHA1 matches `mzm_eu.sha1`. It takes the ROM from, in order:

1. `mzm_eu_baserom.gba` already in the repo root (local builds; `*.gba` is gitignored),
2. `$BASEROM_DIR/mzm_eu_baserom.gba` (CI: a checkout of a private ROM repository),
3. `$BASEROM_EU_URL`, a `.gba` or a `.zip` holding exactly one `.gba` (CI: a private link).

### Local

```sh
cp /path/to/your/dump.gba mzm_eu_baserom.gba
translation/ca/tools/get_baserom.sh            # verifies the SHA1
make extract REGION=eu && make eu -j"$(nproc)" && sha1sum -c mzm_eu.sha1
```

### Base ROM in CI

`.github/workflows/catalan.yml` needs the ROM on every run. GitHub secrets are capped at 48 KB,
so the 8 MB ROM can't be a secret itself. Pick one of these.

**Option A (recommended): a private ROM repository with a read-only deploy key.** It stays
private, never expires, and is the same approach upstream metroidret/mzm uses.

1. Create a **private** repository, e.g. `GuillemRoca/mzm-roms`, and commit your dump at its root
   as `mzm_eu_baserom.gba`. It must never be public.
2. Make a key pair just for this (no passphrase):
   `ssh-keygen -t ed25519 -N "" -C "mzm-cat CI" -f mzm-roms-ci`
3. In **mzm-roms**: Settings → Deploy keys → Add deploy key. Paste `mzm-roms-ci.pub` and leave
   "Allow write access" **unchecked**.
4. In **mzm-cat**: Settings → Secrets and variables → Actions.
   - Secrets tab: new secret `BASEROM_REPO_KEY` = the full contents of `mzm-roms-ci` (the private key).
   - Variables tab: new variable `BASEROM_REPO` = `GuillemRoca/mzm-roms`.
5. Delete both key files.

The same with the `gh` CLI:

```sh
gh repo deploy-key add mzm-roms-ci.pub -R GuillemRoca/mzm-roms -t "mzm-cat CI"
gh secret set BASEROM_REPO_KEY -R GuillemRoca/mzm-cat < mzm-roms-ci
gh variable set BASEROM_REPO -R GuillemRoca/mzm-cat --body GuillemRoca/mzm-roms
rm mzm-roms-ci mzm-roms-ci.pub
```

**Option B: a private link.** Set the secret `BASEROM_EU_URL` to a direct download link for the
`.gba` or a `.zip` of it. Anyone with the link can download the ROM, so share it with nobody else.
Signed URLs that expire will break CI when they do.

Either way, the workflow never prints the source, uploads the ROM or caches it. Pull requests from
forks get no secrets, so their runs stop at "Get base ROM".

Upstream's own workflow (`.github/workflows/build.yml`, named "Ci") depends on upstream's private
ROM repository, so in this fork it fails whenever it triggers. That is on every pull request; its
push trigger is `master`, which this fork doesn't have. Disable it in the Actions tab rather than
editing it, so upstream merges stay clean.
