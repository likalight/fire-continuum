import {quantile,makeBrief} from './briefing.ts';
import type {ActivityMonth} from './briefing.ts';
const months=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
function peak(values:number[]){let best=0;for(let i=1;i<12;i++)if([0,1,2].reduce((s,k)=>s+values[(i+k)%12],0)>[0,1,2].reduce((s,k)=>s+values[(best+k)%12],0))best=i;return best;}
export function seasonPlan(data:ActivityMonth[],excludeYear:number){
 const history=data.filter(d=>d.year>=2003&&d.year<=2017&&d.year!==excludeYear);
 const years=[...new Set(history.map(d=>d.year))];
 if(years.length<10||years.some(y=>new Set(history.filter(d=>d.year===y).map(d=>d.month)).size!==12))return null;
 const profile=(omit?:number)=>Array.from({length:12},(_,i)=>quantile(history.filter(d=>d.month===i+1&&d.year!==omit).map(d=>d.active[0]),.5));
 const rhythm=profile(),sum=rhythm.reduce((s,v)=>s+v,0);if(sum<=0)return null;
 const start=peak(rhythm),concentration=[0,1,2].reduce((s,k)=>s+rhythm[(start+k)%12],0)/sum;
 const omissions=years.map(year=>({year,peak:peak(profile(year))}));
 return {start,concentration,rhythm,years:years.length,stable:omissions.filter(o=>o.peak===start).length,omissions};
}
export function planningMarkup(data:ActivityMonth[],year:number,month:number){
 const p=seasonPlan(data,year),b=makeBrief(data,year,month);
 if(!p)return '<p>No stable seasonal reference can be described for this area. Missing observation coverage remains unknown.</p>';
 const peakLabel=[0,1,2].map(k=>months[(p.start+k)%12]).join(', ');
 return `<div class="section-heading"><div><p class="eyebrow">SEASON PLANNING / SELECTED AREA</p><h2>When has monitoring mattered most?</h2></div><p>A historical planning cue for a fire analyst. This does not predict future fire or prescribe a response.</p></div>
 <div class="planning-layout"><div><strong class="planning-peak">${peakLabel}</strong><p>The largest three-month sum contains <b>${(p.concentration*100).toFixed(0)}%</b> of the summed monthly medians.</p><p><b>${p.stable} of ${p.years}</b> leave-one-year-out checks keep this exact window. This measures sensitivity to the historical sample, not forecast confidence.</p></div>
 <ol class="decision-steps"><li><b>Plan the seasonal review</b><span>Use this window to organize historical comparisons and local preparedness discussions. Local conditions can differ.</span></li><li><b>Check the selected month</b><span>${months[month-1]} ${year}: ${b.adjustedClass.toLowerCase()}. ${b.agreement===false?'The sensor changes the category; investigate before interpreting the anomaly.':b.agreement===true?'Aqua and adjusted VIIRS share the category; inspect the count discrepancy separately.':'Aqua-only or insufficient comparison; no cross-sensor confirmation.'}</span></li><li><b>Resolve the evidence gap</b><span>Check cloud and observation timing, corroborate the event, then export the evidence. A quiet hotspot calendar alone does not establish quiet conditions on the ground.</span></li></ol></div>
 <details><summary>Seasonal sensitivity by omitted year</summary><div class="audit-scroll"><table><thead><tr><th>Omitted year</th><th>Largest three-month window</th></tr></thead><tbody>${p.omissions.map(o=>`<tr><td>${o.year}</td><td>${[0,1,2].map(k=>months[(o.peak+k)%12]).join(', ')}</td></tr>`).join('')}</tbody></table></div><p>Baseline: Aqua 2003–2017, excluding the selected year when applicable. Each check removes one additional year. Ties choose the earliest starting month; windows wrap across December. No cloud/overpass correction.</p></details>`;
}
