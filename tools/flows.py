"""Interaction smoke tests for the prototype (desktop + mobile)."""
import sys
from playwright.sync_api import sync_playwright

BASE = 'http://localhost:8765'
V = sys.argv[1] if len(sys.argv) > 1 else 'v1'
L = sys.argv[2] if len(sys.argv) > 2 else 'de'
ok = []


def check(name, cond):
    ok.append((name, bool(cond)))
    print(('PASS ' if cond else 'FAIL ') + name)


with sync_playwright() as pw:
    b = pw.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
    errors = []
    for w, h in ((1440, 900), (390, 844)):
        ctx = b.new_context(viewport={'width': w, 'height': h})
        ctx.add_init_script("try{localStorage.setItem('sr-cookie','all')}catch(e){}")
        pg = ctx.new_page()
        pg.on('pageerror', lambda e: errors.append(str(e)))
        tag = f'@{w}'
        # repair wizard full flow
        pg.goto(f'{BASE}/{V}/{L}/reparatur-auftrag.html')
        pg.click('[data-next]')
        check('wizard blocks empty step' + tag, pg.is_visible('[data-field=hersteller].is-invalid'))
        pg.click('[data-ai-demo]')
        pg.wait_for_timeout(2300)
        check('ai fills brand' + tag, pg.is_checked('input[name=hersteller][value=Olympus]'))
        pg.click('[data-next]')
        pg.click('[data-next]')
        check('defect required' + tag, pg.is_visible('[data-field=defekt].is-invalid'))
        pg.click('input[name=defekt][value=dicht]', force=True)
        pg.click('[data-next]')
        pg.click('input[name=leihgeraet][value=ja]', force=True)
        check('loaner panel' + tag, pg.is_visible('[data-show-if="leihgeraet=ja"]'))
        pg.click('[data-next]')
        pg.click('[data-step]:not([hidden]) [data-demo]')
        pg.click('[data-next]')
        pg.click('[data-step]:not([hidden]) [data-demo]')
        pg.click('[data-next]')
        txt = pg.inner_text('[data-review-box]')
        check('review shows device' + tag, 'CF-HQ190L' in txt)
        pg.click('[data-submit]')
        check('consent required' + tag, pg.is_visible('[data-field=consent].is-invalid'))
        pg.click('input[name=consent]', force=True)
        pg.click('[data-submit]')
        pg.wait_for_timeout(1500)
        check('wizard success' + tag, pg.is_visible('#done'))
        # error state
        pg.goto(f'{BASE}/{V}/{L}/kontakt.html')
        pg.click('input[name=anrede] >> nth=1', force=True)
        pg.select_option('#f-betreff', 'beratung')
        pg.fill('#f-firma', 'Praxis')
        pg.fill('#f-vorname', 'A'); pg.fill('#f-nachname', 'B')
        pg.fill('#f-email', 'fehler@test.de'); pg.fill('#f-nachricht', 'Test')
        pg.click('#msg-form input[name=consent]', force=True)
        pg.click('#msg-form [type=submit]')
        pg.wait_for_timeout(1500)
        check('send error shown' + tag, pg.is_visible('#msg-form [data-send-error]'))
        pg.fill('#f-email', 'ok@test.de')
        pg.click('#msg-form [type=submit]')
        pg.wait_for_timeout(1500)
        check('contact success' + tag, pg.is_visible('#msg-ok'))
        # callback tab via URL
        pg.goto(f'{BASE}/{V}/{L}/kontakt.html?tab=rueckruf')
        check('callback tab from url' + tag, pg.is_visible('#panel-cb'))
        # catalog filter
        pg.goto(f'{BASE}/{V}/{L}/gebrauchte-endoskope.html?hersteller=pentax&typ=koloskop')
        n = pg.locator('[data-p]:not(.is-hidden)').count()
        cnt = pg.inner_text('[data-count]')
        check(f'catalog prefilter ({cnt})' + tag, '23' in cnt and n == 12)
        pg.click('[data-more]')
        check('load more' + tag, pg.locator('[data-p]:not(.is-hidden)').count() == 23)
        pg.fill('[data-search]', 'ec-3890')
        pg.wait_for_timeout(400)
        check('search' + tag, 0 < pg.locator('[data-p]:not(.is-hidden)').count() < 12)
        # product gallery + inquiry
        pg.goto(f'{BASE}/{V}/{L}/endoskop/gastroskop-pentax-eg-1580k.html')
        check('gallery prev disabled at start' + tag, pg.is_disabled('[data-gal-prev]'))
        pg.click('[data-gal-next]')
        check('gallery next' + tag, pg.is_enabled('[data-gal-prev]'))
        pg.click('[data-inq-open]')
        check('inquiry opens' + tag, pg.is_visible('#inq'))
        # calculator
        pg.goto(f'{BASE}/{V}/{L}/rechner.html')
        for k, v in (('devices', '4'), ('contract', '12000'), ('repairs', '3'), ('cost', '1500')):
            pg.fill(f'[name={k}]', v)
        check('calculator result' + tag, pg.is_visible('[data-calc-res]') and '7' in pg.inner_text('[data-out-diff]'))
        if w < 500:
            pg.goto(f'{BASE}/{V}/{L}/')
            pg.click('[data-burger]')
            pg.wait_for_timeout(400)
            check('mobile menu opens' + tag, pg.is_visible('[data-mnav]') and pg.evaluate("document.body.classList.contains('is-locked')"))
            pg.click('[data-mnav-toggle] >> nth=0')
            pg.wait_for_timeout(400)
            check('mobile submenu' + tag, pg.is_visible('.mnav-sub.is-open a >> nth=0'))
            pg.click('[data-burger]')
            pg.wait_for_timeout(400)
            check('mobile menu closes' + tag, not pg.is_visible('[data-mnav]'))
        else:
            pg.goto(f'{BASE}/{V}/{L}/')
            pg.hover('.nav-item[data-dd] >> nth=0')
            pg.wait_for_timeout(300)
            check('dropdown hover' + tag, pg.is_visible('.nav-item .dd.is-open a >> nth=0'))
            pg.click('.lang-btn')
            check('lang dropdown' + tag, pg.is_visible('.lang .dd.is-open'))
        ctx.close()
    check('no JS errors ' + str(errors[:3]), not errors)
    b.close()
print('\n%d/%d passed' % (sum(1 for _, x in ok if x), len(ok)))
