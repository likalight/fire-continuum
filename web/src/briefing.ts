export type ActivityMonth={year:number;month:number;raw:number[];active:number[];adjusted:number[]};
export function quantile(values:number[],p:number):number{
  if(!values.length)throw Error('A baseline requires observations');
  const a=[...values].sort((x,y)=>x-y),i=(a.length-1)*p,lo=Math.floor(i),hi=Math.ceil(i);
  return a[lo]+(a[hi]-a[lo])*(i-lo);
}
export function category(value:number,median:number,p90:number):string{
  if(median<=0)return 'Insufficient baseline';
  return value>p90?'Unusually high':value>median?'Above typical':'At or below typical';
}
export function makeBrief(data:ActivityMonth[],year:number,month:number){
  const item=data.find(d=>d.year===year&&d.month===month);if(!item)throw Error('Selected month unavailable');
  const source=year<=2012?0:year<=2021?1:2;
  // A single-sensor reference baseline, excluding the selected year to avoid self-comparison.
  const history=data.filter(d=>d.year>=2003&&d.year<=2017&&d.year!==year);
  const baseline=history.filter(d=>d.month===month).map(d=>d.active[0]);
  const median=quantile(baseline,.5),p90=quantile(baseline,.9),p10=quantile(baseline,.1);
  const value=item.adjusted[source],aqua=item.active[0];
  const supported=baseline.length>=10&&median>0;
  const adjustedClass=supported?category(value,median,p90):'Insufficient baseline';
  const referenceClass=supported?category(aqua,median,p90):'Insufficient baseline';
  const rhythm=Array.from({length:12},(_,i)=>quantile(history.filter(d=>d.month===i+1).map(d=>d.active[0]),.5));
  let peak=0;for(let i=1;i<12;i++)if([0,1,2].reduce((a,k)=>a+rhythm[(i+k)%12],0)>[0,1,2].reduce((a,k)=>a+rhythm[(peak+k)%12],0))peak=i;
  return {year,month,source,value,aqua,median,p90,p10,baselineYears:baseline.length,adjustedClass,referenceClass,agreement:source===0||!supported?null:adjustedClass===referenceClass,ratio:supported?value/median:null,referenceRatio:supported?aqua/median:null,peakMonths:[peak,(peak+1)%12,(peak+2)%12],hasRhythm:rhythm.some(v=>v>0),rhythm,supported};
}
