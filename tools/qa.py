"""QA: screenshots at 1440/390, horizontal overflow, blocked clicks, console errors.

    python3 tools/qa.py v1 de index reparatur ...   (pages optional; default all)
Screens go to /tmp/qa/<variant>/<lang>/<page>-<w>.png
"""
import json
import os
import sys

from playwright.sync_api import sync_playwright

BASE = os.environ.get('QA_BASE', 'http://localhost:8765')
ALL = ['index', 'reparatur', 'reparatur-auftrag', 'leihgeraete', 'leihgeraet-anfragen', 'gebrauchte-endoskope',
       'endoskop/gastroskop-pentax-eg-1580k', 'ankauf', 'ankauf-anfrage', 'endoskopie-anlagen', 'rechner', 'ueber-uns',
       'kontakt', 'impressum', 'datenschutz', 'agb', 'rechtliches']

CHECK_JS = r"""
() => {
  const out = {overflow: document.documentElement.scrollWidth - window.innerWidth, blocked: [], wide: []};
  const els = [...document.querySelectorAll('a[href], button, input, select, textarea, summary, [tabindex]')];
  for (const el of els) {
    const r = el.getBoundingClientRect();
    if (r.width < 2 || r.height < 2) continue;
    const st = getComputedStyle(el);
    if (st.visibility === 'hidden' || st.opacity === '0' || el.closest('[hidden],[inert]')) continue;
    if (el.type === 'radio' || el.type === 'checkbox' || el.type === 'file') continue;
    const x = r.left + r.width / 2, y = r.top + r.height / 2;
    if (y < 0 || y > window.innerHeight || x < 0 || x > window.innerWidth) continue;
    const hit = document.elementFromPoint(x, y);
    if (!hit) continue;
    if (hit === el || el.contains(hit) || hit.contains(el) || (el.labels && [...el.labels].some(l => l.contains(hit)))) continue;
    if (hit.closest('.hdr') && !el.closest('.hdr')) continue; // sticky header overlaps content while scrolling: expected
    if (hit.closest('.wz-foot') && !el.closest('.wz-foot')) continue; // sticky wizard footer on mobile: expected while scrolling
    if (el.closest('label') && el.closest('label').contains(hit)) continue;
    out.blocked.push((el.tagName + ' ' + (el.textContent || el.name || el.className || '').trim().slice(0, 40)) + ' <- ' + hit.tagName + '.' + (hit.className && hit.className.baseVal === undefined ? hit.className : '').toString().slice(0, 40));
  }
  for (const el of document.querySelectorAll('body *')) {
    const r = el.getBoundingClientRect();
    if (r.right > window.innerWidth + 1 && r.width > 0 && getComputedStyle(el).position !== 'fixed' && !el.closest('[data-gal-track],.chips,.mnav,.dd,.lb,.toasts,.hero-img,.phero-img,svg')) out.wide.push(el.tagName + '.' + String(el.className).slice(0, 40) + ' ' + Math.round(r.right));
  }
  out.wide = out.wide.slice(0, 8);
  return out;
}
"""


def run(variant, lang, pages, widths=(1440, 390), full=True):
    os.makedirs(f'/tmp/qa/{variant}/{lang}', exist_ok=True)
    report = {}
    with sync_playwright() as pw:
        b = pw.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
        for w in widths:
            ctx = b.new_context(viewport={'width': w, 'height': 900 if w > 500 else 844}, device_scale_factor=1)
            ctx.add_init_script("try{localStorage.setItem('sr-cookie','all')}catch(e){}")
            page = ctx.new_page()
            errs = []
            page.on('console', lambda m: errs.append(m.text) if m.type == 'error' else None)
            page.on('pageerror', lambda e: errs.append(str(e)))
            for pid in pages:
                url = f'{BASE}/{variant}/{lang}/' + ('' if pid == 'index' else pid + '.html')
                errs.clear()
                page.goto(url, wait_until='networkidle')
                page.add_style_tag(content='.rvl{opacity:1!important;transform:none!important}*{animation:none!important;transition:none!important}')
                page.wait_for_timeout(150)
                res = {'top': page.evaluate(CHECK_JS)}
                # scroll through to check blocked clicks at several positions
                h = page.evaluate('document.body.scrollHeight')
                for y in range(900, min(h, 9000), 1400):
                    page.evaluate(f'window.scrollTo(0,{y})')
                    page.wait_for_timeout(60)
                    r = page.evaluate(CHECK_JS)
                    res['top']['blocked'] += r['blocked']
                page.evaluate('window.scrollTo(0,0)')
                name = pid.replace('/', '_')
                page.screenshot(path=f'/tmp/qa/{variant}/{lang}/{name}-{w}.png', full_page=full)
                res['errors'] = list(errs)
                report[f'{pid}@{w}'] = res
            ctx.close()
        b.close()
    bad = {k: v for k, v in report.items() if v['top']['overflow'] > 0 or v['top']['blocked'] or v['errors'] or v['top']['wide']}
    print(json.dumps(bad, indent=1, ensure_ascii=False) if bad else 'QA OK: no overflow, no blocked clicks, no console errors')
    return report


if __name__ == '__main__':
    v = sys.argv[1] if len(sys.argv) > 1 else 'v1'
    lang = sys.argv[2] if len(sys.argv) > 2 else 'de'
    pages = sys.argv[3:] or ALL
    run(v, lang, pages)
