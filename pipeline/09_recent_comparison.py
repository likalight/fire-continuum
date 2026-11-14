"""Frozen-model, date-matched NRT comparison with auditable short-window tests."""
import gzip, hashlib, json
from datetime import datetime, timedelta, timezone
from pathlib import Path
import numpy as np
import pandas as pd
from pyproj import Transformer
from shapely.geometry import shape
from shapely.ops import unary_union
from shapely import contains_xy
from harmonize import sector, quarter, metrics

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'web/public/data'
REGIONS = {'indonesia':[94,-12,142,7], 'sumatra':[95,-6,106,6], 'kalimantan':[108,-5,120,4.5], 'java':[105,-9,116,-5], 'papua':[130,-10,142,.5]}

def date_window(snapshot):
    retrieved = datetime.fromisoformat(snapshot['retrieved_utc'])
    start = max(datetime.fromisoformat(s['global_file_date_span'][0]).date() for s in snapshot['sources']) + timedelta(days=1)
    end = min(min(datetime.fromisoformat(s['global_file_date_span'][1]).date() for s in snapshot['sources']), (retrieved-timedelta(hours=24)).date()-timedelta(days=1))
    if start.month != end.month or start.year != end.year or (end-start).days < 2:
        raise ValueError('Need at least three settled dates in a single month; inspect source spans')
    return start, end

def category(value, median, p90):
    if median <= 0: return 'Insufficient baseline'
    return 'Unusually high' if value > p90 else 'Above typical' if value > median else 'At or below typical'

def select(d, bbox):
    x=(d.cx+.5)*.25; y=(d.cy+.5)*.25
    return d[x.ge(bbox[0]) & x.lt(bbox[2]) & y.ge(bbox[1]) & y.lt(bbox[3])]

def occupied(d, project):
    d=d.copy(); x,y=project.transform(d.longitude.to_numpy(),d.latitude.to_numpy())
    d['gx']=np.floor(x/1000).astype(int); d['gy']=np.floor(y/1000).astype(int)
    # Stable tie break makes historical/NRT row order irrelevant.
    return d.sort_values(['acq_time','longitude','latitude'],kind='stable').drop_duplicates(['acq_date','gx','gy'])

def score(z):
    a=metrics(z.aqua,z.adjusted); single=metrics(z.aqua,z.single)
    return {'windows':len(z),'wape':a['wape'],'mae':a['mae'],'relative_bias':a['relative_bias'],'single_factor_wape':single['wape']}

def main():
    snapshot=json.loads((OUT/'recent.json').read_text());start,end=date_window(snapshot)
    meta=json.loads((OUT/'metadata.json').read_text());factors={(f['sector'],f['quarter']):f['factor'] for f in meta['factors']['noaa20']}
    single=sum(f['reference_total'] for f in meta['factors']['noaa20'])/sum(f['sensor_total'] for f in meta['factors']['noaa20'])
    boundary_bytes=(ROOT/'data/raw/boundary.geojson').read_bytes();boundary=json.loads(boundary_bytes)
    polygon=unary_union([shape(f['geometry']) for f in boundary['features']]);project=Transformer.from_crs(4326,6933,always_xy=True)
    spatial=[];regional=[];audits=[]
    sources=json.loads((ROOT/'reports/source_manifest.json').read_text())
    inputs=[(s, int(s['filename'].split('_')[1]), 'aqua' if s['filename'].startswith('modis') else 'noaa20') for s in sources if s['filename'].startswith('modis') or (s['filename'].startswith('viirs-jpss1') and int(s['filename'].split('_')[1])>=2019)]
    assert len(inputs)==30, 'Expected 23 Aqua and 7 complete NOAA-20 archive years'
    for src,year,sensor in inputs+[(None,start.year,'aqua'),(None,start.year,'noaa20')]:
        if src:
            path=ROOT/'data/raw'/src['filename']; assert path.stat().st_size==int(src['size'])
            d=pd.read_csv(path,dtype={'acq_time':str,'confidence':str,'version':str})
            if sensor=='aqua': d=d[d.satellite.isin(['A','Aqua']) & (pd.to_numeric(d.confidence)>=30)]
            else: d=d[d.confidence.str.lower().isin(['n','h','nominal','high'])]
        else:
            d=pd.DataFrame([r for r in snapshot['records'] if r['sensor']==sensor]);d['satellite']=sensor
        d=d.copy();d['acq_time']=d.acq_time.astype(str).str.zfill(4)
        dates=pd.to_datetime(d.acq_date);d['month']=dates.dt.month;d['day']=dates.dt.day
        d=d[d.day.between(start.day,end.day)]
        if not src: d=d[d.month.eq(start.month)]
        before=len(d);d=d[contains_xy(polygon,d.longitude.to_numpy(),d.latitude.to_numpy())].copy()
        d=d.drop_duplicates(['latitude','longitude','acq_date','acq_time','satellite'])
        d['cx']=np.floor(d.longitude/.25).astype(int);d['cy']=np.floor(d.latitude/.25).astype(int)
        u=occupied(d,project);u['adjusted']=1. if sensor=='aqua' else [factors[(int(s),int(q))] for s,q in zip(sector(u.longitude),quarter(u.month))]
        for key,bbox in REGIONS.items():
            r=select(d,bbox);a=select(u,bbox)
            for month in ([start.month] if not src else range(1,13)):
                sub=a[a.month==month]
                regional.append({'region':key,'year':year,'month':month,'sensor':sensor,'raw':int((r.month==month).sum()),'active':len(sub),'adjusted':float(sub.adjusted.sum())})
        r=d[d.month==start.month].groupby(['day','cx','cy']).size().rename('raw')
        a=u[u.month==start.month].groupby(['day','cx','cy']).agg(active=('gx','size'),adjusted=('adjusted','sum'))
        z=pd.concat([r,a],axis=1).fillna(0).reset_index();z['year']=year;z['sensor']=sensor;spatial.append(z)
        audits.append({'file':src['filename'] if src else 'recent.json:'+sensor,'year':year,'sensor':sensor,'selected_dates_before_mask':before,'retained_detections':len(d),'active_cell_days':len(u),'sha256':src.get('sha256') if src else hashlib.sha256((OUT/'recent.json').read_bytes()).hexdigest()})
        print('Matched dates:',sensor,year,len(d),flush=True)
    ledger=pd.DataFrame(regional);ledger.to_csv(ROOT/'reports/recent_window_counts.csv',index=False)
    detail=pd.concat(spatial,ignore_index=True)
    raw=detail.pivot(index=['year','day','cx','cy'],columns='sensor',values='raw').reindex(columns=['aqua','noaa20']).fillna(0)
    active=detail.pivot(index=['year','day','cx','cy'],columns='sensor',values='active').reindex(columns=['aqua','noaa20']).fillna(0)
    adjusted=detail.pivot(index=['year','day','cx','cy'],columns='sensor',values='adjusted').reindex(columns=['noaa20']).fillna(0)
    rows=np.column_stack([raw.index.to_frame(index=False).values,raw.values,active.values,adjusted.values]).tolist()
    reports={}
    for key,bbox in REGIONS.items():
        d=ledger[ledger.region==key]
        wide=d.pivot(index=['year','month'],columns='sensor',values='active').reset_index()
        pred=d[d.sensor=='noaa20'][['year','month','adjusted']];wide=wide.merge(pred,on=['year','month'],how='left');wide['single']=wide.noaa20*single
        test=wide[wide.year.between(2022,2025)].copy();matched=test[test.month==start.month].copy()
        baseline=wide[wide.year.between(2003,2017)].groupby('month').aqua.agg(median='median',p90=lambda x:x.quantile(.9))
        def comparisons(z):
            return [{'year':int(r.year),'month':int(r.month),'aqua':int(r.aqua),'noaa20':int(r.noaa20),'adjusted':float(r.adjusted),'aqua_category':category(r.aqua,baseline.loc[r.month,'median'],baseline.loc[r.month,'p90']),'adjusted_category':category(r.adjusted,baseline.loc[r.month,'median'],baseline.loc[r.month,'p90'])} for r in z.itertuples()]
        comp=comparisons(test);valid=[r for r in comp if r['aqua_category']!='Insufficient baseline']
        now=comparisons(wide[wide.year==start.year])[0]
        now['median']=float(baseline.loc[start.month,'median']);now['p90']=float(baseline.loc[start.month,'p90'])
        sd=select(detail,bbox);sensitivity=[]
        for omit in range(start.day,end.day+1):
            sub=sd[sd.day!=omit];aqua=sub[sub.sensor=='aqua'].groupby('year').active.sum().reindex(range(2003,2018),fill_value=0)
            med=float(aqua.median());p90=float(aqua.quantile(.9));n=sub[sub.year==start.year]
            sensitivity.append({'omitted_day':omit,'median':med,'p90':p90,'aqua_category':category(n[n.sensor=='aqua'].active.sum(),med,p90),'adjusted_category':category(n[n.sensor=='noaa20'].adjusted.sum(),med,p90)})
        reports[key]={'bbox':bbox,'all_month_windows':score(test),'same_calendar_dates':score(matched),'category_agreement':{'agree':sum(r['aqua_category']==r['adjusted_category'] for r in valid),'eligible':len(valid)},'matched_years':comparisons(matched),'current':now,'leave_one_day_out':sensitivity}
    payload={'window':{'start':str(start),'end':str(end),'days':(end-start).days+1,'month':start.month,'start_day':start.day,'end_day':end.day},'retrieved_utc':snapshot['retrieved_utc'],'baseline_years':[2003,2017],'historical_years':[2003,2025],'noaa20_historical_years':[2019,2025],'training_years':[2019,2021],'test_years':[2022,2025],'sources':snapshot['sources'],'snapshot_sha256':hashlib.sha256((OUT/'recent.json').read_bytes()).hexdigest(),'boundary_sha256':hashlib.sha256(boundary_bytes).hexdigest(),'regions':reports,'columns':['year','day','longitude_cell','latitude_cell','aqua_detections','noaa20_detections','aqua_cell_days','noaa20_cell_days','adjusted_noaa20_cell_days'],'limits':['Provisional NRT-to-standard comparison; processing continuity is unvalidated.','Complete UTC dates do not establish complete observations; no cloud or overpass denominator.','All thermal source types retained; occupied cell-days are not distinct fires or burned area.','Same mask applied to archive and recent points; archive country assignments may already exclude some coastal detections.','Frozen monthly-trained calibration tested on shorter windows; no per-window confidence interval.','Current inter-sensor agreement is not ground truth; four same-calendar held-out years provide limited evidence.','Missing 2026 dates outside this snapshot remain unavailable; this is not a full month or a live feed.']}
    (OUT/'recent-comparison.json').write_text(json.dumps(payload,indent=2,allow_nan=False))
    (ROOT/'reports/recent-comparison.json').write_text(json.dumps(payload,indent=2,allow_nan=False))
    (OUT/'recent-history.json.gz').write_bytes(gzip.compress(json.dumps(rows,separators=(',',':'),allow_nan=False).encode(),mtime=0))
    (ROOT/'reports/recent_input_audit.json').write_text(json.dumps(audits,indent=2))
    (OUT/'recent_protocol.json').write_bytes((ROOT/'reports/recent_protocol.json').read_bytes())
    print(json.dumps({'window':payload['window'],'regions':reports},indent=2),flush=True)

if __name__=='__main__': main()
