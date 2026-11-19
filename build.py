"""Static site generator for the scopeREPAIR prototype.

    python3 build.py            # build everything into site/
    python3 build.py v1         # only one variant (+ hub)

Output:
    site/index.html             hub (variant overview)
    site/mobile.html            phone-frame viewer (?v=v1&p=de/index.html)
    site/v1/<lang>/…            variant 1 (approved design)
    site/v2/<lang>/…            variant 2 (alternative)
    site/img/…                  web-sized images (shared)
    site/static/…               css, js, fonts
"""
import json
import datetime
import hashlib
import os
import shutil
import sys
import zipfile
from collections import OrderedDict, defaultdict

from jinja2 import TemplateNotFound, ChoiceLoader, Environment, FileSystemLoader, select_autoescape
from markupsafe import Markup

import content as C

ROOT = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.join(ROOT, 'site')
PHOTOS = os.path.join(ROOT, 'assets', 'photos')
VARIANTS = ['v1', 'v2']

# page id -> (template, faq key or None)
PAGES = OrderedDict([
    ('index', ('home.html', 'home')),
    ('index-b', ('home_b.html', 'home')),
    ('index-c', ('home_c.html', 'home')),
    ('reparatur', ('reparatur.html', 'repair')),
    ('reparatur-auftrag', ('wizard_repair.html', None)),
    ('leihgeraete', ('leihgeraete.html', 'loaner')),
    ('leihgeraet-anfragen', ('wizard_loaner.html', None)),
    ('gebrauchte-endoskope', ('katalog.html', 'used')),
    ('ankauf', ('ankauf.html', 'buy')),
    ('ankauf-anfrage', ('wizard_buy.html', None)),
    ('endoskopie-anlagen', ('anlagen.html', 'systems')),
    ('rechner', ('rechner.html', None)),
    ('ueber-uns', ('ueber_uns.html', None)),
    ('kontakt', ('kontakt.html', None)),
    ('impressum', ('legal.html', None)),
    ('datenschutz', ('legal.html', None)),
    ('agb', ('legal.html', None)),
    ('rechtliches', ('legal.html', None)),
])

# screen list for the mobile viewer / hub (label in DE – the viewer UI is German)
SCREENS = [
    ('index', 'Startseite'), ('reparatur', 'Reparatur'), ('reparatur-auftrag', 'Abholauftrag (Wizard)'),
    ('leihgeraete', 'Leihgeräte'), ('leihgeraet-anfragen', 'Leihgerät anfragen (Wizard)'),
    ('gebrauchte-endoskope', 'Gebrauchte Endoskope'), ('produkt', 'Produktseite'),
    ('ankauf', 'Ankauf'), ('ankauf-anfrage', 'Gerät verkaufen (Wizard)'), ('endoskopie-anlagen', 'Endoskopie-Anlagen'),
    ('rechner', 'Kostenrechner'), ('index-b', 'Startseite B (nur 02)'), ('index-c', 'Startseite C (nur 02)'), ('ueber-uns', 'Über uns'), ('kontakt', 'Kontakt / Rückruf'),
    ('impressum', 'Impressum'), ('datenschutz', 'Datenschutz'), ('agb', 'AGB'), ('rechtliches', 'Text- und Bildrechte'),
]
DEMO_PRODUCT = 'gastroskop-pentax-eg-1580k'


# ──────────────────────────────────────────────────────────────────────────
# Images
# ──────────────────────────────────────────────────────────────────────────
HERO_DIR = os.path.join(ROOT, 'assets', 'hero')
HERO_NAMES = {'hero-endoscopes': '01-startseite', 'banner-repair': '02-reparatur', 'banner-pickup': '03-leihgeraete',
              'banner-buy': '04-ankauf', 'banner-systems': '05-endoskopie-anlagen', 'banner-about': '06-ueber-uns',
              'banner-contact': '07-kontakt'}


def build_images():
    """Resize live photos to web sizes once (cached) and return a lookup."""
    from PIL import Image
    out = os.path.join(SITE, 'img')
    os.makedirs(out, exist_ok=True)
    manifest = {}
    with open(os.path.join(PHOTOS, 'manifest.csv'), encoding='utf-8') as f:
        next(f)
        for line in f:
            parts = line.rstrip('\n').split(',')
            rel, src = parts[0], parts[3]
            manifest[src] = rel
    lookup = {}

    def make(rel, sizes=(480, 960, 1600)):
        src_path = os.path.join(PHOTOS, rel)
        base = os.path.splitext(rel)[0].replace('/', '__')
        # product photos on the glass backdrop (tools/glass_batch.py) replace the originals when present
        if rel.startswith('products/'):
            g = os.path.join(PHOTOS, 'products-glass', rel[len('products/'):])
            if os.path.exists(g):
                src_path, base = g, base + '__g'
        res = {}
        try:
            im = None
            for w in sizes:
                dst = os.path.join(out, f'{base}-{w}.webp')
                if not os.path.exists(dst):
                    if im is None:
                        im = Image.open(src_path)
                        im = im.convert('RGBA') if im.mode in ('P', 'LA', 'RGBA') else im.convert('RGB')
                    w2 = min(w, im.width)
                    h2 = round(im.height * w2 / im.width)
                    im.resize((w2, h2), Image.LANCZOS).save(dst, 'WEBP', quality=82, method=5)
                res[w] = f'/img/{base}-{w}.webp'
            if im is None:
                im = Image.open(src_path)
            res['ratio'] = im.width / im.height
        except Exception as e:  # noqa
            print('image failed', rel, e)
            return None
        return res

    for src, rel in manifest.items():
        lookup[src] = make(rel)
    # crops for page banners: remove the baked-in chevron at the bottom of the live banners
    from PIL import Image
    crops = {
        'hero-endoscopes': ('pages/gebrauchte-endoskope/scopREPAIR-Gebrauchte-Endoskope-res.webp', (0, 0, 1600, 760)),
        'banner-repair': ('pages/reparatur/scopeREPAIR-GmbH-Reparatur-res.webp', (0, 0, 2400, 760)),
        'banner-buy': ('pages/ankauf/scopeREPAIR-GmbH-Ankauf.webp', (0, 0, 2400, 760)),
        'banner-systems': ('pages/endoskopie-anlagen/scopeREPAIR-GmbH-Endoskopie-Anlagen.webp', (0, 0, 2400, 760)),
        'banner-pickup': ('pages/abholauftrag/scopeREPAIR-GmbH-Abholauftrag.webp', (0, 0, 2400, 760)),
        'banner-about': ('pages/ueber-uns/scopeREPAIR-Ueber-uns_2.webp', (0, 0, 2400, 760)),
        'banner-contact': ('pages/kontakt/scopeREPAIR-GmbH-Kontakt.webp', (0, 0, 2400, 760)),
    }
    # assets/hero/<page>.(jpg|png|webp) is the editable source of every hero image;
    # if a file is missing there, it is re-created from the live-site crop above.
    os.makedirs(HERO_DIR, exist_ok=True)
    for key, (rel, box) in crops.items():
        hero_src = None
        for ext in ('jpg', 'jpeg', 'png', 'webp'):
            cand = os.path.join(HERO_DIR, f'{HERO_NAMES[key]}.{ext}')
            if os.path.exists(cand):
                hero_src = cand
                break
        if hero_src:
            c = Image.open(hero_src).convert('RGB')
        else:
            im = Image.open(os.path.join(PHOTOS, rel)).convert('RGB')
            box = (box[0], box[1], min(box[2], im.width), min(box[3], im.height))
            c = im.crop(box)
            hero_src = os.path.join(HERO_DIR, f'{HERO_NAMES[key]}.jpg')
            c.save(hero_src, 'JPEG', quality=92)
        sig = f'{os.path.getmtime(hero_src):.0f}-{os.path.getsize(hero_src)}'
        res = {}
        for w in (800, 1600, 2400):
            dst = os.path.join(out, f'{key}-{w}.webp')
            stamp = dst + '.src'
            if not os.path.exists(dst) or not os.path.exists(stamp) or open(stamp).read() != sig:
                open(stamp, 'w').write(sig)
                w2 = min(w, c.width)
                c.resize((w2, round(c.height * w2 / c.width)), Image.LANCZOS).save(dst, 'WEBP', quality=80, method=5)
            res[w] = f'/img/{key}-{w}.webp?v=' + hashlib.md5(sig.encode()).hexdigest()[:8]
        res['ratio'] = c.width / c.height
        lookup[key] = res
    # team / workshop photos (assets/photos/team/<name>.png|jpg) -> images['team-<name>']
    team_dir = os.path.join(PHOTOS, 'team')
    for fn in sorted(os.listdir(team_dir)) if os.path.isdir(team_dir) else []:
        stem, ext = os.path.splitext(fn)
        if ext.lower() not in ('.png', '.jpg', '.jpeg', '.webp'):
            continue
        src = os.path.join(team_dir, fn)
        sig = f'{os.path.getmtime(src):.0f}-{os.path.getsize(src)}'
        im = None
        res = {}
        for w in (480, 960, 1600):
            dst = os.path.join(out, f'team-{stem}-{w}.webp')
            stamp = dst + '.src'
            if not os.path.exists(dst) or not os.path.exists(stamp) or open(stamp).read() != sig:
                im = im or Image.open(src).convert('RGB')
                w2 = min(w, im.width)
                im.resize((w2, round(im.height * w2 / im.width)), Image.LANCZOS).save(dst, 'WEBP', quality=82, method=5)
                open(stamp, 'w').write(sig)
            res[w] = f'/img/team-{stem}-{w}.webp?v=' + hashlib.md5(sig.encode()).hexdigest()[:8]
        lookup[f'team-{stem}'] = res
    # brand assets
    for name in ('scopeREPAIR-Logo2025-300small.webp', 'QAS-International-GM3329.webp', 'Favicon_Scoperepair_neu_2024_transparent.png'):
        shutil.copy(os.path.join(PHOTOS, 'pages', 'brand', name), os.path.join(out, name))
    return lookup


def zip_photos():
    dst = os.path.join(SITE, 'downloads', 'scoperepair-fotos.zip')
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    if os.path.exists(dst):
        return
    with zipfile.ZipFile(dst, 'w', zipfile.ZIP_STORED) as z:
        for base, _, files in os.walk(PHOTOS):
            for fn in files:
                p = os.path.join(base, fn)
                z.write(p, os.path.join('scoperepair-fotos', os.path.relpath(p, PHOTOS)))


def zip_hero():
    dst = os.path.join(SITE, 'downloads', 'scoperepair-hero.zip')
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    with zipfile.ZipFile(dst, 'w', zipfile.ZIP_STORED) as z:
        for fn in sorted(os.listdir(HERO_DIR)):
            z.write(os.path.join(HERO_DIR, fn), os.path.join('scoperepair-hero', fn))


# ──────────────────────────────────────────────────────────────────────────
# Data helpers for templates
# ──────────────────────────────────────────────────────────────────────────
_hide = os.path.join(ROOT, 'assets', 'photos', 'products-glass', '_hide_from_gallery.txt')
HIDDEN_PHOTOS = ['products__' + os.path.splitext(l.strip())[0].replace('/', '__')
                 for l in (open(_hide).read().split() if os.path.exists(_hide) else [])]


def product_view(p, lang, images):
    gal = [images.get(u) for u in p['gallery']]
    gal = [g for g in gal if g and not any(h + '-' in str(g) or h + '__g-' in str(g) for h in HIDDEN_PHOTOS)]
    # lead with a glass-backdrop shot so catalog cards look consistent
    if gal and '__g-' not in str(gal[0]):
        gi = next((i for i, g in enumerate(gal) if '__g-' in str(g)), None)
        if gi:
            gal.insert(0, gal.pop(gi))
    t_type = C.TYPES.get(p['type'], {}).get(lang, p['type'])
    if lang in ('de', 'en'):
        title = p['title'][lang]
    else:
        title = f"{t_type} {p['brand']} {p['model']}" if p['kind'] != 'system' else f"{p['brand']} {p['model']}"
    specs = []
    for s in p['specs']:
        vals = s['de'] if lang == 'de' else s['en']
        vals = [C.SPEC_VALUE_TR.get(v, {}).get(lang, v) if lang in ('fr', 'ru') else v for v in (s['de'] if lang in ('fr', 'ru') else vals)]
        specs.append({'label': C.SPEC_LABELS.get(s['key'], {}).get(lang, s['key']),
                      'hint': C.SPEC_HINT.get(s['key'], {}).get(lang, ''), 'vals': vals, 'key': s['key']})
    acc_src = p['acc']['de' if lang == 'de' else 'en']
    acc = []
    for a in acc_src:
        img = images.get(a['img'])
        if not img:  # EN pages use "-1" duplicates of the same photo
            for k, v in images.items():
                if isinstance(k, str) and k.endswith('/' + os.path.basename(a['img']).replace('-1.webp', '.webp')):
                    img = v
                    break
        acc.append({'name': a['name'], 'desc': a['desc'] if a['desc'] != a['name'] else '', 'img': img})
    dlang = 'de' if lang == 'de' else 'en'
    return {
        **p, 'title_l': title, 'type_l': t_type, 'cond_l': C.CONDITIONS.get(p['cond'], {}).get(lang, p['cond']),
        'price': (C.fmt_eur(C.price_eur(p), lang) if C.price_eur(p) else None),
        'imgs': gal, 'img': gal[0] if gal else None, 'specs_l': specs, 'acc_l': acc,
        'desc_l': p['desc'][dlang] or p['desc']['de'], 'desc_fallback': lang in ('fr', 'ru') and bool(p['desc']['en']),
    }


def model_index():
    d = defaultdict(set)
    for p in C.PRODUCTS:
        if p['kind'] == 'endoscope':
            d[p['brand'] + '|' + p['type']].add(p['model'])
    return {k: sorted(v) for k, v in d.items()}


# ──────────────────────────────────────────────────────────────────────────
# Rendering
# ──────────────────────────────────────────────────────────────────────────
def asset_version():
    import hashlib
    h = hashlib.md5()
    for base, _, files in os.walk(os.path.join(ROOT, 'static')):
        for fn in sorted(files):
            if fn.endswith(('.css', '.js')):
                h.update(open(os.path.join(base, fn), 'rb').read())
    return h.hexdigest()[:8]


AV = asset_version()


def make_env(variant):
    dirs = [variant] + (['v1'] if variant != 'v1' else []) + ['shared']
    env = Environment(
        loader=ChoiceLoader([FileSystemLoader(os.path.join(ROOT, 'templates', d)) for d in dirs]),
        autoescape=select_autoescape(['html']), trim_blocks=True, lstrip_blocks=True)
    return env


def render_variant(variant, images):
    env = make_env(variant)
    models = model_index()
    for lang in C.LANGS:
        def tr(d, lang=lang):
            if isinstance(d, dict):
                return d.get(lang) or d.get('en') or d.get('de') or ''
            return d

        def t(key, **kw):
            s = tr(C.T[key])
            for k, v in kw.items():
                s = s.replace('{' + k + '}', str(v))
            return s

        def url(page_id, query='', l=None):
            l = l or lang
            if page_id == 'index':
                return f'/{variant}/{l}/' + query
            return f'/{variant}/{l}/{page_id}.html' + query

        def purl(slug, l=None):
            return f'/{variant}/{l or lang}/endoskop/{slug}.html'

        def img(src, size=960):
            r = images.get(src) if isinstance(src, str) else src
            if not r:
                return ''
            return r.get(size) or r.get(960) or r.get(1600) or ''

        def srcset(src):
            r = images.get(src) if isinstance(src, str) else src
            if not r:
                return ''
            return ', '.join(f'{v} {k}w' for k, v in r.items() if isinstance(k, int))

        def heads_json(heads):
            return json.dumps([[tr(a), tr(b)] for a, b in heads], ensure_ascii=False)

        prods = [product_view(p, lang, images) for p in C.PRODUCTS]
        by_slug = {p['slug']: p for p in prods}
        endos = [p for p in prods if p['kind'] == 'endoscope']
        systems = [p for p in prods if p['kind'] == 'system']
        matrix = defaultdict(int)
        for p in endos:
            matrix[(p['brand'], p['type'])] += 1

        g = dict(lang=lang, langs=C.LANGS, lang_names=C.LANG_NAMES, variant=variant, C=C, T=C.T, tr=tr, t=t, url=url, purl=purl,
                 img=img, srcset=srcset, company=C.COMPANY, nav=C.NAV, endos=endos, systems=systems, by_slug=by_slug,
                 matrix=matrix, models_json=Markup(json.dumps(models, ensure_ascii=False)), images=images,
                 Markup=Markup, json=json, now_year=datetime.date.today().year, heads_json=heads_json, av=AV)

        for pid, (tpl, faq_key) in PAGES.items():
            try:
                env.get_template(tpl)
            except TemplateNotFound:
                continue  # page exists only in some variants (e.g. v2 home alternatives)
            ppid = 'index' if pid.startswith('index-') else pid
            ctx = dict(g, page=ppid, pid=pid, p=C.P.get(ppid, {}), faq=C.faq(faq_key, lang) if faq_key else None)
            if tpl == 'legal.html':
                ctx['legal'] = C.LEGAL[pid]['de' if lang == 'de' else 'en']
                ctx['legal_title'] = tr(C.LEGAL_TITLES[pid])
            html = env.get_template(tpl).render(**ctx)
            path = os.path.join(SITE, variant, lang, 'index.html' if pid == 'index' else f'{pid}.html')
            write(path, html)
        tpl = env.get_template('produkt.html')
        for p in prods:
            related = [x for x in prods if x['kind'] == p['kind'] and x['type'] == p['type'] and x['slug'] != p['slug']]
            related.sort(key=lambda x: (x['brand'] != p['brand'], not x['img']))
            html = tpl.render(**dict(g, page='produkt', p=C.P['produkt'], prod=p, related=related[:3], faq=None))
            write(os.path.join(SITE, variant, lang, 'endoskop', f"{p['slug']}.html"), html)
    print('built', variant)


def render_hub():
    env = Environment(loader=FileSystemLoader(os.path.join(ROOT, 'templates', 'hub')), autoescape=select_autoescape(['html']))
    variants = json.load(open(os.path.join(ROOT, 'data', 'variants.json'), encoding='utf-8'))
    screens = [{'id': s, 'label': l, 'path': ('endoskop/' + DEMO_PRODUCT + '.html') if s == 'produkt' else ('index.html' if s == 'index' else s + '.html')} for s, l in SCREENS]
    for name in ('index.html', 'mobile.html'):
        html = env.get_template(name).render(variants=variants, screens=screens, screens_json=Markup(json.dumps(screens, ensure_ascii=False)),
                                             variants_json=Markup(json.dumps(variants, ensure_ascii=False)), langs=C.LANGS, av=AV)
        write(os.path.join(SITE, name), html)


def write(path, html):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)


def copy_static():
    dst = os.path.join(SITE, 'static')
    if os.path.exists(dst):
        shutil.rmtree(dst)
    shutil.copytree(os.path.join(ROOT, 'static'), dst)
    # v2 = v1 component layer + v2 visual layer
    over = os.path.join(ROOT, 'static', 'css', 'v2.over.css')
    if os.path.exists(over):
        with open(os.path.join(dst, 'css', 'v2.css'), 'w', encoding='utf-8') as f:
            f.write(open(os.path.join(ROOT, 'static', 'css', 'v1.css'), encoding='utf-8').read())
            f.write('\n/* ===== v2 layer ===== */\n')
            f.write(open(over, encoding='utf-8').read())


def main():
    only = sys.argv[1:] or VARIANTS
    os.makedirs(SITE, exist_ok=True)
    copy_static()
    images = build_images()
    zip_photos()
    zip_hero()
    for v in only:
        if os.path.isdir(os.path.join(ROOT, 'templates', v)):
            render_variant(v, images)
    render_hub()
    write(os.path.join(SITE, '404.html'), '<!doctype html><meta charset="utf-8"><meta http-equiv="refresh" content="0;url=/">')


if __name__ == '__main__':
    main()
