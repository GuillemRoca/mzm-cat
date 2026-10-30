// CA_PREVIEW=1 only, never in a release. Included by src/in_game.c; called once per in-game
// frame, before SpriteUpdate().
//
//   L + R + SELECT  show the next message banner (MESSAGE_DUMMY .. MESSAGE_ENEMY_LOCATION_ABNORMAL)
//   L + R + B       show the next location banner (LT_BRINSTAR .. LT_STARSHIP)
//   L + R + A       set energy to 0, to reach the game over screen (Start would pause)
//   L + R + UP      play the credits (no ending save is written)
//   L + R + RIGHT   play the Chozodia escape's end: "Mission accomplished", then the credits
//   L + R + LEFT    play the next story text cutscene: Planet Zebes, the Mother Ship monologue,
//                   "Could I survive" (Samus is back in the room afterwards)
//   L + R + DOWN    give every item and full ammo; again: cycle the suit (normal, fully powered,
//                   suitless) to see the unknown-item, real and pistol descriptions in the pause
//                   screen. Switching to fully powered plays the unknown items' reveal.
//
// The banner is spawned with a harmless message as its behaviour (no item, save or escape side
// effects), then its text is swapped for the previewed one: TextStartMessage() copies the
// message ID once, when the banner initializes, and the text is drawn from that copy.
// Location banners are drawn the way a room load does it (TextDrawLocation into the banner's
// graphics slot, then an area banner sprite that shows it).
// State lives in RAM padding that the game never uses, so the RAM layout doesn't change.

#include "sprite.h"
#include "text.h"
#include "location_text.h"
#include "constants/cutscene.h"
#include "constants/game_state.h"
#include "constants/samus.h"
#include "constants/sprite.h"
#include "constants/text.h"
#include "structs/cutscene.h"
#include "structs/game_state.h"
#include "structs/samus.h"
#include "structs/text.h"

extern u8 gUnk_3001670[28];
#define CA_PREVIEW_PENDING (gUnk_3001670[0]) // previewed message + 1, 0 if none
#define CA_PREVIEW_NEXT (gUnk_3001670[1])
#define CA_PREVIEW_SLOT (gUnk_3001670[2])
#define CA_PREVIEW_NEXT_LOCATION (gUnk_3001670[3])
#define CA_PREVIEW_NEXT_STORY (gUnk_3001670[4])

static void CaPreviewLocation(void)
{
    u8 lt;
    u8 gfxSlot;
    u8 i;
    u8 slot;

    lt = CA_PREVIEW_NEXT_LOCATION;
    CA_PREVIEW_NEXT_LOCATION = lt >= LT_STARSHIP ? 0 : lt + 1;

    // Same slot choice as a room load: the spriteset's banner slot, else the last slot
    gfxSlot = SPRITE_GFX_SLOT_MAX;
    for (i = 0; i < MAX_AMOUNT_OF_SPRITE_TYPES; i++)
    {
        if (gSpritesetSpritesId[i] == PSPRITE_AREA_BANNER)
        {
            gfxSlot = gSpritesetGfxSlots[i];
            break;
        }
    }
    if (gfxSlot >= SPRITE_GFX_SLOT_MAX)
    {
        gfxSlot = SPRITE_GFX_SLOT_MAX - 1;
        SpriteLoadGfx(PSPRITE_AREA_BANNER, gfxSlot);
        SpriteLoadPal(PSPRITE_AREA_BANNER, gfxSlot, 1);
    }

    TextDrawLocation(lt, gfxSlot);
    slot = SpriteSpawnPrimary(PSPRITE_AREA_BANNER, lt, gfxSlot, gSamusData.yPosition, gSamusData.xPosition, 0);
    if (slot < MAX_AMOUNT_OF_SPRITES)
    {
        // As SpriteUtilInitLocationText(): screen coordinates, drawn on top
        gSpriteData[slot].properties |= SP_ABSOLUTE_POSITION;
        gSpriteData[slot].status |= SPRITE_STATUS_HIGH_PRIORITY;
        gSpriteData[slot].bgPriority = 0;
        gSpriteData[slot].drawOrder = 1;
    }
}

static void CaPreviewUpdate(void)
{
    u8 msg;
    u8 carrier;
    u8 slot;

    if (CA_PREVIEW_PENDING != 0)
    {
        // Banner gone before it initialized (e.g. room change): give up on it
        if (!(gSpriteData[CA_PREVIEW_SLOT].status & SPRITE_STATUS_EXISTS))
            CA_PREVIEW_PENDING = 0;
        // The banner initialized last frame: swap the message it is about to draw
        else if (gSpriteData[CA_PREVIEW_SLOT].pose != 0)
        {
            gCurrentMessage.messageId = CA_PREVIEW_PENDING - 1;
            CA_PREVIEW_PENDING = 0;
        }
        return;
    }

    if ((gButtonInput & (KEY_L | KEY_R)) != (KEY_L | KEY_R))
        return;

    if (gChangedInput & KEY_A)
    {
        gEquipment.currentEnergy = 0;
        return;
    }

    if (gChangedInput & KEY_B)
    {
        CaPreviewLocation();
        return;
    }

    if (gChangedInput & KEY_LEFT)
    {
        // No const table: the linker script keeps no .rodata from in_game.o
        if (CA_PREVIEW_NEXT_STORY == 0)
            gCurrentCutscene = CUTSCENE_INTRO_TEXT;
        else if (CA_PREVIEW_NEXT_STORY == 1)
            gCurrentCutscene = CUTSCENE_MOTHERSHIP_MONOLOGUE;
        else
            gCurrentCutscene = CUTSCENE_COULD_I_SURVIVE;
        CA_PREVIEW_NEXT_STORY = CA_PREVIEW_NEXT_STORY >= 2 ? 0 : CA_PREVIEW_NEXT_STORY + 1;
        gMainGameMode = GM_CUTSCENE;
        gSubGameMode1 = 0;
        return;
    }

    if (gChangedInput & KEY_DOWN)
    {
        if (gEquipment.beamBombs == (BBF_LONG_BEAM | BBF_ICE_BEAM | BBF_WAVE_BEAM | BBF_PLASMA_BEAM |
            BBF_CHARGE_BEAM | BBF_BOMBS))
        {
            gEquipment.suitType = gEquipment.suitType >= SUIT_SUITLESS ? SUIT_NORMAL : gEquipment.suitType + 1;
            // As after the Chozo ruins test: the status screen reveals the unknown items
            if (gEquipment.suitType == SUIT_FULLY_POWERED)
                gPauseScreenFlag = PAUSE_SCREEN_FULLY_POWERED_SUIT_ITEMS;
            return;
        }
        gEquipment.beamBombs = BBF_LONG_BEAM | BBF_ICE_BEAM | BBF_WAVE_BEAM | BBF_PLASMA_BEAM |
            BBF_CHARGE_BEAM | BBF_BOMBS;
        gEquipment.beamBombsActivation = gEquipment.beamBombs;
        gEquipment.suitMisc = SMF_HIGH_JUMP | SMF_SPEEDBOOSTER | SMF_SPACE_JUMP | SMF_SCREW_ATTACK |
            SMF_VARIA_SUIT | SMF_GRAVITY_SUIT | SMF_MORPH_BALL | SMF_POWER_GRIP;
        gEquipment.suitMiscActivation = gEquipment.suitMisc;
        gEquipment.maxMissiles = gEquipment.currentMissiles = 250;
        gEquipment.maxSuperMissiles = gEquipment.currentSuperMissiles = 30;
        gEquipment.maxPowerBombs = gEquipment.currentPowerBombs = 9;
        return;
    }

    if (gChangedInput & KEY_RIGHT)
    {
        gMainGameMode = GM_CHOZODIA_ESCAPE;
        gSubGameMode1 = 0;
        return;
    }

    if (gChangedInput & KEY_UP)
    {
        // As the Chozodia escape does once it ends, without its ending save
        gMainGameMode = GM_CREDITS;
        gSubGameMode1 = 0;
        return;
    }

    if (!(gChangedInput & KEY_SELECT))
        return;

    msg = CA_PREVIEW_NEXT;
    CA_PREVIEW_NEXT = msg >= MESSAGE_ENEMY_LOCATION_ABNORMAL ? 0 : msg + 1;

    // One-line messages in a one-line banner, two-line ones in a two-line banner
    if ((MESSAGE_IS_ITEM(msg)) || (MESSAGE_IS_FIRST_TANK(msg)) || (MESSAGE_IS_MAP(msg)) ||
        msg == MESSAGE_SAVE_COMPLETE || msg == MESSAGE_FULLY_POWERED_SUIT)
        carrier = MESSAGE_SAVE_COMPLETE;
    else
        carrier = MESSAGE_WEAPONS_AND_ENERGY_RESTORED;

    slot = SpriteSpawnPrimary(PSPRITE_MESSAGE_BANNER, carrier, SPRITE_GFX_SLOT_SPECIAL,
        gSamusData.yPosition, gSamusData.xPosition, 0);
    if (slot < MAX_AMOUNT_OF_SPRITES)
    {
        CA_PREVIEW_SLOT = slot;
        CA_PREVIEW_PENDING = msg + 1;
    }
}
