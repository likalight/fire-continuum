"""Generic country-package compiler; raw source identity and held-out errors retained.
Run python pipeline/21_geographic_workbench.py. Existing Indonesia model is unchanged.
"""
import csv,gzip,hashlib,io,json
from pathlib import Path
from datetime import datetime,timezone
import numpy as np
import pandas as pd
import requests
from pyproj import Transformer
from shapely.geometry import shape,mapping
from shapely import contains_xy,prepare
ROOT=Path(__file__).resolve().parents[1]; RAW=ROOT/'data/raw'; OUT=ROOT/'web/public/data/world'; OUT.mkdir(exist_ok=True)
BOUNDARY_URL='https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_10m_admin_0_countries.geojson'
COUNTRIES={'Indonesia':'IDN','India':'IND','Australia':'AUS'}
COLS=['year','month','x_half_degree','y_half_degree','aqua_detections','aqua_cell_days','noaa20_detections','noaa20_cell_days']
PROJECT=Transformer.from_crs(4326,6933,always_xy=True)
def digest(b):return hashlib.sha256(b).hexdigest()
def write_json(path,obj):path.write_bytes((json.dumps(obj,ensure_ascii=False,allow_nan=False,separators=(',',':'))+'\n').encode())
def gz_json(path,obj):path.write_bytes(gzip.compress(json.dumps(obj,allow_nan=False,separators=(',',':')).encode(),mtime=0))
def filtered(d,sensor,polygon=None):
 d=d.copy();required={'latitude','longitude','acq_date','acq_time','satellite','confidence','version'}
 if not required.issubset(d.columns):raise ValueError('Invalid FIRMS schema')
 if sensor=='aqua':d=d[d.satellite.astype(str).str.upper().isin(['A','AQUA']) & pd.to_numeric(d.confidence,errors='coerce').ge(30)]
 else:d=d[d.satellite.astype(str).str.upper().isin(['N20','NOAA-20','JPSS-1']) & d.confidence.astype(str).str.lower().isin(['n','h','nominal','high'])]
 d=d[d.longitude.between(-180,180,inclusive='left') & d.latitude.between(-86,86,inclusive='neither')].copy()
 if polygon is not None:d=d[contains_xy(polygon,d.longitude.to_numpy(),d.latitude.to_numpy())].copy()
 d['acq_time']=d.acq_time.astype(str).str.replace(':','',regex=False).str.zfill(4)
 d=d.drop_duplicates(['latitude','longitude','acq_date','acq_time','satellite'])
 t=pd.to_datetime(d.acq_date,errors='raise');d['year']=t.dt.year;d['month']=t.dt.month;d['day']=t.dt.day
 d['x']=np.floor(d.longitude*2).astype(int);d['y']=np.floor(d.latitude*2).astype(int)
 return d

def aggregate(d,sensor):
 keys=['year','month','day','x','y'];raw=d.groupby(keys).size().rename('raw')
 x,y=PROJECT.transform(d.longitude.to_numpy(),d.latitude.to_numpy());d=d.assign(gx=np.floor(x/1000).astype(int),gy=np.floor(y/1000).astype(int))
 u=d.sort_values(['acq_time','longitude','latitude'],kind='stable').drop_duplicates(['acq_date','gx','gy'])
 active=u.groupby(keys).size().rename('active');a=pd.concat([raw,active],axis=1).fillna(0).astype(int).reset_index()
 a['sensor']=sensor;return a,len(d),len(u)

def combined(parts,daily=False):
 cols=['year','month']+(['day'] if daily else [])+['x','y']
 a=pd.concat(parts,ignore_index=True).groupby(cols+['sensor'])[['raw','active']].sum().unstack('sensor',fill_value=0)
 for metric in ['raw','active']:
  for sensor in ['aqua','noaa20']:
   if (metric,sensor) not in a.columns:a[(metric,sensor)]=0
 return a[[('raw','aqua'),('active','aqua'),('raw','noaa20'),('active','noaa20')]].reset_index().to_numpy(dtype=int).tolist()

def fit_model(rows):
 a=np.array(rows); weights=[]
 for q in range(4):
  z=a[(a[:,0]>=2019)&(a[:,0]<=2021)&((a[:,1]-1)//3==q)&~((a[:,0]==2020)&np.isin(a[:,1],[8,9]))]
  den=z[:,7].sum();num=z[:,5].sum()
  if den<=0 or num<=0:raise ValueError('Insufficient overlap support')
  weights.append({'quarter':q,'factor':float(num/den),'aqua':int(num),'noaa20':int(den)})
 return weights

def assess(rows,weights):
 a=np.array(rows);monthly=[]
 for year in range(2003,2026):
  for month in range(1,13):
   z=a[(a[:,0]==year)&(a[:,1]==month)];s=z[:,4:].sum(axis=0) if len(z) else np.zeros(4)
   monthly.append({'year':year,'month':month,'raw_aqua':int(s[0]),'aqua':int(s[1]),'raw_noaa20':int(s[2]) if year>=2019 else None,'noaa20':int(s[3]) if year>=2019 else None,'adjusted':float(s[3]*weights[(month-1)//3]['factor']) if year>=2019 else None})
 category=lambda v,m,p:None if m<=0 else 2 if v>p else 1 if v>m else 0
 test=[]
 for r in monthly:
  if r['year']<2022:continue
  hist=[x['aqua'] for x in monthly if x['month']==r['month'] and x['year']<=2017];median=float(np.median(hist));p90=float(np.quantile(hist,.9))
  test.append(dict(r,median=median,p90=p90,aqua_category=category(r['aqua'],median,p90),adjusted_category=category(r['adjusted'],median,p90)))
 total=sum(r['aqua'] for r in test);valid=[r for r in test if r['aqua_category'] is not None]
 extreme=[r for r in valid if r['aqua_category']==2]
 return {'years':[2022,2025],'months':len(test),'wape':sum(abs(r['aqua']-r['adjusted']) for r in test)/total if total else None,'category_agreement':sum(r['aqua_category']==r['adjusted_category'] for r in valid)/len(valid) if valid else None,'reference_extreme_months':len(extreme),'missed_extreme_months':sum(r['adjusted_category']!=2 for r in extreme),'rows':test},monthly

def main():
 boundary=RAW/'world-boundaries-natural-earth.geojson'
 if not boundary.exists():
  r=requests.get(BOUNDARY_URL,timeout=90);r.raise_for_status();json.loads(r.content);boundary.write_bytes(r.content)
 feature_collection=json.loads(boundary.read_bytes());polygons={};display=[]
 for name,iso in COUNTRIES.items():
  f=next(f for f in feature_collection['features'] if f['properties']['ADM0_A3']==iso);p=shape(f['geometry']);prepare(p);polygons[name]=p
  display.append({'type':'Feature','properties':{'id':name.lower(),'name':name},'geometry':mapping(p.simplify(.035,preserve_topology=True))})
 write_json(OUT/'coverage.geojson',{'type':'FeatureCollection','features':display})
 manifests=json.loads((ROOT/'reports/source_manifest.json').read_text(encoding='utf-8'))+json.loads((ROOT/'reports/transfer-source-manifest.json').read_text(encoding='utf-8'))
 daily_sources=json.loads((ROOT/'reports/month-to-date-sources.json').read_text(encoding='utf-8'));global_frames={}
 for sensor in ['aqua','noaa20']:
  frames=[]
  for source in [s for s in daily_sources if s['sensor']==sensor]:
   b=(RAW/source['file']).read_bytes();assert digest(b)==source['sha256'];frames.append(pd.read_csv(io.BytesIO(b),dtype={'acq_time':str,'confidence':str,'version':str}))
  global_frames[sensor]=filtered(pd.concat(frames,ignore_index=True),sensor)
 global_parts=[]
 for sensor,d in global_frames.items():
  a,_,_=aggregate(d,sensor);global_parts.append(a)
 global_rows=combined(global_parts,True);gz_json(OUT/'global-recent.json.gz',global_rows)
 catalog=[]
 for name in COUNTRIES:
  country_dir=OUT/name.lower();country_dir.mkdir(exist_ok=True);parts=[];audit=[];source_list=[];points_cols=['latitude','longitude','acq_date','acq_time','satellite','confidence','frp','daynight','type','version']
  for year in range(2003,2026):
   yearparts=[]
   for sensor,prefix in [('aqua','modis'),('noaa20','viirs-jpss1')]:
    if sensor=='noaa20' and year<2019:continue
    filename=f'{prefix}_{year}_{name}.csv';source=next(s for s in manifests if s['filename']==filename);b=(RAW/filename).read_bytes();assert digest(b)==source['sha256'];source_list.append(source)
    d=filtered(pd.read_csv(io.BytesIO(b),dtype={'acq_time':str,'confidence':str,'version':str}),sensor,polygons[name]);assert d.year.eq(year).all()
    a,raw,active=aggregate(d,sensor);yearparts.append(a);audit.append({'file':filename,'retained_detections':raw,'active_cell_days':active,'versions':sorted(d.version.dropna().unique().tolist()),'source_sha256':source['sha256']})
    if (sensor=='aqua' and year<=2021) or (sensor=='noaa20' and year>=2022):
     for month in range(1,13):
      z=d[d.month==month].reindex(columns=points_cols);(country_dir/f'points-{year}-{month:02}.csv.gz').write_bytes(gzip.compress(z.to_csv(index=False,lineterminator='\n').encode(),mtime=0))
    print(name,year,sensor,raw,flush=True)
   parts+=yearparts;gz_json(country_dir/f'days-{year}.json.gz',combined(yearparts,True))
  monthly=combined(parts);weights=fit_model(monthly);score,totals=assess(monthly,weights)
  recentparts=[];recentpoints=[]
  for sensor,d in global_frames.items():
   z=d[contains_xy(polygons[name],d.longitude.to_numpy(),d.latitude.to_numpy())].copy();a,_,_=aggregate(z,sensor);recentparts.append(a);z['sensor']=sensor;recentpoints.append(z.reindex(columns=points_cols+['sensor']))
  recent=combined(recentparts,True);gz_json(country_dir/'days-2026.json.gz',recent)
  (country_dir/'points-2026-11.csv.gz').write_bytes(gzip.compress(pd.concat(recentpoints).to_csv(index=False,lineterminator='\n').encode(),mtime=0))
  bounds=[float(np.floor(polygons[name].bounds[0]*2)/2),float(np.floor(polygons[name].bounds[1]*2)/2),float(np.ceil(polygons[name].bounds[2]*2)/2),float(np.ceil(polygons[name].bounds[3]*2)/2)]
  package={'schema':'fire-continuum-geography-v1','id':name.lower(),'name':name,'bounds':bounds,'grid_degrees':.5,'years':[2003,2025],'primary_periods':[{'from':2003,'to':2021,'sensor':'aqua'},{'from':2022,'to':2025,'sensor':'noaa20'}],'columns':COLS,'rows':monthly,'factors':weights,'validation':score,'totals':totals,'baseline_years':[2003,2017],'training_years':[2019,2021],'sources':source_list,'input_audit':audit,'boundary':{'url':BOUNDARY_URL,'sha256':digest(boundary.read_bytes()),'license':'Public domain','name':'Natural Earth 1:10m administrative country outlines','mask':'Same polygon applied to historical country archives and global NRT; border/coast omissions in country archives cannot be recovered.'},'recent':{'start':'2026-11-01','end':'2026-11-13','sources':daily_sources,'rows':recent},'limits':['A separate country-quarter model; original Indonesia research model is unchanged.','Evaluation years excluded from fitting, but earlier transfer results had already been inspected; exploratory extension, not an untouched final benchmark.','Aqua is a reference, not ground truth. Country validation does not establish accuracy for an arbitrary smaller AOI.','Zero detections are not proof of no fire. Clear-sky and overpass completeness are unknown.','Known Aqua outage affects August–September 2020; those months are excluded from fitting.','Only November 1–13 is loaded for 2026; remaining 2026 dates are unavailable.','Country archives may omit border/coast observations before the identical polygon filter.','All retained thermal sources included; hotspots are neither distinct fires nor burned area.']}
  gz_json(country_dir/'package.json.gz',package);write_json(country_dir/'manifest.json',{k:v for k,v in package.items() if k not in ['rows','recent','totals']})
  catalog.append({'id':name.lower(),'name':name,'bounds':bounds,'years':[2003,2025],'package':name.lower()+'/package.json.gz','sha256':digest((country_dir/'package.json.gz').read_bytes()),'bytes':(country_dir/'package.json.gz').stat().st_size,'validation':{k:v for k,v in score.items() if k!='rows'},'sources':len(source_list)})
 report={'schema':'fire-continuum-catalog-v1','created_utc':datetime.now(timezone.utc).isoformat(),'countries':catalog,'global_recent':{'path':'global-recent.json.gz','start':'2026-11-01','end':'2026-11-13','columns':['year','month','day','x_half_degree','y_half_degree','aqua_detections','aqua_cell_days','noaa20_detections','noaa20_cell_days'],'sources':daily_sources,'sha256':digest((OUT/'global-recent.json.gz').read_bytes()),'totals':{s:len(d) for s,d in global_frames.items()},'meaning':'Worldwide observations, no worldwide harmonized baseline. Global tiles extend to ±86° latitude; missing detections do not establish no fire.'},'boundary_source':BOUNDARY_URL,'boundary_sha256':digest(boundary.read_bytes())}
 write_json(OUT/'catalog.json',report);write_json(ROOT/'reports/geographic-workbench.json',report)
 print(json.dumps(catalog,indent=2),flush=True)
if __name__=='__main__':main()
