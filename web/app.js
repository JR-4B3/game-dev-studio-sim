'use strict';
// App shell: talks to the server, keeps the latest view, draws the frame and routes input.
let state = null, page = 'Studio', busy = false, connected = true, lastDrawn = '', shownDecision = '';
const app = document.querySelector('#app');
const PAGES = [['Studio', 'H'], ['Projects', 'G'], ['People', 'T'], ['Business', 'B'], ['Market', 'S']];

function notify(text) {
  const n = document.querySelector('#notice');
  n.textContent = text;
  n.style.display = 'block';
  clearTimeout(notify.timer);
  notify.timer = setTimeout(() => { n.style.display = 'none'; }, 5000);
}

async function send(action, fields = {}, quiet = false) {
  if (busy) return false;
  busy = true;
  try {
    const response = await fetch('/api/action', {
      method: 'POST',
      headers: {'Content-Type': 'application/json', 'X-Game-Token': state?.token || ''},
      body: JSON.stringify({action, ...fields}),
    });
    const next = await response.json();
    if (!response.ok) throw Error(next.error || 'Request failed.');
    const before = state?.log?.[0];
    state = next;
    connected = true;
    render(true);
    if (!quiet && state.log && state.log[0] !== before) notify(state.log[0].replace(/^[^:]+: /, ''));
    return true;
  } catch (e) {
    notify(e.message);
    return false;
  } finally {
    busy = false;
  }
}

async function poll() {
  if (busy || document.hidden) return;
  try {
    const response = await fetch('/api/state');
    if (!response.ok) throw Error('Disconnected');
    const text = await response.text();
    if (busy) return;
    state = JSON.parse(text);
    connected = true;
    render();
    if (state.decision && !dialogOpen()) {
      const key = state.project?.id + ':' + state.decision.title;
      if (key !== shownDecision) { shownDecision = key; openDialog('decision'); }
    } else if (!state.decision) shownDecision = '';
  } catch {
    connected = false;
    drawClock();
  }
}

function render(force = false) {
  if (!state) return;
  if (!state.started) { welcome(); return; }
  if (state.closed) { campaignOver(); return; }
  // Don't redraw under the player's hands: an open <select> would collapse.
  const editing = document.activeElement?.tagName === 'SELECT';
  const signature = JSON.stringify([page, state.day, state.log[0], state.studio, state.project, state.held,
    state.contracts, state.updates, state.commitments, state.research_progress, selectedProduct]);
  if ((force || signature !== lastDrawn) && !editing) {
    const focusKey = document.activeElement?.dataset?.focusKey;
    app.innerHTML = `${header()}<main>${PAGE_VIEWS[page]()}</main>${footer()}`;
    lastDrawn = signature;
    if (focusKey) app.querySelector(`[data-focus-key="${focusKey}"]`)?.focus({preventScroll: true});
    refreshDialog();
  }
  drawClock();
}

function header() {
  return `<header><nav aria-label="Main navigation">${PAGES.map(([name, key]) =>
    `<button data-page="${name}" class="${name === page ? 'active' : ''}" ${name === page ? 'aria-current="page"' : ''}>[${key}]${name}</button>`).join('')}</nav>
    <span class="studio-name">${esc(state.studio.name)}${state.ironman ? ' · IRONMAN' : ''}</span>
    <button data-dialog="settings">[Esc] Menu</button></header>`;
}

function footer() {
  const s = state.studio;
  return `<footer><div class="time-strip"><progress id="day-progress" max="1" value="0" aria-label="Day progress"></progress>
    <span id="date"></span><span class="financial">${money(s.cash)} | ${state.runway ? state.runway.toFixed(1) + ' mo' : (s.cash < 0 ? 'insolvent' : '—')}</span>
    <span class="trust">Rep ${s.reputation.toFixed(0)} | Clients ${state.client_trust.toFixed(0)} | Fans ${short(state.fans)}</span></div>
    <div class="footer-controls"><button data-speed="-1" aria-label="Slower">[&lt;]</button><button id="pause" data-pause>[Space]</button>
    <button data-speed="1" aria-label="Faster">[&gt;]</button><span id="clock-status"></span></div></footer>`;
}

function drawClock() {
  if (!state?.started || state.closed) return;
  const date = document.querySelector('#date');
  if (!date) return;
  const d = new Date(state.date + 'T12:00:00');
  date.textContent = d.toLocaleDateString('en-GB', {weekday: 'short', day: '2-digit', month: 'short', year: 'numeric'});
  const c = state.clock;
  document.querySelector('#pause').textContent = `[Space] ${c.speed ? '▶'.repeat(c.speed) : 'Ⅱ'}`;
  document.querySelector('#clock-status').textContent = !connected ? 'Disconnected' : c.held || (c.speed ? 'Running' : 'Paused');
  document.querySelector('#day-progress').value = c.fraction || 0;
}

function welcome() {
  app.innerHTML = `<div class="welcome"><span class="kicker">A brutally honest game studio simulation</span>
    <h1>GAME DEV<br>STUDIO SIM</h1>
    <p>You quit your job to make games. You have some savings, rent to pay and no audience. Take client work to survive, test your ideas honestly, and find out whether anyone wants what you make.</p>
    <div class="actions modes" style="justify-content:center">${act('[Enter] New studio', 'new', {}, 'primary')}${act('New Ironman studio', 'new', {ironman: true})}
    ${state.can_load ? act('Load saved studio', 'load') : ''}</div>
    <p class="small muted">Ironman: one save that updates itself, no reloading. Bankruptcy is final.</p></div>`;
}

function campaignOver() {
  const s = state.studio;
  const mine = state.catalog || [];
  app.innerHTML = `<div class="campaign-over"><span class="kicker">${esc(state.date)}</span><h1>${esc(state.closed.toUpperCase())}</h1>
    <p>${esc(s.name)} lasted ${Math.round(state.day / 30.4)} months, released ${mine.length} game${mine.length === 1 ? '' : 's'}
    and earned ${money(s.lifetime_revenue)} in total.</p>
    ${mine.length ? table(['Game', 'Copies', 'Rating', 'Revenue'], mine.map(p => `<tr><td>${esc(p.title)}</td><td class="n">${num(p.units)}</td><td class="n">${p.rating}</td><td class="n">${money(p.revenue)}</td></tr>`)) : ''}
    <div class="actions" style="justify-content:center;margin-top:18px">${act('Start a new studio', 'new', {}, 'primary')}${!state.ironman && state.can_load ? act('Load last save', 'load') : ''}</div></div>`;
}

// --- Input -------------------------------------------------------------------

function confirmFirst(button) {
  const text = button.dataset.confirm;
  if (!text) return Promise.resolve(true);
  return openConfirm(text);
}

document.addEventListener('click', async event => {
  const b = event.target.closest('button, tr[data-select]');
  if (!b || busy) return;
  if (b.dataset.page) { page = b.dataset.page; render(true); return; }
  if (b.dataset.dialog) { openDialog(b.dataset.dialog, JSON.parse(b.dataset.args || '{}')); return; }
  if (b.dataset.select) {
    selectedProduct = Number(b.dataset.select);
    if (b.dataset.pageHint) page = b.dataset.pageHint;
    render(true);
    return;
  }
  if (b.hasAttribute('data-close')) { closeDialog(); return; }
  if (b.hasAttribute('data-pause')) { send('pause', {}, true); return; }
  if (b.dataset.speed) { send('speed', {index: Math.max(0, Math.min(3, state.clock.speed + Number(b.dataset.speed)))}, true); return; }
  if (b.dataset.act) {
    if (!await confirmFirst(b)) return;
    const ok = await send(b.dataset.act, JSON.parse(b.dataset.fields || '{}'));
    if (ok && b.dataset.after === 'close') closeDialog();
    if (ok && b.dataset.after === 'projects') { page = 'Projects'; closeDialog(); render(true); }
  }
});

document.addEventListener('change', event => {
  const el = event.target;
  if (el.tagName !== 'SELECT' || !el.dataset.cmd) return;
  const fields = JSON.parse(el.dataset.extra || '{}');
  fields[el.dataset.param || 'value'] = JSON.parse(el.value);
  if (el.dataset.field && el.dataset.cmd === 'plan') fields.field = el.dataset.field;
  el.blur();
  send(el.dataset.cmd, fields, true);
});

document.addEventListener('keydown', event => {
  if (event.target.matches('input, select, textarea')) return;
  if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 's') { event.preventDefault(); if (state?.started) send('save'); return; }
  if (event.ctrlKey || event.metaKey || event.altKey || !state) return;
  if (event.key === 'Escape') { event.preventDefault(); dialogOpen() ? closeDialog() : openDialog('settings'); return; }
  if (dialogOpen()) return;
  if (!state.started) { if (event.key === 'Enter') send('new'); return; }
  if (event.key === ' ') { event.preventDefault(); send('pause', {}, true); return; }
  if (['<', ',', 'ArrowLeft'].includes(event.key)) { send('speed', {index: Math.max(0, state.clock.speed - 1)}, true); return; }
  if (['>', '.', 'ArrowRight'].includes(event.key)) { send('speed', {index: Math.min(3, state.clock.speed + 1)}, true); return; }
  const target = PAGES.find(([, key]) => key.toLowerCase() === event.key.toLowerCase());
  if (target) { page = target[0]; render(true); }
});

poll();
setInterval(poll, 250);
