# Catalan translation build hooks, included from the top-level Makefile.
#
#   make eu LANG_CA=1                 mzm_eu_ca.gba: Catalan in the Spanish slot
#   make eu LANG_CA=1 CA_SELFTEST=1   same plumbing with the vanilla Spanish text, font and
#                                     widths: must be byte-identical to vanilla mzm_eu.gba
#   make eu LANG_CA=1 CA_PREVIEW=1    mzm_eu_ca_preview.gba, a test build that is never released:
#                                     L+R+SELECT next message, L+R+B next location banner,
#                                     L+R+A game over, L+R+UP credits, L+R+DOWN all items,
#                                     L+R+LEFT story cutscenes
#                                     (translation/ca/preview/ca_preview.c, translation/ca/TESTING.md)
#
# With LANG_CA=1, generated includes go in $(CA_INC), which is searched before include/:
#   ca/text_<category>.inc     the Spanish blocks of src/data/text_data.c, in Catalan
#   ca/char_widths.inc         the EU sCharacterWidths with font/widths.txt applied
#   ca/credits.inc             the EU sCredits with the translators in credits.txt
#   extracted/data/...inc      overrides of extracted assets (font, edited graphics)
# and $(CA_DIR)/include holds hand-written headers (ca/layout.h: per-language layout constants).
# Objects are built in-tree for both modes, so every object that depends on the mode
# also depends on $(CA_STAMP), which changes whenever the mode does.

# This file is included before the Makefile's `all` rule; keep `all` the default goal.
.DEFAULT_GOAL := all

CA_DIR := translation/ca
CA_TOOLS := $(CA_DIR)/tools
CA_BUILD := $(CA_DIR)/build
CA_INC := $(CA_BUILD)/include
CA_STAMP := $(CA_BUILD)/mode.stamp
CA_GBAGFX := $(CA_BUILD)/gbagfx

LANG_CA ?= 0
CA_SELFTEST ?= 0
CA_PREVIEW ?= 0

CA_TEXT_INCS := $(foreach c,message location description story file_screen,$(CA_INC)/ca/text_$(c).inc)
CA_WIDTHS_INC := $(CA_INC)/ca/char_widths.inc
CA_CREDITS_INC := $(CA_INC)/ca/credits.inc
CA_FONT_INC := $(CA_INC)/extracted/data/text_characters.gfx.inc

ifeq ($(CA_SELFTEST),1)
  CPPFLAGS += -DCA_SELFTEST
  CA_GENTEXT_FLAGS := --fallback spanish
  CA_FONT_FLAGS := --vanilla
  CA_CREDITS_FLAGS := --vanilla
  CA_GFX_PNGS :=
else
  CA_GENTEXT_FLAGS :=
  CA_FONT_FLAGS :=
  CA_CREDITS_FLAGS :=
  CA_GFX_PNGS := $(sort $(shell find $(CA_DIR)/gfx -name '*.png' 2>/dev/null))
endif
# translation/ca/gfx/<data path minus .gfx.lz>.png overrides data/<data path>
CA_GFX_INCS := $(patsubst $(CA_DIR)/gfx/%.png,$(CA_INC)/extracted/data/%.gfx.lz.inc,$(CA_GFX_PNGS))

# Rewrite the stamp only when the mode changes, so its timestamp marks the last switch.
CA_MODE := LANG_CA=$(LANG_CA) CA_SELFTEST=$(CA_SELFTEST) CA_PREVIEW=$(CA_PREVIEW) GFX=$(CA_GFX_PNGS)
$(shell mkdir -p $(CA_BUILD) && (echo '$(CA_MODE)' | cmp -s - $(CA_STAMP) || echo '$(CA_MODE)' > $(CA_STAMP)))

# Objects whose output depends on the mode: sources that mention LANG_CA, plus sources that
# include any asset we can override (the font, every graphic in gfx_assets.json), whether or
# not it has a PNG right now: removing a PNG must rebuild its object too.
CA_GFX_KEYS := $(shell sed -n 's/^  "\([a-z][^"]*\)": *{.*/\1/p' $(CA_TOOLS)/gfx_assets.json)
CA_SHADOWABLE := extracted/data/text_characters.gfx.inc $(CA_GFX_KEYS:%=extracted/data/%.gfx.lz.inc)
CA_AFFECTED := $(shell grep -rlF --include='*.c' $(foreach p,LANG_CA CA_PREVIEW $(CA_SHADOWABLE),-e '$(p)') src)
$(CA_AFFECTED:.c=.s): $(CA_STAMP)

ifeq ($(LANG_CA),1)
  CPPFLAGS += -DLANG_CA -I$(CA_INC) -I$(CA_DIR)/include
  TARGET := $(TARGET)_ca

  # Drop overrides of graphics whose PNG is gone, so they can't leak into the build.
  $(foreach f,$(filter-out $(CA_GFX_INCS),$(shell find $(CA_INC)/extracted -name '*.gfx.lz.inc' 2>/dev/null)),$(shell rm -f $(f)))

  src/data/text_data.s: $(CA_TEXT_INCS) $(CA_FONT_INC)
  src/data/menus/pause_screen_data.s: $(CA_WIDTHS_INC)
  src/data/ending_and_gallery_data.s: $(CA_CREDITS_INC)
  # Over-approximate: an edited graphic rebuilds every affected object, which is cheap.
  $(CA_AFFECTED:.c=.s): $(CA_GFX_INCS) $(wildcard $(CA_DIR)/include/ca/*.h)

  ifeq ($(CA_PREVIEW),1)
    CPPFLAGS += -DCA_PREVIEW -I$(CA_DIR)/preview
    TARGET := $(TARGET)_preview
    src/in_game.s: $(CA_DIR)/preview/ca_preview.c
  endif
else ifeq ($(CA_PREVIEW),1)
  $(error CA_PREVIEW=1 needs LANG_CA=1)
endif

$(CA_INC)/ca/text_%.inc: $(CA_DIR)/text/%.txt src/data/text_data.c charmap.txt $(CA_TOOLS)/gentext.py $(CA_TOOLS)/catext.py $(CA_STAMP)
	@test "$(REGION)" = eu || { echo "error: LANG_CA=1 needs REGION=eu (make eu LANG_CA=1)" >&2; exit 1; }
	$(MSG) GENTEXT $@
	$Q$(PYTHON) $(CA_TOOLS)/gentext.py $* $@ $(CA_GENTEXT_FLAGS)

$(CA_WIDTHS_INC): $(wildcard $(CA_DIR)/font/widths.txt) src/data/menus/pause_screen_data.c $(CA_TOOLS)/font.py $(CA_TOOLS)/catext.py $(CA_STAMP)
	$(MSG) WIDTHS $@
	$Q$(PYTHON) $(CA_TOOLS)/font.py widths $@ $(CA_FONT_FLAGS)

$(CA_CREDITS_INC): $(CA_DIR)/credits.txt src/data/ending_and_gallery_data.c $(CA_TOOLS)/gencredits.py $(CA_STAMP)
	$(MSG) CREDITS $@
	$Q$(PYTHON) $(CA_TOOLS)/gencredits.py $@ $(CA_CREDITS_FLAGS)

$(CA_FONT_INC): data/text_characters.gfx $(wildcard $(CA_DIR)/font/glyphs/*.png) $(wildcard $(CA_DIR)/font/widths.txt) $(CA_TOOLS)/font.py $(CA_GBAGFX) $(CA_STAMP)
	$(MSG) FONT $@
	$Q$(PYTHON) $(CA_TOOLS)/font.py build $@ $(CA_FONT_FLAGS)

$(CA_INC)/extracted/data/%.gfx.lz.inc: $(CA_DIR)/gfx/%.png $(CA_TOOLS)/gfx.py $(CA_TOOLS)/gfx_assets.json $(CA_GBAGFX)
	$(MSG) GFX $@
	$Q$(PYTHON) $(CA_TOOLS)/gfx.py build $* $@

CA_GBAGFX_SRC := $(wildcard $(CA_TOOLS)/gbagfx/*.c)
$(CA_GBAGFX): $(CA_GBAGFX_SRC) $(wildcard $(CA_TOOLS)/gbagfx/*.h)
	$(MSG) CC $@
	$Q$(HOSTCC) -std=c11 -O2 -DPNG_SKIP_SETJMP_CHECK $(shell pkg-config --cflags libpng 2>/dev/null) $(CA_GBAGFX_SRC) -o $@ $(shell pkg-config --libs-only-L libpng 2>/dev/null) -lpng -lz

# Headless mGBA tools (need libmgba-dev): scripted screenshots, and patch checks with mGBA's
# own BPS loader.
$(CA_BUILD)/gbashot $(CA_BUILD)/bpscheck: $(CA_BUILD)/%: $(CA_TOOLS)/gbashot/%.c
	$(MSG) CC $@
	$Q$(HOSTCC) -O2 -Wall $< -o $@ -lmgba

.PHONY: ca-tools ca-emu-tools ca-clean
ca-tools: $(CA_GBAGFX)
ca-emu-tools: $(CA_BUILD)/gbashot $(CA_BUILD)/bpscheck
ca-clean:
	$(RM) -r $(CA_BUILD)
