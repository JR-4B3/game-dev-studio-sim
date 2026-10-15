'use strict';
// The five pages. Each returns HTML for <main> from the current `state`.
let selectedProduct = null;

const ALLOC = {
  project: ['Game', 'var(--blue)'], contract: ['Client work', 'var(--yellow-bold)'], research: ['Research', 'var(--green)'],
  update: ['Updates', 'var(--purple)'], support: ['Support', 'var(--red-soft)'], commitments: ['Promotion', '#94e2d5'],
};
const STAGES = ['concept', 'design', 'production', 'polish'];

function allocationBar() {
  const a = state.allocation;
  const idle = Math.max(0, 1 - Object.values(a).reduce((x, y) => x + y, 0));
  const parts = Object.entries(a).map(([k, v]) => `<i style="width:${v * 100}%;background:${ALLOC[k][1]}" title="${ALLOC[k][0]} ${pct(v)}"></i>`).join('');
  const legend = Object.entries(a).map(([k, v]) => `<span><i style="background:${ALLOC[k][1]}"></i>${ALLOC[k][0]} ${pct(v)}</span>`).join('')
    + (idle > 0.005 ? `<span><i style="background:#33364f"></i>Idle ${pct(idle)}</span>` : '');
  return `<div class="allocation">${parts}</div><div class="legend">${legend}</div>`;
}

function stageRail(stage) {
  const at = STAGES.indexOf(stage);
  return `<div class="stage-rail">${STAGES.map((s, i) => `<span class="${i < at ? 'done' : i === at ? 'current' : ''}">${s}</span>`).join('')}<span>release</span></div>`;
}

function summary() {
  const s = state.studio;
  const runwayTone = !state.runway ? 'runway-danger' : state.runway < 4 ? 'runway-danger' : state.runway < 8 ? 'runway-caution' : 'runway-good';
  return `<div class="studio-summary" aria-label="Studio health">
    ${metric('Cash', money(s.cash), s.cash < 0 ? 'cash-danger' : 'cash-good')}
    ${metric('Monthly costs', money(state.burn), 'burn-expense')}
    ${metric('Income / month', money(state.average_income), state.average_income >= state.burn ? 'cash-good' : '')}
    ${metric('Runway', state.runway ? (state.runway >= 10 ? Math.round(state.runway) : state.runway.toFixed(1)) + ' mo' : s.cash < 0 ? `${state.bankruptcy_weeks - s.insolvent_weeks} wk left` : '∞', runwayTone)}
    ${metric('Fans', short(state.fans), 'audience')}
    ${metric('Reputation', s.reputation.toFixed(0), 'rep')}
    ${metric('Client trust', state.client_trust.toFixed(0), 'trust')}
  </div>`;
}

// --- Studio ---------------------------------------------------------------------

function nowGame() {
  const p = state.project;
  if (!p) {
    return `<div class="card"><span class="kicker">Original game</span><p class="big">Nothing in development</p>
      <p>${state.ideas.length} idea${state.ideas.length === 1 ? '' : 's'} on the shelf.</p><div class="actions">${goBtn('[G] Explore an idea', 'Projects', 'primary')}</div></div>`;
  }
  let line = '', control = goBtn('Open', 'Projects');
  if (p.stage === 'concept') line = p.activity ? `${p.activity_name} · ${pct(p.activity_progress)}` : 'Waiting for your next experiment.';
  if (p.stage === 'design') line = 'Planning. Commit when the plan holds up.';
  if (p.stage === 'production') line = `${pct(p.progress)} built · about ${p.eta_weeks} weeks left · ${p.known_bugs} known bugs`;
  if (p.stage === 'polish') {
    line = `Content complete · ${p.known_bugs} known bugs left`;
    control = act('[R] Release', 'release', {}, 'primary', {confirm: `Release "${p.idea.title}" now?`, after: 'projects'});
  }
  if (state.decision) control = openBtn('Decision needed', 'decision', {}, 'primary');
  const progress = p.stage === 'concept' ? p.activity_progress : p.stage === 'production' ? p.progress : p.stage === 'polish' ? 1 : 0;
  return `<div class="card focus"><div class="split"><span class="kicker">Original game · ${esc(p.idea.genre)}</span>${control}</div>
    <p class="big">${esc(p.idea.title)}</p>${stageRail(p.stage)}${bar(progress)}<p>${esc(line)}</p></div>`;
}

function nowContract() {
  const c = state.contracts[0];
  if (!c) return `<div class="card"><span class="kicker">Client work</span><p>No contract. ${state.contract_offers.length} offers on the board.</p><div class="actions">${goBtn('[B] Contract board', 'Business')}</div></div>`;
  return `<div class="card"><div class="split"><span class="kicker">Client work · ${esc(c.client)}</span>${goBtn('Board', 'Business')}</div>
    <p class="big">${esc(c.title)}</p>${bar(c.done, c.work, c.days_left < 7 ? 'danger' : '')}
    <p>${num(c.done)} / ${num(c.work)} work · ${c.days_left} days left · pays ${money(c.pay)}${state.contracts.length > 1 ? ` · ${state.contracts.length - 1} queued` : ''}</p></div>`;
}

function nowResearch() {
  const active = state.research.find(r => r.status === 'active');
  const queued = state.research.filter(r => r.status === 'queued').length;
  if (!active) return '';
  return `<div class="card"><span class="kicker">Research</span><p class="big">${esc(active.name)}</p>${bar(state.research_progress)}<p>${esc(active.effect)}${queued ? ` · ${queued} queued` : ''}</p></div>`;
}

function nowOperations() {
  const rows = state.updates.map((u, i) => `<p>${i ? 'Queued' : 'Building'}: ${esc(u.size)} for ${esc(u.product)} · ${pct(u.progress)}</p>`)
    .concat(state.commitments.map(c => `<p>${esc(c.name)} for ${esc(c.target)} · ${c.weeks_left} weeks left</p>`));
  return rows.length ? `<div class="card"><span class="kicker">Operations</span>${rows.join('')}</div>` : '';
}

function gamesTable(limit = 99) {
  if (!state.catalog.length) return empty('No releases yet. Your games will show up here with their sales.');
  const rows = [...state.catalog].reverse().slice(0, limit).map(p => `<tr class="clickable ${p.id === selectedProduct ? 'selected' : ''}" data-select="${p.id}" data-page-hint="Market">
    <td><strong>${esc(p.title)}</strong><small>${esc(p.scope)} · ${esc(p.genre)} · ${p.weeks}w</small></td>
    <td class="n">${num(p.weekly_units)}</td><td class="n">${num(p.units)}</td><td class="n">${p.rating}</td>
    <td class="n">${money(p.revenue)}</td><td class="n ${p.profit < 0 ? 'danger' : 'green'}">${money(p.profit)}</td></tr>`);
  return table(['Game', 'Week', 'Copies', 'Rating', 'Revenue', 'Profit'], rows);
}

function chartTable(limit) {
  const rows = state.chart.slice(0, limit).map((g, i) => `<tr class="${g.mine ? 'mine' : ''}"><td class="n">${i + 1}</td>
    <td><strong>${esc(g.title)}</strong><small>${esc(g.studio)} · ${esc(g.genre)}</small></td><td class="n">${num(g.weekly_units)}</td><td class="n">${g.rating}</td></tr>`);
  return table(['#', 'Game', 'Copies / wk', 'Rating'], rows);
}

function studioPage() {
  const team = state.team.map(p => {
    const tone = p.fatigue >= 70 ? 'danger' : p.fatigue >= 40 ? 'warning' : 'green';
    return `<tr><td>${esc(p.name)}<small>${esc(p.role)}</small></td><td>${p.status === 'Available' ? '' : `<span class="pill">${esc(p.status)}</span>`}</td>
      <td class="n ${tone}">${p.fatigue}</td><td class="n ${p.morale < 40 ? 'danger' : ''}">${p.morale}</td></tr>`;
  });
  return `${summary()}<div class="page cols-3">
    <div class="col"><section class="box grow"><div class="section-line"><h2>Right now</h2></div><div class="box-body">
      ${nowGame()}${nowContract()}${nowResearch()}${nowOperations()}
      <div><span class="kicker">Where the team's time goes</span>${allocationBar()}</div></div></section></div>
    <div class="col">${section('Your games', gamesTable(8), goBtn('[S] Market →', 'Market'), 'grow')}
      ${section('Top sellers this week', chartTable(10), openBtn('News', 'news'))}</div>
    <div class="col">${section(`Team · ${state.team.length}`, table(['Name', '', 'Fatigue', 'Morale'], team), goBtn('[T] People →', 'People'))}
      ${section('Recent activity', `<div class="log">${state.log.slice(0, 9).map(l => `<div class="event">${esc(l)}</div>`).join('')}</div>`, openBtn('Full log', 'log'), 'grow')}</div>
  </div>`;
}

// --- Projects -------------------------------------------------------------------

function ideaCard(i, canExplore) {
  return `<div class="card"><div class="split"><h3>${esc(i.title)}</h3><span class="pill blue">${esc(i.genre)}</span></div>
    <p>${esc(i.fantasy[0].toUpperCase() + i.fantasy.slice(1))}: ${esc(i.activity)} in ${esc(i.setting)}.${i.hook ? ` Twist: ${esc(i.hook)}.` : ''}</p>
    <div class="knowledge"><span>Fun</span>${rangeBar(i.fun, 0, 100)}</div>
    <p class="small">By ${esc(i.author)} · ${esc(i.topic)} · ${i.weeks_left} weeks before the team moves on${i.franchise ? ` · follows ${esc(i.franchise)}` : ''}</p>
    <div class="actions">${canExplore ? act('Explore', 'explore', {id: i.id}, 'primary', {after: 'projects'}) : ''}${act('Discard', 'discard_idea', {id: i.id}, '', {confirm: `Throw away "${i.title}"?`})}</div></div>`;
}

function ideaShelf() {
  const canExplore = !state.project;
  const cards = state.ideas.map(i => ideaCard(i, canExplore)).join('');
  return section(`Idea shelf · ${state.ideas.length}/${state.idea_capacity}`, cards || empty('No ideas right now. People pitch ideas while they work, and more often when they have nothing to build.'), '', 'grow');
}

function knowledge(i) {
  return `<div class="knowledge"><span>Fun</span>${rangeBar(i.fun, 0, 100)}
    <span>Build effort</span>${rangeBar(i.complexity, 0.5, 2, v => v.toFixed(2) + '×')}
    <span>Audience appeal</span>${rangeBar(i.appeal, -40, 40, v => (v > 0 ? '+' : '') + v)}</div>
    <p class="note">Bars show what the studio believes. The truth is always inside the range; experiments narrow it.</p>`;
}

function projectHeader(p) {
  const i = p.idea;
  return section(i.title, `<div class="split"><span class="kicker">${esc(i.genre)} · ${esc(i.secondary)} · ${esc(i.topic)}</span>${stageRail(p.stage)}</div>
    <p class="note">${esc(i.fantasy[0].toUpperCase() + i.fantasy.slice(1))}: ${esc(i.activity)} in ${esc(i.setting)}.${i.hook ? ` Twist: ${esc(i.hook)}.` : ''}</p>
    <p class="note"><b>Open question:</b> ${esc(i.question)}</p>
    ${p.stage === 'concept' || p.stage === 'design' ? knowledge(i) : ''}`,
  `<span class="small muted">${p.weeks} weeks in · ${p.iterations} iterations · ${p.pivots} pivots</span>`);
}

function findingsBox(p) {
  return section('Findings', `<div class="findings">${[...p.findings].reverse().map(f => `<p>${esc(f)}</p>`).join('')}</div>`, '', 'grow');
}

function conceptBody(p) {
  const busyNow = !!p.activity;
  const experiments = state.experiments.map(e => `<div class="choice"><div><strong>${esc(e.name)}</strong> <span class="pill">${esc(e.skill)}</span> <span class="small muted">${e.work} work</span><p>${esc(e.blurb)}</p></div>
    ${act('Run', 'experiment', {key: e.key}, '', {disabled: busyNow || !e.available, title: e.available ? '' : 'This idea has no unusual hook'})}</div>`).join('');
  const iterate = `<div class="choice"><div><strong>Iterate on the core loop</strong> <span class="pill">design</span><p>Rebuild and retest the core. Raises fun, with diminishing returns.</p></div>${act('Iterate', 'iterate', {}, '', {disabled: busyNow})}</div>`;
  const running = busyNow ? `<div class="card focus"><span class="kicker">In progress</span><p class="big">${esc(p.activity_name)}</p>${bar(p.activity_progress)}</div>` : '';
  const discoveries = p.discoveries.map((d, n) => `<div class="choice"><div><p>${esc(d)}</p></div>${act('Pivot', 'pivot', {index: n}, '', {confirm: 'Pivot to this direction? Much of what you learned becomes uncertain again.'})}</div>`).join('');
  return section('Concept work', `${running}<div class="choice-list">${experiments}${iterate}</div>
    ${discoveries ? `<span class="kicker">Discoveries</span><div class="choice-list">${discoveries}</div>` : ''}`,
  `<div class="tools">${act('Plan it →', 'to_design', {}, 'primary', {disabled: busyNow})}${act('Shelve', 'shelve', {}, '', {confirm: 'Put this idea back on the shelf? What you learned stays with it.'})}</div>`, 'grow');
}

function designBody(p) {
  const o = state.plan_options, plan = p.plan;
  const sel = (field, options, current) => `<label>${field}${cmdSelect('plan', options, current, {field})}</label>`;
  const free = o.model.find(m => m.name === plan.model)?.free;
  const stores = o.storefront.map(s => `<button class="${plan.storefronts.includes(s.name) ? 'on' : ''}" data-act="plan" data-fields='${esc(JSON.stringify({field: 'storefront', value: s.name}))}' ${s.lock ? `disabled title="${esc(s.lock)}"` : ''}>${esc(s.name)} · ${s.fee ? money(s.fee) : 'free'}</button>`).join('');
  const f = p.forecast;
  const deal = p.deal ? `<div class="card focus"><span class="kicker">Publisher deal</span><p class="big">${esc(p.deal.publisher)} · ${money(p.deal.advance)}</p>
    <p>They keep ${pct(p.deal.recoup_share)} of sales until the advance is paid back, then ${pct(p.deal.share)}.</p><div class="actions">${act('Turn it down', 'drop_deal')}</div></div>` : '';
  const pitches = p.deal ? '' : o.publishers.map(x => `<div class="choice"><div><strong>${esc(x.name)}</strong></div>${act(p.pitched.includes(x.name) ? 'Pitched' : 'Pitch', 'pitch', {publisher: x.name}, '', {disabled: p.pitched.includes(x.name)})}</div>`).join('');
  const commitCost = f.setup + f.fees;
  return section('Plan', `<div class="plan-grid">
      ${sel('scope', o.scope.map(s => ({value: s.name, label: `${s.name} · ${num(s.work)} work`})), plan.scope)}
      ${sel('format', o.format.map(x => ({value: x.name, label: `${x.name}${x.work > 1 ? ' · ' + x.work + '× work' : ''}`, lock: x.lock})), plan.format)}
      ${sel('presentation', o.presentation.map(x => ({value: x.name, label: `${x.name} · ${x.work}× work`})), plan.presentation)}
      ${sel('model', o.model.map(x => ({value: x.name, label: x.name, lock: x.lock})), plan.model)}
      ${free ? '<label>price<select disabled><option>Free to download</option></select></label>' : sel('price', o.price.map(v => ({value: v, label: price(v)})), plan.price)}
      ${sel('marketing', o.marketing.map(x => ({value: x.name, label: `${x.name}${x.cost ? ' · ' + money(x.cost) : ''}`})), plan.marketing)}
      ${sel('announcement', o.announcement.map(x => ({value: x.name, label: x.name})), plan.announcement)}
    </div><span class="kicker">Storefronts</span><div class="stores">${stores}</div>
    <span class="kicker">Forecast</span><div class="kv">
      <div><span>Build time</span><b>${f.weeks[0]}–${f.weeks[1]} wk</b></div><div><span>Work</span><b>${num(f.work[0])}–${num(f.work[1])}</b></div>
      <div><span>Quality</span><b>${f.quality[0]}–${f.quality[1]}</b></div><div><span>Setup + fees</span><b>${money(commitCost)}</b></div>
      <div><span>Launch marketing</span><b>${money(f.marketing)}</b></div><div><span>Total budget</span><b>${money(f.budget[0])}–${money(f.budget[1])}</b></div></div>
    <p class="note">Build time assumes the whole team works on this game. Client work and research slow it down.</p>
    ${deal}${pitches ? `<span class="kicker">Publishers</span><p class="note">Publishers judge the evidence that the game is fun and your Reputation. Each hears a pitch once.</p><div class="choice-list">${pitches}</div>` : ''}`,
  `<div class="tools">${act('Commit to production', 'commit', {}, 'primary', {confirm: `Commit? Setup and store fees cost ${money(commitCost)} now.`})}${act('← Concept', 'to_concept')}${act('Shelve', 'shelve', {}, '', {confirm: 'Put this idea back on the shelf?'})}</div>`, 'grow');
}

function productionBody(p) {
  const polish = p.stage === 'polish';
  const q = p.quality_estimate;
  return section(polish ? 'Polish' : 'Production', `${bar(p.progress)}
    <div class="kv"><div><span>Built</span><b>${num(p.work_done)} / ${num(p.work_total)}</b></div><div><span>${polish ? 'Ready' : 'ETA'}</span><b>${polish ? 'now' : '~' + p.eta_weeks + ' weeks'}</b></div>
      <div><span>Known bugs</span><b class="${p.known_bugs ? 'warning' : 'green'}">${num(p.known_bugs)}</b></div><div><span>Quality estimate</span><b>${q[0]}–${q[1]}</b></div>
      <div><span>People aware</span><b>${short(p.aware)}</b></div><div><span>Spent so far</span><b>${money(p.costs)}</b></div>
      <div><span>Scope</span><b>${esc(p.plan.scope)}</b></div><div><span>Price</span><b>${price(p.plan.price)}</b></div>
      ${p.deal ? `<div><span>Publisher</span><b>${esc(p.deal.publisher)}</b></div>` : ''}</div>
    <p class="note">${polish ? 'Every week of polish fixes bugs, and testing keeps finding more. Release when it is good enough. Bugs cost you ratings and refunds.' : 'Bugs pile up while the team builds. Milestones will ask for decisions.'}</p>
    <div class="actions">${openBtn('Promote', 'promote', {target: 0})}${openBtn('Community', 'community', {target: 0})}</div>`,
  `<div class="tools">${polish ? act('[R] Release', 'release', {}, 'primary', {confirm: `Release "${p.idea.title}" now with ${p.known_bugs} known bugs?`}) : ''}${state.decision ? openBtn('Decision needed', 'decision', {}, 'primary') : ''}${act('Cancel game', 'cancel_project', {}, '', {confirm: 'Cancel this game? Everything spent is lost, and the team takes it hard.'})}</div>`, 'grow');
}

function projectsPage() {
  const p = state.project;
  if (!p) {
    return `<div class="page cols-2"><div class="col">${section('No game in development', `<p class="note">Pick an idea from the shelf to explore it. In the concept stage you run experiments to find out how fun it really is, how hard it is to build and who it speaks to. Iterate to make it better, pivot when an experiment finds something stronger, or shelve it. Then plan it, commit, build it, polish it and release.</p>`)}
      ${section('Released games', gamesTable(), '', 'grow')}</div><div class="col">${ideaShelf()}</div></div>`;
  }
  const body = p.stage === 'concept' ? conceptBody(p) : p.stage === 'design' ? designBody(p) : productionBody(p);
  return `<div class="page cols-3"><div class="col">${projectHeader(p)}${body}</div><div class="col">${findingsBox(p)}</div><div class="col">${ideaShelf()}</div></div>`;
}

// --- People ---------------------------------------------------------------------

function skills(p) {
  const keys = ['design', 'art', 'audio', 'code', 'research'];
  const best = Math.max(...keys.map(k => p[k]));
  return `<div class="skills">${keys.map(k => `<span>${k}</span><div class="meter ${p[k] === best ? 'best' : ''}"><i style="width:${p[k]}%"></i></div><b>${p[k]}</b>`).join('')}</div>`;
}

function personCard(p) {
  const status = p.status === 'Available' ? '<span class="pill green">Available</span>' : `<span class="pill">${esc(p.status)} · ${p.status_days}d</span>`;
  return `<div class="card"><div class="split"><div><h3>${esc(p.name)}</h3><p>${p.founder ? '' : esc(p.seniority) + ' '}${esc(p.role)} · ${esc(p.trait)}${p.founder ? '' : ` · ${money(p.monthly_salary)}/mo`}</p></div>${status}</div>
    ${skills(p)}<div class="kv"><div><span>Fatigue</span><b class="${p.fatigue >= 70 ? 'danger' : p.fatigue >= 40 ? 'warning' : ''}">${p.fatigue}</b></div><div><span>Morale</span><b class="${p.morale < 40 ? 'danger' : ''}">${p.morale}</b></div></div>
    <div class="actions">${act('Vacation', 'vacation', {id: p.id}, '', {disabled: p.status !== 'Available'})}${openBtn('Train', 'train', {id: p.id})}
    ${p.founder ? '' : act('Let go', 'fire', {id: p.id}, '', {confirm: `Let ${p.name} go? Two weeks of severance, and the team's morale drops.`})}</div></div>`;
}

function peoplePage() {
  const payroll = state.team.reduce((t, p) => t + p.monthly_salary, 0);
  const rows = state.applicants.map(a => `<tr><td><strong>${esc(a.name)}</strong><small>${esc(a.seniority)} ${esc(a.role)} · ${esc(a.trait)}</small></td>
    <td class="n">${a.design}</td><td class="n">${a.art}</td><td class="n">${a.audio}</td><td class="n">${a.code}</td><td class="n">${a.research}</td>
    <td class="n">${money(a.monthly_salary)}</td><td>${act('Hire', 'hire', {id: a.id}, '', {confirm: `Hire ${a.name} for ${money(a.monthly_salary)} a month plus a ${money(a.hiring_fee)} hiring fee? Employer costs add 13% on top of salary.`})}</td></tr>`);
  return `<div class="page cols-2"><div class="col">${section(`Team · ${state.team.length} · ${money(payroll)}/mo payroll`, `<div class="cards">${state.team.map(personCard).join('')}</div>`, '', 'grow')}</div>
    <div class="col">${section('Applicants', table(['Name', 'Des', 'Art', 'Aud', 'Code', 'Res', 'Salary', ''], rows) || empty('Nobody is looking right now. The pool refreshes every month.'), '<span class="small muted">Refreshes monthly. Better studios attract better people.</span>', 'grow')}
      ${section('Where the time goes', `${allocationBar()}<p class="note">Released games and promotion take their share first. Client work takes the share you set on the Business page, research takes a fifth and updates a quarter. The game in development gets the rest, and always at least half of what is left.</p>`)}</div></div>`;
}

// --- Business ---------------------------------------------------------------------

function businessPage() {
  const s = state.studio;
  const costs = Object.entries(state.monthly_costs).map(([k, v]) => `<div><span>${esc(k)}</span><b>${money(v)}</b></div>`).join('');
  const ledgerRows = [...state.ledgers].reverse().slice(0, 8).map(l => {
    const income = Object.values(l.income).reduce((a, b) => a + b, 0), expenses = Object.values(l.expenses).reduce((a, b) => a + b, 0);
    return `<tr><td>${esc(l.month)}</td><td class="n green">${money(income)}</td><td class="n danger">${money(expenses)}</td><td class="n ${l.net < 0 ? 'danger' : 'green'}">${money(l.net)}</td></tr>`;
  });
  const loans = state.loan_offers.map(l => `<div class="choice"><div><strong>${esc(l.name)} · ${money(l.principal)}</strong><p>${l.weeks} weeks at ${pct(l.rate)} a year</p></div>
    ${act(l.taken ? 'Taken' : 'Apply', 'loan', {name: l.name}, '', {disabled: l.taken, confirm: `Borrow ${money(l.principal)}? Repayments start next week.`})}</div>`).join('');
  const active = state.loans.map(l => `<div class="choice"><div><strong>${esc(l.name)}</strong><p>${money(l.balance)} left · ${money(l.monthly)}/mo · ${l.weeks_left} weeks</p></div>${act('Repay', 'repay', {name: l.name}, '', {confirm: `Repay ${money(l.balance)} now?`})}</div>`).join('');
  const offers = state.contract_offers.map(c => {
    const late = c.estimate_weeks === null || c.estimate_weeks > c.weeks;
    const weak = c.your_quality < c.quality_target;
    return `<div class="choice"><div><strong>${esc(c.title)}</strong> <span class="pill">${esc(c.skill)} · level ${c.difficulty}</span>
      <p>${esc(c.client)} · pays <b class="green">${money(c.pay)}</b> · expires in ${c.expires_in} days</p>
      <p>You'd need <b class="${late ? 'danger' : 'green'}">${c.estimate_weeks ?? '–'} weeks</b> of the ${c.weeks}-week deadline · your quality <b class="${weak ? 'danger' : 'green'}">${c.your_quality}</b> of ${c.quality_target} needed</p></div>
      ${act('Accept', 'accept_contract', {id: c.id}, '', {disabled: c.locked, title: c.locked ? 'Needs more client trust' : ''})}</div>`;
  }).join('');
  const current = state.contracts.map((c, i) => `<div class="card ${i ? '' : 'focus'}"><div class="split"><strong>${esc(c.title)}</strong><span class="pill">${i ? 'queued' : c.days_left + ' days left'}</span></div>
    <p>${esc(c.client)} · ${esc(c.skill)} · ${money(c.pay)}</p>${bar(c.done, c.work)}</div>`).join('');
  const branches = [...new Set(state.research.map(r => r.branch))];
  const research = branches.map(b => `<span class="kicker">${esc(b)}</span><div class="choice-list">${state.research.filter(r => r.branch === b).map(r => {
    const control = r.status === 'done' ? '<span class="pill green">Done</span>' : r.status === 'active' ? `<span class="pill blue">${pct(state.research_progress)}</span>`
      : r.status === 'queued' ? act('Unqueue', 'cancel_research', {key: r.key}) : act(r.cost ? money(r.cost) : 'Free', 'research', {key: r.key}, '', {title: r.prereq.length ? 'Needs ' + r.prereq.join(', ') : ''});
    return `<div class="choice"><div><strong>${esc(r.name)}</strong> <span class="small muted">${num(r.work)} work${r.monthly ? ` · ${money(r.monthly)}/mo after` : ''}</span><p>${esc(r.effect)}${r.prereq.length ? ` · needs ${esc(r.prereq.join(', '))}` : ''}</p></div>${control}</div>`;
  }).join('')}</div>`).join('');
  return `${summary()}<div class="page cols-3">
    <div class="col">${section('Money', `<div class="kv"><div><span>Cash</span><b>${money(s.cash)}</b></div><div><span>Earned in total</span><b>${money(s.lifetime_revenue)}</b></div>
        <div><span>Credit available</span><b>${money(state.credit_limit)}</b></div></div>
      <span class="kicker">Next month's fixed costs</span><div class="kv">${costs}</div>
      <span class="kicker">Monthly books</span>${table(['Month', 'Income', 'Expenses', 'Net'], ledgerRows)}
      <span class="kicker">Loans</span>${active}<div class="choice-list">${loans}</div>
      ${s.cash < 0 ? `<p class="danger">Cash is negative. ${state.bankruptcy_weeks - s.insolvent_weeks} weeks until bankruptcy.</p>` : ''}`, openBtn('Ledger detail', 'ledger'), 'grow')}</div>
    <div class="col">${section('Client work', `<label>Share of the team's time while a game is in development
        ${cmdSelect('contract_share', [0.25, 0.5, 0.75].map(v => ({value: v, label: pct(v)})), state.contract_share, {label: 'Contract share'})}</label>
      ${current || empty('No contract running.')}
      <span class="kicker">Offers</span>${offers ? `<div class="choice-list">${offers}</div>` : empty('No offers. New ones arrive every month.')}
      <p class="note">Time estimate uses your team's skill and the share above. Late jobs aren't paid; weak work gets sent back once.</p>`,
      `<span class="small muted">${state.completed_contracts} delivered</span>`, 'grow')}</div>
    <div class="col">${section('Research', research, '', 'grow')}</div></div>`;
}

// --- Market -------------------------------------------------------------------------

function productPanel(p) {
  if (!p) return empty('Select one of your games to manage it.');
  const o = state;
  const prices = [0.99, 1.99, 2.99, 4.99, 7.99, 9.99, 14.99, 19.99, 24.99, 29.99, 39.99, 49.99, 59.99, 69.99];
  const updates = o.update_sizes.map(u => act(`${u.name}${u.cost ? ' · ' + money(u.cost) : ''}`, 'update', {id: p.id, size: u.name}, '', {disabled: !!u.lock, title: u.lock})).join('');
  return `<div class="split"><p class="big">${esc(p.title)}</p><span class="pill blue">v${esc(p.version)}</span></div>
    <p class="note">${esc(p.scope)} ${esc(p.genre)} · ${esc(p.model)} · ${esc(p.storefronts.join(', '))}${p.deal ? ' · published by ' + esc(p.deal) : ''}</p>
    ${sparkBars(p.history)}
    <div class="kv"><div><span>This week</span><b>${num(p.weekly_units)}</b></div><div><span>Copies</span><b>${num(p.units)}</b></div>
      <div><span>Players</span><b>${num(p.players)}</b></div><div><span>People aware</span><b>${short(p.aware)}</b></div>
      <div><span>Rating</span><b>${p.rating}</b></div><div><span>Press score</span><b>${p.review || '–'}</b></div>
      <div><span>Quality</span><b>${p.quality}</b></div><div><span>Sentiment</span><b class="${p.sentiment < 40 ? 'danger' : ''}">${p.sentiment}</b></div>
      <div><span>Bugs</span><b class="${p.bugs ? 'warning' : ''}">${num(p.bugs)}</b></div><div><span>Revenue</span><b>${money(p.revenue)}</b></div>
      <div><span>Costs</span><b>${money(p.costs)}</b></div><div><span>Profit</span><b class="${p.profit < 0 ? 'danger' : 'green'}">${money(p.profit)}</b></div></div>
    <div class="plan-grid">${p.model === 'Premium' || p.model === 'Subscription' ? `<label>Price${cmdSelect('price', prices.map(v => ({value: v, label: price(v)})), p.price, {param: 'price', extra: {id: p.id}})}</label>` : ''}
      <label>Support${cmdSelect('support', o.support_levels.map(v => ({value: v, label: v})), p.support, {param: 'level', extra: {id: p.id}})}</label></div>
    <span class="kicker">Updates</span><div class="actions">${updates}</div>
    <div class="actions">${openBtn('Promote', 'promote', {target: p.id})}${openBtn('Community', 'community', {target: p.id})}</div>`;
}

function marketPage() {
  const mine = state.catalog;
  if (selectedProduct === null && mine.length) selectedProduct = mine[mine.length - 1].id;
  const product = mine.find(p => p.id === selectedProduct);
  const hot = state.trends.slice(0, 6), cold = state.trends.slice(-4);
  const trend = t => `<div><span>${esc(t.genre)}</span><b class="${t.label === 'Hot' || t.label === 'Rising' ? 'green' : t.label === 'Cooling' ? 'danger' : ''}">${esc(t.label)}${t.heat ? ' ' + t.heat : ''}</b></div>`;
  const rivals = state.rivals.slice(0, 40).map(r => `<tr class="${r.status === 'Independent' ? '' : 'muted'}"><td><strong>${esc(r.name)}</strong><small>${esc(r.status)}${r.recent[0] ? ` · latest: ${esc(r.recent[0].title)} (${r.recent[0].rating})` : ''}</small></td>
    <td class="n">${num(r.staff)}</td><td class="n">${short(r.fans)}</td><td class="n">${r.reputation}</td>${r.revenue_year !== null ? `<td class="n">${short(r.revenue_year)}</td>` : ''}</tr>`);
  const rivalHeaders = ['Studio', 'Staff', 'Fans', 'Rep'].concat(state.rivals[0]?.revenue_year !== null ? ['Revenue/yr'] : []);
  return `<div class="page cols-3">
    <div class="col">${section('Top sellers this week', chartTable(30), `<span class="small muted">Spending mood ${pct(state.confidence)}</span>`, 'grow')}</div>
    <div class="col">${section('Your games', gamesTable(), '', '')}${section('Manage', productPanel(product), '', 'grow')}</div>
    <div class="col">${section('Genre trends', `<div class="kv">${hot.map(trend).join('')}</div><span class="kicker">Cooling</span><div class="kv">${cold.map(trend).join('')}</div>
        ${state.trends[0].heat === null ? '<p class="note">Market Research shows trends as numbers.</p>' : ''}`)}
      ${section('Studios', table(rivalHeaders, rivals), openBtn('News', 'news'), 'grow')}</div></div>`;
}

const PAGE_VIEWS = {Studio: studioPage, Projects: projectsPage, People: peoplePage, Business: businessPage, Market: marketPage};
