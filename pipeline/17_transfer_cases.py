"""Fixed external-region transfer experiment using real NASA annual FIRMS archives."""
import argparse,csv,hashlib,io,json,time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timezone
from pathlib import Path
import numpy as np
import pandas as pd
from pyproj import Transformer
import requests
from harmonize import metrics,sector

ROOT=Path(__file__).resolve().parents[1]
BASE='https://firms.modaps.eosdis.nasa.gov/data/country/'
OUT=ROOT/'web/public/data'
MODELS=['raw','occupied','transferred','local']

def category(value,median,p90):
    if median<=0:return 'Insufficient baseline'
    return 'Unusually high' if value>p90 else 'Above typical' if value>median else 'At or below typical'

def support(aqua,viirs,median):
    return bool(aqua>=20 and viirs>=20 and median>=5)

def peak_window(values):
    a=np.asarray(values,float)
    if len(a)!=12 or not np.isfinite(a).all() or np.any(a<0):raise ValueError('Twelve finite nonnegative months required')
    if a.sum()==0:return None
    sums=[sum(a[(i+j)%12] for j in range(3)) for i in range(12)]
    return int(np.argmax(sums))+1

def month_distance(first,second):
    if first is None or second is None:return None
    gap=abs(first-second)
    return min(gap,12-gap)

def fit_local(rows):
    weights=[]
    for q in range(4):
        sample=[r for r in rows if 2019<=r['year']<=2021 and (r['month']-1)//3==q and not (r['year']==2020 and r['month'] in [8,9])]
        den=sum(r['viirs_occupied'] for r in sample)
        if den<=0:raise ValueError('Insufficient local calibration support; no fallback')
        weights.append({'quarter':q,'factor':sum(r['aqua'] for r in sample)/den,'months':len(sample),'aqua_total':sum(r['aqua'] for r in sample),'viirs_total':den})
    return weights

def get_catalog(protocol,cached):
    path=ROOT/'reports/transfer-source-manifest.json'
    if cached:
        return json.loads(path.read_text(encoding='utf-8'))
    session=requests.Session();session.trust_env=False
    r=session.get(BASE+'yearly_summary_files.txt',timeout=45);r.raise_for_status()
    rows=list(csv.DictReader(io.StringIO(r.text)));countries={x['country'] for x in protocol['regions']}
    chosen=[]
    for country in sorted(countries):
        for prefix,years in [('modis',range(2003,2026)),('viirs-jpss1',range(2019,2026))]:
            for year in years:
                filename=f'{prefix}_{year}_{country}.csv';entry=next((x for x in rows if x['filename']==filename),None)
                if entry is None:raise ValueError('Required source missing: '+filename)
                chosen.append(dict(entry,url=BASE+filename))
    return chosen

def download_sources(rows,cached):
    def get(row):
        path=ROOT/'data/raw'/row['filename']
        for attempt in range(3):
            try:
                if not path.exists() or path.stat().st_size!=int(row['size']):
                    if cached:raise ValueError('Pinned source missing')
                    session=requests.Session();session.trust_env=False
                    with session.get(row['url'],stream=True,timeout=(20,90)) as response:
                        response.raise_for_status()
                        part=path.with_suffix('.csv.part')
                        with part.open('wb') as stream:
                            for block in response.iter_content(1024*1024):stream.write(block)
                    if part.stat().st_size!=int(row['size']):raise ValueError('Advertised size differs')
                    part.replace(path)
                digest=hashlib.sha256(path.read_bytes()).hexdigest()
                if cached and digest!=row['sha256']:raise ValueError('Pinned source hash differs')
                with path.open() as stream:
                    if not {'latitude','longitude','acq_date','acq_time','confidence','satellite'}<=set(next(csv.reader(stream))):raise ValueError('Wrong source schema')
                result=dict(row,sha256=digest)
                result.setdefault('retrieved_utc',datetime.now(timezone.utc).isoformat())
                print('Verified',row['filename'],path.stat().st_size,flush=True)
                return result
            except Exception as error:
                if attempt==2:raise RuntimeError(row['filename']+': '+type(error).__name__) from None
                time.sleep(2)
    with ThreadPoolExecutor(max_workers=6) as pool:return list(pool.map(get,rows))

def count_source(source,bounds,project):
    filename=source['filename'];path=ROOT/'data/raw'/filename;year=int(filename.split('_')[1]);sensor='aqua' if filename.startswith('modis') else 'noaa20'
    selected=[];versions=set();downloaded=0
    west,south,east,north=bounds
    for chunk in pd.read_csv(path,dtype={'acq_time':str,'confidence':str,'version':str},chunksize=150000):
        downloaded+=len(chunk);versions.update(chunk.version.dropna().unique())
        z=chunk[chunk.longitude.ge(west)&chunk.longitude.lt(east)&chunk.latitude.ge(south)&chunk.latitude.lt(north)]
        if sensor=='aqua':z=z[z.satellite.isin(['A','Aqua']) & pd.to_numeric(z.confidence).ge(30)]
        else:z=z[z.confidence.isin(['n','h'])]
        if len(z):selected.append(z[['latitude','longitude','acq_date','acq_time','satellite','confidence','version']])
    if selected:
        d=pd.concat(selected,ignore_index=True).drop_duplicates(['latitude','longitude','acq_date','acq_time','satellite'])
        dates=pd.to_datetime(d.acq_date)
        if not dates.dt.year.eq(year).all():raise ValueError('Wrong source year')
        d['month']=dates.dt.month;d['acq_time']=d.acq_time.str.zfill(4)
        x,y=project.transform(d.longitude.to_numpy(),d.latitude.to_numpy());d['gx']=np.floor(x/1000).astype(int);d['gy']=np.floor(y/1000).astype(int)
        u=d.sort_values(['acq_time','longitude','latitude'],kind='stable').drop_duplicates(['acq_date','gx','gy'])
        raw=d.groupby('month').size();active=u.groupby('month').size()
        counts=[{'year':year,'month':m,'sensor':sensor,'raw':int(raw.get(m,0)),'active':int(active.get(m,0))} for m in range(1,13)]
        retained=len(d);occupied=len(u)
    else:
        counts=[{'year':year,'month':m,'sensor':sensor,'raw':0,'active':0} for m in range(1,13)];retained=occupied=0
    audit={'file':filename,'sensor':sensor,'year':year,'downloaded_rows':downloaded,'retained_detections':retained,'active_cell_days':occupied,'versions':sorted(versions),'source_sha256':source['sha256']}
    return counts,audit

def comparison_score(rows,key):
    valid=[r for r in rows if r['baseline_median']>0];gated=[r for r in rows if r['support_gate_passed']]
    correct=lambda z:sum(r['classes'][key]==r['classes']['aqua'] for r in z)
    agreement=lambda z:correct(z)/len(z) if z else None
    output=metrics([r['aqua'] for r in rows],[r[key] for r in rows])
    output.update(category_months=len(valid),category_correct=correct(valid),category_agreement=agreement(valid),gated_months=len(gated),gated_correct=correct(gated),gated_category_agreement=agreement(gated),retained_fraction=len(gated)/len(rows),withheld_months=len(rows)-len(gated))
    return output

def summarize_region(region,counts,frozen):
    lookup={(r['year'],r['month'],r['sensor']):r for r in counts}
    baselines={}
    for m in range(1,13):
        values=[lookup[(y,m,'aqua')]['active'] for y in range(2003,2018)]
        baselines[m]={'median':float(np.median(values)),'p90':float(np.quantile(values,.9)),'samples':values}
    rows=[]
    for y in range(2019,2026):
        for m in range(1,13):
            a=lookup[(y,m,'aqua')];v=lookup[(y,m,'noaa20')]
            rows.append({'year':y,'month':m,'aqua':a['active'],'viirs_raw':v['raw'],'viirs_occupied':v['active'],'baseline_median':baselines[m]['median'],'baseline_p90':baselines[m]['p90']})
    local=fit_local(rows);midlon=(region['bounds'][0]+region['bounds'][2])/2;sec=int(sector(midlon));weights=[next(x for x in frozen if x['sector']==sec and x['quarter']==q) for q in range(4)]
    for row in rows:
        q=(row['month']-1)//3
        row.update(raw=float(row['viirs_raw']),occupied=float(row['viirs_occupied']),transferred=float(row['viirs_occupied']*weights[q]['factor']),local=float(row['viirs_occupied']*local[q]['factor']))
        row['classes']={key:category(row[key],row['baseline_median'],row['baseline_p90']) for key in ['aqua']+MODELS}
        row['support_gate_passed']=support(row['aqua'],row['viirs_occupied'],row['baseline_median'])
        row['coverage_status']='unknown; annual file available'
        row['known_outage_warning']=row['year']==2020 and row['month'] in [8,9]
    evaluated=[r for r in rows if r['year']>=2022]
    scores={key:comparison_score(evaluated,key) for key in MODELS}
    seasonal=[]
    for y in range(2022,2026):
        z=[r for r in evaluated if r['year']==y]
        aqua=peak_window([r['aqua'] for r in z])
        seasonal.append({'year':y,'aqua_start_month':aqua,'methods':{key:{'start_month':peak_window([r[key] for r in z]),'start_month_error':month_distance(aqua,peak_window([r[key] for r in z]))} for key in MODELS}})
    for key in MODELS:
        errors=[r['methods'][key]['start_month_error'] for r in seasonal if r['methods'][key]['start_month_error'] is not None]
        scores[key]['mean_peak_start_error_months']=float(np.mean(errors)) if errors else None
    history=[{'year':y,'month':m,'aqua':lookup[(y,m,'aqua')]['active']} for y in range(2003,2026) for m in range(1,13)]
    return dict(region,baseline_years=[2003,2017],fit_years=[2019,2021],audit_years=[2022,2025],transfer_sector=sec,factors={'transferred':weights,'local':local},baseline=[dict(month=m,**b) for m,b in baselines.items()],metrics=scores,months=rows,history=history,seasonal_windows=seasonal)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--cached',action='store_true');parser.add_argument('--download-only',action='store_true');args=parser.parse_args()
    protocol=json.loads((ROOT/'reports/transfer-protocol.json').read_text(encoding='utf-8-sig'))
    sources=download_sources(get_catalog(protocol,args.cached),args.cached)
    (ROOT/'reports/transfer-source-manifest.json').write_text(json.dumps(sources,indent=2)+'\n',encoding='utf-8')
    if args.download_only:return
    frozen=json.loads((OUT/'metadata.json').read_text())['factors']['noaa20'];project=Transformer.from_crs(4326,6933,always_xy=True)
    regions=[];input_audit=[];ledger=[]
    for region in protocol['regions']:
        counts=[]
        for source in [s for s in sources if s['filename'].endswith('_'+region['country']+'.csv')]:
            values,audit=count_source(source,region['bounds'],project);counts+=values;input_audit.append(dict(region=region['id'],**audit));ledger.extend(dict(region=region['id'],**r) for r in values)
            print('Counted',source['filename'],audit['retained_detections'],flush=True)
        regions.append(summarize_region(region,counts,frozen))
    result={'frozen_model_sha256':hashlib.sha256((OUT/'metadata.json').read_bytes()).hexdigest(),'frozen_model_path':'metadata.json','title':'Two external-region transfer tests','protocol':'transfer-protocol.json','source_files':len(sources),'source_bytes':sum(int(s['size']) for s in sources),'sources':sources,'input_audit':input_audit,'regions':regions,'interpretation':'Frozen transfer and external local refitting are separate experiments. Cross-sensor agreement is not ground-truth fire accuracy.','limits':['Only these two fixed rectangles are supported; not global coverage.','Retrospective support gate uses concurrent Aqua and is not an operational VIIRS-only gate.','Annual files do not establish clear-sky coverage; missing detection rows are not proof of no fire.','Local adaptation excludes known Aqua outage months August and September2020; frozen Indonesia coefficients remain unchanged.','Regions were selected for contrasting context, not to classify every hotspot by cause.','Historical baseline and audit represent past seasonal observations, not forecasts.','Audit years were excluded from local fitting; Indonesia results had already been inspected before this follow-up.']}
    payload=json.dumps(result,indent=2,allow_nan=False)+'\n'
    for p in [ROOT/'reports/transfer-cases.json',OUT/'transfer-cases.json']:p.write_text(payload,encoding='utf-8')
    (OUT/'transfer-protocol.json').write_text(json.dumps(protocol,indent=2)+'\n',encoding='utf-8')
    pd.DataFrame(ledger).to_csv(ROOT/'reports/transfer-monthly-counts.csv',index=False)
    pd.DataFrame([{'region':r['id'],**{k:v for k,v in m.items() if k!='classes'},**{k+'_category':v for k,v in m['classes'].items()}} for r in regions for m in r['months']]).to_csv(OUT/'transfer-months.csv',index=False)
    print(json.dumps({r['id']:{'metrics':r['metrics'],'seasonal':r['seasonal_windows']} for r in regions},indent=2),flush=True)

if __name__=='__main__':main()
