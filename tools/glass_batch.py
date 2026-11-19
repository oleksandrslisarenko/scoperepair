"""Batch: product photos -> tone 3A glass backdrop (real device cut-out, generated background).

Writes assets/photos/products-glass/<same path>.webp. Photos where the device touches the
frame edge (close-ups) are skipped and listed in products-glass/_skipped.txt; the site keeps
the original for those.

usage: python3 tools/glass_batch.py [--shard i/n]
"""
import os
import sys

from PIL import Image

sys.path.insert(0, os.path.dirname(__file__))
import glass_variants as g  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'assets', 'photos', 'products')
DST = os.path.join(ROOT, 'assets', 'photos', 'products-glass')
BG = g.bg_arcs_tone((250, 252, 254), (234, 240, 248))


def touches_edge(alpha, frac=0.03):
    w, h = alpha.size
    px = alpha.load()
    sides = [[px[x, 0] for x in range(w)], [px[x, h - 1] for x in range(w)],
             [px[0, y] for y in range(h)], [px[w - 1, y] for y in range(h)]]
    return any(sum(1 for v in s if v > 128) / len(s) > frac for s in sides)


def main():
    shard = (0, 1)
    if '--shard' in sys.argv:
        a, b = sys.argv[sys.argv.index('--shard') + 1].split('/')
        shard = (int(a), int(b))
    files = sorted(os.path.join(b, f) for b, _, fs in os.walk(SRC) for f in fs if f.endswith('.webp'))
    files = files[shard[0]::shard[1]]
    skipped = []
    for i, src in enumerate(files):
        rel = os.path.relpath(src, SRC)
        dst = os.path.join(DST, rel)
        if os.path.exists(dst):
            continue
        im = Image.open(src).convert('RGB')
        cut = g.remove(im, session=g.session(), post_process_mask=True)
        a = cut.getchannel('A')
        if touches_edge(a) or not a.point(lambda v: 255 if v > 24 else 0).getbbox():
            skipped.append(rel)
            print('skip', rel, flush=True)
            continue
        cut = cut.crop(a.point(lambda v: 255 if v > 24 else 0).getbbox())
        bg, opts = BG()
        out = g.place(bg, cut, opts)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        out.save(dst, 'WEBP', quality=88, method=5)
        print(f'{i + 1}/{len(files)} ok', rel, flush=True)
    if skipped:
        with open(os.path.join(DST, f'_skipped_{shard[0]}.txt'), 'a') as f:
            f.write('\n'.join(skipped) + '\n')


if __name__ == '__main__':
    main()
