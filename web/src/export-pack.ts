import {zipSync,strToU8} from 'fflate';
import {makeBrief} from './briefing.ts';
import type {ActivityMonth} from './briefing.ts';
import type {AnalysisState} from './analysis-state.ts';
import {analysisLink} from './analysis-state.ts';

export function monthsBetween(start:string,end:string){
 if(!/^\d{4}-\d{2}-\d{2}$/.test(start)||!/^\d{4}-\d{2}-\d{2}$/.test(end)||start>end||start<'2003-01-01'||end>'2025-12-31'||new Date(start).toISOString().slice(0,10)!==start||new Date(end).toISOString().slice(0,10)!==end)throw Error('Choose valid dates from 2003 through 2025, with the start before the end.');
 const first=+start.slice(0,4)*12+(+start.slice(5,7)-1),last=+end.slice(0,4)*12+(+end.slice(5,7)-1);
 return Array.from({length:last-first+1},(_,i)=>`${Math.floor((first+i)/12)}-${String((first+i)%12+1).padStart(2,'0')}`);
}
export function filterPointCSV(text:string,bounds:number[],start:string,end:string){
 const lines=text.trim().split(/\r?\n/),header=lines.shift()!;
 if(header!=='latitude,longitude,acq_date,acq_time,satellite,confidence,frp,daynight,type,version')throw Error('Unexpected source schema; no partial export was produced.');
 return {header,rows:lines.filter(line=>{const f=line.split(',');return f.length===10&&+f[1]>=bounds[0]&&+f[1]<bounds[2]&&+f[0]>=bounds[1]&&+f[0]<bounds[3]&&f[2]>=start&&f[2]<=end;})};
}
const sourceIndex=(year:number)=>year<=2012?0:year<=2021?1:2;
export function analyticsCSV(data:ActivityMonth[],s:AnalysisState){
 const header='year,month,primary_sensor,filtered_detections,active_cell_days,aqua_equivalent_cell_days,reference_aqua_cell_days,west,south,east,north,baseline_median,baseline_p90,baseline_years,ratio,category,aqua_category,observation_completeness';
 const sensors=['aqua','snpp','noaa20'];
 return [header,...data.filter(d=>d.year>=s.from&&d.year<=s.to).map(d=>{const i=sourceIndex(d.year),b=makeBrief(data,d.year,d.month);return [d.year,d.month,sensors[i],d.raw[i],d.active[i],d.adjusted[i].toFixed(6),d.active[0],...s.bbox,b.median,b.p90,b.baselineYears,b.ratio??'',b.adjustedClass,b.referenceClass,'unknown'].join(',');})].join('\n');
}
export async function evidencePack(data:ActivityMonth[],state:AnalysisState,region:string,base:string,href:string){
 const s={...state,bbox:[...state.bbox]};
 const files:Record<string,Uint8Array>={};
 files['monthly-analytics.csv']=strToU8(analyticsCSV(data,s));
 const chosen=data.filter(d=>d.year>=s.from&&d.year<=s.to),value=(d:ActivityMonth)=>s.mode==='raw'?d.raw[sourceIndex(d.year)]:s.mode==='unadjusted'?d.active[sourceIndex(d.year)]:d.adjusted[sourceIndex(d.year)];
 const max=Math.max(1,...chosen.map(value)),palette=['#f3e9cb','#ebce8e','#dfa45a','#cc743c','#ac492b','#793222'],height=(s.to-s.from+1)*25+150;
 const escape=(t:string)=>t.replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]!));
 const unit=s.mode==='raw'?'Filtered hotspot detections':s.mode==='unadjusted'?'Occupied 1 km cell-days':'Estimated Aqua-equivalent cell-days';
 const labels=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
 let svg=`<svg xmlns="http://www.w3.org/2000/svg" width="820" height="${height}" role="img" aria-label="Exported burning activity calendar"><rect width="820" height="${height}" fill="#f7f7ef"/><g font-family="Arial,sans-serif" fill="#203638"><text x="25" y="28" font-size="18">${escape(region)} · ${s.from}–${s.to}</text><text x="25" y="50" font-size="11">${unit} · logarithmic colors · NASA FIRMS</text>`;
 labels.forEach((m,i)=>svg+=`<text x="${80+i*57}" y="75" font-size="11">${m}</text>`);
 for(const d of chosen){const x=75+(d.month-1)*57,y=86+(d.year-s.from)*25,v=value(d),fill=v?palette[Math.min(5,Math.floor(Math.log1p(v)/Math.log1p(max)*6))]:'#eef0e9';if(d.month===1)svg+=`<text x="25" y="${y+14}" font-size="11">${d.year}</text>`;svg+=`<rect x="${x}" y="${y}" width="50" height="19" fill="${fill}"><title>${labels[d.month-1]} ${d.year}: ${v.toFixed(2)}</title></rect>`;}
 svg+=`<text x="25" y="${height-30}" font-size="10">Hotspots are not distinct fires. Observation completeness unknown. Known 2020 outage affects interpretation.</text><text x="25" y="${height-13}" font-size="10">Read analysis.json and provenance/ for effective area, baseline, model and source identity.</text></g></svg>`;
 files['calendar.svg']=strToU8(svg);

 const selected=makeBrief(data,s.year,s.month);
 const sourceFiles=['metadata.json','sources.json','method.md','input_audit.json'];
 for(const name of sourceFiles){const r=await fetch(base+name);if(!r.ok)throw Error('Could not load source evidence: '+name);files['provenance/'+name]=new Uint8Array(await r.arrayBuffer());}
 const pointName=`detections/${s.year}-${String(s.month).padStart(2,'0')}.csv.gz`;
 const response=await fetch(base+pointName);if(!response.ok||!response.body)throw Error('Selected-month observations unavailable');
 const text=await new Response(response.body.pipeThrough(new DecompressionStream('gzip'))).text();
 const points=filterPointCSV(text,s.bbox,`${s.year}-${String(s.month).padStart(2,'0')}-01`,`${s.year}-${String(s.month).padStart(2,'0')}-31`);
 files['selected-month-hotspots.csv']=strToU8([points.header,...points.rows].join('\n'));
 const payload={schema:'fire-continuum-analysis-pack-v1',created_utc:new Date().toISOString(),area:region,state:s,reopen:analysisLink(href,s),selected_month:selected,point_export:{scope:'selected month only; filtered original primary-platform detections',rows:points.rows.length},analytics_scope:'full selected calendar-year range',units:{raw:'retained thermal-anomaly pixel detections',active:'occupied 1 km cells per UTC day',adjusted:'estimated Aqua-equivalent occupied cell-days'},limits:['Not distinct fires, burned area, danger or forecast.','Observation completeness unknown. No detections do not establish no fire.','Effective AOI is snapped outward to 0.25 degrees, within Indonesia.','Known Aqua archive outage 16 August–2 September 2020.','Regional calibration is exploratory for arbitrary small AOIs.','Independent case imagery does not automatically validate this selected area.']};
 files['analysis.json']=strToU8(JSON.stringify(payload,null,2));
 files['README.txt']=strToU8(`FIRE CONTINUUM / REPRODUCIBLE ANALYSIS PACK\n\n${region}\nCalendar: ${s.from}–${s.to}; selected month: ${s.year}-${String(s.month).padStart(2,'0')}\n\nmonthly-analytics.csv covers the selected year range. selected-month-hotspots.csv contains only the selected month's original primary-platform observations. For other dates, use the app's explicit observation-date export.\n\nRead analysis.json for effective bounds, units, baseline, finding and limitations. provenance/ includes the frozen model, source manifest and full method. SHA256.json verifies the exact files in this pack, not scientific accuracy.\n\nReopen: ${payload.reopen}\n\nNASA LANCE FIRMS / ESDIS. NASA does not endorse this project. No operational fire warning.\n`);
 const hashes:Record<string,string>={};for(const [name,bytes] of Object.entries(files)){const digest=await crypto.subtle.digest('SHA-256',bytes as BufferSource);hashes[name]=Array.from(new Uint8Array(digest)).map(b=>b.toString(16).padStart(2,'0')).join('');}
 files['SHA256.json']=strToU8(JSON.stringify(hashes,null,2));
 return zipSync(files,{level:6});
}
