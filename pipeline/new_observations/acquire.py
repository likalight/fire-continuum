from pathlib import Path
import json,requests,hashlib
from datetime import datetime,timezone
from concurrent.futures import ThreadPoolExecutor
from common import OUT, ROOT, REPORTS, verify_input
inventory=json.loads((OUT/'discovery.json').read_text(encoding='utf-8'))
jobs=[]
for item in inventory:
 if item['kind'] not in ['MYD14','VJ114IMG']:continue
 g=next(x for x in item['granules'] if x['daynight']=='DAY');url=next(u for u in g['links'] if u.endswith(('.hdf','.nc')));jobs.append((item['kind'],url))
for country in ['Mexico','Australia']:
 for sensor in ['modis','viirs-jpss1']:jobs.append((country+'-'+sensor,'https://firms.modaps.eosdis.nasa.gov/data/country/'+sensor+'_2026_'+country+'.csv'))
def fetch(item):
 kind,url=item
 try:
  r=requests.get(url,timeout=120);result={'kind':kind,'url':url,'http':r.status_code,'retrieved_utc':datetime.now(timezone.utc).isoformat(),'bytes':len(r.content),'content_type':r.headers.get('Content-Type')}
  valid=r.status_code==200 and (r.content[:4]==b'\x0e\x03\x13\x01' or r.content[:8]==b'\x89HDF\r\n\x1a\n' or (url.endswith('.csv') and r.content.startswith(b'latitude,longitude,')))
  if valid:
   path=OUT/url.rsplit('/',1)[-1];verify_input(path.name,r.content);path.write_bytes(r.content);result.update(status='downloaded',file=path.name,sha256=hashlib.sha256(r.content).hexdigest())
  else:result['status']='not_valid_product'
  return result
 except Exception as e:return {'kind':kind,'url':url,'status':'request_failed','error':type(e).__name__}
with ThreadPoolExecutor(max_workers=4) as p:results=list(p.map(fetch,jobs))
(OUT/'acquisition.json').write_text(json.dumps(results,indent=2),encoding='utf-8');print(json.dumps(results,indent=2))
