export const statusInfo:Record<string,{label:string;color:string;detail:string}>={
 agreement_checks_passed:{label:'Agreement checks passed',color:'#37665c',detail:'Supported national calibration passed the frozen agreement and rare-month checks. This is agreement with Aqua, not ground truth.'},
 limited_event_evidence:{label:'Limited rare-event evidence',color:'#b19247',detail:'Count and category checks passed, but fewer than five unusually high reference months were tested.'},
 mixed_or_poor_agreement:{label:'Calibration failed checks',color:'#a75839',detail:'The candidate failed one or more agreement checks. The published history stays with Aqua for every year.'},
 insufficient_support:{label:'Insufficient calibration evidence',color:'#929b9d',detail:'Too little training or testing support for the full screening protocol. Unsupported coefficients are withheld; the history stays with Aqua.'}
};
export type CountryEntry={id:string;name:string;primary_policy:string;validation:{status:string;wape:number|null;category_agreement:number|null;reference_extreme_months:number;[key:string]:unknown};[key:string]:unknown};
export function filterCountries(countries:CountryEntry[],query:string,status:string){const q=query.trim().toLocaleLowerCase();return countries.filter(c=>(!q||c.name.toLocaleLowerCase().includes(q)||c.id.includes(q))&&(!status||c.validation.status===status));}
export function catalogCSV(countries:CountryEntry[]){const quote=(v:unknown)=>'"'+String(v??'').replaceAll('"','""')+'"';return [['country','status','primary_history','held_out_wape','category_agreement','rare_reference_months'],...countries.map(c=>[c.name,c.validation.status,c.primary_policy,c.validation.wape,c.validation.category_agreement,c.validation.reference_extreme_months])].map(r=>r.map(quote).join(',')).join('\n');}
export function wrapLongitude(lon:number){return ((lon+180)%360+360)%360-180;}
