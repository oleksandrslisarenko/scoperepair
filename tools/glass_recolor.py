"""Recolor the light studio background to tone 3A without cutting out the device.

Dark/saturated pixels (the device, coloured rings, labels) stay untouched; bright
background pixels are replaced by the 3A gradient, shaded by the original luminance
so soft shadows survive. Used for close-ups where segmentation fails.

usage: python3 tools/glass_recolor.py LIST.txt   (paths relative to assets/photos/products)
"""
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(__file__))
import glass_batch as gb  # noqa: E402


def recolor(rel):
    im = Image.open(os.path.join(gb.SRC, rel)).convert('RGB')
    a = np.asarray(im).astype(np.float32)
    L = a.mean(axis=2)
    bgL = max(np.percentile(L, 85), 150)
    t = np.clip((L - 120) / (bgL - 120), 0, 1)
    t = t * t * (3 - 2 * t)
    sat = a.max(axis=2) - a.min(axis=2)
    t *= 1 - np.clip((sat - 28) / 30, 0, 1)
    bg, _ = gb.BG()
    g = np.asarray(bg.resize(im.size, Image.LANCZOS)).astype(np.float32)
    shade = 1 - 0.25 * (1 - np.clip(L / bgL, 0, 1.05))  # keep shadows, but softer than the original grey
    out = a * (1 - t[..., None]) + g * shade[..., None] * t[..., None]
    dst = os.path.join(gb.DST, rel)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).save(dst, 'WEBP', quality=88, method=5)


if __name__ == '__main__':
    for rel in [l.strip() for l in open(sys.argv[1]) if l.strip()]:
        recolor(rel)
        print('ok', rel, flush=True)
