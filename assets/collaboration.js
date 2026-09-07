const root = document.querySelector('#collaboration');
const esc = value => String(value).replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
let snapshot;
let state = {range:84, tool:'All tools', from:'', to:'', date:'', paused:matchMedia('(prefers-reduced-motion: reduce)').matches, limit:40};

function matching(commit) { return state.tool === 'All tools' ? commit.tools.length > 0 : commit.tools.includes(state.tool); }
function selectedDays() { return snapshot.days.filter(day => day.date >= state.from && day.date <= state.to); }
function selectedCommits() { return snapshot.commits.filter(commit => commit.date >= state.from && commit.date <= state.to); }

function setRange(days) {
  state.range = days;
  state.to = snapshot.to;
  state.from = snapshot.days[Math.max(0, snapshot.days.length - days)].date;
  state.date = '';
  state.limit = 40;
  render();
}

function chart(days, records) {
  const daily = days.map(day => ({...day, matched:records.filter(c => c.date === day.date && matching(c)).length}));
  const columns = Math.ceil(days.length / 7);
  const step = Math.min(48, 890 / Math.max(columns, 1));
  const size = Math.min(30, step * .67);
  const depth = Math.max(6, size * .64);
  const max = Math.max(1, ...daily.map(day => day.total));
  let svg = '<svg viewBox="0 0 1200 470" role="group" aria-label="Interactive daily commit landscape. Select a day to inspect its commits.">';
  svg += '<path d="M90,266L296,380L1150,210L955,102Z" fill="#e5eff1" stroke="#d4e4e8"/>';
  daily.forEach((day, i) => {
    const col = Math.floor(i / 7), row = i % 7;
    const x = 240 + col * step - row * depth;
    const y = 150 + col * Math.min(3, 110 / columns) + row * 19;
    const height = 4 + 145 * day.total / max;
    const aiHeight = 145 * day.matched / max;
    const top = y - height;
    const selected = state.date === day.date;
    const label = `${day.date}: ${day.total} public commits; ${day.matched} matching AI commits`;
    svg += `<g tabindex="0" role="button" data-day="${day.date}" aria-label="${label}" aria-pressed="${selected}"><title>${label}</title>`;
    svg += `<path d="M${x},${y}l${size},8 0,${-height} ${-size},-8Z" fill="#a6bfc9"/><path d="M${x+size},${y+8}l${depth},-10 0,${-height} ${-depth},10Z" fill="#819eac"/>`;
    if (aiHeight) svg += `<path d="M${x},${top}l${size},8 0,${aiHeight} ${-size},-8Z" fill="#57ad99"/><path d="M${x+size},${top+8}l${depth},-10 0,${aiHeight} ${-depth},10Z" fill="#2b8776"/>`;
    svg += `<path d="M${x},${top}l${depth},-10 ${size},8 ${-depth},10Z" fill="${day.matched ? '#a2dccb' : '#d5e4ea'}" stroke="${selected ? '#bf8d36' : '#f7fbfc'}" stroke-width="${selected ? 3 : 1}"/>`;
    if (day.matched) svg += `<circle class="anim-glow" cx="${x+size/2+depth/2}" cy="${top-5}" r="3" fill="#c49949"/>`;
    svg += '</g>';
  });
  svg += `<text x="70" y="402" font-family="Arial,sans-serif" font-size="18" fill="#42616e">${state.from}</text><text x="980" y="402" font-family="Arial,sans-serif" font-size="18" fill="#42616e">${state.to}</text><text x="70" y="440" font-family="Arial,sans-serif" font-size="17" fill="#59717b">Column heights: linear scale, 0–${max} commits/day · Select a column or choose a date below</text></svg>`;
  return svg;
}

function render() {
  const days = selectedDays();
  const records = selectedCommits();
  const ai = records.filter(matching);
  const unattributed = records.filter(c => !c.tools.length);
  const providers = [...new Set(snapshot.commits.flatMap(c => c.tools))].sort();
  const filtered = records.filter(c => (!state.date || c.date === state.date) && (state.tool === 'All tools' || matching(c)));
  const rows = filtered.slice(0, state.limit);
  root.classList.toggle('paused',state.paused);
  root.innerHTML = `<div class="meta"><span class="statusdot"></span>Snapshot ${esc(snapshot.updated.replace('T',' ').slice(0,19))} UTC · Updated daily</div>
  <div class="toolbar" aria-label="Date range">${[28,84,365].map(d=>`<button data-range="${d}" aria-pressed="${state.range===d}">${d} days</button>`).join('')}
  <label for="tool">AI tool</label><select id="tool"><option>All tools</option>${providers.map(p=>`<option ${state.tool===p?'selected':''}>${esc(p)}</option>`).join('')}</select><button id="motion" aria-pressed="${state.paused}">${state.paused?'Resume animation':'Pause animation'}</button></div>
  <form id="dates" class="toolbar"><label for="date-from">From</label><input id="date-from" type="date" min="${snapshot.from}" max="${snapshot.to}" value="${state.from}" required><label for="date-to">To</label><input id="date-to" type="date" min="${snapshot.from}" max="${snapshot.to}" value="${state.to}" required><button type="submit">Apply dates</button></form>
  <div class="metricrow"><div class="metric"><b>${records.length}</b><span>Public commits in range</span></div><div class="metric"><b>${ai.length}</b><span>${state.tool==='All tools'?'AI-attributed':'Matching AI'} commits</span></div><div class="metric"><b>${new Set(ai.map(c=>c.date)).size}</b><span>Matching AI days</span></div><div class="metric"><b>${unattributed.length}</b><span>Unattributed commits</span></div></div>
  <div class="viz">${chart(days, records)}<div class="legend"><span><i></i>${state.tool==='All tools'?'AI-attributed':'Selected AI tool'}</span><span><i class="other"></i>Other records in range</span></div></div>
  <div class="toolbar"><label for="inspect-date">Inspect a day</label><select id="inspect-date"><option value="">All dates in range</option>${days.slice().reverse().map(d=>`<option value="${d.date}" ${state.date===d.date?'selected':''}>${d.date} · ${d.total} commits</option>`).join('')}</select></div>
  <div class="dayinfo" aria-live="polite">${state.date?`${state.date}: ${records.filter(c=>c.date===state.date).length} public commits, ${ai.filter(c=>c.date===state.date).length} matching AI commits.`:`${state.from} to ${state.to}: ${ai.length} of ${records.length} public commits have matching AI evidence.`}</div>
  <section class="section"><h2>Tool participation</h2><div class="grid">${providers.map(p=>`<article class="card"><span class="number">${records.filter(c=>c.tools.includes(p)).length}</span><h3>${esc(p)}</h3><p>Commits with explicit attribution in the selected date range.</p></article>`).join('') || '<p>No attributed tools in this snapshot.</p>'}</div><p class="meta">A commit may involve more than one tool. Tool counts can overlap.</p></section>
  <section class="section"><h2>Public commit ledger</h2><div class="tablewrap"><table><caption>${filtered.length} records match the selection. Open a commit to inspect the public evidence.</caption><thead><tr><th>Date</th><th>Repository</th><th>AI tool</th><th>Evidence</th><th>Commit</th></tr></thead><tbody>${rows.map(c=>`<tr><td>${c.date}</td><td>${esc(c.repo)}</td><td>${esc(c.tools.join(', ')||'—')}</td><td>${esc(c.evidence)}</td><td><a href="${esc(c.url)}">${esc(c.sha.slice(0,7))} ↗</a></td></tr>`).join('')}</tbody></table></div>${!filtered.length?'<p class="filterempty">No matching commits in this selection. Try a longer date range or select All tools.</p>':''}${filtered.length>rows.length?'<button class="button" id="more">Show more records</button>':''}</section>`;
  root.querySelectorAll('[data-range]').forEach(b=>b.addEventListener('click',()=>setRange(Number(b.dataset.range))));
  root.querySelector('#tool').addEventListener('change',event=>{state.tool=event.target.value;state.limit=40;render();});
  root.querySelector('#motion').addEventListener('click',()=>{state.paused=!state.paused;render();root.querySelector('#motion').focus();});
  ['#date-from','#date-to'].forEach(selector=>root.querySelector(selector).addEventListener('input',()=>root.querySelector('#date-to').setCustomValidity('')));
  root.querySelector('#dates').addEventListener('submit',event=>{
    event.preventDefault();
    const from=root.querySelector('#date-from'),to=root.querySelector('#date-to');
    to.setCustomValidity(to.value<from.value?'The end date must be on or after the start date.':'');
    if(!to.reportValidity())return;
    state.from=from.value;state.to=to.value;state.range=0;state.date='';state.limit=40;render();
  });
  const selectDay = date => {state.date=date;state.limit=40;render();root.querySelector('#inspect-date').focus();};
  root.querySelector('#inspect-date').addEventListener('change',event=>selectDay(event.target.value));
  root.querySelectorAll('[data-day]').forEach(day=>{
    day.addEventListener('click',()=>selectDay(day.dataset.day));
    day.addEventListener('keydown',event=>{if(event.key==='Enter'||event.key===' '){event.preventDefault();selectDay(day.dataset.day);}});
  });
  root.querySelector('#more')?.addEventListener('click',()=>{state.limit+=80;render();});
}

fetch('/data/activity.json').then(response=>{
  if(!response.ok)throw new Error('Snapshot unavailable');
  return response.json();
}).then(data=>{snapshot=data;setRange(84);}).catch(()=>{
  root.innerHTML='<p class="filterempty">The collaboration snapshot could not be loaded. <a href="/data/activity.json">Open the snapshot</a> or reload this page.</p>';
});
