# Glossari

Terms for the Catalan translation, shared with AM2R-cat where they overlap.

- **APPROVED**: use exactly as written.
- **PROPOSED**: options in order of preference (1 is the default until confirmed), each with a
  one-line rationale. Every PROPOSED term in use is also listed in `notes/translator-notes.md`.

Naming policy: sentence case for item and UI names ("Raig de càrrega", not "Raig de Càrrega").
Proper names and the Galactic Federation keep their capitals. Location banners are drawn in
capitals by the game data itself ("NAU NODRISSA PIRATA"). In prose write "la Samus".

Optional: `tools/glossary.py import translation/ca/reference/am2r-glossary.<csv|tsv|md>` approves every
PROPOSED term that AM2R-cat already translates, and reports any APPROVED term that AM2R-cat
translates differently. The reference folder is gitignored.

Names marked *pause box* are drawn inside the fixed-size pause-screen graphics
(`menus/pause_screen/equipment_names_spanish`): check their rendered width there before
approving them.

## Characters and factions

| English | Spanish (EU) | Catalan | status | notes |
|---|---|---|---|---|
| Samus Aran | Samus Aran | Samus Aran | APPROVED | "la Samus" in prose. |
| Mother Brain | Mother Brain | Mother Brain | APPROVED | Untranslated, no article in titles; "la Mother Brain" in prose. |
| Ridley | Ridley | Ridley | APPROVED | Boss and area name. |
| Kraid | Kraid | Kraid | APPROVED | Boss and area name. |
| Mecha Ridley | Mecha Ridley | Mecha Ridley | APPROVED | |
| Chozo | Chozo | Chozo | APPROVED | |
| Galactic Federation | (not in MZM) | Federació Galàctica | PROPOSED | 1. Federació Galàctica: keeps its capitals per the naming policy; only reasonable rendering. |
| Space Pirates | piratas (Nave nodriza pirata) | pirates de l'espai | APPROVED | Literal, natural Catalan; your preference. |

## Places

| English | Spanish (EU) | Catalan | status | notes |
|---|---|---|---|---|
| Zebes | Zebes | Zebes | APPROVED | |
| Brinstar, Norfair, Crateria, Tourian, Chozodia | same | same | APPROVED | Area names stay unchanged. |
| Kraid, Ridley (areas) | KRAID, RIDLEY | KRAID, RIDLEY | APPROVED | |
| Mother Ship | nave nodriza | Nau nodrissa | APPROVED | |
| Zero Mission (Samus's first mission) | Misión Zero | Missió Zero | APPROVED | A name, like "Vestit Zero". |
| Space Pirate Mother Ship (banner) | NAVE NODRIZA PIRATA | Nau nodrissa pirata | APPROVED | Banner shows NAU NODRISSA PIRATA. |
| Planet Zebes | PLANETA ZEBES | Planeta Zebes | APPROVED | Banner text, as in Spanish and English. |
| Save Room | ESTACIÓN DE GUARDADO | Sala de guardat | APPROVED | Chosen by Guillem; same verb as the save prompts (Guardar？, Partida guardada). |
| Research Room | SALA DE INVESTIGACIÓN | Sala d'investigació | APPROVED | Literal, matches the other "Sala de…" rooms. |
| Map Room | SALA DE MAPAS | Sala de mapes | APPROVED | Matches the Spanish and the other rooms. |
| Chozo Ruins | RUINAS CHOZO | Ruïnes chozo | APPROVED | "chozo" as an adjective like "ruïnes romanes". |
| Starship (Samus's ship) | STARSHIP | Nau de la Samus | APPROVED | Says what it is; fits the banner. |

## Equipment and items

| English | Spanish (EU) | Catalan | status | notes |
|---|---|---|---|---|
| Power Suit | traje | Vestit | APPROVED | *pause box* |
| Varia Suit | Traje climático | Vestit climàtic | APPROVED | *pause box* |
| Gravity Suit | (Traje) gravitatorio | Vestit gravitatori | APPROVED | Your preference; mirrors "climàtic" as an adjective. *pause box* |
| Fully Powered Suit | traje totalmente equipado | Vestit complet | APPROVED | short. |
| Zero Suit | (no name in text) | 1. Vestit Zero<br>2. vestit zero | PROPOSED | 1. Your preference; "Zero" as the suit's name, like "Mission Zero".<br>2. Fully sentence case. |
| Energy Tank | Tanque de energía | Tanc d'energia | APPROVED | the established series term. |
| Missile | Misil | Míssil | APPROVED | Míssil: only option. *pause box* (MISIL) |
| Missile Tank | Tanque de misiles | Tanc de míssils | APPROVED | parallel to "Tanc d'energia". |
| Super Missile | Supermisil | Supermíssil | APPROVED | one word like the Spanish. *pause box* (SÚPER) |
| Super Missile Tank | Tanque de supermisiles | Tanc de supermíssils | APPROVED | Follows "Tanc de míssils" and "Supermíssil". |
| Bomb | Bomba | Bomba | APPROVED | Bomba: only option. *pause box* |
| Power Bomb | Bomba de energía | Bomba d'energia | APPROVED | |
| Power Bomb Tank | Tanque de bomba de energía | Tanc de bombes d'energia | APPROVED | |
| Long Beam | Rayo Largo | Raig llarg | APPROVED | short. *pause box* (LARGO) |
| Charge Beam | Rayo Recarga | Raig de càrrega | APPROVED | *pause box* (RECARGA) |
| Ice Beam | Rayo de Hielo | Raig de gel | APPROVED | parallel to the Spanish. *pause box* (HIELO) |
| Wave Beam | Rayo de Ondas | Raig d'ones | APPROVED | Your preference. *pause box* (ONDAS) |
| Plasma Beam | (Rayo) Plasma | Raig de plasma | APPROVED | Your preference. *pause box* (PLASMA) |
| Morph Ball | Morfosfera | Morfosfera | APPROVED | *pause box* |
| Speed Booster | Aceleración | Acceleració | APPROVED | *pause box* |
| Hi-Jump | Supersalto | Supersalt | APPROVED | *pause box* |
| Screw Attack | Salto en barrena | Atac espiral | APPROVED | *pause box* |
| Space Jump | Salto espacial | Salt espacial | APPROVED | Your preference; mirrors the Spanish. *pause box* |
| Power Grip | Agarre | Arrapada | APPROVED | *pause box* |
| Pistol (Zero Suit) | Pistola | Pistola | APPROVED | Pistola: only option. *pause box* |
| Unknown Item | Objeto desconocido | Objecte desconegut | APPROVED | literal. |
| Hatch (door) | escotilla | comporta | APPROVED | A sealed door that opens like a gate; reads as sci-fi. Used in the descriptions ("comportes vermelles"). |
| Charge Attack | Ataque carga | Atac de càrrega | APPROVED | Parallel to "Raig de càrrega". |
| Somersault (spin jump) | voltereta | tombarella (gir for short) | APPROVED | Standard Catalan for a somersault; "en ple gir" where space is short. |
| Damage (noun) | daño | dany | APPROVED | Standard; "mal" is more colloquial. "Ferir" for "damage enemies" (verb). |

## Enemies

MZM's text names no regular enemies; only these appear (messages, story, banners, credits).

| English | Spanish (EU) | Catalan | status | notes |
|---|---|---|---|---|
| Metroid (species) | Metroid | metroide / metroides | APPROVED | Your preference; adapted as a common noun, plural with -s. |
| Kraid, Ridley, Mecha Ridley, Mother Brain | same | same | APPROVED | See Characters. |

## UI terms

| English | Spanish (EU) | Catalan | status | notes |
|---|---|---|---|---|
| Save (verb) | Guardar | Guardar | APPROVED | Chosen by Guillem over "desar", to match "Sala de guardat". |
| Save complete | Datos almacenados | Partida guardada | APPROVED | |
| Yes / No | Sí / No | Sí / No | APPROVED | Only option; widths match the Spanish, so the cursor positions carry over. |
| Start Game | Jugar | Juga | APPROVED | Imperative, like the other menu commands (Softcatalà style). |
| Language (title menu) | Idioma | Idioma | APPROVED | Common in menus. |
| Copy / Erase / Options | COPIAR / BORRAR / OPCIONES | 1. Copia / Esborra / Opcions<br>2. Copiar / Esborrar / Opcions | PROPOSED | 1. Imperative commands (Softcatalà).<br>2. Infinitives like the Spanish. |
| Samus Data (file select title) | DATOS DE SAMUS | 1. Dades de la Samus<br>2. Partides | PROPOSED | 1. Literal, with the personal article.<br>2. Shorter, says what the screen holds. |
| Easy / Normal / Hard | FÁCIL / NORMAL / DIFÍCIL | Fàcil / Normal / Difícil | APPROVED | Only option; each label must fit 40 px (difficulty graphic). |
| Time Attack | TIME ATTACK | Contrarellotge | APPROVED | Natural Catalan sports term. |
| Map / Status (pause tabs) | MAPA / ESTADO | Mapa / Estat | PROPOSED | Only option. *pause box* |
| Change area (map) | CAMBIAR ZONA | 1. Canvia zona<br>2. Canvia d'àrea | PROPOSED | 1. Imperative per the menu convention, like the Italian "Cambia area"; drawn in the pause graphic (V drawn).<br>2. Uses "àrea" like the English, needs À. |
| Energy (status) | ENERGÍA | Energia | APPROVED | Only option. *pause box* |
| Beam (status group) | RAYO | Raig | APPROVED | Only option. *pause box* |
| Suit (status group) | TRAJE | Vestit | APPROVED | *pause box* |
| Misc (status group) | OTROS | Altres | APPROVED | Mirrors the Spanish. *pause box* |
| Gun (status group, suitless) | PISTOLA (item: LÁSER) | Arma (item: Pistola) | APPROVED | Follows the English GUN / PISTOL; the Spanish has PISTOLA / LÁSER. *pause box* |
| Gallery | Galería | Galeria | APPROVED | Only option. |
| Sound Test | Prueba de sonido | Prova de so | APPROVED | Literal. |
| Original Metroid | Metroid original | Metroid original | APPROVED | Only option. |
| Data file / save file (file select) | archivo | fitxer | APPROVED | The standard computing term ("Tria el fitxer…", "Fitxer A malmès"). |
| New (file select: new game) | Nuevo | Nova partida | APPROVED | Says what it starts. |
| Password (Time Attack) | Contraseña | Contrasenya | APPROVED | Only option. |
| Linking / link (Fusion link) | Conectando / conexión | Connectant / connexió | APPROVED | Only option. |
| Easy Sleep | salvapantallas (tab SALVAP.) | Mode repòs (tab REPÒS) | APPROVED | Describes the feature (the GBA sleeps); the pause tab says REPÒS (Ò drawn like the German Ä). |
| Try again? / Yes (continue) / No (quit) (game over) | ¿VOLVER A INTENTARLO? / SÍ (CONTINUAR) / NO (SALIR) | TORNAR-HO A PROVAR? / SÍ (CONTINUA) / NO (SURT) | APPROVED | Imperatives, as decided for menu commands. The hyphen is drawn for the prompt font (tools/gfx_game_over.py). |
| Mission Accomplished | ¡MISIÓN CUMPLIDA! | 1. Missió complerta!<br>2. Missió acomplerta! | PROPOSED | 1. Standard; buildable from the existing ending glyphs.<br>2. Also correct, more formal. |
| New Record | ¡NUEVO RÉCORD! | Nou rècord! | PROPOSED | Only option. |
