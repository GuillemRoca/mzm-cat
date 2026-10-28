# Translator notes

Ambiguous lines and open decisions. Each entry: where, the options, the current choice, and
who still needs to confirm it.

## Decisions

### Middle dot glyph (font/glyphs/0357.png) — DECIDED
Option A: dot at mid x-height, width 2. Confirmed by Guillem at the Phase 2 checkpoint.

### Credits — DECIDED
Add a Catalan translation credit (Guillem). `include/ca/credits.inc` replaces `sCredits[280..294]`,
the blank lines between the executive producer and the copyright: "CATALAN TRANSLATION" (blue)
and "Guillem Roca" (white), with the same entry count and height, so the credits scroll for as
long as vanilla and stay in time with the music. The heading is in English like every other
credit, and because the blue font has no accents ("TRADUCCIO AL CATALA" would lose them).

## Terms used in the Message block — APPROVED

Approved by Guillem after the Message pilot playtest: Tanc d'energia, Tanc de míssils,
Supermíssil (Tanc de supermíssils), Bomba, Raig llarg, Raig de gel, Raig d'ones, Objecte
desconegut, Desar, Partida desada, Vestit complet, Mode repòs (pause tab REPÒS).

## Terms used in the Location block — APPROVED

Approved by Guillem: Planeta Zebes, Sala de guardat (Guillem's choice over "Sala de desament"; the
verb stays "desar"), Sala de mapes, Ruïnes chozo, Sala d'investigació and Nau de la Samus (the
last two are never shown by the game). Area names (BRINSTAR … CHOZODIA) are kept, and NAU
NODRISSA PIRATA is APPROVED. All banners shown by the game were checked in game.

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
- **MESSAGE_SAVE_PROMPT** — DECIDED: "Desar？" exactly centred, like the English. The Spanish
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
