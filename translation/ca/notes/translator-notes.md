# Translator notes

Ambiguous lines and open decisions. Each entry: where, the options, the current choice, and
who still needs to confirm it.

## Decisions

### Middle dot glyph (font/glyphs/0357.png) — DECIDED
Option A: dot at mid x-height, width 2. Confirmed by Guillem at the Phase 2 checkpoint.

### Credits — OPEN
Keep the vanilla staff credits, or add a "CATALAN TRANSLATION" entry (fixed-size `sCredits`,
uppercase credits font without accents). To decide before release.

## PROPOSED terms in use (Message block)

Each is option 1 of its glossary row. Confirm or pick another; `glossary.md` then becomes
APPROVED and the lines below are updated.

| Term | Used in | Notes |
|---|---|---|
| Tanc d'energia | MESSAGE_ENERGY_TANK_ACQUIRED, ..._RECHARGE_COMPLETE ("tancs d'energia") | |
| Tanc de míssils | MESSAGE_MISSILE_TANK_ACQUIRED, MESSAGE_FIRST_MISSILE_TANK | |
| Supermíssil | MESSAGE_SUPER_MISSILE_TANK_ACQUIRED, MESSAGE_FIRST_SUPER_MISSILE_TANK ("Tanc de supermíssils") | Line 2 is 197 px of 224. |
| Bomba | MESSAGE_BOMB | Same word as the Spanish (in identical.txt). |
| Raig llarg, Raig de gel, Raig d'ones | MESSAGE_LONG_BEAM, MESSAGE_ICE_BEAM, MESSAGE_WAVE_BEAM | |
| Objecte desconegut | the three MESSAGE_UNKNOWN_ITEM_* | |
| Desar | MESSAGE_SAVE_PROMPT ("Desar？") | |
| Partida desada | MESSAGE_SAVE_COMPLETE | |
| Vestit complet | MESSAGE_FULLY_POWERED_SUIT ("el vestit complet", lowercase in prose) | |
| Mode repòs | MESSAGE_ACTIVATE_EASY_SLEEP | The pause screen's L tab still shows the Spanish graphic "SALVAP."; it must say the same (e.g. REPÒS) when menu_names is redrawn. |

## Line notes (Message block)

- **Tanks: "obtingut"** for "acquired" throughout (tanks, maps, suit), and "augmentada" for
  "capacity increased". Alternatives: "aconseguit"; "ampliada" (closer to the Spanish).
- **MESSAGE_POWER_BOMB_TANK_ACQUIRED**: like the English, line 1 has no "obtingut" (the
  Spanish adds "almacenado"). Line 2, "Capacitat de bombes d'energia augmentada.", is the
  widest Message line at 208 px of 224.
- **MESSAGE_SAVE_PROMPT**: keeps the Spanish (and Italian) extra `{GAP(8)}` after the
  centring GAP, so "Desar？" sits where the Spanish prompt does over Sí/No. Without it the
  text is exactly centred, as in English. Check in game which reads better.
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
