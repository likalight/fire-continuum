import requests,json
from concurrent.futures import ThreadPoolExecutor
from common import OUT,verify_input
inventory=json.loads((OUT/'geolocation-inventory.json').read_text(encoding='utf-8'))
chosen=[next(x for x in inventory[0] if '.061.' in x['id']),inventory[1][0]]
def fetch(g):
 path=OUT/g['id']
 if path.exists():data=path.read_bytes()
 else:
  r=requests.get(g['links'][0],timeout=180);r.raise_for_status();data=r.content
 verify_input(path.name,data);path.write_bytes(data)
 import hashlib
 return dict(g,sha256=hashlib.sha256(data).hexdigest(),bytes=len(data),status='downloaded')
with ThreadPoolExecutor(max_workers=2) as p:result=list(p.map(fetch,chosen))
(OUT/'geolocation-acquisition.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print('Verified two geolocation products')
