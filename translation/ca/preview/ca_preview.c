// CA_PREVIEW=1 only, never in a release. Included by src/in_game.c; called once per in-game
// frame, before SpriteUpdate().
//
//   L + R + SELECT  show the next message banner (MESSAGE_DUMMY .. MESSAGE_ENEMY_LOCATION_ABNORMAL)
//   L + R + B       show the next location banner (LT_BRINSTAR .. LT_STARSHIP)
//   L + R + A       set energy to 0, to reach the game over screen (Start would pause)
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
#include "constants/sprite.h"
#include "constants/text.h"
#include "structs/samus.h"
#include "structs/text.h"

extern u8 gUnk_3001670[28];
#define CA_PREVIEW_PENDING (gUnk_3001670[0]) // previewed message + 1, 0 if none
#define CA_PREVIEW_NEXT (gUnk_3001670[1])
#define CA_PREVIEW_SLOT (gUnk_3001670[2])
#define CA_PREVIEW_NEXT_LOCATION (gUnk_3001670[3])

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
