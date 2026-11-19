"""Second pass for close-ups skipped by glass_batch: keep framing, swap only the background."""
import glob
import os
import sys

from PIL import Image, ImageFilter

sys.path.insert(0, os.path.dirname(__file__))
import glass_batch as gb  # noqa: E402
import glass_variants as g  # noqa: E402

shard = (0, 1)
if '--shard' in sys.argv:
    a, b = sys.argv[sys.argv.index('--shard') + 1].split('/')
    shard = (int(a), int(b))
skipped = []
for f in glob.glob(os.path.join(gb.DST, '_skipped_*.txt')):
    skipped += [l.strip() for l in open(f) if l.strip()]
skipped = sorted(set(skipped))[shard[0]::shard[1]]
for rel in skipped:
    dst = os.path.join(gb.DST, rel)
    if os.path.exists(dst):
        continue
    im = Image.open(os.path.join(gb.SRC, rel)).convert('RGB')
    cut = g.remove(im, session=g.session(), post_process_mask=True)
    a = cut.getchannel('A')
    bg, _ = gb.BG()
    bg = bg.resize(im.size, Image.LANCZOS)
    W, H = im.size
    for blur, dx, dy, alpha in ((4, 3, 6, .32), (28, 14, 28, .2)):
        sh = Image.new('L', (W, H), 0)
        sh.paste(a, (dx, dy))
        sh = sh.filter(ImageFilter.GaussianBlur(blur * W / 1600)).point(lambda v, al=alpha: int(v * al))
        bg = Image.composite(Image.new('RGB', (W, H), (20, 46, 76)), bg, sh)
    bg.paste(cut.convert('RGB'), (0, 0), a)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    bg.save(dst, 'WEBP', quality=88, method=5)
    print('ok', rel, flush=True)
