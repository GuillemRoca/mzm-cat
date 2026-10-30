#ifndef CA_LAYOUT_H
#define CA_LAYOUT_H

// Per-language layout constants for Catalan in the Spanish slot (LANG_CA=1).
// Values in sub-pixels (4 per pixel), like the tables they replace. CA_SELFTEST builds get the
// vanilla Spanish values, so the self-test stays byte-identical to vanilla.

// sGameOverSamusHeadXPositions[LANGUAGE_SPANISH] (src/data/menus/game_over_data.c): the
// helmet cursor sits at the options' left edge + 2 px in every EU language. Our options
// (gfx/menus/game_over/text_prompt_spanish.png, from tools/gfx_game_over.py) start at
// x = 86, so 88 px. Vanilla Spanish: 82 px.
#ifdef CA_SELFTEST
#define CA_GAME_OVER_SAMUS_HEAD_X (BLOCK_SIZE * 5 + EIGHTH_BLOCK_SIZE)
#else // !CA_SELFTEST
#define CA_GAME_OVER_SAMUS_HEAD_X (88 * 4)
#endif // CA_SELFTEST

#endif // CA_LAYOUT_H
