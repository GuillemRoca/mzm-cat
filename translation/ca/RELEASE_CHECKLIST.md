# Release checklist

Copy this list into the release issue and tick every item. A release is a `.bps` against the
vanilla EU ROM (SHA1 `0fd107445a42e6f3a3e5ce8c865f412583179903`); never distribute a ROM.

## Build and CI

- [ ] CI green on the release commit, run with **release mode** (Actions → Catalan → Run
      workflow → release): lint has 0 errors, 0 warnings, 0 TODOs and 127/127 translated.
- [ ] Vanilla EU still matches `mzm_eu.sha1`, and the LANG_CA self-test is byte-identical (CI).
- [ ] `translation/ca/VERSION` bumped (e.g. `1.0.0`), committed and tagged `ca-v1.0.0`; the patch
      file name carries that version.
- [ ] `gap.py check` clean; `gfx.py roundtrip` all identical.
- [ ] Every PROPOSED glossary term in use is confirmed (APPROVED) or listed as an open choice
      in `notes/translator-notes.md`.

## Graphics (all 17 language assets reviewed)

- [ ] Pause screen: equipment names, menu names, unknown-item names. Every name checked for
      width inside its fixed box (`gfx.py export` to compare with the Spanish).
- [ ] Area names (map, Chozo statue hints, minimap): unchanged by policy; confirmed on screen.
- [ ] Erase SRAM: question and confirmation.
- [ ] Title screen: menu top and bottom.
- [ ] Game over prompt, with `sGameOverSamusHeadXPositions[LANGUAGE_SPANISH]` adjusted.
- [ ] File select: options, large text, difficulty labels (40 px each).
- [ ] Ending: text, typed-letter OAM frames, numbers/misc, "New record".
- [ ] "Mission Accomplished" OAM frame.
- [ ] Language selector shows "Català" in the Spanish slot.

## Playthrough coverage (Catalan slot, real hardware or mGBA)

- [ ] Language selector → title → file select: new file, copy, erase, erase all, difficulty,
      options (gallery, sound test, time attack records, original Metroid when unlocked).
- [ ] Intro: "Emergency order" sequence and the Planet Zebes prologue.
- [ ] Every item pickup banner, including all three Unknown Items and the Fully Powered Suit.
- [ ] Save station (prompt, Yes/No, complete), map stations (all five), recharge stations.
- [ ] Every area and room banner, including Chozo Ruins and the Mother Ship.
- [ ] Pause screen: map, status, every equipment description (both pages where there are two).
- [ ] Easy Sleep prompt and messages.
- [ ] Zebes escape, Zero Suit section (story text, pistol description), Chozodia escape,
      Mission Accomplished.
- [ ] Ending: clear time, collection rate, New record, "next mission" line, credits.
- [ ] Game over prompt (both options).
- [ ] Time Attack and its password/ID screen; Fusion link messages (at least the error ones).

## Credits

- [ ] Decision recorded in `notes/translator-notes.md`: keep the vanilla credits, or add a
      Catalan translation credit (needs extra entries in the fixed-size `sCredits` array, which
      uses its own uppercase font).

## Patch

- [ ] Publish only `mzm-cat-<version>.bps`, never the `-PREVIEW-TEST-ONLY` patch (test
      shortcuts) or any ROM.
- [ ] Patch applied with Flips and with Rom Patcher JS to a **clean EU dump** (SHA1 above): the
      result boots and matches the CI build's SHA1.
- [ ] Vanilla EU saves load and play correctly with the patched ROM (language slot = Catalan).
- [ ] Release notes: base ROM name and SHA1, version, how to apply, credits, licence.
