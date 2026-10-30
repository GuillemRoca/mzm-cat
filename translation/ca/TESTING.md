# Testing the Catalan build in mGBA

Two builds come out of CI (Actions → Catalan → the run → Artifacts → `mzm-cat-<commit>`):

- `mzm-cat-<version>.bps`: the real game, what a release ships.
- `mzm-cat-<version>-PREVIEW-TEST-ONLY.bps`: the same game plus seven test shortcuts. Never
  distribute it.

Locally, `make eu LANG_CA=1` and `make eu LANG_CA=1 CA_PREVIEW=1` build the same two ROMs
(`mzm_eu_ca.gba`, `mzm_eu_ca_preview.gba`).

## Load it in mGBA

1. Copy your EU dump (SHA1 `0fd107445a42e6f3a3e5ce8c865f412583179903`) to a folder as
   `mzm.gba`, and the patch next to it as `mzm.bps`. mGBA applies a `.bps` with the same name
   automatically (Flips or Rom Patcher JS work too).
2. Open `mzm.gba`. Default keys: A = X, B = Z, L = A, R = S, Start = Enter, Select = Backspace.
   Save state: Shift+F1…F9; load: F1…F9.
3. On the language screen pick the **5th entry ("Català")**: it is the Spanish slot.
4. Title: press Start, then A on the first option. File A → A → pick a difficulty. Skip the
   intro with A. Once Samus can move, save a state (Shift+F1) to come back here.

Every graphic of the Spanish slot is redrawn in Catalan; the area names of the map are shared by
all languages and stay as they are.

## Every Message line (preview build)

Hold **L + R** and press **SELECT**: the next message banner appears, in the order below, then
wraps around. Press A or B to close it. The banner only shows the text: no item is given, no
save happens and the escape timer doesn't start.

| Press | ID | Catalan |
|---|---|---|
| 1 | `MESSAGE_DUMMY` | DUMMY MESSAGE (OBJ Cell B1) |
| 2 | `MESSAGE_ENERGY_TANK_ACQUIRED` | Tanc d'energia obtingut. / Capacitat d'energia augmentada. |
| 3 | `MESSAGE_MISSILE_TANK_ACQUIRED` | Tanc de míssils obtingut. / Capacitat de míssils augmentada. |
| 4 | `MESSAGE_FIRST_MISSILE_TANK` | Tanc de míssils |
| 5 | `MESSAGE_SUPER_MISSILE_TANK_ACQUIRED` | Tanc de supermíssils obtingut. / Capacitat de supermíssils augmentada. |
| 6 | `MESSAGE_FIRST_SUPER_MISSILE_TANK` | Tanc de supermíssils |
| 7 | `MESSAGE_POWER_BOMB_TANK_ACQUIRED` | Tanc de bombes d'energia / Capacitat de bombes d'energia augmentada. |
| 8 | `MESSAGE_FIRST_POWER_BOMB_TANK` | Tanc de bombes d'energia |
| 9 | `MESSAGE_LONG_BEAM` | Raig llarg |
| 10 | `MESSAGE_CHARGE_BEAM` | Raig de càrrega |
| 11 | `MESSAGE_ICE_BEAM` | Raig de gel |
| 12 | `MESSAGE_WAVE_BEAM` | Raig d'ones |
| 13 | `MESSAGE_UKNOWN_ITEM_PLASMA` | Objecte desconegut |
| 14 | `MESSAGE_BOMB` | Bomba |
| 15 | `MESSAGE_VARIA_SUIT` | Vestit climàtic |
| 16 | `MESSAGE_UNKNOWN_ITEM_GRAVITY` | Objecte desconegut |
| 17 | `MESSAGE_MORPH_BALL` | Morfosfera |
| 18 | `MESSAGE_SPEED_BOOSTER` | Acceleració |
| 19 | `MESSAGE_HIGH_JUMP` | Supersalt |
| 20 | `MESSAGE_SCREW_ATTACK` | Atac espiral |
| 21 | `MESSAGE_UNKNOWN_ITEM_SPACE_JUMP` | Objecte desconegut |
| 22 | `MESSAGE_POWER_GRIP` | Arrapada |
| 23 | `MESSAGE_SAVE_PROMPT` | Guardar？ / SíNo |
| 24 | `MESSAGE_SAVE_COMPLETE` | Partida guardada |
| 25 | `MESSAGE_WEAPON_RESUPPLY_COMPLETE` | Reposició de l'armament / completada. |
| 26 | `MESSAGE_ENERGY_TANK_RECHARGE_COMPLETE` | Recàrrega dels tancs / d'energia completada. |
| 27 | `MESSAGE_WEAPONS_AND_ENERGY_RESTORED` | Armament i energia / restablerts del tot. |
| 28 | `MESSAGE_BRINSTAR_MAP_ACQUIRED` | Mapa de Brinstar obtingut. |
| 29 | `MESSAGE_KRAID_MAP_ACQUIRED` | Mapa de Kraid obtingut. |
| 30 | `MESSAGE_NORFAIR_MAP_ACQUIRED` | Mapa de Norfair obtingut. |
| 31 | `MESSAGE_RIDLEY_MAP_ACQUIRED` | Mapa de Ridley obtingut. |
| 32 | `MESSAGE_MOTHER_SHIP_MAP_ACQUIRED` | Mapa de la nau nodrissa obtingut. |
| 33 | `MESSAGE_FULLY_POWERED_SUIT` | Has obtingut el vestit complet. |
| 34 | `MESSAGE_ZEBES_ESCAPE` | Mecanisme d'autodestrucció activat! / Evacuació immediata! |
| 35 | `MESSAGE_CHOZODIA_ESCAPE` | Mecanisme d'autodestrucció activat! / Evacuació immediata! |
| 36 | `MESSAGE_ENEMY_LOCATION_ABNORMAL` | Posició anòmala de l'enemic. / Revisa la posició del missatge. |

The last three messages are the Easy Sleep screen. In any build: **Start** (pause), then **L** on
the map screen. A on "No" closes it; "Sí" puts the GBA to sleep until Select + L + R.

## Every Location banner (preview build)

Hold **L + R** and press **B**: the next area or room banner appears, as a room load would show
it (area names at the bottom, rooms in the middle). Save and map room banners only stay for
under a second, as in vanilla.

| Press | ID | Catalan |
|---|---|---|
| 1 | `LT_BRINSTAR` | BRINSTAR |
| 2 | `LT_KRAID` | KRAID |
| 3 | `LT_NORFAIR` | NORFAIR |
| 4 | `LT_RIDLEY` | RIDLEY |
| 5 | `LT_TOURIAN` | TOURIAN |
| 6 | `LT_CRATERIA` | CRATERIA |
| 7 | `LT_CHOZODIA` | CHOZODIA |
| 8 | `LT_MOTHERSHIP` | NAU NODRISSA PIRATA |
| 9 | `LT_PLANET_ZEBES` | PLANETA ZEBES |
| 10 | `LT_SAVE_ROOM` | SALA DE GUARDAT |
| 11 | `LT_RESEARCH_ROOM` | SALA D'INVESTIGACIÓ |
| 12 | `LT_MAP_ROOM` | SALA DE MAPES |
| 13 | `LT_CHOZO_RUINS` | RUÏNES CHOZO |
| 14 | `LT_STARSHIP` | NAU DE LA SAMUS |

Only the first nine IDs, plus the save room, map room and Chozo ruins, appear in normal play
(entering the area or room). `LT_RESEARCH_ROOM` and `LT_STARSHIP` are never used by the game;
`LT_UNUSED_*` are placeholders.

## Every equipment description (preview build)

Hold **L + R** and press **Down**: Samus gets every item and full ammo. Pause (Start), press R
for the status screen, and move over each item: its description types out at the bottom, one
line per page (A for the next page). Every page must fit, with the arrow after the text.

Press **L + R + Down** again (before pausing) to cycle the suit: normal (Plasma Beam, Gravity
Suit and Space Jump show "Anàlisi no concloent."), fully powered (their real descriptions),
suitless (the pistol). Switching to fully powered plays the reveal of the unknown items, as
after the Chozo ruins test: PLASMA, GRAVITATORI and SALT ESPACIAL flash in their bars (A goes
through their descriptions; afterwards Samus is back at the start of Brinstar). In the release
build, the descriptions appear as items are collected.

The same screens show the equipment names (the graphic): headings ENERGIA, RAIG, MÍSSIL,
BOMBA, VESTIT, ALTRES (ARMA when suitless) and every item name, each inside its bar.

## Story texts

- Intro: after the language screen, don't press anything. "Ordre d'emergència", "Exterminar
  tots els organismes metroides del planeta Zebes..." and "I derrotar la forma de vida
  mecànica, Mother Brain." appear under the typed English graphic.
- Preview build: hold **L + R** and press **Left** for the next story cutscene: the Planet
  Zebes prologue, the Mother Ship monologue (7 lines), "Aconseguiria sobreviure prou temps per
  escapar?". A ends each one; Samus is back in the room afterwards.
- In the release build: the prologue at the start of a new file; the other two after the Zebes
  escape.

## Title screen

After the intro (or Start): "JUGA" and "Idioma", centred one above the other; Up/Down moves the
highlight between them.

## Erase-save screens

Hold L + R while the game starts: "Vols esborrar totes les dades guardades?", No / Sí; Sí
opens "Segur que vols esborrar totes les dades?" (No / Sí). Answer No to keep the saves.

## File select

The file select shows "DADES DE LA SAMUS" and COPIA / ESBORRA / OPCIONS; OPCIONS lists SO and
CONNEXIÓ A METROID FUSION (the other options appear as they are unlocked). Title → JUGA → file select. On an empty file, A shows "Juga" and then "Dificultat / FÀCIL /
NORMAL". With a saved game (save once at a save station): A on that file shows "Continua /
Nova partida", COPIAR shows "Tria el fitxer que vols copiar." and "Tria el fitxer on vols
copiar les dades.", BORRAR "Tria el fitxer que vols esborrar." and "Vols esborrar aquest
fitxer?". Time Attack, the unlock messages and the Fusion link need later saves or a second
GBA.

## Game over prompt (pilot graphic)

Preview build: hold **L + R** and press **A**. Energy drops to 0 and the game over screen
appears: "TORNAR-HO A PROVAR? / SÍ (CONTINUA) / NO (SURT)". Up/Down moves the Samus helmet, which
must sit just left of the option text for both options. In the release build, die normally.

## Credits

Preview build: hold **L + R** and press **Up**. The credits start right away (no ending save is
written). In the TRANSLATION section, after "ITALIAN / Massimo Maietti", comes
"CATALAN / Guillem Roca Castany" (`credits.txt`); the credits must still end in time with the
music. In the release build, finish the game.

## Ending

Preview build: hold **L + R** and press **Right**. The end of the Chozodia escape plays: the
ship takes off and "MISSIÓ COMPLERTA!" appears, then the credits. After the credits (a little over
two minutes; **L + R + Up** starts them directly), the results screen types "TEMPS TOTAL
DE JOC" and "OBJECTES ACONSEGUITS" letter by letter, then shows them whole with the time and
the percentage, and "Fins a la propera missió!" in blue underneath. With a new best time, the box
beside the time reads "NOU / RÈCORD!". In the
release build, finish the game.

## Where the messages appear in normal play

Item and tank banners appear when collecting them, "Guardar？ / Partida guardada" at any save
station, "Mapa de … obtingut." at map stations, the recharge messages at Chozo statues and
recharge stations, the escape messages after Mother Brain and in Chozodia, and "Has obtingut el
vestit complet." after the ruins test. `MESSAGE_ENEMY_LOCATION_ABNORMAL` is a debug message and
`MESSAGE_DUMMY` a placeholder: neither appears in normal play.
