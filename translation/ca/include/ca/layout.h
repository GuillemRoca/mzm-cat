#ifndef CA_LAYOUT_H
#define CA_LAYOUT_H

// Per-language layout constants for Catalan in the German slot (LANG_CA=1).
// CA_SELFTEST builds get the vanilla German values, so the self-test stays byte-identical to
// vanilla. The Spanish slot keeps its vanilla values in every build.

// sGameOverSamusHeadXPositions[LANGUAGE_GERMAN] (src/data/menus/game_over_data.c), in
// sub-pixels (4 per pixel): the helmet cursor sits at the options' left edge + 2 px in every EU
// language. Our options (gfx/menus/game_over/text_prompt_german.png, from
// tools/gfx_game_over.py) start at x = 86, so 88 px. Vanilla German: 66 px.
#ifdef CA_SELFTEST
#define CA_GAME_OVER_SAMUS_HEAD_X (BLOCK_SIZE * 4 + EIGHTH_BLOCK_SIZE)
#else // !CA_SELFTEST
#define CA_GAME_OVER_SAMUS_HEAD_X (88 * 4)
#endif // CA_SELFTEST

// sEndingImageOam_ClearTime_German and sEndingImageOam_Collecting_German
// (include/data/ending_and_gallery_data.h): one typed sprite per letter of the two ending
// result lines. The Catalan lines are typed with copies of the Spanish tables
// (tools/genending.py, ca/ending_tables.inc), so they have the Spanish sizes: TEMPS TOTAL DE JOC
// (15 letters) and OBJECTES ACONSEGUITS (19). Vanilla German: 13 and 14. A size that doesn't
// match the generated tables is a compile error (conflicting types).
#ifdef CA_SELFTEST
#define CA_ENDING_CLEAR_TIME_LETTERS 13
#define CA_ENDING_COLLECTING_LETTERS 14
#else // !CA_SELFTEST
#define CA_ENDING_CLEAR_TIME_LETTERS 15
#define CA_ENDING_COLLECTING_LETTERS 19
#endif // CA_SELFTEST

#endif // CA_LAYOUT_H
