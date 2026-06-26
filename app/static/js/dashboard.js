/**
 * dashboard.js — Interactive Pipeline Control Panel
 * Handles button actions, live stat updates, animated counters, and chart redraws.
 */

'use strict';

// ─── Plotly dark theme ───────────────────────────────────────────────────────
const DARK = {
  paper_bgcolor: 'transparent', plot_bgcolor: 'transparent',
  font: { color: '#94a3b8', family: 'Inter, sans-serif', size: 12 },
  margin: { t: 20, b: 40, l: 50, r: 20 },
  legend: { bgcolor: 'transparent', borderwidth: 0 },
};

// ─── Step 1: Load Data (fetch JSON → timed step animation) ───────────────────
async function runLoadData() {
  setStepStatus('step-data-badge', 'running');
  setBtnState('btn-load-data', 'loading', 'Loading Data…');

  const progressBox = document.getElementById('load-progress-box');
  progressBox.style.display = 'block';
  const bar       = document.getElementById('load-progress-bar');
  const barLabel  = document.getElementById('load-progress-pct');
  const stageLog  = document.getElementById('load-stage-log');
  const stageLine = document.getElementById('load-stage-current');

  bar.style.width = '5%';
  barLabel.textContent = '5%';
  stageLine.textContent = 'Connecting to database…';
  stageLog.innerHTML = '';

  try {
    const r = await fetch('/api/pipeline/load-data');
    const d = await r.json();
    if (d.status !== 'ok') throw new Error('Bad response from server');

    // Replay each stage with a 550ms delay so the bar visibly moves
    for (let i = 0; i < d.stages.length; i++) {
      await new Promise(res => setTimeout(res, 550));
      const s = d.stages[i];

      // Move bar
      bar.style.width = s.pct + '%';
      barLabel.textContent = s.pct + '%';
      stageLine.textContent = s.stage;

      // Turn bar green on completion
      if (s.pct === 100) bar.classList.add('complete');

      // Append log line
      const line = document.createElement('div');
      line.className = 'log-line';
      line.innerHTML =
        `<span class="log-pct">${s.pct}%</span> ` +
        `<span class="log-stage">${s.stage}</span> — ` +
        `<span class="log-detail">${s.detail}</span>`;
      stageLog.appendChild(line);
      stageLog.scrollTop = stageLog.scrollHeight;

      if (s.done) {
        setStepStatus('step-data-badge', 'done');
        setBtnState('btn-load-data', 'done', 'Data Loaded ✅');
        if (s.totals) {
          animateCounter('stat-runs', s.totals.runs);
        }
        // Unlock Step 2
        const btn2 = document.getElementById('btn-generate-alarms');
        if (btn2) btn2.disabled = false;
      }
    }
  } catch (e) {
    setStepStatus('step-data-badge', 'error');
    setBtnState('btn-load-data', 'error', 'Try Again');
    stageLine.textContent = '❌ Error: ' + e.message;
  }
}


// ─── Animate a number counter rolling up ─────────────────────────────────────
function animateCounter(elId, target, duration = 900) {
  const el = document.getElementById(elId);
  if (!el) return;
  const start = parseInt(el.textContent.replace(/,/g, '')) || 0;
  const startTime = performance.now();
  function step(now) {
    const t = Math.min((now - startTime) / duration, 1);
    const ease = t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t; // ease-in-out
    const current = Math.round(start + (target - start) * ease);
    el.textContent = current.toLocaleString();
    if (t < 1) requestAnimationFrame(step);
  }
  requestAnimationFrame(step);
}

// ─── Button state helpers ─────────────────────────────────────────────────────
function setBtnState(btnId, state, label) {
  const btn = document.getElementById(btnId);
  if (!btn) return;
  btn.disabled = (state === 'loading');
  const icons = { idle: '', loading: '⏳ ', done: '✅ ', error: '❌ ' };
  btn.innerHTML = (icons[state] || '') + label;
  btn.className = btn.className.replace(/\bbtn-\S+/g, '');
  const classes = { idle: 'btn-primary', loading: 'btn-secondary', done: 'btn-success', error: 'btn-danger' };
  btn.classList.add(classes[state] || 'btn-primary');
}

function setStepStatus(stepId, state) {
  const el = document.getElementById(stepId);
  if (!el) return;
  const map = {
    pending:  { icon: '⬜', cls: 'step-pending',  text: 'Pending' },
    running:  { icon: '🔄', cls: 'step-running',  text: 'Running…' },
    done:     { icon: '✅', cls: 'step-done',      text: 'Done' },
    skipped:  { icon: '⏭️', cls: 'step-skipped',  text: 'Already done' },
    error:    { icon: '❌', cls: 'step-error',     text: 'Error' },
  };
  const s = map[state] || map.pending;
  el.className = `step-badge ${s.cls}`;
  el.textContent = `${s.icon} ${s.text}`;
}

function showResultBanner(containerId, html, type = 'success') {
  const el = document.getElementById(containerId);
  if (!el) return;
  const colors = { success: '#10b981', warning: '#f59e0b', error: '#ef4444', info: '#3b82f6' };
  el.innerHTML = `<div class="result-banner" style="border-left:3px solid ${colors[type] || colors.success}">${html}</div>`;
  el.style.display = 'block';
}

// ─── Draw / refresh charts ───────────────────────────────────────────────────
function drawAlarmChart(critical, warning) {
  if (typeof Plotly === 'undefined') return;
  Plotly.react('chart-alarm-severity', [{
    type: 'bar',
    x: ['Critical', 'Warning'],
    y: [critical, warning],
    marker: { color: ['#ef4444', '#f59e0b'] },
    text: [critical.toLocaleString(), warning.toLocaleString()],
    textposition: 'auto',
  }], {
    ...DARK,
    yaxis: { gridcolor: '#253148', title: 'Count' },
    xaxis: { gridcolor: '#253148' },
  }, { responsive: true, displayModeBar: false });
}

function drawIncidentChart(criticalInc, warningInc) {
  if (typeof Plotly === 'undefined') return;
  Plotly.react('chart-incidents-component', [{
    type: 'pie',
    labels: ['Critical', 'Warning'],
    values: [criticalInc, warningInc],
    marker: { colors: ['#ef4444', '#f59e0b'] },
    hole: 0.45,
    textinfo: 'label+value',
    textfont: { color: '#e2e8f0', size: 13 },
  }], {
    ...DARK,
    margin: { t: 10, b: 10, l: 10, r: 10 },
    showlegend: true,
    legend: { orientation: 'h', y: -0.15, font: { color: '#94a3b8' } },
  }, { responsive: true, displayModeBar: false });
}

function drawReadinessGauge(pct) {
  if (typeof Plotly === 'undefined') return;
  const color = pct >= 75 ? '#10b981' : pct >= 50 ? '#f59e0b' : '#ef4444';
  Plotly.react('chart-readiness-gauge', [{
    type: 'indicator',
    mode: 'gauge+number',
    value: pct,
    number: { suffix: '%', font: { size: 28, color } },
    gauge: {
      axis: { range: [0, 100], tickcolor: '#94a3b8', tickfont: { color: '#94a3b8' } },
      bar: { color },
      bgcolor: '#1e2a3a',
      bordercolor: '#253148',
      steps: [
        { range: [0, 50],  color: 'rgba(239,68,68,0.15)' },
        { range: [50, 75], color: 'rgba(245,158,11,0.15)' },
        { range: [75, 100],color: 'rgba(16,185,129,0.15)' },
      ],
    },
  }], { ...DARK, margin: { t: 20, b: 10, l: 30, r: 30 } },
  { responsive: true, displayModeBar: false });
}

// ─── Load initial status on page load ────────────────────────────────────────
async function loadInitialStatus() {
  try {
    const r = await fetch('/api/pipeline/status');
    const d = await r.json();
    // Update all stat cards silently (no animation on first load)
    ['stat-runs','stat-alarms','stat-critical','stat-incidents','stat-sims'].forEach(id => {
      const el = document.getElementById(id);
    });
    document.getElementById('stat-runs')      && (document.getElementById('stat-runs').textContent      = d.runs.toLocaleString());
    document.getElementById('stat-alarms')    && (document.getElementById('stat-alarms').textContent    = d.alarms.toLocaleString());
    document.getElementById('stat-critical')  && (document.getElementById('stat-critical').textContent  = d.critical.toLocaleString());
    document.getElementById('stat-incidents') && (document.getElementById('stat-incidents').textContent = d.incidents.toLocaleString());
    document.getElementById('stat-sims')      && (document.getElementById('stat-sims').textContent      = d.simulations.toLocaleString());

    // Readiness
    const readEl = document.getElementById('stat-readiness');
    if (readEl) readEl.textContent = d.readiness_pct !== null ? `${d.readiness_pct}%` : '—';

    // Step badge states
    if (d.runs > 0)         setStepStatus('step-data-badge', 'done');
    if (d.alarms > 0)       setStepStatus('step-alarm-badge', 'done');
    if (d.incidents > 0)    setStepStatus('step-incident-badge', 'done');
    if (d.readiness_pct !== null) setStepStatus('step-readiness-badge', 'done');

    // Charts
    if (d.alarms > 0) drawAlarmChart(d.critical, d.warning);
    if (d.incidents > 0) drawIncidentChart(d.critical_incidents, d.warning_incidents);
    if (d.readiness_pct !== null) drawReadinessGauge(d.readiness_pct);
  } catch (e) {
    console.warn('Could not load pipeline status:', e);
  }
}

// ─── Step 2: Generate Alarms ─────────────────────────────────────────────────
async function runGenerateAlarms() {
  setStepStatus('step-alarm-badge', 'running');
  setBtnState('btn-generate-alarms', 'loading', 'Generating Alarms…');

  try {
    const r = await fetch('/api/pipeline/generate-alarms', { method: 'POST' });
    const d = await r.json();

    if (d.status !== 'ok') throw new Error(d.error || 'Unknown error');

    // Animate counters
    animateCounter('stat-alarms', d.total_alarms);
    animateCounter('stat-critical', d.critical);

    // Redraw chart
    drawAlarmChart(d.critical, d.warning);

    setStepStatus('step-alarm-badge', d.already_existed ? 'skipped' : 'done');
    setBtnState('btn-generate-alarms', 'done', 'Alarms Generated');

    const msg = d.already_existed
      ? `ℹ️ Alarms already existed. Total: <strong>${d.total_alarms.toLocaleString()}</strong> | Critical: <strong>${d.critical.toLocaleString()}</strong> | Warning: ${d.warning.toLocaleString()}`
      : `✅ Generated <strong>${d.new_alarms.toLocaleString()} new alarms</strong>! Total: ${d.total_alarms.toLocaleString()} | Critical: <strong>${d.critical.toLocaleString()}</strong> | Warning: ${d.warning.toLocaleString()}`;
    showResultBanner('alarm-result', msg, d.already_existed ? 'info' : 'success');

    // Unlock next step
    document.getElementById('btn-group-incidents') && (document.getElementById('btn-group-incidents').disabled = false);
  } catch (e) {
    setStepStatus('step-alarm-badge', 'error');
    setBtnState('btn-generate-alarms', 'error', 'Try Again');
    showResultBanner('alarm-result', `❌ Error: ${e.message}`, 'error');
  }
}

// ─── Step 3: Group Incidents ──────────────────────────────────────────────────
async function runGroupIncidents() {
  setStepStatus('step-incident-badge', 'running');
  setBtnState('btn-group-incidents', 'loading', 'Grouping Incidents…');

  try {
    const r = await fetch('/api/pipeline/group-incidents', { method: 'POST' });
    const d = await r.json();

    if (d.status !== 'ok') throw new Error(d.error || 'Unknown error');

    animateCounter('stat-incidents', d.total_incidents);
    drawIncidentChart(d.critical, d.warning);

    setStepStatus('step-incident-badge', d.already_existed ? 'skipped' : 'done');
    setBtnState('btn-group-incidents', 'done', 'Incidents Grouped');

    const msg = d.already_existed
      ? `ℹ️ Incidents already grouped. Total: <strong>${d.total_incidents.toLocaleString()}</strong> | Critical: <strong>${d.critical.toLocaleString()}</strong> | Warning: ${d.warning.toLocaleString()}`
      : `✅ Grouped into <strong>${d.new_incidents.toLocaleString()} incidents</strong>! Critical: <strong>${d.critical.toLocaleString()}</strong> | Warning: ${d.warning.toLocaleString()}`;
    showResultBanner('incident-result', msg, d.already_existed ? 'info' : 'success');

    document.getElementById('btn-run-readiness') && (document.getElementById('btn-run-readiness').disabled = false);
  } catch (e) {
    setStepStatus('step-incident-badge', 'error');
    setBtnState('btn-group-incidents', 'error', 'Try Again');
    showResultBanner('incident-result', `❌ Error: ${e.message}`, 'error');
  }
}

// ─── Step 4: Run Readiness ────────────────────────────────────────────────────
async function runReadiness() {
  setStepStatus('step-readiness-badge', 'running');
  setBtnState('btn-run-readiness', 'loading', 'Assessing Readiness…');

  try {
    const r = await fetch('/api/pipeline/run-readiness', { method: 'POST' });
    const d = await r.json();

    if (d.status !== 'ok') throw new Error(d.error || 'Unknown error');

    const pct = d.percentage_score;
    animateCounter('stat-readiness-num', pct);
    const readEl = document.getElementById('stat-readiness');
    if (readEl) {
      // Animate the readiness card percentage
      const startVal = parseFloat(readEl.textContent) || 0;
      const dur = 900, t0 = performance.now();
      (function step(now) {
        const t = Math.min((now - t0) / dur, 1);
        const v = (startVal + (pct - startVal) * t).toFixed(1);
        readEl.textContent = `${v}%`;
        const color = pct >= 75 ? 'var(--accent-green)' : pct >= 50 ? 'var(--accent-amber)' : 'var(--accent-red)';
        readEl.style.color = color;
        if (t < 1) requestAnimationFrame(step);
      })(t0);
    }

    drawReadinessGauge(pct);
    setStepStatus('step-readiness-badge', 'done');
    setBtnState('btn-run-readiness', 'done', 'Assessment Complete');

    const color = pct >= 75 ? 'success' : pct >= 50 ? 'warning' : 'error';
    const emoji = pct >= 75 ? '🟢' : pct >= 50 ? '🟡' : '🔴';
    showResultBanner('readiness-result',
      `${emoji} Readiness Score: <strong>${pct}%</strong> &mdash; ${d.title}<br>
       Score: ${d.total_score.toFixed(1)} / ${d.max_score.toFixed(1)} points`, color);
  } catch (e) {
    setStepStatus('step-readiness-badge', 'error');
    setBtnState('btn-run-readiness', 'error', 'Try Again');
    showResultBanner('readiness-result', `❌ Error: ${e.message}`, 'error');
  }
}

// ─── Boot ────────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', loadInitialStatus);
