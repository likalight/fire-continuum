"""Chronological method selection, later audit, and candid model promotion gate."""
import gzip,json
from pathlib import Path
import numpy as np
import pandas as pd
from importlib import import_module
recent=import_module('09_recent_comparison')
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'web/public/data'
MODELS=['original','sector_refit','local_monthly','local_short','local_blend']
LABELS={'original':'Original sector / season','sector_refit':'Updated sector / season','local_monthly':'Local monthly / season','local_short':'Local five-day / season','local_blend':'Equal blend of local fits'}
REGIONS=recent.REGIONS;SELECTION=['sumatra','kalimantan','java','papua']

def ratio(d,reference='aqua',sensor='noaa20'):
    den=d[sensor].sum()
    if den<=0: raise ValueError('No training sensor support; do not invent a coefficient')
    return float(d[reference].sum()/den)

def fit_models(monthly,short,sector_monthly,original,first,last):
    local={};sectors={}
    for sec in range(3):
        for q in range(4):
            d=sector_monthly[sector_monthly.year.between(first,last)&sector_monthly.sector.eq(sec)&sector_monthly.quarter.eq(q)]
            sectors[(sec,q)]=ratio(d)
    for key in REGIONS:
        for q in range(4):
            a=monthly[monthly.region.eq(key)&monthly.year.between(first,last)&monthly.quarter.eq(q)]
            b=short[short.region.eq(key)&short.year.between(first,last)&short.quarter.eq(q)]
            fm,fs=ratio(a),ratio(b)
            local[(key,q)]={'local_monthly':fm,'local_short':fs,'local_blend':.5*(fm+fs)}
    return {'local':local,'sectors':sectors,'original':original,'years':[first,last]}

def predict(d,model,fit):
    if model=='original':return d.adjusted.to_numpy()
    if model=='sector_refit':
        return np.array([sum(getattr(r,f'n{s}')*fit['sectors'][(s,r.quarter)] for s in range(3)) for r in d.itertuples()])
    return np.array([r.noaa20*fit['local'][(r.region,r.quarter)][model] for r in d.itertuples()])

def evaluate(d,pred):
    y=d.aqua.to_numpy();den=y.sum()
    return {'windows':len(d),'wape':float(abs(pred-y).sum()/den) if den else None,'mae':float(abs(pred-y).mean()),'bias':float((pred-y).sum()/den) if den else None}

def macro(scores):return float(np.mean([scores[k]['all']['wape'] for k in SELECTION]))

def promotion(selected,base):
    improvement=1-macro(selected)/macro(base)
    degraded=[k for k in REGIONS if selected[k]['all']['wape']>1.2*base[k]['all']['wape']]
    november=selected['kalimantan']['same_dates']['wape']<=base['kalimantan']['same_dates']['wape']
    return {'promote':bool(improvement>=.1 and not degraded and november),'macro_improvement':improvement,'regions_degraded_more_than_20_percent':degraded,'kalimantan_same_dates_not_worse':november}

def main():
    raw=np.array(json.loads(gzip.decompress((OUT/'history.json.gz').read_bytes())))
    sparse=pd.DataFrame(raw,columns=['year','month','cx','cy','araw','sraw','nraw','aqua','snpp','noaa20'])
    monthly=[]
    for key,bbox in REGIONS.items():
        z=recent.select(sparse,bbox).groupby(['year','month'])[['aqua','noaa20']].sum().reindex(pd.MultiIndex.from_product([range(2019,2026),range(1,13)],names=['year','month']),fill_value=0).reset_index();z['region']=key;monthly.append(z)
    monthly=pd.concat(monthly);monthly['quarter']=(monthly.month-1)//3
    counts=pd.read_csv(ROOT/'reports/recent_window_counts.csv')
    short=counts.pivot(index=['region','year','month'],columns='sensor',values='active').reset_index()
    short=short.merge(counts[counts.sensor=='noaa20'][['region','year','month','adjusted']],on=['region','year','month'],how='left');short['quarter']=(short.month-1)//3
    # All 5-day windows require sector contributions for a fair updated-sector baseline.
    # Read only relevant 2019–2025 NOAA-20 points, using the same mask and deduplication.
    from pyproj import Transformer
    from shapely.geometry import shape
    from shapely.ops import unary_union
    from shapely import contains_xy
    boundary=json.loads((ROOT/'data/raw/boundary.geojson').read_text(encoding='utf-8'));polygon=unary_union([shape(f['geometry']) for f in boundary['features']]);project=Transformer.from_crs(4326,6933,always_xy=True)
    snapshot=json.loads((OUT/'recent.json').read_text(encoding='utf-8'));meta=json.loads((OUT/'recent-comparison.json').read_text(encoding='utf-8'));w=meta['window'];secl=[]
    for year in list(range(2019,2026))+[2026]:
        d=pd.read_csv(ROOT/f'data/raw/viirs-jpss1_{year}_Indonesia.csv',dtype={'confidence':str,'acq_time':str}) if year<2026 else pd.DataFrame([r for r in snapshot['records'] if r['sensor']=='noaa20'])
        dates=pd.to_datetime(d.acq_date);d['month']=dates.dt.month;d['day']=dates.dt.day
        d=d[d.day.between(w['start_day'],w['end_day'])&d.confidence.str.lower().isin(['n','h','nominal','high'])].copy();d=d[contains_xy(polygon,d.longitude.to_numpy(),d.latitude.to_numpy())].copy()
        d['acq_time']=d.acq_time.astype(str).str.zfill(4);d['cx']=np.floor(d.longitude/.25).astype(int);d['cy']=np.floor(d.latitude/.25).astype(int);d=recent.occupied(d,project);d['sector']=np.where(d.longitude<108,0,np.where(d.longitude<120,1,2))
        for key,bbox in REGIONS.items():
            z=recent.select(d,bbox)
            for month in ([w['month']] if year==2026 else range(1,13)):
                secl.append({'region':key,'year':year,'month':month,**{f'n{s}':int((z.month.eq(month)&z.sector.eq(s)).sum()) for s in range(3)}})
    short=short.merge(pd.DataFrame(secl),on=['region','year','month'],how='left')
    assert (short[short.year.ge(2019)].noaa20==short[short.year.ge(2019)][['n0','n1','n2']].sum(axis=1)).all()
    sec=pd.read_csv(ROOT/'reports/monthly_counts.csv').pivot(index=['year','month','sector'],columns='sensor',values='active').reset_index();sec['quarter']=(sec.month-1)//3
    original=json.loads((OUT/'metadata.json').read_text(encoding='utf-8'))['factors']['noaa20']
    devfit=fit_models(monthly,short,sec,original,2019,2021)
    auditfit=fit_models(monthly,short,sec,original,2019,2023)
    def phase(first,last,fit):
        result={}
        for model in MODELS:
            regions={}
            for key in REGIONS:
                d=short[short.region.eq(key)&short.year.between(first,last)].copy();d['pred']=predict(d,model,fit)
                same=d[d.month==w['month']];hist=short[short.region.eq(key)&short.year.between(2003,2017)].groupby('month').aqua.agg(median='median',p90=lambda x:x.quantile(.9))
                pairs=[{'year':int(r.year),'month':int(r.month),'aqua':int(r.aqua),'adjusted':float(r.pred),'aqua_category':recent.category(r.aqua,hist.loc[r.month,'median'],hist.loc[r.month,'p90']),'adjusted_category':recent.category(r.pred,hist.loc[r.month,'median'],hist.loc[r.month,'p90'])} for r in d.itertuples()]
                valid=[r for r in pairs if r['aqua_category']!='Insufficient baseline']
                regions[key]={'all':evaluate(d,d.pred.to_numpy()),'same_dates':evaluate(same,same.pred.to_numpy()),'category_agreement':{'agree':sum(r['aqua_category']==r['adjusted_category'] for r in valid),'eligible':len(valid)},'annual':[{'year':int(y),**evaluate(z,z.pred.to_numpy())} for y,z in d.groupby('year')],'pairs':pairs}
            result[model]={'regions':regions,'macro_wape':macro(regions)}
        return result
    dev=phase(2022,2023,devfit);selected=min(MODELS,key=lambda name:dev[name]['macro_wape'])
    audit=phase(2024,2025,auditfit);gate=promotion(audit[selected]['regions'],audit['original']['regions']);gate['selected']=selected
    current={}
    for key in REGIONS:
        d=short[short.region.eq(key)&short.year.eq(2026)];reference=float(d.aqua.iloc[0]);baseline=meta['regions'][key]['current'];models={}
        for model in MODELS:
            value=float(predict(d,model,auditfit)[0]);models[model]={'value':value,'relative_disagreement':abs(value-reference)/reference if reference else None,'category':recent.category(value,baseline['median'],baseline['p90']),'over_median':value/baseline['median'] if baseline['median'] else None}
        current[key]={'aqua':reference,'aqua_category':baseline['aqua_category'],'median':baseline['median'],'p90':baseline['p90'],'models':models}
    payload={'labels':LABELS,'window':w,'development':{'fit':[2019,2021],'selection':[2022,2023],'results':dev},'audit':{'fit':[2019,2023],'evaluation':[2024,2025],'results':audit},'gate':gate,'current':current,'local_factors':[{'region':k,'quarter':q,**v} for (k,q),v in auditfit['local'].items()],'sector_factors':[{'sector':s,'quarter':q,'factor':v} for (s,q),v in auditfit['sectors'].items()],'note':'Known historical and current original-model results. Method selection uses 2022–2023 only; audit and current results do not select a replacement. Original results and raw observations retained. No ground-truth, coverage or NRT processing validation.'}
    for path in [ROOT/'reports/correction-trials.json',OUT/'correction-trials.json']:path.write_text(json.dumps(payload,indent=2,allow_nan=False),encoding='utf-8')
    (OUT/'correction_protocol.json').write_bytes((ROOT/'reports/correction_protocol.json').read_bytes())
    print(json.dumps({'selection':{k:v['macro_wape'] for k,v in dev.items()},'audit':{k:v['macro_wape'] for k,v in audit.items()},'gate':gate,'kalimantan':current['kalimantan']},indent=2),flush=True)

if __name__=='__main__':main()
