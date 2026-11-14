"""Run every predeclared grid/filter variant; no choosing the best result afterward."""
import json
from pathlib import Path
import numpy as np
import pandas as pd
from pyproj import Transformer
from harmonize import metrics
from importlib import import_module
robust=import_module('05_robust_validation')
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'web/public/data'
CONFIGS=[('grid_500m',500,'base'),('original_1000m',1000,'base'),('grid_2000m',2000,'base'),('high_confidence',1000,'high'),('vegetation_only',1000,'vegetation'),('daytime_only',1000,'day')]
def main():
    project=Transformer.from_crs(4326,6933,always_xy=True);ledger=[];case=[]
    manifest=json.loads((ROOT/'reports/source_manifest.json').read_text())
    for src in manifest:
        name=src['filename'];year=int(name.split('_')[1]);sensor='aqua' if name.startswith('modis') else 'snpp' if name.startswith('viirs-snpp') else 'noaa20'
        d=pd.read_csv(ROOT/'data/raw'/name,dtype={'acq_time':str,'confidence':str})
        if sensor=='aqua':d=d[d.satellite.isin(['A','Aqua'])&(pd.to_numeric(d.confidence)>=30)].copy()
        else:d=d[d.confidence.isin(['n','h'])].copy()
        d=d.drop_duplicates(['latitude','longitude','acq_date','acq_time','satellite']).sort_values('acq_time')
        d['month']=pd.to_datetime(d.acq_date).dt.month;d['sector']=np.where(d.longitude<108,0,np.where(d.longitude<120,1,2))
        d['x'],d['y']=project.transform(d.longitude.to_numpy(),d.latitude.to_numpy())
        for label,size,kind in CONFIGS:
            z=d
            if kind=='high':z=z[pd.to_numeric(z.confidence)>=80] if sensor=='aqua' else z[z.confidence=='h']
            if kind=='vegetation':z=z[z.type==0]
            if kind=='day':z=z[z.daynight=='D']
            z=z.copy();z['gx']=np.floor(z.x/size).astype(int);z['gy']=np.floor(z.y/size).astype(int)
            u=z.drop_duplicates(['acq_date','gx','gy']);s=u.groupby(['month','sector']).size()
            for month in range(1,13):
                for sec in range(3):ledger.append({'config':label,'year':year,'month':month,'quarter':(month-1)//3,'sector':sec,'sensor':sensor,'active':int(s.get((month,sec),0))})
            k=u[u.longitude.ge(108)&u.longitude.lt(120)&u.latitude.ge(-5)&u.latitude.lt(4.5)&u.month.eq(9)]
            for sec in range(3):case.append({'config':label,'year':year,'sector':sec,'sensor':sensor,'active':int((k.sector==sec).sum())})
        print('Sensitivity',name,flush=True)
    ledger=pd.DataFrame(ledger);cases=pd.DataFrame(case);results=[]
    for label,size,kind in CONFIGS:
        wide=ledger[ledger.config==label].pivot(index=['year','month','quarter','sector'],columns='sensor',values='active').reset_index()
        cw=cases[cases.config==label].pivot(index=['year','sector'],columns='sensor',values='active').reset_index();cw['quarter']=2;cw['month']=9
        row={'config':label,'grid_m':size,'filter':kind,'sensors':{}}
        for sensor,tr,te in [('snpp',[2013,2017],[2018,2025]),('noaa20',[2019,2021],[2022,2025])]:
            f,_=robust.fit(wide[wide.year.between(*tr)],sensor);z=robust.monthly(wide[wide.year.between(*te)],sensor,f)
            row['sensors'][sensor]=metrics(z.aqua,z.pred)
            if sensor=='snpp':
                baseline=cw[cw.year.between(2003,2017)].groupby('year').aqua.sum();b90=float(baseline.quantile(.9));b50=float(baseline.median())
                cc=robust.monthly(cw[cw.year.isin([2019,2020])],sensor,f)
                row['case']=[{'year':int(a.year),'adjusted':float(a.pred),'aqua':int(a.aqua),'median':b50,'p90':b90,'adjusted_above_p90':bool(a.pred>b90),'aqua_above_p90':bool(a.aqua>b90)} for a in cc.itertuples()]
        results.append(row)
    ledger.to_csv(ROOT/'reports/sensitivity_counts.csv',index=False)
    payload={'configurations':results,'note':'Each variant is refitted on the original training years and tested on the original later years. Definitions differ, so lower disagreement does not establish a more accurate count of fires. Case classification uses the corresponding Aqua September 2003-2017 baseline.'}
    (OUT/'sensitivity.json').write_text(json.dumps(payload,indent=2));(ROOT/'reports/sensitivity.json').write_text(json.dumps(payload,indent=2))
    print(json.dumps(results,indent=2),flush=True)
if __name__=='__main__':main()
