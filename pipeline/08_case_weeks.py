"""Thirteen complete seven-day windows, Aug 1-Oct 30; observed activity, not coverage."""
import json
from pathlib import Path
import numpy as np
import pandas as pd
from pyproj import Transformer
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'web/public/data'
def main():
    transform=Transformer.from_crs(4326,6933,always_xy=True);meta=json.loads((OUT/'metadata.json').read_text());weights={(f['sector'],f['quarter']):f['factor'] for f in meta['factors']['snpp']};records=[]
    for sensor,years in [('aqua',list(range(2003,2018))+[2019,2020]),('snpp',[2019,2020])]:
        for year in years:
            name=f"{'modis' if sensor=='aqua' else 'viirs-snpp'}_{year}_Indonesia.csv"
            d=pd.read_csv(ROOT/'data/raw'/name,dtype={'confidence':str,'acq_time':str})
            if sensor=='aqua':d=d[d.satellite.isin(['A','Aqua'])&(pd.to_numeric(d.confidence)>=30)]
            else:d=d[d.confidence.isin(['n','h'])]
            d=d.copy()
            dates=pd.to_datetime(d.acq_date);d['week']=((dates-pd.Timestamp(year=year,month=8,day=1)).dt.days//7);d['quarter']=(dates.dt.month-1)//3;d=d[d.week.between(0,12)]
            x,y=transform.transform(d.longitude.to_numpy(),d.latitude.to_numpy());d['gx']=np.floor(x/1000).astype(int);d['gy']=np.floor(y/1000).astype(int);d=d.sort_values('acq_time').drop_duplicates(['acq_date','gx','gy']);d=d[d.longitude.ge(108)&d.longitude.lt(120)&d.latitude.ge(-5)&d.latitude.lt(4.5)]
            d['adjusted']=1. if sensor=='aqua' else d.quarter.map(lambda q:weights[(1,q)])
            totals=d.groupby('week').agg(active=('gx','size'),adjusted=('adjusted','sum'))
            for week in range(13):
                row=totals.loc[week] if week in totals.index else {'active':0,'adjusted':0}
                records.append({'sensor':sensor,'year':year,'week':week,'active':int(row['active']),'adjusted':float(row['adjusted'])})
    df=pd.DataFrame(records);series=[]
    for week in range(13):
        baseline=df[(df.sensor=='aqua')&(df.year<=2017)&(df.week==week)].active
        start=pd.Timestamp('2019-08-01')+pd.Timedelta(days=week*7)
        row={'week':week,'start':start.strftime('%b %d'),'end':(start+pd.Timedelta(days=6)).strftime('%b %d'),'baseline_median':float(baseline.median()),'baseline_p90':float(baseline.quantile(.9))}
        for year in [2019,2020]:
            for sensor in ['aqua','snpp']:
                a=df[(df.year==year)&(df.sensor==sensor)&(df.week==week)].iloc[0];row[f'{sensor}_{year}']=int(a.active);row[f'{sensor}_{year}_adjusted']=float(a.adjusted)
        series.append(row)
    result={'windows':series,'baseline_years':[2003,2017],'bbox':[108,-5,120,4.5],'note':'13 complete 7-day UTC windows, August 1-October 30. October 31 is omitted to avoid comparing a partial week. No cloud/overpass coverage correction. Median and p90 describe Aqua observations, not true fire occurrence.'}
    (OUT/'case-weeks.json').write_text(json.dumps(result,indent=2));print('Exported',len(series),'weekly windows')
if __name__=='__main__':main()
