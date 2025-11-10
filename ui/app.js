// DOM
const statusBox = document.getElementById('status');
const statusText = document.getElementById('status-text');
const btnTranslate = document.getElementById('btn-translate');
const btnVerify = document.getElementById('btn-verify');
const btnDownload = document.getElementById('btn-download');
const btnLoadExample = document.getElementById('btn-load-example');

const sourceSel = document.getElementById('source');
const targetSel = document.getElementById('target');
const fnameInp  = document.getElementById('fname');
const customInp = document.getElementById('custom');

const codeTa = document.getElementById('code');
const outTa  = document.getElementById('out');

const resultsBox = document.getElementById('results');
const passBadge = document.getElementById('pass-badge');
const totals = document.getElementById('totals');
const casesTbody = document.querySelector('#cases tbody');
const jobMeta = document.getElementById('job-meta');

const historyList = document.getElementById('history-list');
const btnRefreshHistory = document.getElementById('btn-refresh-history');

let lastTarget = 'c';
let lastTranslatedCode = "";

// Status helpers
function showStatus(msg){
  statusText.textContent = msg || "Working…";
  statusBox.style.display = '';
  statusBox.classList.remove('hidden');
}
function hideStatus(){
  statusBox.classList.add('hidden');
  statusBox.style.display = 'none';
}

// API helpers
async function callAPI(url, body){
  const r = await fetch(url, {
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body: JSON.stringify(body)
  });
  if(!r.ok){
    throw new Error(`HTTP ${r.status}: ${await r.text()}`);
  }
  return await r.json();
}

function getPayload(){
  let inputs = null;
  const raw = (customInp.value || "").trim();
  if(raw){
    try { inputs = JSON.parse(raw); } catch(e){ inputs = null; }
  }
  return {
    source_lang: sourceSel.value,
    target_lang: targetSel.value,
    function_name: (fnameInp.value || "func"),
    code: codeTa.value,
    inputs
  };
}

// Render helpers
function showResults(rep, job_id){
  if(!rep){ resultsBox.classList.add('hidden'); return; }
  const pct = Math.round((rep.pass_rate || 0)*100);
  passBadge.textContent = `Pass Rate: ${pct}%`;
  passBadge.classList.toggle('fail', pct < 80);
  totals.textContent = `Passed ${rep.passed}/${rep.total}`;
  jobMeta.textContent = job_id ? `Job: ${job_id}` : '';
  casesTbody.innerHTML = "";
  rep.cases.forEach((c, i)=>{
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${i+1}</td>
      <td>${JSON.stringify(c.args)}</td>
      <td>${c.expected}</td>
      <td>${c.got}</td>
      <td class="${c.ok?'ok':'fail'}">${c.ok?'✓':'✗'}</td>
    `;
    casesTbody.appendChild(tr);
  });
  resultsBox.classList.remove('hidden');
}

function renderHistory(items){
  historyList.innerHTML = "";
  window.historyData = items || [];
  if(!items.length){
    historyList.innerHTML = `<div class="history-item"><div class="history-meta">No history yet.</div></div>`;
    return;
  }
  items.forEach((it)=>{
    const div = document.createElement('div');
    div.className = 'history-item';
    const ts = new Date(it.timestamp || Date.now()).toISOString().replace('T',' ').slice(0,19);
    const title = `${it.source_lang} → ${it.target_lang} · ${it.function_name || 'func'}`;
    const sub = `#${it.job_id || '—'} · ${it.verified ? 'Verified' : 'Unverified'} · ${Math.round((it.pass_rate||0)*100)}% · ${ts}`;
    div.innerHTML = `<div class="history-title">${title}</div><div class="history-meta">${sub}</div>`;
    div.addEventListener('click', ()=>{
      // Load into UI
      sourceSel.value = it.source_lang;
      targetSel.value = it.target_lang;
      fnameInp.value  = it.function_name || 'func';
      codeTa.value    = it.source_code || '';
      outTa.value     = it.translated_code || '';
      lastTranslatedCode = it.translated_code || '';
      lastTarget = it.target_lang || lastTarget;
      // If report exists show it
      if(it.report){
        showResults(it.report, it.job_id);
      }else{
        resultsBox.classList.add('hidden');
      }
      window.scrollTo({top:0, behavior:'smooth'});
    });
    historyList.appendChild(div);
  });
}

// Actions
btnTranslate.addEventListener('click', async ()=>{
  resultsBox.classList.add('hidden');
  const payload = getPayload();
  lastTarget = payload.target_lang;

  showStatus('Translating…');
  try{
    const data = await callAPI('/api/translate', payload);
    const code = data.translated_code || data.error || '';
    lastTranslatedCode = code;
    outTa.value = code;
  }catch(err){
    outTa.value = `Error: ${err.message}`;
  }finally{
    hideStatus();
    loadHistory(); // refresh history sidebar
  }
});

btnVerify.addEventListener('click', async ()=>{
  const payload = getPayload();
  lastTarget = payload.target_lang;

  showStatus('Translating & verifying…');
  try{
    const data = await callAPI('/api/translate_and_verify', payload);
    const code = data.translated_code || data.error || '';
    lastTranslatedCode = code;
    outTa.value = code;

    if(data.report){
      showResults(data.report, data.job_id);
    }else{
      resultsBox.classList.add('hidden');
    }
  }catch(err){
    outTa.value = `Error: ${err.message}`;
    resultsBox.classList.add('hidden');
  }finally{
    hideStatus();
    loadHistory(); // refresh history
  }
});

btnDownload.addEventListener('click', ()=>{
  if(!lastTranslatedCode) return;
  const ext = lastTarget === 'java' ? 'java' : (lastTarget === 'cpp' ? 'cpp' : (lastTarget === 'c' ? 'c' : 'py'));
  const blob = new Blob([lastTranslatedCode], {type:'text/plain'});
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = `translated.${ext}`;
  a.click();
  URL.revokeObjectURL(a.href);
});

btnLoadExample.addEventListener('click', ()=>{
  sourceSel.value = 'python';
  targetSel.value = 'c';
  fnameInp.value = 'gcd';
  codeTa.value = [
    'def gcd(a:int, b:int)->int:',
    '    a = abs(a); b = abs(b)',
    '    while b != 0:',
    '        a, b = b, a % b',
    '    return a',
  ].join('\n');
});

btnRefreshHistory.addEventListener('click', loadHistory);

// History loader
async function loadHistory(){
  try{
    const r = await fetch('/api/history');
    const data = await r.json();
    renderHistory(data.items || []);
  }catch(e){
    console.error('history error', e);
    renderHistory([]);
  }
}

// Init
window.addEventListener('DOMContentLoaded', ()=>{
  loadHistory();
});
