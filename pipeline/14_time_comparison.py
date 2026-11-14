"""Predefined local-time restrictions with excluded-year tests and support gates."""
import hashlib,json
from pathlib import Path
from importlib import import_module
import numpy as np
import pandas as pd
from pyproj import Transformer
from shapely.geometry import shape
from shapely.ops import unary_union
from shapely import contains_xy

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'web/public/data'
recent=import_module('09_recent_comparison')
WINDOWS={'all':[0,1440],'midday':[720,900],'one_hour':[780,840]}

def solar_minutes(times,longitude):
    t=pd.Series(times).astype(str).str.zfill(4)
    h=pd.to_numeric(t.str[:2]);m=pd.to_numeric(t.str[2:])
    if ((h<0)|(h>23)|(m<0)|(m>59)).any():raise ValueError('Invalid UTC time')
    return (h.to_numpy()*60+m.to_numpy()+np.asarray(longitude)*4)%1440

def support(a,n,full_a,full_n):
    return bool(a>=20 and n>=20 and full_a>0 and full_n>0 and a/full_a>=.5 and n/full_n>=.5)

def main():
    boundary=json.loads((ROOT/'data/raw/boundary.geojson').read_text(encoding='utf-8'))
    polygon=unary_union([shape(f['geometry']) for f in boundary['features']]);proj=Transformer.from_crs(4326,6933,always_xy=True)
    ledger=[];hist=[];sources=[]
    for year in range(2019,2027):
        for sensor in ['aqua','noaa20']:
            filename=f"{'modis' if sensor=='aqua' else 'viirs-jpss1'}_{year}_Indonesia.csv" if year<2026 else f'recheck-{sensor}-2026-11-14.csv'
            path=ROOT/'data/raw'/filename;sources.append({'file':filename,'url':f'https://firms.modaps.eosdis.nasa.gov/data/country/{filename}' if year<2026 else next(x['url'] for x in json.loads((ROOT/'reports/daynight-audit.json').read_text())['sources'] if x['sensor']==sensor),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
            d=pd.read_csv(path,dtype={'acq_time':str,'confidence':str})
            if sensor=='aqua':d=d[d.satellite.isin(['A','Aqua'])&(pd.to_numeric(d.confidence)>=30)]
            else:d=d[d.confidence.str.lower().isin(['n','h','nominal','high'])]
            dates=pd.to_datetime(d.acq_date);d=d.copy();d['month']=dates.dt.month;d['day']=dates.dt.day
            d=d[d.day.between(8,12)]
            if year==2026:d=d[d.acq_date.between('2026-11-08','2026-11-12')]
            d=d[contains_xy(polygon,d.longitude.to_numpy(),d.latitude.to_numpy())].copy();d['acq_time']=d.acq_time.str.zfill(4)
            d['solar']=solar_minutes(d.acq_time,d.longitude);d['cx']=np.floor(d.longitude/.25).astype(int);d['cy']=np.floor(d.latitude/.25).astype(int)
            for name,(lo,hi) in WINDOWS.items():
                selected=d[d.solar.ge(lo)&d.solar.lt(hi)];u=recent.select(recent.occupied(selected,proj),[108,-5,120,4.5])
                for month in ([11] if year==2026 else range(1,13)):
                    z=u[u.month.eq(month)];ledger.append({'year':year,'month':month,'quarter':(month-1)//3,'sensor':sensor,'window':name,'active':len(z)})
                    if name=='all' and month==11:
                        counts=np.histogram(z.solar,bins=np.arange(0,1441,60))[0].tolist()
                        hist.append({'year':year,'sensor':sensor,'hourly_detected_cell_days':counts,'total':len(z)})
            print(year,sensor,flush=True)
    df=pd.DataFrame(ledger);df.to_csv(ROOT/'reports/time-window-counts.csv',index=False)
    wide=df.pivot(index=['year','month','quarter','window'],columns='sensor',values='active').reset_index()
    full=wide[wide.window.eq('all')&wide.year.eq(2026)].iloc[0];models={}
    for name in WINDOWS:
        z=wide[wide.window.eq(name)].copy();fit=z[z.year.between(2019,2021)]
        coefficients={}
        for q in range(4):
            t=fit[fit.quarter.eq(q)];den=t.noaa20.sum()
            if den<=0:raise ValueError('No training support; no fallback permitted')
            coefficients[q]=float(t.aqua.sum()/den)
        z['estimate']=z.noaa20*z.quarter.map(coefficients);audit=z[z.year.between(2022,2025)]
        score=lambda a: {'windows':len(a),'wape':float(abs(a.estimate-a.aqua).sum()/a.aqua.sum()) if a.aqua.sum()>0 else None,'aqua_total':int(a.aqua.sum()),'mae':float(abs(a.estimate-a.aqua).mean())}
        now=z[z.year.eq(2026)].iloc[0];passed=support(now.aqua,now.noaa20,full.aqua,full.noaa20)
        models[name]={'minutes':WINDOWS[name],'coefficients':coefficients,'audit':score(audit),'same_november_dates':score(audit[audit.month.eq(11)]),'current':{'aqua':int(now.aqua),'noaa20':int(now.noaa20),'aqua_retained_fraction':float(now.aqua/full.aqua) if full.aqua else None,'noaa20_retained_fraction':float(now.noaa20/full.noaa20) if full.noaa20 else None,'support_gate_passed':passed,'estimate':float(now.estimate) if passed else None,'relative_disagreement':float(abs(now.estimate-now.aqua)/now.aqua) if passed else None},'audit_windows':audit[['year','month','aqua','noaa20','estimate']].to_dict(orient='records')}
    result={'fit':[2019,2021],'audit':[2022,2025],'bounds':[108,-5,120,4.5],'current_dates':['2026-11-08','2026-11-12'],'models':models,'detected_time_histograms':hist,'sources':sources,'independent_time_validation':{'status':'not_completed','candidate':'JAXA Himawari 10-minute wildfire product','guide':'https://www.eorc.jaxa.jp/ptree/userguide.html','access':'https://www.eorc.jaxa.jp/ptree/registration_top.html','reason':'Separate registration and public-release conditions; no product data obtained or published.'},'limits':['Time-restricted detections are not paired clear-sky observations.','Each time restriction changes the quantity being estimated; its WAPE is not directly interchangeable with unrestricted WAPE.','All-time model here is a new fixed regional five-day calibration, not the released sector/monthly model.','No causal decomposition of sensor sensitivity, observing time and actual burning is established.','Current estimates are suppressed when the predefined count/retention gate fails.']}
    text=json.dumps(result,indent=2,allow_nan=False)+'\n'
    for p in [ROOT/'reports/time-comparison.json',OUT/'time-comparison.json']:p.write_text(text)
    print(json.dumps({k:{'audit':v['audit'],'current':v['current']} for k,v in models.items()},indent=2),flush=True)

if __name__=='__main__':main()
