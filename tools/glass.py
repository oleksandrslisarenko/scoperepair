"""Put real product photos on a blue glass backdrop.

The device itself stays the original photo: it is cut out (rembg) and composited
onto a generated background with a soft contact shadow and glass highlights.

usage: python3 tools/glass.py SRC [SRC ...] --out DIR
"""
import argparse
import os
import random

from PIL import Image, ImageChops, ImageDraw, ImageFilter
from rembg import new_session, remove

W, H = 1600, 1200
_session = None


def session():
    global _session
    if _session is None:
        _session = new_session(os.environ.get('GLASS_MODEL', 'isnet-general-use'))
    return _session


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def backdrop(seed=0):
    rnd = random.Random(seed)
    top, bottom = (241, 247, 253), (196, 222, 243)
    bg = Image.new('RGB', (W, H))
    px = bg.load()
    for y in range(H):
        for x in range(W):
            t = min(1, max(0, (y * 0.75 + x * 0.25) / (H * 0.75 + W * 0.25)))
            px[x, y] = lerp(top, bottom, t ** 1.2)
    # soft light pools
    glow = Image.new('L', (W, H), 0)
    d = ImageDraw.Draw(glow)
    d.ellipse((-300, -380, 900, 520), fill=255)
    d.ellipse((900, 650, 1900, 1400), fill=120)
    glow = glow.filter(ImageFilter.GaussianBlur(160))
    bg = Image.composite(Image.new('RGB', (W, H), (255, 255, 255)), bg, glow.point(lambda v: int(v * .75)))
    # glass streaks: diagonal bright bands with a sharp edge line
    streaks = Image.new('L', (W, H), 0)
    d = ImageDraw.Draw(streaks)
    off = rnd.randint(-120, 120)
    for x0, wdt, a in ((420 + off, 220, 90), (760 + off, 70, 70), (1180 + off, 140, 55)):
        d.polygon([(x0, -50), (x0 + wdt, -50), (x0 + wdt - 900, H + 50), (x0 - 900, H + 50)], fill=a)
    streaks = streaks.filter(ImageFilter.GaussianBlur(38))
    lines = Image.new('L', (W, H), 0)
    d = ImageDraw.Draw(lines)
    for x0, a in ((640 + off, 150), (1320 + off, 110)):
        d.line([(x0, -50), (x0 - 900, H + 50)], fill=a, width=3)
    lines = lines.filter(ImageFilter.GaussianBlur(1.2))
    mask = ImageChops.add(streaks, lines)
    bg = Image.composite(Image.new('RGB', (W, H), (255, 255, 255)), bg, mask)
    return bg


def compose(src, seed=0):
    im = Image.open(src).convert('RGB')
    cut = remove(im, session=session(), post_process_mask=True)  # RGBA
    bbox = cut.getchannel('A').point(lambda v: 255 if v > 24 else 0).getbbox()
    if not bbox:
        return None
    cut = cut.crop(bbox)
    k = min(W * 0.84 / cut.width, H * 0.78 / cut.height)
    cut = cut.resize((max(1, int(cut.width * k)), max(1, int(cut.height * k))), Image.LANCZOS)
    x, y = (W - cut.width) // 2, (H - cut.height) // 2 - 10
    bg = backdrop(seed)
    a = cut.getchannel('A')
    # contact shadow (tight) + ambient shadow (wide), cool navy tint
    for blur, dx, dy, alpha in ((6, 6, 10, .38), (40, 26, 46, .26)):
        sh = Image.new('L', (W, H), 0)
        sh.paste(a, (x + dx, y + dy))
        sh = sh.filter(ImageFilter.GaussianBlur(blur)).point(lambda v, al=alpha: int(v * al))
        bg = Image.composite(Image.new('RGB', (W, H), (22, 48, 78)), bg, sh)
    bg.paste(cut, (x, y), a)
    # faint glass sheen over everything for cohesion
    sheen = Image.new('L', (W, H), 0)
    ImageDraw.Draw(sheen).polygon([(0, 0), (W * .55, 0), (0, H * .7)], fill=26)
    sheen = sheen.filter(ImageFilter.GaussianBlur(120))
    bg = Image.composite(Image.new('RGB', (W, H), (255, 255, 255)), bg, sheen)
    return bg


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('src', nargs='+')
    ap.add_argument('--out', required=True)
    o = ap.parse_args()
    os.makedirs(o.out, exist_ok=True)
    for i, s in enumerate(o.src):
        r = compose(s, seed=i)
        if r is None:
            print('skip', s)
            continue
        name = '-'.join(s.split(os.sep)[-3:]).replace('.webp', '.jpg')
        r.save(os.path.join(o.out, name), 'JPEG', quality=90)
        print('ok', name)
