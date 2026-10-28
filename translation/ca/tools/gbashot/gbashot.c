/* gbashot: headless libmgba runner for scripted screenshots.
 * usage: gbashot ROM SCRIPT [SAV]
 * script lines:  wait N | hold KEYS N | tap KEYS | shot FILE.ppm | save FILE | load FILE | # comment
 * KEYS: any of A B s(elect) S(tart) R L U D r(ight-shoulder) l(eft-shoulder), e.g. "hold Ar 10"
 */
#include <mgba/core/core.h>
#include <mgba/core/interface.h>
#include <mgba/gba/interface.h>
#include <mgba/internal/gba/input.h>
#include <mgba/core/log.h>
#include <mgba-util/vfs.h>
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static color_t buf[256 * 256];

static void quiet(struct mLogger* l, int c, enum mLogLevel lv, const char* f, va_list a) {
    (void) l; (void) c; (void) lv; (void) f; (void) a;
}
static struct mLogger sQuiet = { .log = quiet };

static int keymask(const char* k) {
    int m = 0;
    for (; *k; k++) switch (*k) {
        case 'A': m |= 1 << GBA_KEY_A; break;      case 'B': m |= 1 << GBA_KEY_B; break;
        case 's': m |= 1 << GBA_KEY_SELECT; break; case 'S': m |= 1 << GBA_KEY_START; break;
        case 'R': m |= 1 << GBA_KEY_RIGHT; break;  case 'L': m |= 1 << GBA_KEY_LEFT; break;
        case 'U': m |= 1 << GBA_KEY_UP; break;     case 'D': m |= 1 << GBA_KEY_DOWN; break;
        case 'r': m |= 1 << GBA_KEY_R; break;      case 'l': m |= 1 << GBA_KEY_L; break;
    }
    return m;
}

static void run(struct mCore* core, int keys, int frames) {
    core->setKeys(core, keys);
    for (int i = 0; i < frames; i++) core->runFrame(core);
}

static void shot(struct mCore* core, const char* path) {
    unsigned w, h;
    core->desiredVideoDimensions(core, &w, &h);
    FILE* f = fopen(path, "wb");
    fprintf(f, "P6\n%u %u\n255\n", w, h);
    for (unsigned y = 0; y < h; y++)
        for (unsigned x = 0; x < w; x++) {
            uint32_t c = buf[y * 256 + x];  /* mColor is XBGR8 in 32-bit builds */
            unsigned char rgb[3] = { c & 0xFF, (c >> 8) & 0xFF, (c >> 16) & 0xFF };
            fwrite(rgb, 1, 3, f);
        }
    fclose(f);
}

int main(int argc, char** argv) {
    if (argc < 3) { fprintf(stderr, "usage: %s ROM SCRIPT [SAV]\n", argv[0]); return 2; }
    mLogSetDefaultLogger(&sQuiet);
    struct mCore* core = mCoreFind(argv[1]);
    if (!core || !core->init(core)) { fprintf(stderr, "cannot init core\n"); return 1; }
    mCoreInitConfig(core, NULL);
    core->setVideoBuffer(core, buf, 256);
    if (!mCoreLoadFile(core, argv[1])) { fprintf(stderr, "cannot load ROM\n"); return 1; }
    if (argc > 3) core->loadSave(core, VFileOpen(argv[3], O_CREAT | O_RDWR));
    core->reset(core);

    FILE* s = fopen(argv[2], "r");
    char line[512], cmd[32], a[256];
    int n;
    while (fgets(line, sizeof line, s)) {
        if (line[0] == '#' || sscanf(line, "%31s", cmd) != 1) continue;
        if (!strcmp(cmd, "wait") && sscanf(line, "%*s %d", &n) == 1) run(core, 0, n);
        else if (!strcmp(cmd, "hold") && sscanf(line, "%*s %255s %d", a, &n) == 2) run(core, keymask(a), n);
        else if (!strcmp(cmd, "tap") && sscanf(line, "%*s %255s", a) == 1) { run(core, keymask(a), 2); run(core, 0, 6); }
        else if (!strcmp(cmd, "shot") && sscanf(line, "%*s %255s", a) == 1) shot(core, a);
        else if (!strcmp(cmd, "save") && sscanf(line, "%*s %255s", a) == 1) {
            size_t sz = core->stateSize(core); void* st = malloc(sz);
            core->saveState(core, st); FILE* f = fopen(a, "wb"); fwrite(st, 1, sz, f); fclose(f); free(st);
        } else if (!strcmp(cmd, "load") && sscanf(line, "%*s %255s", a) == 1) {
            size_t sz = core->stateSize(core); void* st = malloc(sz);
            FILE* f = fopen(a, "rb");
            if (!f || fread(st, 1, sz, f) != sz) { fprintf(stderr, "cannot read state %s\n", a); return 1; }
            fclose(f); core->loadState(core, st); free(st);
        } else fprintf(stderr, "bad line: %s", line);
    }
    core->deinit(core);
    return 0;
}
