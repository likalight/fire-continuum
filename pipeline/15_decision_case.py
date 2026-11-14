"""Retrospective annual activity-timing markers and auditable review candidates."""

import gzip,hashlib,json

from pathlib import Path

import numpy as np

import pandas as pd

from pyproj import Transformer



ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'web/public/data'



def marker(daily, fraction):

    a=np.asarray(daily,float)

    if len(a)!=365 or np.any(a<0) or not np.isfinite(a).all():raise ValueError('Expected 365 nonnegative finite daily totals')

    return int(np.searchsorted(np.cumsum(a),a.sum()*fraction)+1) if a.sum()>0 else None



def marker_date(day):

    return (pd.Timestamp('2001-01-01')+pd.Timedelta(days=day-1)).strftime('%b %d') if day else None



def main():

    project=Transformer.from_crs(4326,6933,always_xy=True);meta=json.loads((OUT/'metadata.json').read_text());factors={(f['sector'],f['quarter']):f['factor'] for f in meta['factors']['snpp']}

    samples=[];sources=[]

    for sensor,years in [('aqua',list(range(2003,2018))+[2019,2020]),('snpp',[2019,2020])]:

        for year in years:

            path=ROOT/'data/raw'/f"{'modis' if sensor=='aqua' else 'viirs-snpp'}_{year}_Indonesia.csv"

            sources.append({'file':path.name,'url':f'https://firms.modaps.eosdis.nasa.gov/data/country/{path.name}','sha256':hashlib.sha256(path.read_bytes()).hexdigest()})

            d=pd.read_csv(path,dtype={'confidence':str,'acq_time':str})

            if sensor=='aqua':d=d[d.satellite.isin(['A','Aqua'])&(pd.to_numeric(d.confidence)>=30)]

            else:d=d[d.confidence.isin(['n','h'])]

            d=d.copy();d['acq_time']=d.acq_time.str.zfill(4);x,y=project.transform(d.longitude.to_numpy(),d.latitude.to_numpy());d['gx']=np.floor(x/1000).astype(int);d['gy']=np.floor(y/1000).astype(int)

            d=d.sort_values(['acq_time','longitude','latitude'],kind='stable').drop_duplicates(['acq_date','gx','gy'])

            d=d[d.longitude.ge(108)&d.longitude.lt(120)&d.latitude.ge(-5)&d.latitude.lt(4.5)].copy();dt=pd.to_datetime(d.acq_date);d['month']=dt.dt.month;d['day']=dt.dt.day

            d=d[~(d.month.eq(2)&d.day.eq(29))].copy();d['day_index']=pd.to_datetime('2001-'+d.acq_date.str[5:]).dt.dayofyear

            d['weight']=1. if sensor=='aqua' else d.month.map(lambda m:factors[(1,(m-1)//3)])

            daily=d.groupby('day_index').weight.sum().reindex(range(1,366),fill_value=0).to_numpy();samples.append({'sensor':sensor,'year':year,'annual_activity':float(daily.sum()),'markers':{str(q):marker(daily,q) for q in [.05,.1,.2]}})

            print('Timing',sensor,year,flush=True)

    reference={}

    for q in ['0.05','0.1','0.2']:

        values=[s['markers'][q] for s in samples if s['sensor']=='aqua' and s['year']<=2017 and s['markers'][q] is not None]

        reference[q]={'n':len(values),'median_day':float(np.median(values)),'p10_day':float(np.quantile(values,.1)),'p90_day':float(np.quantile(values,.9)),'median_date':marker_date(int(np.median(values)))}

    cases=[]

    for year in [2019,2020]:

        row={'year':year,'coverage_warning':'Aqua archive outage in August–September 2020: annual timing marker is coverage-affected, not evidence of earlier burning.' if year==2020 else None,'sensors':{}}

        for sensor in ['aqua','snpp']:

            record=next(s for s in samples if s['sensor']==sensor and s['year']==year)

            row['sensors'][sensor]={'annual_activity':record['annual_activity'],'markers':{q:{'day':v,'date':marker_date(v),'days_from_reference_median':v-reference[q]['median_day'] if v else None} for q,v in record['markers'].items()}}

        cases.append(row)

    history=json.loads(gzip.decompress((OUT/'history.json.gz').read_bytes()));cells={}

    for r in history:

        if r[1]!=9 or not (108<=(r[2]+.5)*.25<120 and -5<=(r[3]+.5)*.25<4.5):continue

        k=(r[2],r[3]);cells.setdefault(k,{})[r[0]]=r

    candidates=[]

    for (cx,cy),years in cells.items():

        if 2019 not in years:continue

        baseline=[years[y][7] if y in years else 0 for y in range(2003,2018)];median=float(np.median(baseline));p90=float(np.quantile(baseline,.9));r=years[2019];aqua=r[7];adjusted=r[8]*factors[(1,2)]

        if median>=5 and aqua>p90 and adjusted>p90:

            candidates.append({'bounds':[cx*.25,cy*.25,(cx+1)*.25,(cy+1)*.25],'centre':[(cx+.5)*.25,(cy+.5)*.25],'aqua':aqua,'adjusted':adjusted,'median':median,'p90':p90,'review_score':min(aqua-median,adjusted-median)})

    candidates.sort(key=lambda c:(-c['review_score'],c['centre'][0],c['centre'][1]));chosen=[]

    for c in candidates:

        if all(np.linalg.norm(np.array(c['centre'])-np.array(other['centre']))>=.5 for other in chosen):chosen.append(c)

        if len(chosen)==3:break

    result={'title':'Kalimantan September 2019 decision briefing','area':[108,-5,120,4.5],'reference':reference,'cases':cases,'reference_samples':samples,'candidates':chosen,'eligible_candidate_cells':len(candidates),'sources':sources,'external_user_validation':{'status':'not_conducted','participants':0},'definition':'Retrospective date at which 10% of full-year observed activity has accumulated; 5% and 20% are sensitivity checks. Not first ignition or a forecast.','limitations':['The 2020 Aqua annual marker is coverage-affected by a documented archive outage; it must not support an earlier-season claim.','Full-year totals are required; no prospective onset warning is claimed.','Coverage and detection sensitivity can shift timing markers.','Review cells use exploratory regional calibration at a smaller spatial scale.','Local daily-mask case covers a different, smaller rectangle; it cannot correct these regional markers or review cells.','Candidate scores measure hotspot evidence, not people, assets, severity, burned area or response priority.']}

    text=json.dumps(result,indent=2,allow_nan=False)+'\n'

    for path in [ROOT/'reports/decision-case.json',OUT/'decision-case.json']:path.write_text(text)

    print(json.dumps({'reference':reference,'cases':cases,'candidates':chosen,'eligible':len(candidates)},indent=2),flush=True)



if __name__=='__main__':main()
