# Translator notes

Ambiguous lines and open decisions. Each entry: where, the options, the current choice, and
who still needs to confirm it.

## Decisions

### Middle dot glyph (font/glyphs/0357.png) — DECIDED
Option A: dot at mid x-height, width 2. Confirmed by Guillem at the Phase 2 checkpoint.

### Credits — DECIDED
A Catalan translation credit, alongside the other languages: in the TRANSLATION section of the
EU staff credits, after "ITALIAN / Massimo Maietti", comes "CATALAN / Guillem Roca Castany",
laid out like the other languages. Names are in `credits.txt`; `tools/gencredits.py` builds the credits
from the vanilla array. The rows added are taken from the empty lines before the copyright, so
the credits scroll for exactly as long as vanilla and stay in time with the music. The credits
fonts have no accents (the heading would read "CATALA"), so the heading is in English like the
other languages'. Checked in game.

## Terms used in the Message block — APPROVED

Approved by Guillem after the Message pilot playtest: Tanc d'energia, Tanc de míssils,
Supermíssil (Tanc de supermíssils), Bomba, Raig llarg, Raig de gel, Raig d'ones, Objecte
desconegut, Guardar (was "Desar", changed with the save room), Partida guardada, Vestit complet, Mode repòs (pause tab REPÒS).

## Terms used in the Location block — APPROVED

Approved by Guillem: Planeta Zebes, Sala de guardat (Guillem's choice over "Sala de desament"; the
save prompts use the same verb: Guardar？, Partida guardada), Sala de mapes, Ruïnes chozo, Sala d'investigació and Nau de la Samus (the
last two are never shown by the game). Area names (BRINSTAR … CHOZODIA) are kept, and NAU
NODRISSA PIRATA is APPROVED. All banners shown by the game were checked in game.

## Terms used in the Description block — APPROVED

Approved by Guillem:

| Term | Where | Notes |
|---|---|---|
| comporta (hatch) | Missiles, Super Missiles, Power Bombs | "Obren les comportes vermelles / verdes / grogues". |
| Atac de càrrega | Charge Beam | "Charge Attack". |
| tombarella, gir | Screw Attack, Space Jump | "Fes tombarelles…", "en ple gir" (short form in the same entry). |
| dany | Varia Suit, Gravity Suit | "Redueix el dany…". |

## Terms used in the Story block — APPROVED

Approved by Guillem:

| Term | ID | Notes |
|---|---|---|
| pirates de l'espai | STORY_TEXT_THE_TIMING | First use of "Space Pirates" in running text. |
| metroides (organismes metroides) | STORY_TEXT_EXTERMINATE | "Metroid organisms": adapted as a common noun, here an adjective. |
| Missió Zero | STORY_TEXT_PLANET_ZEBES | "My so-called Zero Mission". |

## Line notes (Story block)

Story screens take as many lines as the longest shipped language uses for that text (the
linter checks it): THE_TIMING has 7 lines (Spanish 6, German 7, English 8), so the Space
Pirates' attack and the "rather useless" pistol of the English stay. Lines are kept within the
widest shipped line of each text.

- **STORY_TEXT_PLANET_ZEBES**: "Planeta Zebes... Fa molt, en temps de pau, abans que el mal
  s'escampés per les cavernes, aquest lloc era casa meva. Ara, per fi, explicaré la meva
  primera batalla aquí... L'anomenada Missió Zero." ("haunted" as "s'escampés per": spread
  through). The signature keeps its vanilla position.
- **STORY_TEXT_THE_TIMING**: "La fuga no podia arribar en pitjor moment." for "The timing of
  my escape couldn't have been worse"; pluperfect for the attack that came before.
- **STORY_TEXT_COULD_I_SURVIVE**: two lines like the Spanish ("Aconseguiria sobreviure prou
  temps / per escapar?").
- **Intro subtitles** (EMERGENCY, EXTERMINATE, DEFEAT): under the typed English graphic, as
  in every language. Orders in the infinitive, like the Spanish ("Exterminar…", "I
  derrotar…"). "planeta Zebes" in lowercase in running text (IEC: generic noun + name); the
  banner keeps "PLANETA ZEBES". Mother Brain without an article, as an apposition.
- All six checked in game (intro after the language screen; story cutscenes with the preview
  L+R+Left).

## PROPOSED terms in use (FileScreen block)

Option 1 of each glossary row. To confirm:

| Term | Where | Notes |
|---|---|---|
| Juga / Juga (Link) | FILE_SCREEN_TEXT_START_GAME | Imperative (menu command). Seen in game. |
| fitxer | copy, erase, corrupt-file messages | "Tria el fitxer…", "Fitxer A malmès." |
| Continua / Nova partida / Nova contrarellotge | CONTINUE_NEW(_TIME_ATTACK) | Continue is a command (imperative); New is a noun phrase. |
| Dificultat, Nivell de dificultat, FÀCIL / NORMAL / DIFÍCIL | DIFFICULTY(_HARD) | Seen in game. |
| contrarellotge (Time Attack), Rècords de contrarellotge | several | Feminine: "la contrarellotge". |
| Galeria, Prova de so, Metroid original, OPCIONS | unlock messages | OPCIONS must match the options screen graphic when it is redrawn. |
| Contrasenya, Millor temps | Time Attack screens | |
| Connectant / connexió, cartutx | Fusion link messages | "Game Pak" = cartutx. |

## Line notes (FileScreen block)

- Each pop-up is drawn into one of four text areas (sFileScreenMessagesInfo); the linter now
  bounds every line by the widest shipped line in the same area, and the unlock messages
  (drawn elsewhere) by their own widest shipped line. Line counts are fixed as in the Spanish.
- Yes/No keep the Spanish GAP positions ("Sí" and "No" have the Spanish widths). The "Best
  Time" labels are centred in 96 px: GAP = floor((96 - w) / 2), a rule now in gap.py that
  reproduces all 10 vanilla ones.
- **Corrupt files**: "Fitxer A malmès. / Recuperant les / dades anteriors." and "Esborrant
  fitxer A..." (no article: "el fitxer C" was 2 px too wide for its area).
- **ERASE_ALL_REFORMAT**: "tornar a formatar" for "reformat".
- **ERASE_FILE_CONFIRM**: the three ideographic spaces hold the place of what is kept (as in
  every language); "(　　　no s'esborrarà)." like the Spanish.
- **LINKING_ERROR_TRY_AGAIN / CHECK_CONNECTION**: "torna-ho a provar", like the game over
  prompt.
- Seen in game: Juga and the difficulty menu. The copy and erase pop-ups need a file with a
  saved game, and the corrupt-file and Fusion link messages special conditions: not seen yet
  (widths checked by the linter only).

## Game over prompt (pilot graphic) — DECIDED

- `gfx/menus/game_over/text_prompt_spanish.png`, made by `tools/gfx_game_over.py` from the
  glyphs of the five vanilla prompts: "TORNAR-HO A PROVAR?" / "SÍ (CONTINUA)" / "NO (SURT)".
  Imperatives and the hyphenated "tornar-ho" chosen by Guillem; the hyphen isn't in any vanilla
  prompt, so it is drawn like the middle bar of the red E.
- No space before "?" (Catalan typography), unlike the EU art. The off-screen katakana label
  (a developer note, "Spanish") is dropped.
- Layout: options left-aligned at x = 86, helmet at 88 px (`include/ca/layout.h`, vanilla
  Spanish 82 px). Checked in game for both options.

## Pause menu names (menu_names graphic)

- `gfx/menus/pause_screen/menu_names_spanish.png`, made by `tools/gfx_menu_names.py`: L tab
  "REPÒS", R tab "ESTAT", area label "CANVIA ZONA" (both copies).
- No vanilla tab has an accented letter: Ò follows the German Ä of the label font (accent on top,
  4-row body), with a 2-px grave stroke (candidates a/b/c in the tool; c chosen). V isn't in any
  label font either and is drawn.
- REPÒS and ESTAT checked in game (map, world map, status screen). "CANVIA ZONA" fits its box
  (41 of 47 px) but isn't on screen at the start of the game: **not yet seen in game**.

## Equipment names (status screen graphic)

- `gfx/menus/pause_screen/equipment_names_spanish.png`, made by `tools/gfx_equipment_names.py`
  from the glyphs of the English, Spanish and Italian sheets. Every name has a fixed run of
  tiles (5 to 7, the POWER bomb only 4); names are left-aligned like vanilla. The headings'
  letters touch, so they are cut by hand; the item letters are cut automatically, keeping the
  vanilla kerning (LT) and word gap. ENERGIA is the Italian bar as is.
- Headings: ENERGIA, RAIG, MÍSSIL (the accent on the bar's top line, like ENERGÍA's in the
  Spanish item font; the Spanish heading drops it), BOMBA, VESTIT, ALTRES, ARMA (suitless).
- Items: LLARG, CÀRREGA, GEL, ONES, PLASMA, NORMAL, SÚPER, NORMAL, ENERGIA (31 of 31 px, like
  the Spanish ENERGÍA), CLIMÀTIC, GRAVITATORI, MORFOSFERA, ARRAPADA, ACCELERACIÓ, SUPERSALT,
  ATAC ESPIRAL, SALT ESPACIAL (55 of 55 px), PISTOLA.
- Checked in game with the normal suit (unknown items), the fully powered suit and suitless.

### Terms used in the equipment names — APPROVED

Approved by Guillem: Míssil (heading MÍSSIL), Vestit gravitatori (GRAVITATORI), Raig de plasma
(PLASMA), Salt espacial (SALT ESPACIAL), Pistola (PISTOLA), and the status groups Energia,
Raig, Altres and Arma (the suitless group, GUN in English).

## Unknown item names (revealed with the fully powered suit)

- `gfx/menus/pause_screen/map_screen_unknown_items_names_spanish.png`, made by
  `tools/gfx_unknown_items.py`: the three names drawn as sprites over the status screen bars
  while the fully powered suit reveals them. PLASMA stays; "SALTO ESPACIAL" (drawn without its
  space in the Spanish) becomes SALT ESPACIAL (54 of 55 px, with the space), GRAVITATORIO
  becomes GRAVITATORI, matching the equipment names. Letters are cut from the Spanish names,
  same font as the status screen items.
- Checked in game: preview L+R+Down twice plays the reveal; all three names flash in their bars.

## Language selector

- `gfx/menus/language_select/background.png`, made by `tools/gfx_language_select.py`: "Català"
  in the Spanish slot (5th entry), left-aligned like the other labels, 38 of 48 px, so the
  tilemap is unchanged. "a", "t" and "l" are cut from "Italiano"; the capital C (stair corners
  like the D of "Deutsch", mirrored) and the grave accent (rows 3-5 like the ñ tilde, 2-px
  stroke; candidates a/b in the tool, a chosen) are drawn. Checked in game, selected and not.

## Line notes (Message block)

- **Tanks: "obtingut"** for "acquired" throughout (tanks, maps, suit), and "augmentada" for
  "capacity increased". Alternatives: "aconseguit"; "ampliada" (closer to the Spanish).
- **MESSAGE_POWER_BOMB_TANK_ACQUIRED**: like the English, line 1 has no "obtingut" (the
  Spanish adds "almacenado"). Line 2, "Capacitat de bombes d'energia augmentada.", is the
  widest Message line at 208 px of 224.
- **MESSAGE_SAVE_PROMPT** — DECIDED: "Guardar？" exactly centred, like the English. The Spanish
  and Italian add an extra `{GAP(8)}` after the centring GAP; we don't (the linter accepts the
  GAP layout of either the Spanish or the English).
- **MESSAGE_WEAPON_RESUPPLY_COMPLETE**: "Reposició de l'armament / completada."
  ("resupply" = replenishment). Alternatives: "Armament recarregat / del tot.", or
  "Recàrrega de l'armament / completada." (parallel to the energy message, but loses the
  resupply/recharge distinction the English keeps).
- **MESSAGE_ENERGY_TANK_RECHARGE_COMPLETE**: "Recàrrega dels tancs / d'energia completada."
- **MESSAGE_WEAPONS_AND_ENERGY_RESTORED**: "Armament i energia / restablerts del tot."
  (masculine plural agreement for a mixed pair). Alternative: "completament restablerts".
- **Maps**: "Mapa de Brinstar obtingut." keeps the Spanish colour order (Mapa yellow, the area
  in its colour). Kraid and Ridley are the areas here, not the bosses. The Spanish has a double
  space before "adquirido" on the Mother Ship line; ours doesn't.
- **MESSAGE_FULLY_POWERED_SUIT**: "Has obtingut el vestit complet." for "You got your fully
  powered suit". Alternatives: "Ara tens el vestit complet.", "Has recuperat el vestit complet."
  (narratively she regains her suit's full power).
- **Escapes**: "Mecanisme d'autodestrucció activat! / Evacuació immediata!" uses an alarm-style
  noun like the Spanish, rather than an imperative ("Evacua immediatament!") addressed to Samus.
- **Easy Sleep** (three messages drawn together): "Vols activar el mode repòs？ / Per
  sortir-ne, prem / SELECT, L i R / alhora.". The verb ends message 35 as in the Spanish, so
  message 36 keeps the Spanish codes order.
- **MESSAGE_ENEMY_LOCATION_ABNORMAL**: a debug message (enemy placed outside a message frame);
  translated literally.
- **MESSAGE_DUMMY**: debug placeholder, left as is (identical.txt).

## Line notes (Description block)

Each line of a description is a page of its own (A turns the page), with an arrow drawn 10 px
after the text, so lines are kept to 206 px (vanilla goes up to 208) rather than 224.

- **Second person imperatives**, as in the messages: "Prem", "Mantén", "Fes", "Arrapa't".
- **"Obren les comportes…"**: plural verb, agreeing with the items (Míssils, Supermíssils,
  Bombes d'energia); the English and Spanish use a singular "Opens / Abre".
- **DESCRIPTION_TEXT_CHARGE_BEAM** — DECIDED: "Mantén B per carregar. Allibera i dispara."
  (Guillem's wording; "Deixa'l anar per disparar" didn't fit at 240 px).
- **DESCRIPTION_TEXT_SUPER_MISSILES**: "Arm with SELECT" becomes "Tria'ls amb SELECT" (SELECT
  switches to them); "Activa'ls" and "Arma'ls" were too wide with the SELECT glyph.
- **DESCRIPTION_TEXT_BOMBS**: two lines like the Spanish ("En morfosfera, prem B per /
  col·locar-ne una."); one line was 232 px.
- **DESCRIPTION_TEXT_GRAVITY_SUIT**: "damage from foes" as "dany rebut" (the Spanish "daño
  sufrido") so the sentence fits its two pages; lava protection kept as its own sentence.
- **DESCRIPTION_TEXT_SPACE_JUMP**: "en ple gir" on line 2 ("en plena tombarella" was 230 px).
- **DESCRIPTION_TEXT_PISTOL**: "Una pistola de càrrega automàtica." The vanilla text has no
  colour reset after "auto-charging" (the full stop is yellow in every language); the codes are
  kept as they are.
- Morph Ball is "morfosfera" in lowercase in running text, like "vestit complet".
- All 19 checked in game, every page, including the unknown-item text and the pistol.
