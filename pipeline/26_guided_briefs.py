"""Fast national briefings from the unchanged, hashed global packages.

No fitting or new observation claims. Recent comparisons use identical Nov 1–13
UTC dates in every year. File availability is not observation completeness.
"""
import gzip,hashlib,json
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'web/public/data/global'
OUT=ROOT/'web/public/data/briefs'

def run():
 OUT.mkdir(exist_ok=True)
 catalog=json.loads((DATA/'catalog.json').read_text(encoding='utf-8'));receipts=[]
 for c in catalog['countries']:
  blob=(DATA/c['package']).read_bytes()
  assert hashlib.sha256(blob).hexdigest()==c['sha256']
  p=json.loads(gzip.decompress(blob));recent=[];daily_sources=[]
  for year in range(2003,2027):
   path=DATA/c['id']/f'days-{year}.json.gz';b=path.read_bytes();rows=np.asarray(json.loads(gzip.decompress(b)),dtype=float).reshape(-1,9)
   z=rows[(rows[:,1]==11)&(rows[:,2]<=13)]
   a=z[:,5:9].sum(axis=0);factor=p['factors'][3]['factor']
   recent.append(dict(year=year,raw_aqua=int(a[0]),aqua=int(a[1]),raw_noaa20=int(a[2]) if year>=2019 else None,noaa20=int(a[3]) if year>=2019 else None,adjusted=float(a[3]*factor) if year>=2019 and factor is not None else None))
   daily_sources.append(dict(year=year,path=f'global/{c["id"]}/days-{year}.json.gz',sha256=hashlib.sha256(b).hexdigest()))
  totals=[]
  for t in p['totals']:
   f=p['factors'][(t['month']-1)//3]['factor'];totals.append({**t,'noaa20':t['noaa20'] if t['year']>=2019 else None,'raw_noaa20':t['raw_noaa20'] if t['year']>=2019 else None,'adjusted':t['noaa20']*f if t['year']>=2019 and f is not None else None})
  result=dict(schema='fire-continuum-guided-brief-v1',id=c['id'],name=c['name'],bounds=p['bounds'],primary_policy=p['primary_policy'],validation=p['validation'],monthly=totals,recent=recent,recent_start='2026-11-01',recent_end='2026-11-13',baseline=[2003,2017],source_package=c['package'],source_package_sha256=c['sha256'],daily_sources=daily_sources,sources=p['sources'],limitations=p['limits'])
  payload=json.dumps(result,allow_nan=False,separators=(',',':')).encode();out=gzip.compress(payload,mtime=0);(OUT/f'{c["id"]}.json.gz').write_bytes(out)
  receipts.append(dict(id=c['id'],sha256=hashlib.sha256(out).hexdigest(),bytes=len(out)))
 (OUT/'manifest.json').write_text(json.dumps(dict(countries=receipts,scope='Unchanged national models; exact-date November snapshot; observation completeness unknown'),indent=2)+'\n',encoding='utf-8')
 print(f'Built {len(receipts)} briefings, {sum(x["bytes"] for x in receipts):,} bytes compressed')
if __name__=='__main__':run()
