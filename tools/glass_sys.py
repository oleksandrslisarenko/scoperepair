"""Systems/other: u2net segmentation (cleaner on boxy devices), mask scaled back to full size."""
import glob
import os
import sys

from PIL import Image

sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('GLASS_MODEL', 'u2net')
import glass_batch as gb  # noqa: E402
import glass_variants as g  # noqa: E402

files = sorted(glob.glob(os.path.join(gb.SRC, 'systems', '**', '*.webp'), recursive=True) +
               glob.glob(os.path.join(gb.SRC, 'other', '**', '*.webp'), recursive=True))
for src in files:
    rel = os.path.relpath(src, gb.SRC)
    dst = os.path.join(gb.DST, rel)
    keep = os.path.join(gb.DST, '_keep_original.txt')
    if os.path.exists(dst) or (os.path.exists(keep) and rel in open(keep).read().split()):
        continue
    im = Image.open(src).convert('RGB')
    k = min(1, 1600 / max(im.size))
    small = im.resize((int(im.width * k), int(im.height * k)), Image.LANCZOS)
    a = g.remove(small, session=g.session(), only_mask=True, post_process_mask=True).resize(im.size, Image.LANCZOS)
    cut = im.convert('RGBA'); cut.putalpha(a)
    bin_ = a.point(lambda v: 255 if v > 24 else 0)
    bg, opts = gb.BG()
    if gb.touches_edge(a):
        from PIL import ImageFilter
        W, H = im.size
        bg = bg.resize(im.size, Image.LANCZOS)
        for blur, dx, dy, al in ((4, 3, 6, .32), (28, 14, 28, .2)):
            sh = Image.new('L', (W, H), 0); sh.paste(a, (dx, dy))
            sh = sh.filter(ImageFilter.GaussianBlur(blur * W / 1600)).point(lambda v, al=al: int(v * al))
            bg = Image.composite(Image.new('RGB', (W, H), (20, 46, 76)), bg, sh)
        bg.paste(im, (0, 0), a)
        out = bg
    else:
        out = g.place(bg, cut.crop(bin_.getbbox()), opts)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    out.save(dst, 'WEBP', quality=88, method=5)
    print('ok', rel, flush=True)
