'use strict';
function syncAssistant(){
  if(!db)return;
  $('#ai-mode').textContent=db.ai.mode==='ollama'?'Local model mode: '+db.ai.model:'Demo preview: no generative model connected';
  $('#agent-request').textContent=`Current request: ${$('#query').value} · ${$('#quantity').value} units · ${$('#recipient').selectedOptions[0]?.textContent||''} · ${$('#radius').value} km`;
}
document.addEventListener('reloop-ready',syncAssistant);
['query','quantity','recipient','radius','repair'].forEach(id=>$('#'+id).addEventListener('change',syncAssistant));
function sourceMarkup(sources){return (sources||[]).map(s=>`<details><summary>${esc(s.section)} <small>[${esc(s.id)}]</small></summary><p>${esc(s.text)}</p><small>${esc(s.file)} · relevance ${Number(s.score).toFixed(2)}</small></details>`).join('');}
async function assistantAction(form, target, action){
  const buttons=[...form.querySelectorAll('button')];buttons.forEach(b=>b.disabled=true);
  target.textContent='Working… A local model may take a minute. No transfer is being recorded.';
  try{if(!db)throw Error('Wait for the workspace to load.');await action();}
  catch(e){target.textContent=e.message;}
  finally{buttons.forEach(b=>b.disabled=false);}
}
$('#ask-form').addEventListener('submit',async e=>{e.preventDefault();await assistantAction(e.target,$('#ask-result'),async()=>{
  const r=await api('/api/ask',{question:$('#ai-question').value});
  $('#ask-result').innerHTML=`<p class="assistant-label">${esc(r.mode==='rag_ollama'?'RAG answer':'Retrieved excerpts (preview)')}</p><div class="answer-text">${esc(r.answer)}</div><p class="dialog-note">${esc(r.notice)}</p><h3>Evidence</h3>${sourceMarkup(r.sources)}`;
});});
$('#agent-form').addEventListener('submit',async e=>{e.preventDefault();syncAssistant();await assistantAction(e.target,$('#agent-result'),async()=>{
  const r=await api('/api/agent',{query:$('#query').value,quantity:Number($('#quantity').value),recipient:$('#recipient').value,radius:Number($('#radius').value),repair:$('#repair').checked,price:Number($('#agent-price').value),transport:Number($('#agent-transport').value),refurbishment:Number($('#agent-refurb').value)});
  const p=r.proposal;
  $('#agent-result').innerHTML=`<p class="assistant-label">${esc(r.notice)}</p><p>${esc(r.message)}</p>${p?`<h3>${esc(p.title)}</h3><p>${num(p.quantity)} units proposed · ${num(p.remaining_need)} still needed</p><p>${num(p.estimated_mass_reused_kg)} kg estimated reused mass<br>INR ${num(p.estimated_net_savings_inr)} estimated net savings</p><p class="dialog-note">Synthetic estimates. No stock reserved or transferred.</p><button type="button" class="primary" id="agent-review">Inspect and review proposal ↗</button>`:''}<h3>Tool activity</h3>${r.trace.map(t=>`<details><summary>${t.step}. ${esc(t.tool)}</summary><pre>${esc(JSON.stringify({arguments:t.arguments,observation:t.observation},null,2))}</pre></details>`).join('')}<h3>Retrieved guidance</h3>${sourceMarkup(r.sources)}`;
  if(p)$('#agent-review').addEventListener('click',()=>{
    const item=r.matches.find(m=>m.id===p.item_id);
    openTransfer({...item,recipient:p.recipient,requested:p.quantity,offered_quantity:p.quantity});
    $('#price').value=p.price;$('#transport').value=p.transport;$('#refurbishment').value=p.refurbishment;estimate();
  });
});});
