# Glossari

Terms for the Catalan translation, shared with AM2R-cat where they overlap.

- **APPROVED**: use exactly as written.
- **PROPOSED**: options in order of preference (1 is the default until confirmed), each with a
  one-line rationale. Every PROPOSED term in use is also listed in `notes/translator-notes.md`.

Naming policy: sentence case for item and UI names ("Raig de càrrega", not "Raig de Càrrega").
Proper names and the Galactic Federation keep their capitals. Location banners are drawn in
capitals by the game data itself ("NAU NODRISSA PIRATA"). In prose write "la Samus".

`tools/glossary.py import translation/ca/reference/am2r-glossary.<csv|tsv|md>` approves every
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
| Space Pirates | piratas (Nave nodriza pirata) | 1. pirates de l'espai<br>2. pirates espacials<br>3. pirates | PROPOSED | 1. Literal, natural Catalan; your preference.<br>2. Adjectival like the Spanish, a little more technical.<br>3. For tight boxes, where context makes "de l'espai" redundant. |

## Places

| English | Spanish (EU) | Catalan | status | notes |
|---|---|---|---|---|
| Zebes | Zebes | Zebes | APPROVED | |
| Brinstar, Norfair, Crateria, Tourian, Chozodia | same | same | APPROVED | Area names stay unchanged. |
| Kraid, Ridley (areas) | KRAID, RIDLEY | KRAID, RIDLEY | APPROVED | |
| Mother Ship | nave nodriza | Nau nodrissa | APPROVED | |
| Space Pirate Mother Ship (banner) | NAVE NODRIZA PIRATA | Nau nodrissa pirata | APPROVED | Banner shows NAU NODRISSA PIRATA. |
| Planet Zebes | PLANETA ZEBES | 1. Planeta Zebes<br>2. Zebes | PROPOSED | 1. Banner text, as in Spanish and English.<br>2. Shorter, if the banner ever needs it. |
| Save Room | ESTACIÓN DE GUARDADO | 1. Sala de desament<br>2. Estació de desament | PROPOSED | 1. Your preference; "desar" is the standard computing verb.<br>2. Mirrors the Spanish "estación", fits the save pod. |
| Research Room | SALA DE INVESTIGACIÓN | 1. Sala d'investigació<br>2. Laboratori | PROPOSED | 1. Literal, matches the other "Sala de…" rooms.<br>2. Shorter and natural, but loses the parallel. |
| Map Room | SALA DE MAPAS | 1. Sala de mapes<br>2. Sala del mapa | PROPOSED | 1. Matches the Spanish and the other rooms.<br>2. Each room holds one area's map; slightly more precise. |
| Chozo Ruins | RUINAS CHOZO | 1. Ruïnes chozo<br>2. Ruïnes dels chozo | PROPOSED | 1. "chozo" as an adjective like "ruïnes romanes"; first use of Ï on screen.<br>2. Possessive, clearer but longer. |
| Starship (Samus's ship) | STARSHIP | 1. Nau de la Samus<br>2. Starship | PROPOSED | 1. Says what it is; fits the banner.<br>2. Kept as a name, as the Spanish did. |

## Equipment and items

| English | Spanish (EU) | Catalan | status | notes |
|---|---|---|---|---|
| Power Suit | traje | Vestit | APPROVED | *pause box* |
| Varia Suit | Traje climático | Vestit climàtic | APPROVED | *pause box* |
| Gravity Suit | (Traje) gravitatorio | 1. Vestit gravitatori<br>2. Vestit de gravetat | PROPOSED | 1. Your preference; mirrors "climàtic" as an adjective. *pause box*<br>2. Noun complement; also common. |
| Fully Powered Suit | traje totalmente equipado | Vestit complet | APPROVED | short. |
| Zero Suit | (no name in text) | 1. Vestit Zero<br>2. vestit zero | PROPOSED | 1. Your preference; "Zero" as the suit's name, like "Mission Zero".<br>2. Fully sentence case. |
| Energy Tank | Tanque de energía | Tanc d'energia | APPROVED | the established series term. |
| Missile | Misil | Míssil | PROPOSED | 1. Míssil: only option. *pause box* (MISIL) |
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
| Plasma Beam | (Rayo) Plasma | 1. Raig de plasma<br>2. Raig plasmàtic | PROPOSED | 1. Your preference. *pause box* (PLASMA)<br>2. Adjective, less natural. |
| Morph Ball | Morfosfera | Morfosfera | APPROVED | *pause box* |
| Speed Booster | Aceleración | Acceleració | APPROVED | *pause box* |
| Hi-Jump | Supersalto | Supersalt | APPROVED | *pause box* |
| Screw Attack | Salto en barrena | Atac espiral | APPROVED | *pause box* |
| Space Jump | Salto espacial | 1. Salt espacial<br>2. Salt a l'espai | PROPOSED | 1. Your preference; mirrors the Spanish. *pause box*<br>2. More literal, longer. |
| Power Grip | Agarre | Arrapada | APPROVED | *pause box* |
| Pistol (Zero Suit) | Pistola | Pistola | PROPOSED | 1. Pistola: only option. *pause box* |
| Unknown Item | Objeto desconocido | Objecte desconegut | APPROVED | literal. |

## Enemies

MZM's text names no regular enemies; only these appear (messages, story, banners, credits).

| English | Spanish (EU) | Catalan | status | notes |
|---|---|---|---|---|
| Metroid (species) | Metroid | 1. metroide / metroides<br>2. Metroid (invariable) | PROPOSED | 1. Your preference; adapted as a common noun, plural with -s.<br>2. Kept as in English and Spanish, but awkward in Catalan plurals. |
| Kraid, Ridley, Mecha Ridley, Mother Brain | same | same | APPROVED | See Characters. |

## UI terms

| English | Spanish (EU) | Catalan | status | notes |
|---|---|---|---|---|
| Save (verb) | Guardar | Desar | APPROVED | the standard computing verb (Softcatalà). |
| Save complete | Datos almacenados | Partida desada | APPROVED | |
| Yes / No | Sí / No | Sí / No | PROPOSED | Only option; widths match the Spanish, so the cursor positions carry over. |
| Start Game | Jugar | 1. Juga<br>2. Comença la partida<br>3. Jugar | PROPOSED | 1. Imperative, like the other menu commands (Softcatalà style).<br>2. Literal, may not fit.<br>3. Infinitive, mirrors the Spanish. |
| Language (title menu) | Idioma | 1. Idioma<br>2. Llengua | PROPOSED | 1. Common in menus.<br>2. Preferred by IEC usage for languages as such. |
| Copy / Erase / Options | COPIAR / BORRAR / OPCIONES | 1. Copia / Esborra / Opcions<br>2. Copiar / Esborrar / Opcions | PROPOSED | 1. Imperative commands (Softcatalà).<br>2. Infinitives like the Spanish. |
| Samus Data (file select title) | DATOS DE SAMUS | 1. Dades de la Samus<br>2. Partides | PROPOSED | 1. Literal, with the personal article.<br>2. Shorter, says what the screen holds. |
| Easy / Normal / Hard | FÁCIL / NORMAL / DIFÍCIL | Fàcil / Normal / Difícil | PROPOSED | Only option; each label must fit 40 px (difficulty graphic). |
| Time Attack | TIME ATTACK | 1. Contrarellotge<br>2. Time Attack | PROPOSED | 1. Natural Catalan sports term.<br>2. Kept as in the Spanish. |
| Map / Status (pause tabs) | MAPA / ESTADO | Mapa / Estat | PROPOSED | Only option. *pause box* |
| Change area (map) | CAMBIAR ZONA | 1. Canvia zona<br>2. Canvia d'àrea | PROPOSED | 1. Imperative per the menu convention, like the Italian "Cambia area"; drawn in the pause graphic (V drawn).<br>2. Uses "àrea" like the English, needs À. |
| Energy (status) | ENERGÍA | Energia | PROPOSED | Only option. *pause box* |
| Beam (status group) | RAYO | Raig | PROPOSED | Only option. *pause box* |
| Suit (status group) | TRAJE | Vestit | APPROVED | *pause box* |
| Misc (status group) | OTROS | 1. Altres<br>2. Diversos | PROPOSED | 1. Mirrors the Spanish. *pause box*<br>2. Slightly more precise. |
| Gallery | Galería | Galeria | PROPOSED | Only option. |
| Sound Test | Prueba de sonido | 1. Prova de so<br>2. Test de so | PROPOSED | 1. Literal.<br>2. Shorter, common in Catalan games. |
| Original Metroid | Metroid original | Metroid original | PROPOSED | Only option. |
| Easy Sleep | salvapantallas (tab SALVAP.) | Mode repòs (tab REPÒS) | APPROVED | Describes the feature (the GBA sleeps); the pause tab says REPÒS (Ò drawn like the German Ä). |
| Try again? / Yes (continue) / No (quit) (game over) | ¿VOLVER A INTENTARLO? / SÍ (CONTINUAR) / NO (SALIR) | TORNAR-HO A PROVAR? / SÍ (CONTINUA) / NO (SURT) | APPROVED | Imperatives, as decided for menu commands. The hyphen is drawn for the prompt font (tools/gfx_game_over.py). |
| Mission Accomplished | ¡MISIÓN CUMPLIDA! | 1. Missió complerta!<br>2. Missió acomplerta! | PROPOSED | 1. Standard; buildable from the existing ending glyphs.<br>2. Also correct, more formal. |
| New Record | ¡NUEVO RÉCORD! | Nou rècord! | PROPOSED | Only option. |
