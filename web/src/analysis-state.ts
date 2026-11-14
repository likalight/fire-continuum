export type AnalysisState={bbox:number[];year:number;month:number;from:number;to:number;mode:'adjusted'|'unadjusted'|'raw'};
export function parseState(search:string):AnalysisState|null{
 const p=new URLSearchParams(search);if(!p.has('area'))return null;
 const bbox=p.get('area')!.split(',').map(Number),year=Number(p.get('year')),month=Number(p.get('month')),from=Number(p.get('from')),to=Number(p.get('to')),mode=p.get('mode');
 if(bbox.length!==4||bbox.some(n=>!Number.isFinite(n)||!Number.isInteger(n*4))||bbox[0]<94||bbox[2]>142||bbox[1]<-12||bbox[3]>7||bbox[0]>=bbox[2]||bbox[1]>=bbox[3])return null;
 if(![year,month,from,to].every(Number.isInteger)||from<2003||to>2025||from>to||year<from||year>to||month<1||month>12||!['adjusted','unadjusted','raw'].includes(mode||''))return null;
 return {bbox,year,month,from,to,mode:mode as AnalysisState['mode']};
}
export function analysisLink(base:string,s:AnalysisState):string{
 const u=new URL(base);u.search=new URLSearchParams({area:s.bbox.join(','),year:String(s.year),month:String(s.month),from:String(s.from),to:String(s.to),mode:s.mode}).toString();u.hash='season-briefing';return u.href;
}
