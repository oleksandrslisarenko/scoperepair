/* scopeREPAIR prototype — shared behaviour for all variants.
   Header, menus, dropdowns, accordions, tabs, galleries, lightbox, catalog filters,
   fake forms + wizards, calculator, toasts, live TOC, reveal-on-scroll. */
(function () {
  'use strict';
  var I = window.I18N || {};
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var params = new URLSearchParams(location.search);
  var fmt = function (s, o) { return String(s).replace(/\{(\w+)\}/g, function (_, k) { return o[k] != null ? o[k] : ''; }); };

  /* ── hero parallax: endoscope follows the pointer (desktop, motion allowed) ── */
  (function () {
    var hero = $('.hero') || $('.x-hero-panel'), img = hero && $('.hero-img, .x-hero-media img', hero);
    if (!img || reduce || !window.matchMedia('(hover:hover) and (pointer:fine)').matches) return;
    hero.addEventListener('mousemove', function (e) {
      var r = hero.getBoundingClientRect(), x = (e.clientX - r.left) / r.width - 0.5, y = (e.clientY - r.top) / r.height - 0.5;
      img.style.setProperty('--mx', (-x * 48).toFixed(1) + 'px'); img.style.setProperty('--my', (-y * 48).toFixed(1) + 'px');
    });
    hero.addEventListener('mouseleave', function () { img.style.setProperty('--mx', '0px'); img.style.setProperty('--my', '0px'); });
  })();

  /* ── cookie banner (choice stored per browser) ── */
  (function () {
    var ck = $('[data-cookie]'); if (!ck) return;
    function get() { try { return localStorage.getItem('sr-cookie'); } catch (e) { return null; } }
    function show(v) { ck.hidden = !v; if (v) requestAnimationFrame(function () { ck.classList.add('is-in'); }); else ck.classList.remove('is-in'); }
    $$('[data-cookie-set]', ck).forEach(function (b) {
      b.addEventListener('click', function () { try { localStorage.setItem('sr-cookie', b.dataset.cookieSet); } catch (e) {} show(false); });
    });
    $$('[data-cookie-open]').forEach(function (a) { a.addEventListener('click', function (e) { e.preventDefault(); show(true); var f = $('[data-cookie-set=all]', ck); if (f) f.focus(); }); });
    if (!get()) setTimeout(function () { show(true); }, 600);
  })();

  /* ── blueprint hero: magnifier shows the real photo under the cursor ── */
  (function () {
    var bp = $('[data-bp]'); if (!bp) return;
    var lens = $('[data-lens]', bp), li = $('[data-lens-img]', bp), lines = $('img.x-bp-lines', bp);
    var ZOOM = 1.6, R = 110;
    li.style.backgroundImage = 'url(/static/img/hero-photo.jpg)';
    var dot = $('[data-bp-dot]', bp);
    function placeDot() { if (!dot) return; var br = bp.getBoundingClientRect(), ir = lines.getBoundingClientRect(); dot.style.left = (ir.left - br.left + ir.width * 0.71) + 'px'; dot.style.top = (ir.top - br.top + ir.height * 0.47) + 'px'; }
    placeDot(); window.addEventListener('resize', placeDot); if (!lines.complete) lines.addEventListener('load', placeDot);
    function place(cx, cy) {
      var br = bp.getBoundingClientRect(), ir = lines.getBoundingClientRect();
      var x = cx - br.left, y = cy - br.top;
      lens.style.transform = ''; lens.style.left = x + 'px'; lens.style.top = y + 'px';
      var w = ir.width * ZOOM, h = ir.height * ZOOM;
      var px = (cx - ir.left) * ZOOM, py = (cy - ir.top) * ZOOM;
      li.style.backgroundSize = w + 'px ' + h + 'px';
      li.style.backgroundPosition = (R - px) + 'px ' + (R - py) + 'px';
    }
    /* lens works only over the right half of the hero; the 'hover me' dot hides only while the pointer is there */
    function inZone(cx) { var r = bp.getBoundingClientRect(); return cx >= r.left + r.width / 2; }
    function off() { lens.classList.remove('is-on'); bp.classList.remove('is-used', 'is-zone'); }
    bp.addEventListener('pointermove', function (e) {
      if (e.pointerType === 'touch') return;
      if (!inZone(e.clientX)) { off(); return; }
      place(e.clientX, e.clientY); lens.classList.add('is-on'); bp.classList.add('is-used', 'is-zone');
    });
    bp.addEventListener('pointerleave', off);
    /* touch: tap to drop the lens */
    bp.addEventListener('pointerdown', function (e) { if (e.pointerType !== 'touch') return; place(e.clientX, e.clientY); lens.classList.add('is-on'); bp.classList.add('is-used'); });
  })();

  /* ── toasts ───────────────────────────── */
  function toast(msg, ms) {
    var box = $('[data-toasts]'); if (!box) return;
    var el = document.createElement('div'); el.className = 'toast';
    el.innerHTML = '<svg class="icon" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="8.5"/><path d="M12 11v5.5M12 7.8v.2"/></svg><span></span>';
    el.lastChild.textContent = msg; box.appendChild(el);
    setTimeout(function () { el.classList.add('is-out'); setTimeout(function () { el.remove(); }, 260); }, ms || 2600);
  }
  window.srToast = toast;
  document.addEventListener('click', function (e) {
    var a = e.target.closest('a[href="#"], [data-todo]');
    if (a) { e.preventDefault(); toast(I.todo); }
  });

  /* ── header ───────────────────────────── */
  var hdr = $('[data-hdr]');
  if (hdr) {
    var onScroll = function () { hdr.classList.toggle('is-scrolled', window.scrollY > 8); };
    onScroll(); window.addEventListener('scroll', onScroll, { passive: true });
  }

  /* ── dropdowns (desktop nav + language) ─ */
  var openDD = null;
  function closeDD(dd) {
    if (!dd) return; var b = $('[data-dd-btn]', dd), m = $('[data-dd-menu]', dd);
    b.setAttribute('aria-expanded', 'false'); m.classList.remove('is-open'); if (openDD === dd) openDD = null;
  }
  function openDDfn(dd) {
    if (openDD && openDD !== dd) closeDD(openDD);
    $('[data-dd-btn]', dd).setAttribute('aria-expanded', 'true'); $('[data-dd-menu]', dd).classList.add('is-open'); openDD = dd;
  }
  $$('[data-dd]').forEach(function (dd) {
    var btn = $('[data-dd-btn]', dd), timer;
    btn.addEventListener('click', function (e) { e.stopPropagation(); btn.getAttribute('aria-expanded') === 'true' ? closeDD(dd) : openDDfn(dd); });
    if (dd.hasAttribute('data-dd-hover') && window.matchMedia('(hover:hover)').matches) {
      dd.addEventListener('mouseenter', function () { clearTimeout(timer); openDDfn(dd); });
      dd.addEventListener('mouseleave', function () { timer = setTimeout(function () { closeDD(dd); }, 160); });
    }
    dd.addEventListener('keydown', function (e) {
      var items = $$('[data-dd-menu] a', dd), i = items.indexOf(document.activeElement);
      if (e.key === 'Escape') { closeDD(dd); btn.focus(); }
      if (e.key === 'ArrowDown') { e.preventDefault(); openDDfn(dd); (items[i + 1] || items[0]).focus(); }
      if (e.key === 'ArrowUp') { e.preventDefault(); (items[i - 1] || items[items.length - 1]).focus(); }
    });
  });
  document.addEventListener('click', function (e) { if (openDD && !openDD.contains(e.target)) closeDD(openDD); });
  document.addEventListener('focusin', function (e) { if (openDD && !openDD.contains(e.target)) closeDD(openDD); });

  /* ── mobile menu ──────────────────────── */
  var burger = $('[data-burger]'), mnav = $('[data-mnav]');
  function setMenu(open) {
    if (!mnav) return;
    burger.setAttribute('aria-expanded', open ? 'true' : 'false');
    document.body.classList.toggle('is-locked', open);
    if (open) { mnav.hidden = false; requestAnimationFrame(function () { mnav.classList.add('is-open'); }); }
    else { mnav.classList.remove('is-open'); setTimeout(function () { if (!mnav.classList.contains('is-open')) mnav.hidden = true; }, 260); }
    burger.innerHTML = open
      ? '<svg class="icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M6 6l12 12M18 6 6 18"/></svg>'
      : '<svg class="icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg>';
  }
  if (burger) {
    burger.addEventListener('click', function () { setMenu(burger.getAttribute('aria-expanded') !== 'true'); });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && burger.getAttribute('aria-expanded') === 'true') { setMenu(false); burger.focus(); } });
    window.addEventListener('resize', function () { if (window.innerWidth > 900 && burger.getAttribute('aria-expanded') === 'true') setMenu(false); });
    $$('[data-mnav-toggle]').forEach(function (b) {
      b.addEventListener('click', function () { var o = b.getAttribute('aria-expanded') !== 'true'; b.setAttribute('aria-expanded', o); b.nextElementSibling.classList.toggle('is-open', o); });
    });
  }

  /* ── reveal on scroll ─────────────────── */
  if (!reduce && 'IntersectionObserver' in window) {
    document.documentElement.classList.add('rvl-on');
    var io = new IntersectionObserver(function (es) { es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('is-shown'); io.unobserve(e.target); } }); }, { rootMargin: '0px 0px -8% 0px', threshold: .05 });
    $$('.rvl').forEach(function (el) { io.observe(el); });
  }

  /* ── FAQ: one open at a time ──────────── */
  $$('[data-faq]').forEach(function (f) {
    $$('details', f).forEach(function (d) { d.addEventListener('toggle', function () { if (d.open) $$('details', f).forEach(function (o) { if (o !== d) o.open = false; }); }); });
  });

  /* ── tabs ─────────────────────────────── */
  $$('[data-tabs]').forEach(function (tabs) {
    var btns = $$('[role=tab]', tabs);
    function sel(b, focus) {
      btns.forEach(function (x) { var on = x === b; x.setAttribute('aria-selected', on); x.tabIndex = on ? 0 : -1; var p = document.getElementById(x.getAttribute('aria-controls')); p.hidden = !on; if (on && !reduce) { p.classList.remove('is-entering'); void p.offsetWidth; p.classList.add('is-entering'); } });
      if (focus) b.focus();
    }
    btns.forEach(function (b, i) {
      b.addEventListener('click', function () { sel(b); });
      b.addEventListener('keydown', function (e) { if (e.key === 'ArrowRight') sel(btns[(i + 1) % btns.length], true); if (e.key === 'ArrowLeft') sel(btns[(i - 1 + btns.length) % btns.length], true); });
    });
    var want = params.get('tab'); var m = btns.filter(function (b) { return b.dataset.tab === want; })[0]; if (m) sel(m);
  });

  /* ── gallery + lightbox ───────────────── */
  $$('[data-gallery]').forEach(function (g) {
    var track = $('[data-gal-track]', g), slides = $$('figure', track), thumbs = $$('[data-gal-thumb]', g);
    var prev = $('[data-gal-prev]', g), next = $('[data-gal-next]', g), count = $('[data-gal-count]', g), i = 0;
    function go(n) {
      i = Math.max(0, Math.min(slides.length - 1, n));
      track.style.transform = 'translateX(' + (-100 * i) + '%)';
      if (prev) prev.disabled = i === 0; if (next) next.disabled = i === slides.length - 1;
      thumbs.forEach(function (t, k) { t.setAttribute('aria-current', k === i ? 'true' : 'false'); });
      slides.forEach(function (s, k) { s.inert = k !== i; });
      if (count) count.textContent = fmt(I.photo_n, { n: i + 1, total: slides.length });
    }
    if (prev) prev.addEventListener('click', function () { go(i - 1); });
    if (next) next.addEventListener('click', function () { go(i + 1); });
    thumbs.forEach(function (t, k) { t.addEventListener('click', function () { go(k); }); });
    g.addEventListener('keydown', function (e) { if (e.key === 'ArrowLeft') go(i - 1); if (e.key === 'ArrowRight') go(i + 1); });
    $$('[data-gal-zoom]', g).forEach(function (z) { z.addEventListener('click', function () { lightbox(slides.map(function (s) { return $('img', s).dataset.full || $('img', s).src; }), i, function (k) { go(k); }); }); });
    go(0);
  });
  function lightbox(srcs, start, onChange) {
    var i = start, last = document.activeElement;
    var lb = document.createElement('div'); lb.className = 'lb'; lb.setAttribute('role', 'dialog'); lb.setAttribute('aria-modal', 'true');
    lb.innerHTML = '<img alt=""><button class="lb-close" aria-label="×"><svg class="icon" viewBox="0 0 24 24"><path d="M6 6l12 12M18 6 6 18"/></svg></button>' +
      '<button class="lb-arrow lb-prev" aria-label="‹"><svg class="icon" viewBox="0 0 24 24"><path d="M15 6l-6 6 6 6"/></svg></button>' +
      '<button class="lb-arrow lb-next" aria-label="›"><svg class="icon" viewBox="0 0 24 24"><path d="m9 6 6 6-6 6"/></svg></button><div class="lb-cap"></div>';
    document.body.appendChild(lb); document.body.classList.add('is-locked');
    var img = $('img', lb), p = $('.lb-prev', lb), n = $('.lb-next', lb), cap = $('.lb-cap', lb);
    function show() { img.src = srcs[i]; p.disabled = i === 0; n.disabled = i === srcs.length - 1; cap.textContent = fmt(I.photo_n, { n: i + 1, total: srcs.length }); if (onChange) onChange(i); }
    function close() { lb.classList.remove('is-open'); document.body.classList.remove('is-locked'); document.removeEventListener('keydown', key); setTimeout(function () { lb.remove(); }, 250); if (last) last.focus(); }
    function key(e) { if (e.key === 'Escape') close(); if (e.key === 'ArrowLeft' && i > 0) { i--; show(); } if (e.key === 'ArrowRight' && i < srcs.length - 1) { i++; show(); } }
    p.onclick = function () { if (i > 0) { i--; show(); } }; n.onclick = function () { if (i < srcs.length - 1) { i++; show(); } };
    $('.lb-close', lb).onclick = close; lb.addEventListener('click', function (e) { if (e.target === lb) close(); });
    document.addEventListener('keydown', key); show(); requestAnimationFrame(function () { lb.classList.add('is-open'); $('.lb-close', lb).focus(); });
  }

  /* ── live table of contents ───────────── */
  $$('[data-toc]').forEach(function (toc) {
    var links = $$('a', toc), map = links.map(function (a) { return document.getElementById(a.getAttribute('href').slice(1)); });
    function upd() {
      var y = window.scrollY + (parseInt(getComputedStyle(document.documentElement).scrollPaddingTop) || 120) + 10, cur = 0;
      map.forEach(function (h, k) { if (h && h.getBoundingClientRect().top + window.scrollY <= y) cur = k; });
      links.forEach(function (a, k) { a.classList.toggle('is-active', k === cur); });
    }
    window.addEventListener('scroll', upd, { passive: true }); upd();
    var sel = $('[data-toc-select]'); if (sel) sel.addEventListener('change', function () { var h = document.getElementById(sel.value); if (h) h.scrollIntoView({ behavior: reduce ? 'auto' : 'smooth' }); });
  });

  /* ── catalog filters ──────────────────── */
  var cat = $('[data-catalog]');
  if (cat) {
    var cards = $$('[data-p]', cat), grid = $('[data-grid]', cat), countEl = $('[data-count]', cat), moreBtn = $('[data-more]', cat), empty = $('[data-empty]', cat);
    var search = $('[data-search]', cat), sortSel = $('[data-sort]', cat), reset = $$('[data-reset]', cat);
    var PAGE = 12, shown = PAGE, state = { brand: [], type: [], cond: [], q: '' };
    var keyMap = { hersteller: 'brand', typ: 'type', zustand: 'cond' };
    Object.keys(keyMap).forEach(function (k) { var v = params.get(k); if (v) state[keyMap[k]] = v.split(','); });
    function chipsSync() {
      $$('[data-filter]', cat).forEach(function (b) {
        var k = b.dataset.filter, v = b.dataset.value;
        b.setAttribute('aria-pressed', v === '' ? (state[k].length === 0) : state[k].indexOf(v) >= 0);
      });
    }
    function matches(c, skip) {
      return (skip === 'brand' || !state.brand.length || state.brand.indexOf(c.dataset.brand) >= 0) &&
        (skip === 'type' || !state.type.length || state.type.indexOf(c.dataset.type) >= 0) &&
        (skip === 'cond' || !state.cond.length || state.cond.indexOf(c.dataset.cond) >= 0) &&
        (!state.q || c.dataset.model.indexOf(state.q) >= 0);
    }
    function apply(animate) {
      var list = cards.filter(function (c) { return matches(c); });
      var s = sortSel ? sortSel.value : 'model';
      list.sort(function (a, b) {
        if (s === 'photo' && a.dataset.photo !== b.dataset.photo) return b.dataset.photo - a.dataset.photo;
        if (s === 'brand' && a.dataset.brand !== b.dataset.brand) return a.dataset.brand < b.dataset.brand ? -1 : 1;
        return a.dataset.model < b.dataset.model ? -1 : a.dataset.model > b.dataset.model ? 1 : 0;
      });
      cards.forEach(function (c) { c.classList.add('is-hidden'); c.classList.remove('is-in'); });
      list.forEach(function (c, k) { grid.appendChild(c); if (k < shown) { c.classList.remove('is-hidden'); if (animate && !reduce) { c.style.animationDelay = Math.min(k, 8) * 30 + 'ms'; c.classList.add('is-in'); } } });
      countEl.textContent = fmt(I.count, { n: list.length });
      var rest = list.length - shown;
      moreBtn.hidden = rest <= 0; if (rest > 0) moreBtn.textContent = fmt(I.more, { n: Math.min(rest, PAGE) });
      empty.hidden = list.length > 0;
      reset.forEach(function (r) { r.hidden = !(state.brand.length || state.type.length || state.cond.length || state.q); });
      // counts per chip (faceted)
      $$('[data-filter]', cat).forEach(function (b) {
        var k = b.dataset.filter, v = b.dataset.value, small = $('small', b); if (!small) return;
        var n = cards.filter(function (c) { return matches(c, k) && (v === '' || c.dataset[k] === v); }).length;
        small.textContent = n; b.disabled = n === 0 && b.getAttribute('aria-pressed') !== 'true';
      });
      var showBtn = $('[data-show-results]'); if (showBtn) showBtn.textContent = fmt(I.show, { n: list.length });
      var q = new URLSearchParams();
      if (state.brand.length) q.set('hersteller', state.brand.join(',')); if (state.type.length) q.set('typ', state.type.join(',')); if (state.cond.length) q.set('zustand', state.cond.join(','));
      history.replaceState(null, '', location.pathname + (q.toString() ? '?' + q : ''));
    }
    $$('[data-filter]', cat).forEach(function (b) {
      b.addEventListener('click', function () {
        var k = b.dataset.filter, v = b.dataset.value;
        if (v === '') state[k] = []; else { var i = state[k].indexOf(v); if (i >= 0) state[k].splice(i, 1); else state[k].push(v); }
        shown = PAGE; chipsSync(); apply(true);
      });
    });
    if (search) { var tmr; search.addEventListener('input', function () { clearTimeout(tmr); tmr = setTimeout(function () { state.q = search.value.trim().toLowerCase(); shown = PAGE; apply(true); }, 150); }); }
    if (sortSel) sortSel.addEventListener('change', function () { apply(true); });
    moreBtn.addEventListener('click', function () { var first = shown; shown += PAGE; apply(false); var vis = cards.filter(function (c) { return !c.classList.contains('is-hidden'); }); if (vis[first]) { var link = $('a', vis[first]); if (link) link.focus({ preventScroll: true }); } });
    reset.forEach(function (r) { r.addEventListener('click', function () { state = { brand: [], type: [], cond: [], q: '' }; if (search) search.value = ''; shown = PAGE; chipsSync(); apply(true); }); });
    var ft = $('[data-filters-toggle]'), fp = $('[data-filters-panel]');
    if (ft && fp) ft.addEventListener('click', function () { var o = ft.getAttribute('aria-expanded') !== 'true'; ft.setAttribute('aria-expanded', o); fp.classList.toggle('is-open', o); });
    chipsSync(); apply(false);
  }

  /* ── forms: validation ─────────────────── */
  function fieldOf(el) { return el.closest('[data-field]'); }
  function setErr(f, msg) { if (!f) return; f.classList.toggle('is-invalid', !!msg); var e = $('.err span', f); if (e) e.textContent = msg || ''; var inp = $('input,select,textarea', f); if (inp) inp.setAttribute('aria-invalid', msg ? 'true' : 'false'); }
  function validateField(f) {
    if (!f || f.closest('[hidden]')) return true;
    var msg = '';
    if (f.hasAttribute('data-req-group')) { if (!$('input:checked', f)) msg = I.choose; }
    else {
      var el = $('[data-req],[data-type]', f); if (!el) return true;
      var v = (el.type === 'checkbox') ? el.checked : el.value.trim();
      if (el.hasAttribute('data-req') && !v) msg = el.type === 'checkbox' ? I.consent : (el.tagName === 'SELECT' ? I.choose : I.required);
      else if (v && el.dataset.type === 'email' && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v)) msg = I.email;
      else if (v && el.dataset.type === 'phone' && v.replace(/\D/g, '').length < 6) msg = I.phone;
      else if (v && el.dataset.type === 'zip' && !/^[0-9A-Za-z \-]{4,10}$/.test(v)) msg = I.zip;
    }
    setErr(f, msg); return !msg;
  }
  function validateScope(scope) {
    var fields = $$('[data-field]', scope).filter(function (f) { return f.hasAttribute('data-req-group') || $('[data-req],[data-type]', f); });
    var bad = fields.filter(function (f) { return !validateField(f); });
    var extra = scope.__extraValidate ? scope.__extraValidate() : true;
    if (bad.length) { var first = $('input,select,textarea', bad[0]); bad[0].scrollIntoView({ block: 'center', behavior: reduce ? 'auto' : 'smooth' }); if (first) setTimeout(function () { first.focus({ preventScroll: true }); }, 250); }
    return !bad.length && extra;
  }
  document.addEventListener('input', function (e) { var f = fieldOf(e.target); if (f && f.classList.contains('is-invalid')) validateField(f); });
  document.addEventListener('change', function (e) { var f = fieldOf(e.target); if (f && f.classList.contains('is-invalid')) validateField(f); });
  document.addEventListener('focusout', function (e) { var el = e.target; if (el.matches && el.matches('input[data-type],input[data-req]:not([type=checkbox]):not([type=radio]),textarea[data-req]') && el.value) validateField(fieldOf(el)); });

  /* fake submit: success or (if e-mail contains error/fehler/erreur/ошибка) a send error */
  /* ── sending: collects the form and posts it to /api/send (Resend) ── */
  function clean(t) { return String(t || '').replace(/\s*\((optional|optionnel|необязательно|по желанию)\)\s*/gi, ' ').replace(/\s*\*\s*$/, '').replace(/\s+/g, ' ').trim(); }
  function labelOf(el) {
    var f = el.closest('.field, fieldset, [data-field]');
    var l = f && (f.querySelector('legend') || f.querySelector('.label'));
    if (!l && el.type === 'checkbox') l = el.closest('label');
    if (!l) return clean(el.getAttribute('aria-label') || el.name);
    var c = l.cloneNode(true);
    $$('.req, .opt, .ai-badge, [data-ai-slot], .badge, svg', c).forEach(function (x) { x.remove(); });
    return clean(c.textContent).slice(0, 80);
  }
  function collect(form) {
    var out = [], seen = {};
    Array.prototype.forEach.call(form.elements, function (el) {
      if (!el.name || el.disabled || el.type === 'file' || el.type === 'submit' || el.type === 'button' || el.name === 'consent' || el.name === 'website') return;
      var hd = el.closest('[hidden]'); if (hd && !hd.hasAttribute('data-step')) return;
      var v = '';
      if (el.type === 'radio' || el.type === 'checkbox') { if (!el.checked) return; v = el.dataset.label || (el.closest('label') ? clean(el.closest('label').textContent) : el.value); }
      else if (el.tagName === 'SELECT') { var o = el.selectedOptions[0]; v = o && o.value ? o.textContent : ''; }
      else v = el.value;
      v = String(v || '').trim(); if (!v) return;
      var key = el.name;
      if (seen[key] != null && (el.type === 'checkbox' || el.type === 'radio')) { out[seen[key]].value += ', ' + v; return; }
      seen[key] = out.length; out.push({ label: labelOf(el) || el.name, value: v });
    });
    return out;
  }
  function shrink(file) {
    return new Promise(function (res) {
      if (!/^image\/(jpeg|png|webp|gif)$/i.test(file.type)) { res(null); return; }
      var img = new Image(), url = URL.createObjectURL(file);
      img.onload = function () {
        var k = Math.min(1, 1600 / Math.max(img.width, img.height)), c = document.createElement('canvas');
        c.width = Math.round(img.width * k); c.height = Math.round(img.height * k);
        c.getContext('2d').drawImage(img, 0, 0, c.width, c.height); URL.revokeObjectURL(url);
        res({ name: file.name.replace(/\.[^.]+$/, '') + '.jpg', data: c.toDataURL('image/jpeg', 0.82).split(',')[1] });
      };
      img.onerror = function () { res(null); };
      img.src = url;
    });
  }
  function sendForm(form, btn, done) {
    var errBox = $('[data-send-error]', form); if (errBox) errBox.hidden = true;
    var email = ($('input[type=email]', form) || {}).value || '';
    var label = btn.innerHTML; btn.classList.add('is-loading'); btn.disabled = true; btn.textContent = I.sending;
    function finish(ok) {
      btn.classList.remove('is-loading'); btn.disabled = false; btn.innerHTML = label;
      if (!ok) { if (errBox) { errBox.hidden = false; errBox.scrollIntoView({ block: 'center', behavior: reduce ? 'auto' : 'smooth' }); } return; }
      done();
    }
    if (/fehler|error|erreur|ошибк/i.test(email)) { setTimeout(function () { finish(false); }, reduce ? 200 : 900); return; } // test hook for the error state
    var h = form.closest('[data-wz]') ? $('h1', form.closest('[data-wz]').parentNode) : null;
    var title = form.dataset.subject || (h || $('main h1') || {}).textContent || document.title;
    var files = [], skipped = 0;
    $$('input[type=file]', form).forEach(function (inp) { (inp.__files || []).forEach(function (f) { files.push(f); }); });
    Promise.all(files.map(shrink)).then(function (list) {
      var att = list.filter(Boolean); skipped = list.length - att.length;
      var payload = { title: clean(title), page: location.href, lang: document.documentElement.lang, email: email, fields: collect(form), files: att, filesSkipped: skipped, website: (form.elements.website || {}).value || '' };
      return fetch('/api/send', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
    }).then(function (r) {
      if ([404, 405, 501].indexOf(r.status) >= 0 && /^(localhost|127\.)/.test(location.hostname)) { finish(true); return; } // local preview without API
      return r.json().then(function (j) { finish(r.ok && j && j.ok); }, function () { finish(false); });
    }).catch(function () { finish(false); });
  }
  var fakeSend = sendForm;
  window.srFakeSend = fakeSend;

  /* simple forms (contact, inquiry, callback) */
  $$('form[data-form]').forEach(function (form) {
    form.setAttribute('novalidate', '');
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      if (!validateScope(form)) return;
      var btn = $('[type=submit]', form);
      fakeSend(form, btn, function () {
        var ok = document.getElementById(form.dataset.success);
        form.hidden = true; if (ok) { ok.hidden = false; ok.setAttribute('tabindex', '-1'); ok.focus({ preventScroll: true }); ok.scrollIntoView({ block: 'center', behavior: reduce ? 'auto' : 'smooth' }); }
      });
    });
  });
  $$('[data-reopen]').forEach(function (b) { b.addEventListener('click', function () { var f = document.getElementById(b.dataset.reopen); var ok = b.closest('[data-success-box]'); f.reset(); $$('[data-thumbs]', f).forEach(function (t) { t.innerHTML = ''; }); f.hidden = false; if (ok) ok.hidden = true; }); });

  /* photo inputs → thumbnails */
  function bindPhotos(scope) {
    $$('[data-photos]', scope).forEach(function (inp) {
      var field = inp.closest('.field'), thumbs = $('[data-thumbs]', field), drop = inp.closest('[data-drop]');
      inp.__files = [];
      function render() {
        thumbs.innerHTML = '';
        inp.__files.forEach(function (f, k) {
          var d = document.createElement('div'); d.className = 'thumb';
          var heic = /heic|heif/i.test(f.type) || /\.hei[cf]$/i.test(f.name);
          d.innerHTML = heic ? '<div class="ph"><svg class="icon" viewBox="0 0 24 24"><rect x="4" y="5" width="16" height="14" rx="2"/><circle cx="9" cy="10" r="1.6"/><path d="m5 17 5-4.5 3.5 3 2.5-2 3 3.5"/></svg></div>' : '<img alt="">';
          if (!heic) $('img', d).src = URL.createObjectURL(f);
          var x = document.createElement('button'); x.type = 'button'; x.setAttribute('aria-label', I.photo_remove);
          x.innerHTML = '<svg class="icon" viewBox="0 0 24 24"><path d="M6 6l12 12M18 6 6 18"/></svg>';
          x.onclick = function () { inp.__files.splice(k, 1); render(); inp.dispatchEvent(new Event('photos')); };
          d.appendChild(x); thumbs.appendChild(d);
        });
      }
      inp.addEventListener('change', function () { Array.prototype.forEach.call(inp.files, function (f) { if (inp.__files.length < 10) inp.__files.push(f); }); inp.value = ''; render(); inp.dispatchEvent(new Event('photos')); });
      if (drop) {
        ['dragenter', 'dragover'].forEach(function (ev) { drop.addEventListener(ev, function (e) { e.preventDefault(); drop.classList.add('is-over'); }); });
        ['dragleave', 'drop'].forEach(function (ev) { drop.addEventListener(ev, function () { drop.classList.remove('is-over'); }); });
        drop.addEventListener('drop', function (e) { e.preventDefault(); Array.prototype.forEach.call(e.dataTransfer.files, function (f) { if (inp.__files.length < 10 && /^image\//.test(f.type)) inp.__files.push(f); }); render(); inp.dispatchEvent(new Event('photos')); });
      }
    });
  }
  bindPhotos(document);

  /* calendar */
  var MONTHS = {
    de: ['Januar', 'Februar', 'März', 'April', 'Mai', 'Juni', 'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember'],
    en: ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'],
    fr: ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre'],
    ru: ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь']
  };
  var DOW = { de: ['Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa', 'So'], en: ['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su'], fr: ['Lu', 'Ma', 'Me', 'Je', 'Ve', 'Sa', 'Di'], ru: ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'] };
  function fmtDate(d, lang) { return d.toLocaleDateString({ de: 'de-DE', en: 'en-GB', fr: 'fr-FR', ru: 'ru-RU' }[lang] || 'de-DE', { weekday: 'short', day: '2-digit', month: '2-digit', year: 'numeric' }); }
  $$('[data-cal]').forEach(function (cal) {
    var lang = cal.dataset.lang || 'de', input = (cal.closest('.field') || cal.parentNode).querySelector('input[type=hidden]');
    var today = new Date(); today.setHours(0, 0, 0, 0);
    var view = new Date(today.getFullYear(), today.getMonth(), 1), sel = null;
    var minView = new Date(view), maxView = new Date(view.getFullYear(), view.getMonth() + 2, 1);
    function draw() {
      $('[data-cal-month]', cal).textContent = MONTHS[lang][view.getMonth()] + ' ' + view.getFullYear();
      var g = $('[data-cal-grid]', cal); g.innerHTML = '';
      DOW[lang].forEach(function (d) { var s = document.createElement('span'); s.className = 'cal-dow'; s.textContent = d; g.appendChild(s); });
      var off = (view.getDay() + 6) % 7, n = new Date(view.getFullYear(), view.getMonth() + 1, 0).getDate();
      for (var k = 0; k < off; k++) g.appendChild(document.createElement('span'));
      for (var d = 1; d <= n; d++) (function (d) {
        var dt = new Date(view.getFullYear(), view.getMonth(), d), wd = dt.getDay();
        var b = document.createElement('button'); b.type = 'button'; b.className = 'cal-day'; b.textContent = d;
        if (dt.getTime() === today.getTime()) b.classList.add('is-today');
        b.disabled = wd === 0 || wd === 6 || dt <= today;
        b.setAttribute('aria-pressed', sel && sel.getTime() === dt.getTime() ? 'true' : 'false');
        b.setAttribute('aria-label', fmtDate(dt, lang));
        b.onclick = function () { sel = dt; input.value = fmtDate(dt, lang); input.dispatchEvent(new Event('change', { bubbles: true })); draw(); if (cal.__picked) cal.__picked(); };
        g.appendChild(b);
      })(d);
      $('[data-cal-prev]', cal).disabled = view <= minView; $('[data-cal-next]', cal).disabled = view >= maxView;
    }
    $('[data-cal-prev]', cal).onclick = function () { view.setMonth(view.getMonth() - 1); draw(); };
    $('[data-cal-next]', cal).onclick = function () { view.setMonth(view.getMonth() + 1); draw(); };
    cal.__set = function (dt) { sel = dt; view = new Date(dt.getFullYear(), dt.getMonth(), 1); input.value = fmtDate(dt, lang); draw(); if (cal.__sync) cal.__sync(); };
    draw();
  });

  /* date field → calendar in a dropdown */
  $$('[data-dp]').forEach(function (dp) {
    var btn = $('[data-dp-btn]', dp), pop = $('[data-dp-pop]', dp), cal = $('[data-cal]', dp), out = $('[data-dp-val]', dp);
    var input = dp.querySelector('input[type=hidden]');
    function sync() { out.textContent = input.value || out.dataset.ph; dp.classList.toggle('has-val', !!input.value); }
    function open(v) {
      pop.hidden = !v; btn.setAttribute('aria-expanded', v ? 'true' : 'false');
      if (v) { var r = btn.getBoundingClientRect(); dp.classList.toggle('dp-up', window.innerHeight - r.bottom < 380 && r.top > 380); var f = $('.cal-day[aria-pressed=true]', pop) || $('.cal-day:not([disabled])', pop); if (f) f.focus(); }
    }
    btn.addEventListener('click', function () { open(pop.hidden); });
    cal.__picked = function () { sync(); open(false); btn.focus(); };
    cal.__sync = sync;
    document.addEventListener('click', function (e) { if (!pop.hidden && !dp.contains(e.target)) open(false); });
    dp.addEventListener('keydown', function (e) { if (e.key === 'Escape' && !pop.hidden) { e.stopPropagation(); open(false); btn.focus(); } });
    var f = dp.closest('form'); if (f) f.addEventListener('reset', function () { setTimeout(sync, 0); });
    sync();
  });

  /* ── wizards ──────────────────────────── */
  $$('form[data-wizard]').forEach(function (form) {
    form.setAttribute('novalidate', '');
    var steps = $$('[data-step]', form), bar = $$('.stepper li', form.closest('[data-wz]') || document);
    var head = $('[data-step-head]', form), sub = $('[data-step-sub]', form), no = $('[data-step-no]', form), mNo = $('[data-step-m]');
    var back = $('[data-back]', form), next = $('[data-next]', form), submit = $('[data-submit]', form);
    var heads = JSON.parse(form.dataset.heads || '[]'), cur = 0;
    function show(n, dir) {
      steps.forEach(function (s, k) { s.hidden = k !== n; s.classList.remove('is-entering', 'is-back'); });
      if (!reduce) { void steps[n].offsetWidth; steps[n].classList.add(dir < 0 ? 'is-back' : 'is-entering'); }
      bar.forEach(function (li, k) { li.className = k < n ? 'is-done' : (k === n ? 'is-current' : ''); });
      if (head) head.textContent = heads[n][0]; if (sub) { sub.textContent = heads[n][1]; sub.hidden = !heads[n][1]; }
      var label = fmt(I.step_of, { n: n + 1, total: steps.length });
      if (no) no.textContent = label; if (mNo) mNo.textContent = label;
      back.hidden = n === 0; next.hidden = n === steps.length - 1; submit.hidden = n !== steps.length - 1;
      if (n === steps.length - 1) buildReview();
      cur = n;
      var top = form.closest('[data-wz]'); if (top && dir) top.scrollIntoView({ block: 'start', behavior: reduce ? 'auto' : 'smooth' });
    }
    next.addEventListener('click', function () { if (validateScope(steps[cur])) show(cur + 1, 1); });
    back.addEventListener('click', function () { show(cur - 1, -1); });
    form.addEventListener('submit', function (e) {
      e.preventDefault(); if (!validateScope(steps[cur])) return;
      fakeSend(form, submit, function () {
        var wz = form.closest('[data-wz]'), ok = document.getElementById(form.dataset.success);
        wz.hidden = true; ok.hidden = false; fillDone(ok); ok.setAttribute('tabindex', '-1'); ok.focus({ preventScroll: true });
        window.scrollTo({ top: 0, behavior: reduce ? 'auto' : 'smooth' });
      });
    });
    form.addEventListener('keydown', function (e) { if (e.key === 'Enter' && e.target.tagName === 'INPUT' && e.target.type !== 'checkbox' && cur < steps.length - 1) { e.preventDefault(); next.click(); } });
    // values for review / summary
    function val(name) {
      var els = $$('[name="' + name + '"]', form); if (!els.length) return '';
      if (els[0].type === 'radio' || els[0].type === 'checkbox') return els.filter(function (x) { return x.checked; }).map(function (x) { return x.dataset.label || x.value; }).join(', ');
      if (els[0].type === 'file') return els[0].__files && els[0].__files.length ? String(els[0].__files.length) : '';
      if (els[0].tagName === 'SELECT') { var o = els[0].selectedOptions[0]; return o && o.value ? o.textContent : ''; }
      return els[0].value.trim();
    }
    form.__val = val;
    function buildReview() {
      var box = $('[data-review-box]', form); if (!box) return;
      var groups = JSON.parse(box.dataset.groups); box.innerHTML = '';
      groups.forEach(function (g) {
        var lines = g.fields.map(function (f) { var v = f.custom ? (form.__custom ? form.__custom(f.custom) : '') : val(f.name); return v ? (f.label ? f.label + ': ' : '') + v : ''; }).filter(Boolean);
        var row = document.createElement('div'); row.className = 'rv';
        row.innerHTML = '<h4></h4><div></div><button type="button" class="btn btn-text btn-s"></button>';
        row.children[0].textContent = g.title; row.children[1].textContent = lines.join('\n') || '–';
        row.children[2].textContent = box.dataset.edit; row.children[2].onclick = function () { show(g.step, -1); };
        box.appendChild(row);
      });
    }
    function fillDone(ok) { $$('[data-done]', ok).forEach(function (el) { var v = val(el.dataset.done); el.textContent = v; el.closest('[data-done-row]') && (el.closest('[data-done-row]').hidden = !v); }); }
    // live side summary
    var side = $('[data-summary]', form.closest('[data-wz]'));
    function sync() {
      if (!side) return;
      $$('[data-sum]', side).forEach(function (dd) { var k = dd.dataset.sum; var v = form.__custom && k.charAt(0) === '@' ? form.__custom(k.slice(1)) : val(k); dd.textContent = v || '–'; });
    }
    form.addEventListener('change', sync); form.addEventListener('input', sync); form.addEventListener('photos', sync, true); form.__sync = sync;
    var st = $('[data-sum-toggle]'); if (st) st.addEventListener('click', function () { var w = st.closest('.wz-side'); var o = !w.classList.contains('is-open'); w.classList.toggle('is-open', o); st.setAttribute('aria-expanded', o); });
    $$('[data-demo]', form).forEach(function (b) { b.addEventListener('click', function () { var d = JSON.parse(b.dataset.demo); Object.keys(d).forEach(function (k) { var els = $$('[name="' + k + '"]', form); els.forEach(function (el) { if (el.type === 'radio' || el.type === 'checkbox') el.checked = el.value === d[k]; else el.value = d[k]; }); var f = els[0] && fieldOf(els[0]); if (f) setErr(f, ''); }); var cal = $('[data-cal]', form); if (cal && cal.__set && b.dataset.date) { var t = new Date(); t.setDate(t.getDate() + 7); while (t.getDay() === 0 || t.getDay() === 6) t.setDate(t.getDate() + 1); cal.__set(t); } sync(); }); });
    $$('[data-restart]').forEach(function (b) { b.addEventListener('click', function () { location.reload(); }); });
    show(0, 0); sync();
    if (window.srWizardInit) window.srWizardInit(form, { show: show, sync: sync, validateField: validateField, setErr: setErr });
  });

  /* ── device picker (brand → type → model chips), shared by wizards ── */
  $$('[data-device]').forEach(function (box) {
    var form = box.closest('form'), models = JSON.parse(box.dataset.models || '{}');
    var typeWrap = $('[data-dev-types]', box), modelWrap = $('[data-dev-models]', box), chipsBox = $('[data-model-chips]', box), filter = $('[data-model-filter]', box);
    var freeWrap = $('[data-model-free]', box), free = freeWrap ? $('input', freeWrap) : null, list = $('[data-dev-list]', box), add = $('[data-dev-add]', box);
    var hidden = $('input[name=modell]', box), aiPick = null, devices = [];
    function brand() { var r = $('input[name=hersteller]:checked', box); return r ? r.value : ''; }
    function type() { var r = $('input[name=typ]:checked', box); return r ? r.value : ''; }
    function drawModels() {
      var b = brand(), ty = type(); if (!chipsBox) return;
      typeWrap.hidden = !b; modelWrap.hidden = !(b && ty);
      var arr = (b && ty && models[b + '|' + ty]) || [];
      var other = b === 'Andere';
      chipsBox.parentNode.hidden = other;
      if (filter) { filter.parentNode.hidden = arr.length <= 10 || other; }
      var q = filter ? filter.value.trim().toLowerCase() : '';
      chipsBox.innerHTML = '';
      arr.concat(['__free']).forEach(function (m) {
        if (q && m !== '__free' && m.toLowerCase().indexOf(q) < 0) return;
        var btn = document.createElement('button'); btn.type = 'button'; btn.className = 'chip-btn';
        btn.textContent = m === '__free' ? box.dataset.notListed : m;
        btn.setAttribute('aria-pressed', hidden.value === m ? 'true' : 'false');
        btn.onclick = function () { hidden.value = m; drawModels(); hidden.dispatchEvent(new Event('change', { bubbles: true })); var f = hidden.closest('[data-field]'); if (f) setErr(f, ''); };
        chipsBox.appendChild(btn);
      });
      freeWrap.hidden = !(other || hidden.value === '__free');
    }
    box.addEventListener('change', function (e) {
      if (e.target.name === 'hersteller') { hidden.value = ''; if (free) free.value = ''; }
      if (e.target.name === 'typ') { hidden.value = ''; }
      if (e.target.name === 'hersteller' || e.target.name === 'typ') drawModels();
    });
    if (filter) filter.addEventListener('input', drawModels);
    function current() {
      var b = brand(), ty = type(), m = hidden.value, fv = free ? free.value.trim() : '', sn = ($('input[name=seriennummer]', box) || {}).value || '';
      var tyLabel = ($('input[name=typ]:checked', box) || {}).dataset; tyLabel = tyLabel ? tyLabel.label : '';
      var bl = ($('input[name=hersteller]:checked', box) || {}).dataset; bl = bl ? bl.label : '';
      if (!b) return null;
      var model = b === 'Andere' ? fv : (m === '__free' ? fv : m);
      return { text: (b === 'Andere' ? '' : bl + ' ') + (model || '') + (tyLabel ? ' · ' + tyLabel : '') + (sn ? ' · S/N ' + sn : '') + (box.dataset.qty && $('[name=anzahl]', box) && $('[name=anzahl]', box).value > 1 ? ' · ' + $('[name=anzahl]', box).value + '×' : '') };
    }
    function validDevice() {
      var ok = true, b = brand(), ty = type();
      var fb = $('[data-field=hersteller]', box), ft = $('[data-field=typ]', box), fm = $('[data-field=modell]', box);
      if (!b && !devices.length) { setErr(fb, I.choose); ok = false; } else setErr(fb, '');
      if (b && !ty) { setErr(ft, I.choose); ok = false; } else if (ft) setErr(ft, '');
      if (b && ty) {
        var need = b === 'Andere' || hidden.value === '__free';
        if (need && free && !free.value.trim()) { setErr(fm, I.required); ok = false; }
        else if (!need && !hidden.value && fm && box.dataset.modelReq) { setErr(fm, I.choose); ok = false; }
        else if (fm) setErr(fm, '');
      }
      return ok;
    }
    var step = box.closest('[data-step]'); if (step) step.__extraValidate = function () { var ok = validDevice(); if (!ok) box.scrollIntoView({ block: 'center', behavior: reduce ? 'auto' : 'smooth' }); return ok; };
    function drawList() {
      list.innerHTML = '';
      devices.forEach(function (d, k) {
        var el = document.createElement('div'); el.className = 'dev';
        el.innerHTML = '<svg class="icon" viewBox="0 0 24 24"><path d="m5 12.5 4.5 4.5L19 7.5"/></svg><b></b><button type="button" class="btn btn-text btn-s"></button>';
        el.children[1].textContent = d.text; el.children[2].textContent = box.dataset.remove;
        el.children[2].onclick = function () { devices.splice(k, 1); drawList(); form.__sync && form.__sync(); };
        list.appendChild(el);
      });
    }
    function resetCur() {
      $$('input[name=hersteller],input[name=typ]', box).forEach(function (r) { r.checked = false; });
      hidden.value = ''; if (free) free.value = ''; var sn = $('input[name=seriennummer]', box); if (sn) sn.value = '';
      var q = $('[name=anzahl]', box); if (q) q.value = '1';
      if (box.__aiReset) box.__aiReset(); drawModels();
    }
    if (add) add.addEventListener('click', function () { if (!brand()) { setErr($('[data-field=hersteller]', box), I.choose); return; } if (!validDevice()) return; devices.push(current()); drawList(); resetCur(); form.__sync && form.__sync(); box.scrollIntoView({ block: 'start', behavior: reduce ? 'auto' : 'smooth' }); });
    form.__custom = function (k) {
      if (k === 'devices') { var all = devices.map(function (d) { return d.text; }); var c = current(); if (c && c.text.trim()) all.push(c.text); return all.join('\n'); }
      if (box.__custom) return box.__custom(k);
      return '';
    };
    box.__setDevice = function (b, ty, m, sn) {
      var rb = $('input[name=hersteller][value="' + b + '"]', box); if (rb) rb.checked = true;
      var rt = $('input[name=typ][value="' + ty + '"]', box); if (rt) rt.checked = true;
      hidden.value = m || ''; if (m && models[b + '|' + ty] && models[b + '|' + ty].indexOf(m) < 0) { hidden.value = '__free'; if (free) free.value = m; }
      var s = $('input[name=seriennummer]', box); if (s && sn != null) s.value = sn;
      drawModels(); $$('[data-field]', box).forEach(function (f) { setErr(f, ''); }); form.__sync && form.__sync();
    };
    // prefill from URL (?hersteller=Olympus&typ=Gastroskop&modell=GIF-H190)
    if (params.get('modell')) box.__setDevice(params.get('hersteller') || '', params.get('typ') || '', params.get('modell'), null);
    drawModels();
  });

  /* ── AI type-plate demo ────────────────── */
  $$('[data-ai]').forEach(function (ai) {
    var box = ai.closest('form').querySelector('[data-device]'), prev = $('[data-ai-prev]', ai), img = $('img', prev);
    var idle = $('[data-ai-idle]', ai), scan = $('[data-ai-scanning]', ai), done = $('[data-ai-done]', ai), file = $('input[type=file]', ai);
    var DEMO = { b: 'Olympus', t: 'Koloskop', m: 'CF-HQ190L', sn: '2812345' };
    function state(s) { idle.hidden = s !== 'idle'; scan.hidden = s !== 'scan'; done.hidden = s !== 'done'; prev.hidden = s === 'idle'; prev.classList.toggle('is-scan', s === 'scan'); prev.classList.toggle('is-done', s === 'done'); }
    function badges(on) { $$('[data-ai-slot]', box).forEach(function (s) { s.innerHTML = on ? '<span class="ai-badge"><svg class="icon" viewBox="0 0 24 24" style="width:12px;height:12px;fill:currentColor;stroke:none"><path d="M12 2.5l1.9 5.6 5.6 1.9-5.6 1.9L12 17.5l-1.9-5.6L4.5 10l5.6-1.9z"/></svg>' + ai.dataset.badge + '</span>' : ''; }); }
    function run(src) {
      if (src) { img.src = src; img.hidden = false; $('svg', prev).style.display = 'none'; } else { img.hidden = true; $('svg', prev).style.display = ''; }
      state('scan');
      setTimeout(function () { box.__setDevice(DEMO.b, DEMO.t, DEMO.m, DEMO.sn); state('done'); badges(true); }, reduce ? 300 : 1800);
    }
    $('[data-ai-demo]', ai).onclick = function () { run(''); };
    file.addEventListener('change', function () { var f = file.files[0]; run(f ? URL.createObjectURL(f) : ''); file.value = ''; });
    $('[data-ai-undo]', ai).onclick = function () { box.__setDevice('', '', '', ''); $$('input[name=hersteller],input[name=typ]', box).forEach(function (r) { r.checked = false; }); box.dispatchEvent(new Event('change')); state('idle'); badges(false); };
    box.__aiReset = function () { state('idle'); badges(false); };
    box.addEventListener('change', function (e) { if (e.isTrusted) badges(false); });
    state('idle');
  });

  /* ── conditional blocks: data-show-if="name=value" ── */
  function evalShow() {
    $$('[data-show-if]').forEach(function (el) {
      var p = el.dataset.showIf.split('='), form = el.closest('form') || document;
      var on = $$('[name="' + p[0] + '"]', form).some(function (i) { return (i.type === 'radio' || i.type === 'checkbox') ? i.checked && i.value === p[1] : i.value === p[1]; });
      if (el.hidden === on) { el.hidden = !on; if (on && !reduce) { el.classList.remove('is-entering'); void el.offsetWidth; el.classList.add('is-entering'); } }
    });
  }
  document.addEventListener('change', evalShow); evalShow();

  /* prefill selects/inputs from URL: ?betreff=kauf&nachricht=… */
  $$('[data-prefill]').forEach(function (el) { var v = params.get(el.dataset.prefill); if (v) { el.value = v; } });

  /* product page: inquiry toggle */
  $$('[data-inq-open]').forEach(function (b) {
    var box = document.getElementById(b.getAttribute('aria-controls'));
    function open() { box.hidden = false; b.setAttribute('aria-expanded', 'true'); b.hidden = true; var f = $('input', box); if (f) f.focus({ preventScroll: true }); box.scrollIntoView({ block: 'center', behavior: reduce ? 'auto' : 'smooth' }); }
    b.addEventListener('click', open);
    if (location.hash === '#anfrage') setTimeout(open, 300);
  });

  /* ── calculator ───────────────────────── */
  var calc = $('[data-calc]');
  if (calc) {
    var nf = new Intl.NumberFormat({ de: 'de-DE', en: 'en-GB', fr: 'fr-FR', ru: 'ru-RU' }[I.lang] || 'de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 });
    var num = function (n) { var v = $('[name=' + n + ']', calc).value.replace(/\s/g, '').replace(/\./g, '').replace(',', '.'); return v === '' ? NaN : parseFloat(v); };
    var outEmpty = $('[data-calc-empty]', calc), outRes = $('[data-calc-res]', calc);
    function run() {
      var dev = num('devices'), con = num('contract'), rep = num('repairs'), cost = num('cost');
      var ok = [dev, con, rep, cost].every(function (x) { return !isNaN(x) && x >= 0; }) && dev > 0;
      outEmpty.hidden = ok; outRes.hidden = !ok; if (!ok) return;
      var a = con, b = rep * cost, max = Math.max(a, b, 1), d = a - b;
      $('[data-out-a]', calc).textContent = nf.format(a); $('[data-out-b]', calc).textContent = nf.format(b);
      $('[data-bar-a]', calc).style.width = (a / max * 100) + '%'; $('[data-bar-b]', calc).style.width = (b / max * 100) + '%';
      $('[data-out-diff]', calc).textContent = nf.format(Math.abs(d));
      $('[data-out-diff-l]', calc).textContent = d >= 0 ? calc.dataset.pos : calc.dataset.neg;
      $('[data-out-per]', calc).textContent = nf.format(Math.abs(d) / dev) + ' ' + calc.dataset.per;
    }
    calc.addEventListener('input', run);
    var rs = $('[data-calc-reset]', calc); if (rs) rs.addEventListener('click', function () { $$('input', calc).forEach(function (i) { i.value = ''; }); run(); });
    run();
  }

  /* map consent */
  $$('[data-map]').forEach(function (b) { b.addEventListener('click', function () { toast(I.todo); }); });
})();
