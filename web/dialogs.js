'use strict';
// Modal dialogs. Time keeps running while they are open, except for decisions,
// which hold the clock in the simulation itself.
const dialog = document.createElement('dialog');
dialog.setAttribute('aria-labelledby', 'dialog-title');
document.body.append(dialog);
let current = null, confirmResolve = null;

const dialogOpen = () => dialog.open;

const DIALOGS = {
  settings: () => ['Menu', `<div class="choice-list">
      <div class="choice"><div><strong>Save</strong><p>${state.ironman ? 'Ironman saves itself every week.' : 'Writes your studio to disk. Ctrl+S works anywhere.'}</p></div>${act('Save', 'save', {}, 'primary', {disabled: state.ironman})}</div>
      <div class="choice"><div><strong>Studio name</strong><p><input id="studio-name" maxlength="40" value="${esc(state.studio.name)}" aria-label="Studio name"></p></div><button data-rename>Rename</button></div>
      <div class="choice"><div><strong>New studio</strong><p>Starts over. ${state.ironman ? 'This Ironman studio will be gone.' : 'Save first if you want to keep this one.'}</p></div>${act('New studio', 'new', {}, '', {confirm: 'Start a new studio? Unsaved progress is lost.', after: 'close'})}</div>
    </div>
    <span class="kicker">Keys</span><div class="kv">
      <div><span>Pages</span><b>H G T B S</b></div><div><span>Pause</span><b>Space</b></div><div><span>Speed</span><b>&lt; &gt; or ← →</b></div>
      <div><span>Save</span><b>Ctrl+S</b></div><div><span>Menu / close</span><b>Esc</b></div></div>
    <p class="note">Seed ${state.seed}. Time only runs while this tab is open and visible.</p>`],

  decision: () => {
    const d = state.decision;
    if (!d) return ['Decision', empty('Nothing to decide.')];
    return [d.title, `<p class="note">Time is held until you decide.</p><p class="big">${esc(d.question)}</p><div class="choice-list">${d.options.map((o, i) =>
      `<div class="choice"><div><strong>${esc(o.name)}</strong><p>${esc(o.effect)}</p></div>${act('Choose', 'decide', {index: i}, 'primary', {after: 'close'})}</div>`).join('')}</div>`];
  },

  confirm: args => ['Are you sure?', `<p class="big">${esc(args.text)}</p><div class="actions"><button class="primary" data-confirm-yes>Confirm</button><button data-close>Cancel</button></div>`],

  promote: args => {
    const name = args.target ? state.catalog.find(p => p.id === args.target)?.title : state.project?.idea.title;
    const rows = state.promotions.map(p => `<div class="choice"><div><strong>${esc(p.name)}</strong> <span class="small muted">${p.cost ? money(p.cost) : 'free'} · ${p.weeks} wk · ${pct(p.capacity)} of the team</span><p>${esc(p.effect)} Reaches about ${short(p.people)} people${p.reputation_weight ? ', fewer for an unknown studio' : ''}.</p></div>
      ${p.lock ? '<span class="pill">Locked: needs research</span>' : act('Start', 'promote', {key: p.key, target: args.target}, 'primary', {after: 'close'})}</div>`).join('');
    return [`Promote ${name || ''}`, `<div class="choice-list">${rows}</div>`];
  },

  community: args => {
    const name = args.target ? state.catalog.find(p => p.id === args.target)?.title : state.project?.idea.title;
    const rows = state.community_actions.filter(c => args.target ? !c.project_only : !c.release_only).map(c => `<div class="choice"><div><strong>${esc(c.name)}</strong> <span class="small muted">${c.cost ? money(c.cost) : 'free'} · ${c.weeks} wk · ${pct(c.capacity)} of the team</span><p>${esc(c.effect)}</p></div>
      ${act('Start', 'community', {key: c.key, target: args.target}, 'primary', {after: 'close'})}</div>`).join('');
    return [`Community · ${name || ''}`, `<div class="choice-list">${rows}</div>`];
  },

  train: args => {
    const p = state.team.find(x => x.id === args.id);
    if (!p) return ['Training', empty('That person has left.')];
    const rows = ['design', 'art', 'audio', 'code', 'research'].map(k => `<div class="choice"><div><strong>${k} ${p[k]}</strong><p>Course cost about ${money(Math.round((600 + p[k] * 30) / 50) * 50)}. Away for a few weeks.</p></div>${act('Train', 'train', {id: p.id, skill: k}, '', {after: 'close', disabled: p.status !== 'Available'})}</div>`).join('');
    return [`Train ${p.name}`, `<div class="choice-list">${rows}</div>`];
  },

  log: () => ['Activity', `<div class="log">${state.log.map(l => `<div class="event">${esc(l)}</div>`).join('')}</div>`],
  news: () => ['Industry news', state.news.length ? `<div class="log">${state.news.map(l => `<div class="event">${esc(l)}</div>`).join('')}</div>` : empty('Quiet so far.')],

  ledger: () => ['Monthly books', [...state.ledgers].reverse().map(l => `<div class="card"><div class="split"><strong>${esc(l.month)}</strong><b class="${l.net < 0 ? 'danger' : 'green'}">${money(l.net)}</b></div>
    <div class="kv">${Object.entries(l.income).map(([k, v]) => `<div><span>${esc(k)}</span><b class="green">${money(v)}</b></div>`).join('')}
    ${Object.entries(l.expenses).map(([k, v]) => `<div><span>${esc(k)}</span><b class="danger">${money(v)}</b></div>`).join('')}
    ${Object.entries(l.financing).map(([k, v]) => `<div><span>${esc(k)} (financing)</span><b>${money(v)}</b></div>`).join('')}</div></div>`).join('')],
};

function drawDialog() {
  const [title, body] = DIALOGS[current.name](current.args);
  const scroll = dialog.querySelector('.dialog-body')?.scrollTop || 0;
  dialog.innerHTML = `<div class="dialog-header"><h2 id="dialog-title">${esc(title)}</h2><button data-close aria-label="Close">[Esc] Close</button></div><div class="dialog-body">${body}</div>`;
  dialog.querySelector('.dialog-body').scrollTop = scroll;
}

function openDialog(name, args = {}) {
  current = {name, args};
  drawDialog();
  if (!dialog.open) dialog.showModal();
  dialog.querySelector('.dialog-body button.primary, .dialog-body button')?.focus();
}

function closeDialog() {
  if (confirmResolve) {
    const resolve = confirmResolve;
    confirmResolve = null;
    resolve(false);
    if (current && current.name !== 'confirm') return;  // went back to the dialog that asked
  }
  current = null;
  if (dialog.open) dialog.close();
}

function refreshDialog() {
  if (!dialog.open || !current || current.name === 'confirm') return;
  if (dialog.contains(document.activeElement) && document.activeElement.tagName === 'INPUT') return;
  drawDialog();
}

function openConfirm(text) {
  return new Promise(resolve => {
    const previous = current;
    openDialog('confirm', {text});
    confirmResolve = answer => { confirmResolve = null; if (previous && answer === false) openDialog(previous.name, previous.args); resolve(answer); };
  });
}

dialog.addEventListener('cancel', event => { event.preventDefault(); closeDialog(); });
dialog.addEventListener('click', async event => {
  if (event.target.closest('[data-confirm-yes]')) {
    const resolve = confirmResolve;
    confirmResolve = null;
    current = null;
    dialog.close();
    resolve?.(true);
  }
  if (event.target.closest('[data-rename]')) {
    const name = dialog.querySelector('#studio-name').value;
    if (await send('rename', {name})) closeDialog();
  }
});
