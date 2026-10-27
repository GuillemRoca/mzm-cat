# Metroid: Zero Mission en català

A Catalan fan translation built from this decompilation. Catalan replaces the Spanish slot
(`LANGUAGE_SPANISH`) of the EU build, and releases are `.bps` patches against the vanilla EU ROM
(SHA1 `0fd107445a42e6f3a3e5ce8c865f412583179903`, also in `mzm_eu.sha1`). Everything about the
translation lives under `translation/ca/`. The ROM is never committed or distributed.

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
