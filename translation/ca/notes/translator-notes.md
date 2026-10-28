# Translator notes

Ambiguous lines and open decisions. Each entry: where, the options, the current choice, and
who still needs to confirm it.

## Decisions

### Middle dot glyph (font/glyphs/0357.png) — DECIDED
Option A: dot at mid x-height, width 2. Confirmed by Guillem at the Phase 2 checkpoint.

### Credits — OPEN
Keep the vanilla staff credits, or add a "CATALAN TRANSLATION" entry (fixed-size `sCredits`,
uppercase credits font without accents). To decide before release.

## Terms used in the Message block — APPROVED

Approved by Guillem after the Message pilot playtest: Tanc d'energia, Tanc de míssils,
Supermíssil (Tanc de supermíssils), Bomba, Raig llarg, Raig de gel, Raig d'ones, Objecte
desconegut, Desar, Partida desada, Vestit complet, Mode repòs (pause tab REPÒS).

## PROPOSED terms in use (Location block)

Option 1 of each glossary row, in capitals as the banners are drawn. To confirm:

| Term | ID | Notes |
|---|---|---|
| Planeta Zebes | LT_PLANET_ZEBES | Same as the Spanish (identical.txt). |
| Sala de desament | LT_SAVE_ROOM | Every save room banner. |
| Sala de mapes | LT_MAP_ROOM | Every map station banner. |
| Ruïnes chozo | LT_CHOZO_RUINS | First Ï on screen; checked in game. |
| Sala d'investigació | LT_RESEARCH_ROOM | Never shown by the game. The Japanese text says "recharge room". |
| Nau de la Samus | LT_STARSHIP | Never shown by the game. |

Area names (BRINSTAR … CHOZODIA) are kept, and NAU NODRISSA PIRATA is APPROVED.

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
