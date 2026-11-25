/* bpscheck: applies a patch with mGBA's own loader and compares the patched ROM, as the
 * emulator maps it at 0x08000000, with an expected file. Independent of tools/bps.py.
 * usage: bpscheck BASE_ROM PATCH EXPECTED_ROM
 */
#include <mgba/core/core.h>
#include <mgba/core/log.h>
#include <mgba-util/vfs.h>
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>

static void quiet(struct mLogger* l, int c, enum mLogLevel lv, const char* f, va_list a) {
    (void) l; (void) c; (void) lv; (void) f; (void) a;
}
static struct mLogger sQuiet = { .log = quiet };

int main(int argc, char** argv) {
    if (argc != 4) { fprintf(stderr, "usage: %s BASE_ROM PATCH EXPECTED_ROM\n", argv[0]); return 2; }
    mLogSetDefaultLogger(&sQuiet);
    struct mCore* core = mCoreFind(argv[1]);
    if (!core || !core->init(core) || !mCoreLoadFile(core, argv[1])) { fprintf(stderr, "cannot load ROM\n"); return 1; }
    struct VFile* patch = VFileOpen(argv[2], O_RDONLY);
    if (!patch || !core->loadPatch(core, patch)) { fprintf(stderr, "mGBA rejected the patch\n"); return 1; }

    FILE* f = fopen(argv[3], "rb");
    if (!f) { perror(argv[3]); return 1; }
    fseek(f, 0, SEEK_END);
    long size = ftell(f);
    rewind(f);
    unsigned char* want = malloc(size);
    if (fread(want, 1, size, f) != (size_t) size) { fprintf(stderr, "short read\n"); return 1; }
    fclose(f);

    for (long i = 0; i < size; i++) {
        unsigned got = core->busRead8(core, 0x08000000 + i);
        if (got != want[i]) {
            printf("differs at 0x%06lX: mGBA has %02X, expected %02X\n", i, got, want[i]);
            return 1;
        }
    }
    printf("mGBA-patched ROM matches %s (%ld bytes)\n", argv[3], size);
    core->deinit(core);
    return 0;
}
