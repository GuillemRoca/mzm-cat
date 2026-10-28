# Testing the Catalan build in mGBA

Two builds come out of CI (Actions → Catalan → the run → Artifacts → `mzm-cat-<commit>`):

- `mzm-cat-<version>.bps`: the real game, what a release ships.
- `mzm-cat-<version>-PREVIEW-TEST-ONLY.bps`: the same game plus two test shortcuts. Never
  distribute it.

Locally, `make eu LANG_CA=1` and `make eu LANG_CA=1 CA_PREVIEW=1` build the same two ROMs
(`mzm_eu_ca.gba`, `mzm_eu_ca_preview.gba`).

## Load it in mGBA

1. Copy your EU dump (SHA1 `0fd107445a42e6f3a3e5ce8c865f412583179903`) to a folder as
   `mzm.gba`, and the patch next to it as `mzm.bps`. mGBA applies a `.bps` with the same name
   automatically (Flips or Rom Patcher JS work too).
2. Open `mzm.gba`. Default keys: A = X, B = Z, L = A, R = S, Start = Enter, Select = Backspace.
   Save state: Shift+F1…F9; load: F1…F9.
3. On the language screen pick the **5th entry ("Español")**: that slot is Catalan. Its label
   is still the Spanish graphic until the language selector is redrawn.
4. Title: press Start, then A on the first option. File A → A → pick a difficulty. Skip the
   intro with A. Once Samus can move, save a state (Shift+F1) to come back here.

Graphics that aren't redrawn yet (title, file select, pause screen, ending) still show Spanish;
text that isn't translated yet shows in English.

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
| 23 | `MESSAGE_SAVE_PROMPT` | Desar？ / SíNo |
| 24 | `MESSAGE_SAVE_COMPLETE` | Partida desada |
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

## Game over prompt (pilot graphic)

Preview build: hold **L + R** and press **A**. Energy drops to 0 and the game over screen
appears: "TORNAR A PROVAR? / SÍ (CONTINUA) / NO (SURT)". Up/Down moves the Samus helmet, which
must sit just left of the option text for both options. In the release build, die normally.

## Where the messages appear in normal play

Item and tank banners appear when collecting them, "Desar？ / Partida desada" at any save
station, "Mapa de … obtingut." at map stations, the recharge messages at Chozo statues and
recharge stations, the escape messages after Mother Brain and in Chozodia, and "Has obtingut el
vestit complet." after the ruins test. `MESSAGE_ENEMY_LOCATION_ABNORMAL` is a debug message and
`MESSAGE_DUMMY` a placeholder: neither appears in normal play.
