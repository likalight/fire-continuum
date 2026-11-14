import {quantile,classify,monthNames} from './geography.ts';
export type BriefRow={year:number;month?:number;aqua:number;noaa20:number|null;raw_aqua:number;raw_noaa20:number|null;adjusted:number|null};
export type PlaceBrief={id:string;name:string;primary_policy:string;monthly:BriefRow[];recent:BriefRow[];recent_start:string;recent_end:string;validation:{status:string;wape:number|null;category_agreement:number|null};source_package_sha256:string;[key:string]:unknown};
export type Period={kind:'recent'|'history';year:number;month:number};
export function readBrief(p:PlaceBrief,period:Period){
 const recent=period.kind==='recent',year=recent?2026:period.year,month=recent?11:period.month;
 const rows=recent?p.recent:p.monthly.filter(x=>x.month===month),row=rows.find(x=>x.year===year);
 if(!row)throw Error('This period is not in the available record.');
 const samples=rows.filter(x=>x.year<=2017&&x.year!==year).map(x=>x.aqua),median=quantile(samples,.5),p90=quantile(samples,.9);
 const outage=!recent&&year===2020&&[8,9].includes(month),useNoaa=year>=2022&&p.primary_policy!=='aqua_only';
 const value=outage?null:useNoaa?row.adjusted:row.aqua,category=classify(value,median,p90);
 const aquaCategory=classify(outage?null:row.aqua,median,p90),candidateCategory=classify(row.adjusted,median,p90);
 const comparable=year>=2019&&aquaCategory!=='Insufficient baseline'&&candidateCategory!=='Insufficient baseline';
 const status=outage?'Known observation outage':!median||median<=0?'Insufficient historical baseline':p.validation.status==='insufficient_support'?'Calibration evidence insufficient':p.primary_policy==='aqua_only'?'Sensor adjustment failed checks':comparable&&aquaCategory!==candidateCategory?'Sensors give different answers':(recent||year===2026)?'Current-period accuracy unvalidated':p.validation.status==='limited_event_evidence'?'Limited unusual-event evidence':'Historical agreement checks passed';
 const season=monthNames.map((_,i)=>quantile(p.monthly.filter(x=>x.year<=2017&&x.year!==year&&x.month===i+1).map(x=>x.aqua),.5)??0),sums=season.map((_,i)=>season[i]+season[(i+1)%12]+season[(i+2)%12]);
 const peak=sums.indexOf(Math.max(...sums));
 return {row,rows,year,month,median,p90,samples:samples.length,value,ratio:value!==null&&median!==null&&median>0?value/median:null,category,aquaCategory,candidateCategory,status,comparable,outage,season,peak:Math.max(...sums)>0?[peak,(peak+1)%12,(peak+2)%12].map(i=>monthNames[i]).join('–'):'No seasonal peak established',period:recent?'1–13 November 2026':monthNames[month-1]+' '+year,source:useNoaa?'Adjusted NOAA-20':'Aqua',scope:recent?'Exactly November 1–13 UTC in every comparison year. NRT processing; observation completeness unknown.':year===2026?'Complete October 2026 NRT window; other months may be unavailable. Observation completeness unknown.':'Whole calendar months. Observation completeness unknown.'};
}
export type Task='recent'|'sensors'|'save'|'briefing'|'compare'|'story';
export function taskIntent(q:string):Task|null{
 const s=q.trim().toLowerCase();if(/\b(not|don't|do not|never|avoid|why|how|what)\b/.test(s))return null;
 if(/^(compare|show|open|take me to)\b/.test(s)&&/\b(november|latest|recent|current)\b/.test(s))return 'recent';
 if(/^(compare|show|explain|open)\b/.test(s)&&/\b(sensor|sensors|satellites)\b/.test(s))return 'sensors';
 if(/^(save|remember|bookmark)\b/.test(s)&&/\b(place|region|country)\b/.test(s))return 'save';
 if(/^(make|create|download|export)\b/.test(s)&&/\b(brief|briefing|report)\b/.test(s))return 'briefing';
 if(/^compare\b/.test(s)&&/\b(places|countries|saved)\b/.test(s))return 'compare';
 if(/^(show|open|follow)\b/.test(s)&&/\b(story|fire|event)\b/.test(s))return 'story';
 return null;
}
export function savedPlaces(raw:string|null,allowed:Set<string>):string[]{
 try{const data=JSON.parse(raw??'[]');return Array.isArray(data)?[...new Set(data.filter(x=>typeof x==='string'&&allowed.has(x)))].slice(0,6):[];}catch{return [];}
}
