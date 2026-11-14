"""Stream and reconcile all 5,550 frozen NASA country-year CSVs.

Processes one archive at a time to bound RAM. Checkpoints per CSV permit resume.
Run while downloader is active: only verified, completed ZIPs are consumed.
"""
import csv,gzip,hashlib,io,json,sys,time,zipfile
from pathlib import Path
from datetime import datetime,timezone
import numpy as np
import pandas as pd
import requests
from pyproj import Transformer
from shapely.geometry import shape
from shapely import contains_xy,prepare,make_valid,to_wkb

ROOT=Path(__file__).resolve().parents[1];RAW=ROOT/'data/raw';INTERIM=ROOT/'data/interim/global-185'
PROJECT=Transformer.from_crs(4326,6933,always_xy=True)
FIELDS=['latitude','longitude','acq_date','acq_time','satellite','confidence','version']

def digest(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()

def slug(name):return name.lower().replace('_','-')

def boundaries():
 audit=json.loads((ROOT/'reports/global-boundary-mapping.json').read_text(encoding='utf-8'))
 countries=RAW/'world-boundaries-natural-earth.geojson';units=RAW/'world-map-units-natural-earth.geojson'
 for path,url_key,hash_key in [(countries,'country_layer_url','country_layer_sha256'),(units,'map_units_url','map_units_sha256')]:
  if not path.exists():
   response=requests.get(audit[url_key],timeout=90);response.raise_for_status();assert hashlib.sha256(response.content).hexdigest()==audit[hash_key];path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(response.content)
 assert digest(countries)==audit['country_layer_sha256'];assert digest(units)==audit['map_units_sha256']
 layers={'countries':json.loads(countries.read_bytes())['features'],'map_units':json.loads(units.read_bytes())['features']};result={}
 for r in audit['rows']:
  f=next(f for f in layers[r['source_layer']] if f['properties']['NE_ID']==r['feature']['NE_ID'])
  geom=shape(f['geometry']);repaired=not geom.is_valid
  if repaired:geom=make_valid(geom)
  prepare(geom)
  result[r['firms_name']]={'geometry':geom,'record':dict(r,repair='shapely.make_valid' if repaired else None,processed_geometry_sha256=hashlib.sha256(to_wkb(geom)).hexdigest())}
 return result

class HashReader(io.RawIOBase):
 def __init__(self,source):super().__init__();self.source=source;self.hash=hashlib.sha256();self.length=0
 def readable(self):return True
 def readinto(self,buffer):
  b=self.source.read(len(buffer));self.hash.update(b);self.length+=len(b);buffer[:len(b)]=b;return len(b)

def reduce_observations(chunks):
 """Exact duplicates and cell-day representatives are resolved across chunks."""
 if not chunks:return [],0,0
 d=pd.DataFrame(np.concatenate(chunks),columns=['date','time','lon','lat','x','y','gx','gy'])
 original=len(d);d=d.drop_duplicates(['date','time','lon','lat'])
 d['year']=(d.date//10000).astype(int);d['month']=(d.date//100%100).astype(int);d['day']=(d.date%100).astype(int)
 keys=['year','month','day','x','y'];raw=d.groupby(keys).size().rename('raw')
 u=d.sort_values(['time','lon','lat'],kind='stable').drop_duplicates(['date','gx','gy'])
 active=u.groupby(keys).size().rename('active');table=pd.concat([raw,active],axis=1).fillna(0).astype(int).reset_index()
 return table.to_numpy(dtype=np.int64).tolist(),len(d),original-len(d)

def process_member(archive,member,entry,polygon,sensor,year):
 chunks=[];input_rows=0;instrument_rows=0;quality_rows=0;spatial_rows=0;versions=set();invalid_time=0
 stream=HashReader(archive.open(member));buffer=io.BufferedReader(stream)
 for d in pd.read_csv(buffer,usecols=FIELDS,chunksize=75000,dtype={'acq_time':str,'confidence':str,'version':str,'satellite':str}):
  input_rows+=len(d);sat=d.satellite.str.upper()
  d=d[sat.isin(['A','AQUA']) if sensor=='aqua' else sat.isin(['N20','NOAA-20','JPSS-1'])].copy();instrument_rows+=len(d)
  d=d[pd.to_numeric(d.confidence,errors='coerce').ge(30) if sensor=='aqua' else d.confidence.str.lower().isin(['n','h','nominal','high'])].copy();quality_rows+=len(d)
  d=d[d.longitude.between(-180,180,inclusive='left')&d.latitude.between(-86,86,inclusive='neither')].copy()
  d=d[contains_xy(polygon,d.longitude.to_numpy(),d.latitude.to_numpy())].copy();spatial_rows+=len(d)
  if not len(d):continue
  versions.update(d.version.dropna().unique().tolist());dates=pd.to_datetime(d.acq_date,errors='raise');assert dates.dt.year.eq(year).all()
  hhmm=pd.to_numeric(d.acq_time.str.replace(':','',regex=False),errors='coerce');valid=hhmm.notna()&(hhmm>=0)&(hhmm<=2359)&(hhmm%100<60)&(hhmm%1==0)
  invalid_time+=int((~valid).sum());d=d[valid];dates=dates[valid];hhmm=hhmm[valid]
  if not len(d):continue
  gx,gy=PROJECT.transform(d.longitude.to_numpy(),d.latitude.to_numpy())
  chunks.append(np.column_stack([(dates.dt.year*10000+dates.dt.month*100+dates.dt.day).to_numpy(),hhmm.to_numpy(),d.longitude.to_numpy(),d.latitude.to_numpy(),np.floor(d.longitude.to_numpy()*2),np.floor(d.latitude.to_numpy()*2),np.floor(gx/1000),np.floor(gy/1000)]))
 # Exhaustion verifies ZIP member CRC; identity includes exact original CSV bytes.
 assert stream.length==int(entry['size']),f"CSV size mismatch: {entry['filename']}"
 daily,retained,duplicates=reduce_observations(chunks)
 return {'source':dict(entry,url='https://firms.modaps.eosdis.nasa.gov/data/country/'+entry['filename'],sha256=stream.hash.hexdigest(),archive=Path(archive.filename).name,archive_member=member),'sensor':sensor,'year':year,'columns':['year','month','day','x_half_degree','y_half_degree','detections','cell_days'],'rows':daily,'audit':{'input_rows':input_rows,'instrument_rows':instrument_rows,'quality_rows_before_boundary':quality_rows,'spatial_rows':spatial_rows,'boundary_or_coordinate_exclusions':quality_rows-spatial_rows,'invalid_time_rows':invalid_time,'duplicate_rows':duplicates,'retained_detections':retained,'cell_days':sum(r[6] for r in daily),'versions':sorted(versions)}}

def main():
 inventory=json.loads((ROOT/'reports/global-source-inventory.json').read_text(encoding='utf-8'));polygons=boundaries();entries={r['filename']:r for r in inventory['files']};pending=list(inventory['archives']);done=0
 INTERIM.mkdir(parents=True,exist_ok=True)
 while pending:
  ready=[r for r in pending if (RAW/'global-archives'/r['filename']).exists() and (RAW/'global-archives'/r['filename']).with_suffix('.receipt.json').exists()]
  if not ready:time.sleep(10);continue
  for row in ready:
   path=RAW/'global-archives'/row['filename'];receipt=json.loads(path.with_suffix('.receipt.json').read_text(encoding='utf-8'));assert digest(path)==receipt['sha256']
   prefix,year,_=row['filename'].split('_',2);year=int(year);sensor='aqua' if prefix=='modis' else 'noaa20'
   with zipfile.ZipFile(path) as archive:
    members={Path(m).name:m for m in archive.namelist() if m.endswith('.csv')}
    for name in inventory['countries']:
     filename=f'{prefix}_{year}_{name}.csv';entry=entries[filename];out=INTERIM/slug(name)/f'{sensor}-{year}.json.gz';out.parent.mkdir(exist_ok=True)
     if out.exists():
      previous=json.loads(gzip.decompress(out.read_bytes()))
      if previous.get('archive_sha256')==receipt['sha256']:done+=1;continue
     if filename not in members:raise ValueError('Required member missing: '+filename)
     result=process_member(archive,members[filename],entry,polygons[name]['geometry'],sensor,year);result['archive_sha256']=receipt['sha256'];result['boundary']=polygons[name]['record'];result['processed_utc']=datetime.now(timezone.utc).isoformat()
     tmp=out.with_suffix('.part');tmp.write_bytes(gzip.compress(json.dumps(result,separators=(',',':'),allow_nan=False).encode(),compresslevel=1,mtime=0));tmp.replace(out);done+=1
     if done%25==0:print('Processed',done,'/ 5550',filename,flush=True)
   print('Archive complete',row['filename'],done,flush=True);pending.remove(row)
 print('COMPLETE',done,'country-year files',flush=True)
if __name__=='__main__':main()
