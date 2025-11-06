const form = document.getElementById('form');
const out = document.getElementById('out');
const result = document.getElementById('result');

form.addEventListener('submit', async (e)=>{
  e.preventDefault();
  const body = {
    source_lang: document.getElementById('source').value,
    target_lang: document.getElementById('target').value,
    function_name: document.getElementById('fname').value || null,
    code: document.getElementById('code').value
  };
  const r = await fetch('/api/translate', {
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body: JSON.stringify(body)
  });
  const data = await r.json();
  out.textContent = data.translated_code || data.error || '(no output)';
  result.classList.remove('hidden');
});
