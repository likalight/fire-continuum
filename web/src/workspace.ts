import type {ActivityMonth} from './briefing';

export const evidenceTopics=[
 ['opening','Why satellites disagree','See what changes when the same observations are put on a comparable scale.','Start with the idea'],
 ['case-study','Does the seasonal finding survive?','Try six processing choices for the documented Borneo episode.','Case and sensitivity'],
 ['decision-benchmark','Does the method preserve the conclusion?','Compare a simple baseline with the released method, including rare-category failures.','710 region-month comparisons'],
 ['transfer-cases','Does it work somewhere else?','Inspect separate frozen-transfer and local-calibration tests in India and Australia.','Two contrasting regions'],
 ['imagery-audit','What did the first imagery audit find?','All six fixed candidate/comparison reviews remain inconclusive.','All outcomes retained'],
 ['observation-context','Could the satellite see the ground?','Inspect cloud, non-fire, fire and unavailable daily observations.','167 daily layers + 17 gaps'],
 ['time-comparison','Can observation time explain the gap?','Read the matching experiment, including the estimates that lacked support.','An unresolved result'],
 ['stress-evidence','Where does calibration fail?','Examine excluded years, unseen regions and empirical uncertainty ranges.','Limits and failure cases'],
 ['evidence','How are the records connected?','Follow the common grid, overlap ratios and tests on later years.','Reproducible method'],
 ['decision-briefing','What should an analyst investigate?','Four questions, explicit review candidates and a downloadable case brief.','Decision support'],
 ['season-planner','When is the usual peak?','Inspect the seasonal window and sensitivity to leaving out historical years.','Historical context, not forecast'],
] as const;

export function recordHighlights(data:ActivityMonth[],from:number,to:number){
 const rows=data.filter(d=>d.year>=from&&d.year<=to);
 const source=(y:number)=>y<=2012?0:y<=2021?1:2;
 const valid=rows.filter(d=>!(d.year===2020&&(d.month===8||d.month===9)));
 const ranked=[...valid].sort((a,b)=>b.adjusted[source(b.year)]-a.adjusted[source(a.year)]||a.year-b.year||a.month-b.month);
 const years=Array.from(new Set(rows.map(d=>d.year))).filter(y=>y!==2020&&new Set(rows.filter(d=>d.year===y).map(d=>d.month)).size===12).map(year=>({year,total:rows.filter(d=>d.year===year).reduce((s,d)=>s+d.adjusted[source(year)],0)})).sort((a,b)=>b.total-a.total||a.year-b.year);
 return {month:ranked[0]??null,year:years[0]??null,months:rows.length,excluded:rows.length-valid.length};
}

const glossary=[
 ['Hotspot','A satellite pixel classified as a thermal anomaly. One fire can create many detections; some hotspots come from industrial or volcanic sources.'],
 ['Activity unit (cell-day)','One 1 km grid cell with at least one retained detection on one UTC day. Repeated detections in that cell on that day count once. It is not a fire count or burned area.'],
 ['Comparable activity / harmonization','An estimate that converts VIIRS occupied cell-days onto the historical MODIS Aqua scale using overlap-period ratios. Original detections remain separately downloadable.'],
 ['Typical / median','The middle historical value for the same calendar month or exact dates. The baseline uses Aqua observations from 2003–2017, excluding a target year when it belongs to that baseline.'],
 ['Above typical','Higher than the historical median. This alone is not proof of an emergency, significance, severity or damage.'],
 ['Unusually high / p90','Above the historical 90th percentile: a descriptive upper-tail category. It is not a 90% confidence level or a fire probability.'],
 ['Independent imagery','Another instrument provides a separate view of the event. Same-place, same-date corroboration can support the presence of burning, but cannot by itself validate aggregate counts or an anomaly.'],
 ['QA / quality flags','Product flags describing conditions such as cloud, missing pixels or saturation. Passing QA is not a guarantee that haze or other ambiguity is absent.'],
 ['NRT / near-real-time','A rapid preliminary product. It may differ from the later standard archive, and its retrieval date must remain visible.'],
 ['WAPE','Sum of absolute differences from Aqua, divided by total Aqua activity. Lower means better aggregate count agreement, not better detection of every fire or every rare month.'],
 ['Held-out / excluded year','A year not used to fit the coefficients being evaluated. This checks whether fitting transfers to another time period.'],
 ['Coverage unknown','The available files do not establish how often every location was observable. No detections must not be interpreted as no fire.']
];

export function learningMarkup(){return `<div class="workspace-intro"><p class="eyebrow">EVIDENCE LIBRARY</p><h1>Every claim has a trail.</h1><p>Choose a question. Open the result, its assumptions and the files needed to reproduce it.</p></div><div class="library-tools"><label>Find a topic<input id="evidence-search" type="search" placeholder="Try clouds, calibration or regions"></label><a class="text-link" href="./submission/technical-handbook.html">Read the technical handbook ↗</a><a class="text-link" href="./submission/challenge-coverage.html">Challenge requirements ↗</a></div><div class="evidence-directory">${evidenceTopics.map(([id,title,desc,tag],i)=>`<a class="evidence-entry" href="#${id}" data-topic="${(title+' '+desc+' '+tag).toLowerCase()}"><span class="entry-number">${String(i+1).padStart(2,'0')}</span><div><small>${tag}</small><h2>${title}</h2><p>${desc}</p></div><span aria-hidden="true">↗</span></a>`).join('')}</div><p id="evidence-search-status" role="status"></p>`;}

export function glossaryMarkup(){return `<dialog id="glossary"><div class="dialog-top"><p class="eyebrow">A PLAIN-LANGUAGE FIELD GUIDE</p><button id="close-glossary" class="ghost">Close ×</button></div><h2>What does that mean?</h2><p>Start with “hotspot,” “activity unit” and “typical.” The rest is here when you need it.</p><label>Find a term<input id="glossary-search" type="search" placeholder="e.g. p90, uncertainty, NRT"></label><dl>${glossary.map(([term,meaning])=>`<div data-term="${(term+' '+meaning).toLowerCase()}"><dt>${term}</dt><dd>${meaning}</dd></div>`).join('')}</dl><p id="glossary-status" role="status"></p><a href="./submission/technical-handbook.html">Open the full technical handbook ↗</a></dialog>`;}

export function mountWorkspace(onView:()=>void){
 const main=document.querySelector('main')!;
 const footer=main.querySelector('footer')!;
 const sections=Array.from(main.children).filter(e=>e!==footer);
 const shell=document.createElement('div');shell.className='workspace-shell';
 shell.innerHTML=`<nav class="workspace-nav" aria-label="Workspace"><a href="#start" data-view="story"><b>01</b> The story</a><a href="#explore" data-view="explore"><b>02</b> Explore the calendar</a><a href="#current" data-view="current"><b>03</b> Current comparison</a><a href="#evidence-hub" data-view="evidence"><b>04</b> Evidence & methods</a></nav><div id="workspace-story" class="workspace-pane"></div><div id="workspace-explore" class="workspace-pane"></div><div id="workspace-current" class="workspace-pane"><div id="current" class="workspace-intro"><p class="eyebrow">COMPARE LIKE DATES</p><h1>How does the recent period compare?</h1><p>A dated snapshot, compared with the same UTC dates in past years. Provisional observations are kept separate from the completed archive.</p><p class="current-area">Uses the area selected in the <a href="#explore">calendar</a>. Changing the area updates the comparison.</p></div><section id="month-to-date"></section></div><div id="workspace-evidence" class="workspace-pane"><div id="evidence-hub">${learningMarkup()}</div><div class="evidence-breadcrumb" hidden><a href="#evidence-hub">← All evidence questions</a><span id="evidence-current-title"></span><button class="link-button" data-glossary>Explain the terms</button></div><div id="evidence-content"></div></div>`;
 main.insertBefore(shell,footer);
 const pane=(name:string)=>document.getElementById('workspace-'+name)!;
 for(const element of sections){
  if(element.classList.contains('section-jumps')){element.remove();continue;}
  if(element.classList.contains('record-strip')){element.remove();continue;}
  if(element.id==='start'||element.id==='confirmed-case'){pane('story').append(element);}
  else if(element.id==='explore'){pane('explore').append(element);}
  else if(element.id==='recent-comparison'||element.classList.contains('recent-section')){pane('current').append(element);}
  else {document.getElementById('evidence-content')!.append(element);}
 }
 const prior=document.createElement('details');prior.className='earlier-window';prior.innerHTML='<summary>Earlier November 8–12 comparison and correction experiments</summary>';pane('current').append(prior);for(const section of Array.from(pane('current').querySelectorAll('#recent-comparison,.recent-section')))prior.append(section);
 // Move the seasonal window into the calendar view only when directly requested through its route.
 document.body.insertAdjacentHTML('beforeend',glossaryMarkup());
 const dialog=document.getElementById('glossary') as HTMLDialogElement;
 document.getElementById('close-glossary')!.onclick=()=>dialog.close();
 dialog.addEventListener('click',e=>{if(e.target===dialog)dialog.close();});
 document.addEventListener('click',e=>{if((e.target as HTMLElement).closest('[data-glossary]'))dialog.showModal();});
 (document.getElementById('glossary-search') as HTMLInputElement).oninput=e=>{
  const q=(e.target as HTMLInputElement).value.toLowerCase().trim();let count=0;
  dialog.querySelectorAll<HTMLElement>('[data-term]').forEach(el=>{el.hidden=!el.dataset.term!.includes(q);if(!el.hidden)count++;});
  document.getElementById('glossary-status')!.textContent=count?`${count} terms`:'No matching term. Try “hotspot” or “typical”.';
 };
 (document.getElementById('evidence-search') as HTMLInputElement).oninput=e=>{
  const q=(e.target as HTMLInputElement).value.toLowerCase().trim();let count=0;
  main.querySelectorAll<HTMLElement>('[data-topic]').forEach(el=>{el.hidden=!el.dataset.topic!.includes(q);if(!el.hidden)count++;});
  document.getElementById('evidence-search-status')!.textContent=count?`${count} evidence topics`:'No matching topic. Try “cloud” or “method”.';
 };
 let active='';
 function navigate(id:string,scroll=true){
  const target=document.getElementById(id||'start');if(!target)return;
  let view=target.closest('.workspace-pane')?.id.replace('workspace-','');
  if(!view)return;
  for(const key of ['story','explore','current','evidence'])pane(key).hidden=key!==view;
  shell.querySelectorAll<HTMLElement>('[data-view]').forEach(el=>{if(el.dataset.view===view)el.setAttribute('aria-current','page');else el.removeAttribute('aria-current');});
  const evidence=document.getElementById('evidence-content')!;
  const selected=Array.from(evidence.children).find(el=>el===target||el.contains(target));
  document.getElementById('evidence-hub')!.hidden=view==='evidence'&&!!selected;
  (shell.querySelector('.evidence-breadcrumb') as HTMLElement).hidden=view!=='evidence'||!selected;
  for(const child of Array.from(evidence.children))(child as HTMLElement).hidden=child!==selected;
  document.getElementById('evidence-current-title')!.textContent=evidenceTopics.find(t=>t[0]===selected?.id)?.[1]||'';
  if(active!==view){active=view;onView();}
  let parent=target.parentElement;while(parent){if(parent.tagName==='DETAILS')(parent as HTMLDetailsElement).open=true;parent=parent.parentElement;}
  if(scroll){target.scrollIntoView({block:'start',behavior:'instant'});target.setAttribute('tabindex','-1');target.focus({preventScroll:true});}
 }
 document.addEventListener('click',e=>{
  const a=(e.target as HTMLElement).closest<HTMLAnchorElement>('a[href^="#"]');if(!a)return;
  const id=a.getAttribute('href')!.slice(1)||'start';if(!document.getElementById(id))return;
  e.preventDefault();history.pushState(null,'','#'+id);navigate(id);
 });
 window.addEventListener('popstate',()=>navigate(location.hash.slice(1)||'start'));
 window.addEventListener('hashchange',()=>navigate(location.hash.slice(1)||'start'));
 navigate(location.hash.slice(1)||(location.search?'explore':'start'),false);
 if(location.hash)requestAnimationFrame(()=>navigate(location.hash.slice(1),true));
 return (id:string)=>{history.replaceState(null,'','#'+id);navigate(id);};
}

