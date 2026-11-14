"""Additional predeclared diagnostics. Keep temporal/spatial/ground evidence distinct."""
import gzip,json,math
from pathlib import Path
import numpy as np
import pandas as pd
from harmonize import metrics
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'web/public/data'
REGIONS=json.loads((ROOT/'reports/validation_protocol_v2.json').read_text())['regions']
def select(d,b):
    w,s,e,n=b
    return d.lon.ge(w)&d.lon.lt(e)&d.lat.ge(s)&d.lat.lt(n)
def fit(d,sensor):
    out={};fallback=0
    for sec in range(3):
        for q in range(4):
            z=d[(d.sector==sec)&(d.quarter==q)]
            if z[sensor].sum()==0:z=d[d.quarter==q];fallback+=1
            if z[sensor].sum()==0:raise ValueError('No training support')
            out[(sec,q)]=float(z.aqua.sum()/z[sensor].sum())
    return out,fallback
def predict(d,sensor,f):return d[sensor].to_numpy()*np.array([f[(s,q)] for s,q in zip(d.sector,d.quarter)])
def monthly(d,sensor,f):
    z=d.copy();z['pred']=predict(z,sensor,f)
    return z.groupby(['year','month'])[['aqua',sensor,'pred']].sum().reset_index()
def finite_quantile(scores,alpha=.1):
    a=np.sort(np.asarray(scores,float));rank=math.ceil((len(a)+1)*(1-alpha))
    if rank>len(a):return None
    return float(a[rank-1])
def range_check(z,calyears,testyears):
    cal=z[z.year.between(*calyears)];test=z[z.year.between(*testyears)]
    q=finite_quantile(abs(cal.aqua-cal.pred)/(cal.pred+1))
    assert q is not None
    width=q*(test.pred+1);lo=np.maximum(0,test.pred-width);hi=test.pred+width
    coverage=float(((test.aqua>=lo)&(test.aqua<=hi)).mean())
    return {'nominal':.9,'calibration_years':calyears,'evaluation_years':testyears,'calibration_months':len(cal),'evaluation_months':len(test),'q':q,'observed_reference_coverage':coverage,'mean_interval_width':float((hi-lo).mean()),'mean_reference':float(test.aqua.mean()),'limitation':'Empirical conversion-error range against Aqua; serial dependence and limited years prevent an unconditional 90% guarantee.'}
def main():
    r=json.loads(gzip.decompress((OUT/'history.json.gz').read_bytes()))
    d=pd.DataFrame(r,columns=['year','month','cx','cy','raw_aqua','raw_snpp','raw_noaa20','aqua','snpp','noaa20'])
    d['lon']=(d.cx+.5)*.25;d['lat']=(d.cy+.5)*.25;d['sector']=np.where(d.lon<108,0,np.where(d.lon<120,1,2));d['quarter']=(d.month-1)//3
    meta=json.loads((OUT/'metadata.json').read_text());result={'protocol':'validation_protocol_v2.json','sensors':{}};rng=np.random.default_rng(20261114)
    for sensor in ['snpp','noaa20']:
        spec=meta['validation'][sensor];tr=spec['train_years'];te=spec['test_years'];f={(v['sector'],v['quarter']):v['factor'] for v in meta['factors'][sensor]}
        z=monthly(d[d.year.between(*te)],sensor,f);train=monthly(d[d.year.between(*tr)],sensor,f)
        q25,q75=np.quantile(train.aqua,[.25,.75]);strata={}
        for label,mask in [('quiet',z.aqua<=q25),('middle',(z.aqua>q25)&(z.aqua<=q75)),('high',z.aqua>q75)]:
            u=z[mask];strata[label]=metrics(u.aqua,u.pred) if len(u) else None
        boot=[];years=z.year.unique()
        for _ in range(2000):
            sample=pd.concat([z[z.year==y] for y in rng.choice(years,len(years),replace=True)])
            boot.append(float(abs(sample.pred-sample.aqua).sum()/sample.aqua.sum()))
        spatial=[];local={}
        for name,b in REGIONS.items():
            inside=select(d,b);excluded=d[d.year.between(*tr)&~inside];sf,fb=fit(excluded,sensor)
            held=monthly(d[d.year.between(*te)&inside],sensor,sf)
            spatial.append({'region':name,'bbox':b,'months':len(held),'fallback_sector_quarters':fb,'after':metrics(held.aqua,held.pred)})
            allmonths=monthly(d[d.year.between(*te)&inside],sensor,f)
            cal,ev=([2018,2021],[2022,2025]) if sensor=='snpp' else ([2022,2023],[2024,2025])
            local[name]={'bbox':b,'frozen_test':metrics(allmonths.aqua,allmonths.pred),'range':range_check(allmonths,cal,ev)}
        cal,ev=([2018,2021],[2022,2025]) if sensor=='snpp' else ([2022,2023],[2024,2025])
        rolling=[]
        first=2016 if sensor=='snpp' else 2022
        for year in range(first,2026):
            rf,_=fit(d[d.year.between(year-3,year-1)],sensor);zz=monthly(d[d.year==year],sensor,rf)
            rolling.append({'year':year,'train_years':[year-3,year-1],**metrics(zz.aqua,zz.pred)})
        result['sensors'][sensor]={'test_years':te,'annual':[{'year':int(y),**metrics(a.aqua,a.pred)} for y,a in z.groupby('year')],'activity_thresholds':{'training_q25':q25,'training_q75':q75},'strata':strata,'year_block_bootstrap_wape_95':np.quantile(boot,[.025,.975]).tolist(),'bootstrap_note':'Resampled whole test years; sampling variation of WAPE, not per-month prediction intervals.','spatial_holdouts':spatial,'empirical_range':range_check(z,cal,ev),'regions':local,'rolling_three_year_fit':rolling}
    # Case fixed in the protocol before this computation; no selecting by the strongest anomaly.
    case=d[select(d,REGIONS['kalimantan'])];series=case.groupby(['year','month'])[['aqua','snpp','noaa20']].sum().reset_index()
    factors={(v['sector'],v['quarter']):v['factor'] for v in meta['factors']['snpp']}
    estimated=monthly(case,'snpp',factors);series['snpp_adjusted']=estimated.pred
    samples=[]
    for year in [2019,2020]:
        a=series[(series.year==year)&(series.month==9)].iloc[0];baseline=series[(series.year.between(2003,2017))&(series.month==9)].aqua
        samples.append({'year':year,'month':9,'aqua':int(a.aqua),'snpp':int(a.snpp),'adjusted':float(a.snpp_adjusted),'baseline_median':float(baseline.median()),'baseline_p90':float(baseline.quantile(.9)),'adjusted_over_median':float(a.snpp_adjusted/baseline.median()),'aqua_over_median':float(a.aqua/baseline.median()),'adjusted_above_p90':bool(a.snpp_adjusted>baseline.quantile(.9)),'aqua_above_p90':bool(a.aqua>baseline.quantile(.9))})
    result['case']={'region':'Kalimantan study rectangle','bbox':REGIONS['kalimantan'],'sensor':'snpp','training_years':[2013,2017],'samples':samples,'monthly':series[series.year.isin([2019,2020])].to_dict('records'),'evidence_status':'Event corroboration from separate Landsat instrument; not independent validation of aggregate counts.'}
    payload=json.dumps(result,indent=2,allow_nan=False);(OUT/'robustness.json').write_text(payload);(ROOT/'reports/robustness.json').write_text(payload)
    for s,v in result['sensors'].items():print(s,'annual WAPE',[(x['year'],round(x['wape'],3)) for x in v['annual']],'spatial',[(x['region'],round(x['after']['wape'],3)) for x in v['spatial_holdouts']],'range',v['empirical_range']['observed_reference_coverage'],flush=True)
    print('Case',json.dumps(samples),flush=True)
if __name__=='__main__':main()
