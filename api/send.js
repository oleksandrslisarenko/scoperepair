// Vercel serverless function: forwards prototype form submissions to e-mail via Resend.
// Env vars (Vercel → Project → Settings → Environment Variables):
//   RESEND_API_KEY  – API key from resend.com
//   MAIL_TO         – recipient (while no domain is verified: the e-mail of the Resend account)
//   MAIL_FROM       – optional, default "scopeREPAIR Test <onboarding@resend.dev>"

const MAX_FIELDS = 80;
const MAX_ATTACH_BYTES = 3.6 * 1024 * 1024;

const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

module.exports = async (req, res) => {
  if (req.method !== 'POST') { res.status(405).json({ ok: false, error: 'method' }); return; }
  const key = process.env.RESEND_API_KEY, to = process.env.MAIL_TO;
  if (!key || !to) { res.status(500).json({ ok: false, error: 'not_configured' }); return; }

  let body = req.body;
  if (typeof body === 'string') { try { body = JSON.parse(body); } catch (e) { body = null; } }
  if (!body || !Array.isArray(body.fields)) { res.status(400).json({ ok: false, error: 'bad_request' }); return; }
  if (body.website) { res.status(200).json({ ok: true }); return; } // honeypot

  const fields = body.fields.slice(0, MAX_FIELDS)
    .filter((f) => f && f.label && f.value != null && String(f.value).trim() !== '')
    .map((f) => ({ label: String(f.label).slice(0, 120), value: String(f.value).slice(0, 4000) }));
  const title = String(body.title || 'Anfrage').slice(0, 140);
  const page = String(body.page || '').slice(0, 300);
  const lang = String(body.lang || '').slice(0, 5);
  const replyTo = String(body.email || '').trim();

  let size = 0;
  const attachments = (Array.isArray(body.files) ? body.files : []).filter((f) => {
    if (!f || !f.data || !f.name) return false;
    size += f.data.length * 0.75;
    return size <= MAX_ATTACH_BYTES;
  }).slice(0, 10).map((f) => ({ filename: String(f.name).slice(0, 120), content: String(f.data) }));
  const skipped = (body.files || []).length - attachments.length + (Number(body.filesSkipped) || 0);

  const rows = fields.map((f) => `<tr><th align="left" valign="top" style="padding:6px 16px 6px 0;color:#56697a;font-weight:500;white-space:nowrap">${esc(f.label)}</th><td style="padding:6px 0;color:#193854">${esc(f.value).replace(/\n/g, '<br>')}</td></tr>`).join('');
  const html = `<div style="font-family:Arial,Helvetica,sans-serif;font-size:15px;line-height:1.5;color:#193854">
<p style="margin:0 0 4px;font-size:12px;letter-spacing:.06em;text-transform:uppercase;color:#0d6a9a">scopeREPAIR · Testseite</p>
<h2 style="margin:0 0 16px;font-size:22px">${esc(title)}</h2>
<table cellspacing="0" cellpadding="0" style="border-collapse:collapse">${rows}</table>
${attachments.length ? `<p style="margin-top:16px;color:#56697a">Fotos im Anhang: ${attachments.length}</p>` : ''}
${skipped > 0 ? `<p style="color:#56697a">Nicht angehängt (zu groß oder Format): ${skipped}</p>` : ''}
<p style="margin-top:24px;font-size:12px;color:#8696a3">Seite: ${esc(page)} · Sprache: ${esc(lang)}</p></div>`;
  const text = fields.map((f) => `${f.label}: ${f.value}`).join('\n') + `\n\nSeite: ${page} · Sprache: ${lang}`;

  const payload = {
    from: process.env.MAIL_FROM || 'scopeREPAIR Test <onboarding@resend.dev>',
    to: to.split(',').map((s) => s.trim()).filter(Boolean),
    subject: `[scopeREPAIR Test] ${title}`,
    html, text,
  };
  if (/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(replyTo)) payload.reply_to = replyTo;
  if (attachments.length) payload.attachments = attachments;

  try {
    const r = await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: { Authorization: `Bearer ${key}`, 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const out = await r.json().catch(() => ({}));
    if (!r.ok) { res.status(502).json({ ok: false, error: 'resend', detail: out && out.message }); return; }
    res.status(200).json({ ok: true, id: out.id });
  } catch (e) {
    res.status(502).json({ ok: false, error: 'network' });
  }
};
