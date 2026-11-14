from pathlib import Path
import requests,json,re,hashlib,io,gzip,importlib.util
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timezone
import numpy as np,pandas as pd
from shapely import contains_xy
from common import OUT, ROOT, REPORTS, verify_input
spec=importlib.util.spec_from_file_location('gp',ROOT/'pipeline/23_global_process.py');gp=importlib.util.module_from_spec(spec);spec.loader.exec_module(gp)
polygons=gp.boundaries();inventory=json.loads((OUT/'discovery.json').read_text(encoding='utf-8'))
jobs=[]
for item in inventory:
 if item['kind'] not in ['aqua_daily','noaa20_daily']:continue
 for url in item['links']:
  doy=int(re.search(r'_2026(\d{3})\.txt',url)[1])
  if 274<=doy<=304:jobs.append((item['kind'].replace('_daily',''),url))
raw=OUT/'october-raw';raw.mkdir(exist_ok=True)
def fetch(item):
 sensor,url=item;path=raw/url.rsplit('/',1)[-1]
 if path.exists():blob=path.read_bytes()
 else:
  r=requests.get(url,timeout=120);r.raise_for_status();blob=r.content
  if not blob.startswith(b'latitude,longitude,'):raise ValueError('Not a FIRMS table')
  path.write_bytes(blob)
 verify_input(path.name,blob)
 d=pd.read_csv(io.BytesIO(blob),dtype={'acq_time':str,'confidence':str,'version':str,'satellite':str});day=datetime.strptime(re.search(r'_(2026\d{3})\.txt',url)[1],'%Y%j').date()
 assert pd.to_datetime(d.acq_date).dt.date.eq(day).all()
 sat=d.satellite.str.upper();d=d[sat.isin(['A','AQUA']) if sensor=='aqua' else sat.isin(['N20','NOAA-20','JPSS-1'])].copy()
 d=d[pd.to_numeric(d.confidence,errors='coerce').ge(30) if sensor=='aqua' else d.confidence.str.lower().isin(['n','h','nominal','high'])].copy()
 pieces={}
 for name in ['Mexico','Australia']:
  poly=polygons[name]['geometry'];w,s,e,n=poly.bounds;z=d[d.longitude.between(w,e)&d.latitude.between(s,n)].copy();z=z[contains_xy(poly,z.longitude.to_numpy(),z.latitude.to_numpy())].copy();pieces[name]=z
 return {'sensor':sensor,'date':str(day),'url':url,'file':str(path.relative_to(OUT)),'bytes':len(blob),'sha256':hashlib.sha256(blob).hexdigest(),'retrieved_utc':datetime.now(timezone.utc).isoformat(),'status':'available'},pieces
results=[]
with ThreadPoolExecutor(max_workers=6) as pool:
 for v in pool.map(fetch,jobs):
  results.append(v)
  if len(results)%10==0:print('Downloaded October',len(results),'/62',flush=True)
assert len(results)==62
sources=[r[0] for r in results];countries=[]
for name in ['Mexico','Australia']:
 combined={};audits={}
 for sensor,off in [('aqua',0),('noaa20',2)]:
  d=pd.concat([v[1][name] for v in results if v[0]['sensor']==sensor],ignore_index=True)
  d.to_csv(OUT/f'{name.lower()}-{sensor}-october2026-filtered.csv',index=False)
  dates=pd.to_datetime(d.acq_date);hhmm=pd.to_numeric(d.acq_time.str.replace(':','',regex=False),errors='raise');assert ((hhmm>=0)&(hhmm<=2359)&(hhmm%100<60)).all()
  gx,gy=gp.PROJECT.transform(d.longitude.to_numpy(),d.latitude.to_numpy())
  chunks=[np.column_stack([(dates.dt.year*10000+dates.dt.month*100+dates.dt.day).to_numpy(),hhmm.to_numpy(),d.longitude.to_numpy(),d.latitude.to_numpy(),np.floor(d.longitude.to_numpy()*2),np.floor(d.latitude.to_numpy()*2),np.floor(gx/1000),np.floor(gy/1000)])] if len(d) else []
  rows,retained,duplicates=gp.reduce_observations(chunks)
  audits[sensor]={'retained':retained,'duplicates':duplicates,'cell_days':sum(r[6] for r in rows),'versions':sorted(d.version.unique().tolist())}
  for r in rows:
   key=tuple(r[:5]);v=combined.setdefault(key,[0,0,0,0]);v[off]+=r[5];v[off+1]+=r[6]
 rows=[list(k)+v for k,v in sorted(combined.items())]
 countries.append({'id':name.lower(),'name':name,'start':'2026-10-01','end':'2026-10-31','rows':rows,'sources':sources,'audit':audits,'boundary':polygons[name]['record']})
 payload=json.dumps(countries[-1],separators=(',',':'),allow_nan=False).encode();(OUT/f'{name.lower()}-october2026.json.gz').write_bytes(gzip.compress(payload,mtime=0))
report={'protocol':'protocol.json','status':'complete_october_subset_only','source_count':62,'sources':sources,'countries':[{k:v for k,v in c.items() if k not in ['rows','sources','boundary']} for c in countries],'limitations':['January-August 2026 not present in current 61-day NRT directory; no 2026 annual country files advertised.','October subset selected by source availability within predeclared January-October period, before reading counts.','Science archive and NRT processing differ. Source completeness is not cloud-free observation coverage.']}
(OUT/'october-acquisition.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report['countries'],indent=2))
