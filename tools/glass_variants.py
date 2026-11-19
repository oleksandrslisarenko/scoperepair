"""Five backdrop styles for product photos (real device cut-out + generated background)."""
import math
import os
import random
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(__file__))
from glass import remove, session  # noqa: E402

W, H = 1600, 1200
WHITE = (255, 255, 255)


def grad(c1, c2, angle=0.3, power=1.0):
    """Linear gradient; angle 0 = top->bottom, 1 = left->right."""
    g = Image.linear_gradient('L').resize((W, H))  # top->bottom
    if angle:
        h = Image.linear_gradient('L').rotate(90).resize((W, H)).transpose(Image.FLIP_LEFT_RIGHT)
        g = Image.blend(g, h, angle)
    if power != 1:
        g = g.point(lambda v: int(255 * (v / 255) ** power))
    return Image.composite(Image.new('RGB', (W, H), c2), Image.new('RGB', (W, H), c1), g)


def light(bg, shape_fn, blur, alpha, color=WHITE):
    m = Image.new('L', (W, H), 0)
    shape_fn(ImageDraw.Draw(m))
    m = m.filter(ImageFilter.GaussianBlur(blur)).point(lambda v: int(v * alpha))
    return Image.composite(Image.new('RGB', (W, H), color), bg, m)


# 1 ─ Glass table: bright sky above a reflective floor with a horizon glint
def bg_glass_table():
    bg = grad((236, 245, 253), (188, 216, 240), 0.15)
    floor = Image.new('L', (W, H), 0)
    ImageDraw.Draw(floor).rectangle((0, int(H * .58), W, H), fill=255)
    floor = floor.filter(ImageFilter.GaussianBlur(30))
    bg = Image.composite(grad((205, 228, 247), (160, 198, 232), 0), bg, floor)
    bg = light(bg, lambda d: d.rectangle((0, int(H * .575), W, int(H * .59))), 6, .9)
    bg = light(bg, lambda d: d.ellipse((W * .15, H * .3, W * .85, H * .8)), 140, .55)
    return bg, {'reflect': True, 'cy': .50}


# 2 ─ Studio spotlight: soft round light pool, vignette, no streaks
def bg_studio():
    bg = grad((214, 233, 249), (172, 206, 236), 0.2)
    bg = light(bg, lambda d: d.ellipse((W * .12, H * .05, W * .88, H * .95)), 180, .95)
    vig = Image.new('L', (W, H), 0)
    ImageDraw.Draw(vig).rectangle((0, 0, W, H), fill=255)
    ImageDraw.Draw(vig).ellipse((-W * .1, -H * .15, W * 1.1, H * 1.15), fill=0)
    vig = vig.filter(ImageFilter.GaussianBlur(160)).point(lambda v: int(v * .35))
    bg = Image.composite(Image.new('RGB', (W, H), (120, 160, 200)), bg, vig)
    return bg, {'shadow': 1.4}


# 3 ─ Two lines: brand arcs from the design system ("Две линии")
def bg_arcs():
    bg = grad((246, 250, 255), (205, 228, 248), 0.55)
    bg = light(bg, lambda d: d.ellipse((W * .55, -H * .3, W * 1.25, H * .45)), 120, .8)
    arcs = Image.new('L', (W, H), 0)
    d = ImageDraw.Draw(arcs)
    for r, wdt, a in ((1150, 3, 230), (1270, 2, 150)):
        cx, cy = W * 1.05, H * 1.25
        d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=a, width=wdt)
    arcs = arcs.filter(ImageFilter.GaussianBlur(1))
    bg = Image.composite(Image.new('RGB', (W, H), WHITE), bg, arcs)
    return bg, {}


# 4 ─ Frosted glass with bokeh
def bg_bokeh():
    rnd = random.Random(7)
    bg = grad((228, 241, 252), (176, 210, 240), 0.35)
    b = Image.new('L', (W, H), 0)
    d = ImageDraw.Draw(b)
    for _ in range(26):
        r = rnd.randint(40, 170)
        x, y = rnd.randint(-100, W + 100), rnd.randint(-100, H + 100)
        d.ellipse((x - r, y - r, x + r, y + r), fill=rnd.randint(60, 150))
    b = b.filter(ImageFilter.GaussianBlur(26))
    bg = Image.composite(Image.new('RGB', (W, H), WHITE), bg, b.point(lambda v: int(v * .7)))
    # frosted pane edge: diagonal soft band
    bg = light(bg, lambda d: d.polygon([(W * .62, 0), (W * .74, 0), (W * .34, H), (W * .22, H)]), 50, .35)
    return bg, {}


# 5 ─ Lab grid: fine technical grid fading into a blue glow
def bg_grid():
    bg = grad((243, 248, 253), (199, 224, 246), 0.25)
    g = Image.new('L', (W, H), 0)
    d = ImageDraw.Draw(g)
    step = 64
    for x in range(0, W + 1, step):
        d.line((x, 0, x, H), fill=60 if x % (step * 4) else 110, width=1)
    for y in range(0, H + 1, step):
        d.line((0, y, W, y), fill=60 if y % (step * 4) else 110, width=1)
    fade = Image.new('L', (W, H), 0)
    ImageDraw.Draw(fade).ellipse((-W * .2, -H * .2, W * 1.2, H * 1.2), fill=255)
    fade = ImageChops.invert(fade.filter(ImageFilter.GaussianBlur(220)))
    fade = ImageChops.add(fade, Image.new('L', (W, H), 70))
    g = ImageChops.multiply(g, fade)
    bg = Image.composite(Image.new('RGB', (W, H), (120, 170, 215)), bg, g)
    bg = light(bg, lambda d: d.ellipse((W * .2, H * .15, W * .8, H * .85)), 160, .6)
    return bg, {}


STYLES = [('1 Glas-Tisch', bg_glass_table), ('2 Studio', bg_studio), ('3 Zwei Linien', bg_arcs),
          ('4 Milchglas', bg_bokeh), ('5 Labor-Raster', bg_grid)]


def cutout(src):
    im = Image.open(src).convert('RGB')
    cut = remove(im, session=session(), post_process_mask=True)
    bbox = cut.getchannel('A').point(lambda v: 255 if v > 24 else 0).getbbox()
    return cut.crop(bbox)


def place(bg, cut, opts):
    k = min(W * .82 / cut.width, H * (.62 if opts.get('reflect') else .76) / cut.height)
    c = cut.resize((int(cut.width * k), int(cut.height * k)), Image.LANCZOS)
    a = c.getchannel('A')
    x = (W - c.width) // 2
    y = int(H * opts.get('cy', .5) - c.height / 2) if not opts.get('reflect') else int(H * .6 - c.height)
    s = opts.get('shadow', 1.0)
    for blur, dx, dy, alpha in ((5, 4, 8, .40), (36, 20, 40, .28)):
        sh = Image.new('L', (W, H), 0)
        sh.paste(a, (x + dx, y + dy))
        sh = sh.filter(ImageFilter.GaussianBlur(blur)).point(lambda v, al=alpha * s: int(min(255, v * al)))
        bg = Image.composite(Image.new('RGB', (W, H), (20, 46, 76)), bg, sh)
    if opts.get('reflect'):
        rf = c.transpose(Image.FLIP_TOP_BOTTOM)
        ra = rf.getchannel('A')
        fade = Image.linear_gradient('L').resize(ra.size).transpose(Image.FLIP_TOP_BOTTOM)
        ra = ImageChops.multiply(ra, fade.point(lambda v: int(v * .32)))
        rf = rf.filter(ImageFilter.GaussianBlur(2))
        bg.paste(rf.convert('RGB'), (x, y + c.height + 4), ra)
    bg.paste(c, (x, y), a)
    return bg


if __name__ == '__main__':
    out = sys.argv[1]
    srcs = sys.argv[2:]
    os.makedirs(out, exist_ok=True)
    cuts = [cutout(s) for s in srcs]
    tw, th = 640, 480
    try:
        font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 30)
    except OSError:
        font = ImageFont.load_default()
    sheet = Image.new('RGB', (tw * len(cuts) + 24 * (len(cuts) + 1), (th + 70) * len(STYLES) + 24), WHITE)
    for r, (name, fn) in enumerate(STYLES):
        ImageDraw.Draw(sheet).text((24, r * (th + 70) + 28), name, fill=(25, 56, 84), font=font)
        for i, c in enumerate(cuts):
            bg, opts = fn()
            img = place(bg, c, opts)
            img.save(os.path.join(out, f'v{r + 1}-{i + 1}.jpg'), 'JPEG', quality=90)
            sheet.paste(img.resize((tw, th), Image.LANCZOS), (24 + i * (tw + 24), r * (th + 70) + 70))
        print('style', name)
    sheet.save(os.path.join(out, 'varianten.jpg'), 'JPEG', quality=86)


def bg_arcs_tone(c1, c2, glow=.7, arc=(230, 150)):
    def fn():
        bg = grad(c1, c2, 0.55)
        bg = light(bg, lambda d: d.ellipse((W * .55, -H * .3, W * 1.25, H * .45)), 120, glow)
        arcs = Image.new('L', (W, H), 0)
        d = ImageDraw.Draw(arcs)
        for r, wdt, a in ((1150, 3, arc[0]), (1270, 2, arc[1])):
            cx, cy = W * 1.05, H * 1.25
            d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=a, width=wdt)
        bg = Image.composite(Image.new('RGB', (W, H), WHITE), bg, arcs.filter(ImageFilter.GaussianBlur(1)))
        return bg, {'shadow': .8}
    return fn


TONES = [('3A Fast weiß', bg_arcs_tone((250, 252, 254), (234, 240, 248))),
         ('3B Kühles Grau', bg_arcs_tone((244, 245, 247), (225, 229, 234))),
         ('3C Graublau', bg_arcs_tone((247, 249, 253), (220, 230, 241)))]
