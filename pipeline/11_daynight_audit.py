"""Refresh audit plus official day/night attribution, with fixed later-year tests."""
import argparse,hashlib,io,json
from datetime import datetime,timezone
from pathlib import Path
from importlib import import_module
import numpy as np
import pandas as pd
import requests
from pyproj import Transformer
from shapely.geometry import shape
from shapely.ops import unary_union
from shapely import contains_xy
recent=import_module('09_recent_comparison');ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'web/public/data'

def key(d):
    return list(zip(d.latitude.round(6),d.longitude.round(6),d.acq_date,d.acq_time.astype(str).str.zfill(4)))

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--cached',action='store_true',help='Replay pinned local recheck files without refreshing the feed');args=parser.parse_args()
    old=json.loads((OUT/'recent.json').read_text(encoding='utf-8'));meta=json.loads((OUT/'recent-comparison.json').read_text(encoding='utf-8'));w=meta['window']
    b=json.loads((ROOT/'data/raw/boundary.geojson').read_text(encoding='utf-8'));polygon=unary_union([shape(f['geometry']) for f in b['features']]);proj=Transformer.from_crs(4326,6933,always_xy=True)
    session=requests.Session();session.trust_env=False;audits=[];current={}
    prior=json.loads((ROOT/'reports/daynight-audit.json').read_text(encoding='utf-8')) if args.cached else None
    for source in old['sources']:
        sensor=source['sensor'];cached=ROOT/f'data/raw/recheck-{sensor}-2026-11-14.csv'
        if args.cached:
            content=cached.read_bytes();previous_source=next(s for s in prior['sources'] if s['sensor']==sensor)
            assert hashlib.sha256(content).hexdigest()==previous_source['sha256'],'Cached source hash mismatch'
            retrieved=previous_source['retrieved_utc']
        else:
            response=session.get(source['url'],timeout=90);response.raise_for_status();content=response.content;cached.write_bytes(content);retrieved=datetime.now(timezone.utc).isoformat()
        d=pd.read_csv(io.BytesIO(content),dtype={'confidence':str,'acq_time':str,'version':str})
        d=d[d.acq_date.between(w['start'],w['end'])].copy()
        d=d[contains_xy(polygon,d.longitude.to_numpy(),d.latitude.to_numpy())].copy()
        if sensor=='aqua':d=d[d.satellite.isin(['A','Aqua']) & (pd.to_numeric(d.confidence)>=30)]
        else:d=d[d.confidence.str.lower().isin(['n','h','nominal','high'])]
        d=d.drop_duplicates(['latitude','longitude','acq_date','acq_time','satellite']);d['match_key']=key(d)
        previous=pd.DataFrame([r for r in old['records'] if r['sensor']==sensor and w['start']<=r['acq_date']<=w['end']]);previous['match_key']=key(previous)
        oldkeys=set(previous.match_key);newkeys=set(d.match_key);missing=oldkeys-newkeys
        if missing:raise ValueError(f'{sensor}: {len(missing)} saved observations cannot be exactly matched; do not infer daynight')
        flags=d.drop_duplicates('match_key').set_index('match_key').daynight.to_dict();previous['daynight']=previous.match_key.map(flags)
        assert previous.daynight.isin(['D','N']).all();current[sensor]=previous
        audits.append({'sensor':sensor,'url':source['url'],'retrieved_utc':retrieved,'sha256':hashlib.sha256(content).hexdigest(),'saved_window_points':len(previous),'refreshed_window_points':len(d),'added_points':len(newkeys-oldkeys),'removed_points':len(missing),'official_daynight_matched':len(previous),'versions':sorted(d.version.unique().tolist())})
    ledger=[];passages=[]
    for year in list(range(2019,2026))+[2026]:
        for sensor in ['aqua','noaa20']:
            if year==2026:d=current[sensor].copy()
            else:
                prefix='modis' if sensor=='aqua' else 'viirs-jpss1';d=pd.read_csv(ROOT/f'data/raw/{prefix}_{year}_Indonesia.csv',dtype={'confidence':str,'acq_time':str})
                if sensor=='aqua':d=d[d.satellite.isin(['A','Aqua']) & (pd.to_numeric(d.confidence)>=30)]
                else:d=d[d.confidence.isin(['n','h'])]
            d=d.copy();dates=pd.to_datetime(d.acq_date);d['month']=dates.dt.month;d['day']=dates.dt.day;d=d[d.day.between(w['start_day'],w['end_day'])].copy();d=d[contains_xy(polygon,d.longitude.to_numpy(),d.latitude.to_numpy())].copy()
            d['acq_time']=d.acq_time.astype(str).str.zfill(4);d['cx']=np.floor(d.longitude/.25).astype(int);d['cy']=np.floor(d.latitude/.25).astype(int)
            d=recent.occupied(d,proj);d['sector']=np.where(d.longitude<108,0,np.where(d.longitude<120,1,2));d['quarter']=(d.month-1)//3
            for name,bbox in recent.REGIONS.items():
                r=recent.select(d,bbox)
                for month in ([w['month']] if year==2026 else range(1,13)):
                    for sec in range(3):
                        for dn in ['D','N']:
                            ledger.append({'region':name,'year':year,'month':month,'quarter':(month-1)//3,'sector':sec,'daynight':dn,'sensor':sensor,'active':int((r.month.eq(month)&r.sector.eq(sec)&r.daynight.eq(dn)).sum())})
                if name=='kalimantan':
                    for dn in ['D','N']:
                        z=r[r.month.eq(w['month'])&r.daynight.eq(dn)]
                        minutes=pd.to_numeric(z.acq_time.str[:2])*60+pd.to_numeric(z.acq_time.str[2:]);local=(minutes+z.longitude*4)%1440
                        passages.append({'year':year,'sensor':sensor,'daynight':dn,'occupied_cell_days':len(z),'median_local_solar_hour_of_detected_points':float(local.median()/60) if len(z) else None})
            print('Day/night',sensor,year,flush=True)
    df=pd.DataFrame(ledger);df.to_csv(ROOT/'reports/daynight_counts.csv',index=False)
    wide=df.pivot(index=['region','year','month','quarter','sector','daynight'],columns='sensor',values='active').reset_index();train=wide[wide.year.between(2019,2023)]
    models={};fallbacks=[]
    for model in ['sector_daynight','local_daynight']:
        coeff={}
        group=train[train.region=='indonesia'] if model=='sector_daynight' else train
        keys=['sector','quarter','daynight'] if model=='sector_daynight' else ['region','quarter','daynight']
        for k,z in group.groupby(keys):
            if z.noaa20.sum()>0:f=float(z.aqua.sum()/z.noaa20.sum())
            else:
                parent=group[(group[keys[0]]==k[0])&group.quarter.eq(k[1])];den=parent.noaa20.sum();f=float(parent.aqua.sum()/den) if den else 1.;fallbacks.append({'model':model,'group':str(k),'factor':f,'reason':'No same-component training support; use pooled day/night or identity when both empty'})
            coeff[k]=f
        def pred(z):return np.array([r.noaa20*coeff[((r.sector if model=='sector_daynight' else r.region),r.quarter,r.daynight)] for r in z.itertuples()])
        regions={}
        for region in recent.REGIONS:
            z=wide[wide.region.eq(region)].copy();z['prediction']=pred(z);z=z.groupby(['year','month'])[['aqua','noaa20','prediction']].sum().reset_index()
            audit=z[z.year.between(2024,2025)];now=z[z.year==2026].iloc[0];same=audit[audit.month==w['month']]
            def score(x):
                den=x.aqua.sum();return {'windows':len(x),'wape':float(abs(x.prediction-x.aqua).sum()/den) if den else None,'mae':float(abs(x.prediction-x.aqua).mean())}
            baseline=meta['regions'][region]['current'];regions[region]={'audit':score(audit),'same_dates':score(same),'current':{'aqua':int(now.aqua),'value':float(now.prediction),'relative_disagreement':float(abs(now.prediction-now.aqua)/now.aqua) if now.aqua else None,'category':recent.category(now.prediction,baseline['median'],baseline['p90'])}}
        models[model]={'regions':regions,'macro_wape':float(np.mean([regions[k]['audit']['wape'] for k in ['sumatra','kalimantan','java','papua']]))}
    payload={'window':w,'sources':audits,'fit':[2019,2023],'audit':[2024,2025],'models':models,'fallbacks':fallbacks,'kalimantan_detected_passage_times':passages,'limits':['Day/night flag belongs to the earliest detected observation of a cell/day, preserving total cell-days.','Observed hotspot timestamps are not overpass or cloud-coverage denominators.','New diagnostics specified after earlier correction results; not part of the earlier method selection.','Exact data refresh comparison covers only the fixed analysis window, not every feed date.']}
    for p in [ROOT/'reports/daynight-audit.json',OUT/'daynight-audit.json']:p.write_text(json.dumps(payload,indent=2,allow_nan=False),encoding='utf-8')
    (OUT/'daynight_protocol.json').write_bytes((ROOT/'reports/daynight_protocol.json').read_bytes())
    print(json.dumps({'sources':audits,'models':models,'fallbacks':len(fallbacks)},indent=2),flush=True)

if __name__=='__main__':main()
