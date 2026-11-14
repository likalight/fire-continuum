"""Build a dated, calibrated burning calendar from verified NASA annual archives."""
import gzip,json,hashlib
from pathlib import Path
from collections import defaultdict
import numpy as np
import pandas as pd
from pyproj import Transformer
from harmonize import fit_ratio,metrics,quarter,sector,primary_sensor
ROOT=Path(__file__).resolve().parents[1]
SENSORS=['aqua','snpp','noaa20']
TRAIN={'snpp':(2013,2017),'noaa20':(2019,2021)}
TEST={'snpp':(2018,2025),'noaa20':(2022,2025)}

def main():
    manifest=json.loads((ROOT/'reports/source_manifest.json').read_text())
    out=ROOT/'web/public/data';(out/'detections').mkdir(parents=True,exist_ok=True)
    spatial=[];monthly=[];audit=[];project=Transformer.from_crs(4326,6933,always_xy=True)
    for f in manifest:
        file=ROOT/'data/raw'/f['filename'];assert file.stat().st_size==int(f['size'])
        year=int(f['filename'].split('_')[1]);sensor='aqua' if f['filename'].startswith('modis') else ('snpp' if f['filename'].startswith('viirs-snpp') else 'noaa20')
        df=pd.read_csv(file,dtype={'acq_time':str,'version':str,'confidence':str});total=len(df)
        versions=sorted(df.version.unique().tolist())
        if sensor=='aqua':df=df[df.satellite.isin(['A','Aqua'])].copy();df=df[pd.to_numeric(df.confidence)>=30]
        else:df=df[df.confidence.isin(['n','h'])].copy()
        df=df.drop_duplicates(['latitude','longitude','acq_date','acq_time','satellite'])
        dates=pd.to_datetime(df.acq_date);assert (dates.dt.year==year).all()
        df['month']=dates.dt.month;df['sector']=sector(df.longitude)
        df['cx']=np.floor(df.longitude/.25).astype(int);df['cy']=np.floor(df.latitude/.25).astype(int)
        # Equal-area kilometre grid, one occupied cell per UTC date per sensor.
        x,y=project.transform(df.longitude.to_numpy(),df.latitude.to_numpy());df['gx']=np.floor(x/1000).astype(int);df['gy']=np.floor(y/1000).astype(int)
        unique=df.sort_values('acq_time').drop_duplicates(['acq_date','gx','gy']).copy()
        points=df.groupby(['month','cx','cy']).size().rename('raw')
        active=unique.groupby(['month','cx','cy']).size().rename('active')
        merged=pd.concat([points,active],axis=1).fillna(0).reset_index();merged['year']=year;merged['sensor']=sensor;spatial.append(merged)
        raw=df.groupby(['month','sector']).size();a=unique.groupby(['month','sector']).size()
        for month in range(1,13):
            for sec in range(3):
                monthly.append({'year':year,'month':month,'sector':sec,'sensor':sensor,'raw':int(raw.get((month,sec),0)),'active':int(a.get((month,sec),0))})
        if sensor==primary_sensor(year):
            fields=['latitude','longitude','acq_date','acq_time','satellite','confidence','frp','daynight','type','version']
            for month in range(1,13):
                sub=df[df.month==month][fields]
                payload=sub.to_csv(index=False).encode();(out/'detections'/f'{year}-{month:02}.csv.gz').write_bytes(gzip.compress(payload,mtime=0))
        audit.append({'file':f['filename'],'sensor':sensor,'year':year,'downloaded_rows':total,'retained_detections':len(df),'active_cell_days':len(unique),'versions':versions,'min_date':str(df.acq_date.min()),'max_date':str(df.acq_date.max())})
        print(sensor,year,total,'->',len(df),'detections;',len(unique),'cell-days',flush=True)
    monthly=pd.DataFrame(monthly)
    wide=monthly.pivot(index=['year','month','sector'],columns='sensor',values='active').reset_index()
    factors={};validation={}
    for sensor in ['snpp','noaa20']:
        fit=wide[wide.year.between(*TRAIN[sensor])];test=wide[wide.year.between(*TEST[sensor])].copy()
        weights=[]
        for sec in range(3):
            for q in range(4):
                use=fit[(fit.sector==sec)&(quarter(fit.month)==q)].dropna(subset=['aqua',sensor])
                assert len(use)>=9
                factor=fit_ratio(use.aqua,use[sensor]);weights.append({'sector':sec,'quarter':q,'factor':factor,'training_months':len(use),'reference_total':int(use.aqua.sum()),'sensor_total':int(use[sensor].sum())})
        factors[sensor]=weights
        lookup={(w['sector'],w['quarter']):w['factor'] for w in weights}
        test['pred']=test[sensor]*[lookup[(s,int(q))] for s,q in zip(test.sector,quarter(test.month))]
        national=test.groupby(['year','month'])[['aqua',sensor,'pred']].sum()
        validation[sensor]={'train_years':TRAIN[sensor],'test_years':TEST[sensor],
            'national_before':metrics(national.aqua,national[sensor]),'national_after':metrics(national.aqua,national.pred),
            'sectors':[{'sector':sec,'before':metrics(z.aqua,z[sensor]),'after':metrics(z.aqua,z.pred)} for sec in range(3) for z in [test[test.sector==sec]]]}
    spatial=pd.concat(spatial,ignore_index=True)
    raw=spatial.pivot(index=['year','month','cx','cy'],columns='sensor',values='raw').reindex(columns=SENSORS).fillna(0)
    active=spatial.pivot(index=['year','month','cx','cy'],columns='sensor',values='active').reindex(columns=SENSORS).fillna(0)
    combined=np.column_stack([raw.index.to_frame(index=False).values,raw.values,active.values]).astype(int)
    rows=combined.tolist()
    metadata={'name':'Fire Continuum','country':'Indonesia','years':[2003,2025],'grid_degrees':.25,'columns':['year','month','longitude_cell','latitude_cell','aqua_detections','snpp_detections','noaa20_detections','aqua_cell_days','snpp_cell_days','noaa20_cell_days'],
      'sensor_years':{'aqua':[2003,2025],'snpp':[2012,2025],'noaa20':[2018,2025]},'partial_years':{'snpp':[2012],'noaa20':[2018]},
      'primary_periods':[['aqua',2003,2012],['snpp',2013,2021],['noaa20',2022,2025]],'factors':factors,'validation':validation,
      'total_downloaded_rows':sum(a['downloaded_rows'] for a in audit),'total_retained_rows':sum(a['retained_detections'] for a in audit),'annual_files':len(manifest),
      'reference':'MODIS Aqua filtered active cell-days, not true fire counts','units':'Aqua-equivalent active 1 km cell-days',
      'limits':['Calibration adjusts regional seasonal count differences, not individual hotspot locations or burned area.','No cloud/clear-sky or overpass denominator; zero detections do not prove absence of fire.','Calibration validated on held-out regional months; arbitrary smaller AOIs remain exploratory.','Confidence filters are sensor-specific; categories are not equivalent probabilities.','Historical records contain collection/version changes, retained in source audit.','Archive ends in December 2025. The 2026 rolling feed is separate and is not a complete current-month record.','Industrial, volcanic and other thermal sources are retained; detections are not distinct wildfires.']}
    (out/'history.json.gz').write_bytes(gzip.compress(json.dumps(rows,separators=(',',':')).encode(),mtime=0))
    (out/'metadata.json').write_text(json.dumps(metadata,indent=2,allow_nan=False))
    (ROOT/'reports/validation.json').write_text(json.dumps(validation,indent=2,allow_nan=False))
    (ROOT/'reports/input_audit.json').write_text(json.dumps(audit,indent=2))
    (out/'sources.json').write_text(json.dumps(manifest,indent=2))
    monthly.to_csv(ROOT/'reports/monthly_counts.csv',index=False)
    print(json.dumps(validation,indent=2));print('Sparse rows',len(rows),'data bytes',sum(p.stat().st_size for p in out.rglob('*') if p.is_file()),flush=True)
if __name__=='__main__':main()

