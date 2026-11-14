import {readBrief} from './brief-core.ts';
import type {PlaceBrief,Period} from './brief-core.ts';
import {classify,quantile} from './geography.ts';

export function simpleAnswer(a:ReturnType<typeof readBrief>):string {
 if(a.outage)return 'We cannot compare this month.';
 if(a.ratio===null)return 'There is no usable comparison.';
 if(a.ratio===1)return 'At the usual level';
 const difference=Math.abs(a.ratio-1)*100;
 const amount=difference<0.1?'Less than 0.1%':difference<10?difference.toFixed(1)+'%':Math.round(difference).toLocaleString('en-GB')+'%';
 return `${amount} ${a.ratio>1?'above':'below'} usual`;
}

export function calendarCells(p:PlaceBrief){
 const rows=[];
 for(let year=2026;year>=2003;year--){
  const cells=[];
  for(let month=1;month<=12;month++){
   const partial=year===2026&&month===11;
   const period:Period={kind:partial?'recent':'history',year,month};
   const supplied=partial?p.recent.some(r=>r.year===2026):p.monthly.some(r=>r.year===year&&r.month===month);
   const a=supplied?readBrief(p,period):null;
   const tone=!a||a.ratio===null?'unknown':a.category==='Unusually high'?'high':a.ratio>1?'above':'lower';
   cells.push({year,month,partial,period,analysis:a,tone});
  }
  rows.push({year,cells});
 }
 return rows;
}

export function briefCSV(p:PlaceBrief,period:Period):string {
 const a=readBrief(p,period);
 const quote=(x:unknown)=>'"'+String(x??'').replaceAll('"','""')+'"';
 const header=['place','year','month','window','aqua_cell_days','noaa20_cell_days','adjusted_noaa20_cell_days','displayed_cell_days','displayed_source','baseline_median','ratio_to_baseline','category','observation_coverage','known_outage','baseline_years','primary_policy','historical_package_sha256','extra_source_receipts'];
 return [header,...a.rows.map(r=>{
  const rowPeriod:Period=period.kind==='recent'?period:{kind:'history',year:r.year,month:a.month};
  // readBrief recent selects 2026, so compute each historical comparison explicitly here.
  const outage=period.kind==='history'&&r.year===2020&&[8,9].includes(a.month);
  const adjusted=r.year>=2022&&p.primary_policy!=='aqua_only';
  const value=outage?null:adjusted?r.adjusted:r.aqua;
  const baseline=a.rows.filter(x=>x.year<=2017&&x.year!==r.year).map(x=>x.aqua),median=quantile(baseline,.5),p90=quantile(baseline,.9);
  const ratio=value!==null&&median!==null&&median>0?value/median:null;
  return [p.name,r.year,a.month,period.kind==='recent'?'November 1–13 UTC':'full calendar month',r.aqua,r.noaa20,r.adjusted,value,adjusted?'Adjusted NOAA-20':'Aqua',median,ratio,classify(value,median,p90),'unknown',outage,'2003–2017; row year '+r.year+' excluded',p.primary_policy,p.source_package_sha256,r.year===2026&&rowPeriod.kind==='history'?'https://likalight.github.io/fire-continuum/data/october-transfer.json':''];
 })].map(row=>row.map(quote).join(',')).join('\r\n');
}
