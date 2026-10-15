'use strict';
// Small rendering helpers shared by every page and dialog.
const esc = v => String(v ?? '').replace(/[&<>"']/g, c => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'}[c]));
const money = v => new Intl.NumberFormat('en-US', {style: 'currency', currency: 'USD', maximumFractionDigits: 0}).format(v || 0);
const price = v => v ? new Intl.NumberFormat('en-US', {style: 'currency', currency: 'USD'}).format(v) : 'Free';
const num = v => Math.round(v || 0).toLocaleString('en-US');
const short = v => {
  const n = Math.abs(v || 0), s = v < 0 ? '-' : '';
  return n >= 1e9 ? s + (n / 1e9).toFixed(1) + 'B' : n >= 1e6 ? s + (n / 1e6).toFixed(1) + 'M' : n >= 1e4 ? s + Math.round(n / 1e3) + 'k' : s + num(n);
};
const pct = v => Math.round((v || 0) * 100) + '%';

// data-act buttons send a command with JSON fields. opts.confirm asks first;
// opts.after can be "close" (close the dialog) or "projects" (go to Projects).
function act(label, action, fields = {}, cls = '', opts = {}) {
  const extra = (opts.confirm ? ` data-confirm="${esc(opts.confirm)}"` : '') + (opts.after ? ` data-after="${opts.after}"` : '')
    + (opts.disabled ? ' disabled' : '') + (opts.title ? ` title="${esc(opts.title)}"` : '');
  return `<button class="${cls}" data-act="${action}" data-fields='${esc(JSON.stringify(fields))}'${extra}>${esc(label)}</button>`;
}

// A select that sends `cmd` with its JSON value under `param` (and any extra fields) when changed.
function cmdSelect(cmd, options, current, {param = 'value', extra = {}, field = '', label = ''} = {}) {
  return `<select data-cmd="${cmd}" data-param="${param}" data-extra='${esc(JSON.stringify(extra))}' ${field ? `data-field="${field}"` : ''} aria-label="${esc(label || field || param)}">${options.map(o => {
    const value = typeof o === 'object' ? o.value : o, text = typeof o === 'object' ? o.label : o, lock = typeof o === 'object' && o.lock;
    return `<option value='${esc(JSON.stringify(value))}' ${value === current ? 'selected' : ''} ${lock ? 'disabled' : ''}>${esc(text)}${lock ? ' — ' + esc(lock) : ''}</option>`;
  }).join('')}</select>`;
}
const openBtn = (label, dialogName, args = {}, cls = '') =>
  `<button class="${cls}" data-dialog="${dialogName}" data-args='${esc(JSON.stringify(args))}'>${esc(label)}</button>`;
const goBtn = (label, pageName, cls = '') => `<button class="${cls}" data-page="${pageName}">${esc(label)}</button>`;

function metric(label, value, tone = '') {
  return `<div class="metric ${tone}"><span>${esc(label)}</span><strong>${esc(value)}</strong></div>`;
}
function section(title, body, control = '', cls = '') {
  return `<section class="box ${cls}"><div class="section-line"><h2>${esc(title)}</h2>${control}</div><div class="box-body">${body}</div></section>`;
}
const empty = text => `<p class="empty">${esc(text)}</p>`;
const bar = (value, max = 1, cls = '') => `<progress class="${cls}" value="${Math.max(0, value)}" max="${Math.max(max, 1e-9)}"></progress>`;

// A known range on a scale, drawn as a band: what the studio believes.
function rangeBar(range, lo, hi, fmt = v => v) {
  const left = (range[0] - lo) / (hi - lo) * 100, width = Math.max(1.5, (range[1] - range[0]) / (hi - lo) * 100);
  return `<div class="range"><div class="range-track"><span style="left:${left}%;width:${width}%"></span></div><b>${esc(fmt(range[0]))}–${esc(fmt(range[1]))}</b></div>`;
}

function sparkBars(values, color = 'var(--blue)') {
  if (!values || !values.length) return empty('No sales yet.');
  const peak = Math.max(1, ...values);
  const w = 600 / values.length;
  return `<svg class="spark" viewBox="0 0 600 80" preserveAspectRatio="none" role="img" aria-label="Weekly sales">${values.map((v, i) =>
    `<rect x="${i * w}" y="${78 - v / peak * 74}" width="${Math.max(1, w - 2)}" height="${v / peak * 74}" fill="${color}"><title>${num(v)}</title></rect>`).join('')}</svg>`;
}

function table(headers, rows, cls = '') {
  if (!rows.length) return '';
  return `<div class="table-wrap"><table class="grid ${cls}"><thead><tr>${headers.map(h => `<th>${esc(h)}</th>`).join('')}</tr></thead><tbody>${rows.join('')}</tbody></table></div>`;
}
