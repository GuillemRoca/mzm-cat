# Edited graphics

Put an edited asset here at its path under `data/` without `.gfx.lz`, as a PNG:
`gfx/menus/game_over/text_prompt_german.png` overrides `data/menus/game_over/text_prompt_german.gfx.lz`
when building with `LANG_CA=1`. Catalan takes the German slot: language-specific graphics are the
`*_german` assets (most are composed on the Spanish sheets by the `tools/gfx_*.py` scripts). Start from `tools/gfx.py export KEY` and keep its palette.
