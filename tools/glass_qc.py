"""QC for in-place close-ups: flag cut-outs with floating fragments (bad segmentation)."""
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

sys.path.insert(0, os.path.dirname(__file__))
import glass_variants as g  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'assets', 'photos', 'products')
DST = os.path.join(ROOT, 'assets', 'photos', 'products-glass')


def fragments(rel):
    im = Image.open(os.path.join(SRC, rel)).convert('RGB')
    k = 800 / max(im.size)
    im = im.resize((int(im.width * k), int(im.height * k)))
    a = np.array(g.remove(im, session=g.session(), only_mask=True, post_process_mask=True)) > 128
    lab, n = ndimage.label(a)
    if n == 0:
        return 99, 0
    sizes = np.bincount(lab.ravel())[1:]
    total = sizes.sum()
    small = sizes[sizes < total * 0.02]
    return int((small > 15).sum()), float(sizes.max() / total)


if __name__ == '__main__':
    rels = [l.strip() for l in open(sys.argv[1]) if l.strip()]
    bad = []
    for rel in rels:
        n, main = fragments(rel)
        flag = n >= 2 or main < 0.95
        print(f'{"BAD " if flag else "ok  "}{n:3d} {main:.2f} {rel}', flush=True)
        if flag:
            bad.append(rel)
    open('/tmp/gb/bad.txt', 'w').write('\n'.join(bad))
    print('bad', len(bad), 'of', len(rels))
