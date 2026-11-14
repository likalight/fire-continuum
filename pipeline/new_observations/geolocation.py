from pathlib import Path
import requests,json,hashlib
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timezone
from common import OUT, ROOT, REPORTS, verify_input
def query(product,time):
 r=requests.get('https://cmr.earthdata.nasa.gov/search/granules.json',params={'short_name':product,'temporal':f'2026-05-01T{time}:00Z,2026-05-01T{time}:01Z','bounding_box':'-105,20,-103,22','page_size':100},timeout=60);r.raise_for_status();entries=r.json()['feed']['entry'];(OUT/f'{product}-cmr.json').write_text(json.dumps(entries,indent=2),encoding='utf-8')
 return [{'product':product,'id':g.get('producer_granule_id'),'time':g['time_start'],'size_mb':g.get('granule_size'),'links':[l['href'] for l in g.get('links',[]) if l.get('rel','').endswith('/data#')]} for g in entries]
with ThreadPoolExecutor(max_workers=2) as p:results=list(p.map(lambda x:query(*x),[('MYD03','22:05'),('VJ103IMG','20:00')]))
(OUT/'geolocation-inventory.json').write_text(json.dumps(results,indent=2),encoding='utf-8');print(json.dumps(results,indent=2))
r=requests.get('https://firms.modaps.eosdis.nasa.gov/data/country/yearly_summary_files.txt',timeout=60);r.raise_for_status();(OUT/'annual-catalog.csv').write_text(r.text,encoding='utf-8');print('Advertised 2026 files',sum('_2026_' in x for x in r.text.splitlines()))
