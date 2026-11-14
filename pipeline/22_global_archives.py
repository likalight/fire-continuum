"""Download the frozen 185-country corpus through NASA's 30 bulk archives.

Atomic, resumable downloads. No credentials required; raw archives remain ignored.
"""
import argparse,csv,hashlib,json,time,zipfile
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed
from datetime import datetime,timezone
import requests

ROOT=Path(__file__).resolve().parents[1]
BASE='https://firms.modaps.eosdis.nasa.gov/data/country/'
RAW=ROOT/'data/raw/global-archives'
REQUIRED={'modis':list(range(2003,2026)),'viirs-jpss1':list(range(2019,2026))}

def sha(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for block in iter(lambda:f.read(8*1024*1024),b''):h.update(block)
 return h.hexdigest()

def inventory():
 rows=list(csv.DictReader((ROOT/'reports/global-eligible-catalog.csv').read_text(encoding='utf-8').splitlines()))
 groups={}
 for r in rows:
  if not r['filename'].endswith('.csv'):continue
  sensor,year,country=r['filename'].split('_',2)
  groups.setdefault(country[:-4],{}).setdefault(sensor,set()).add(int(year))
 names=sorted(c for c,d in groups.items() if all(set(years)<=d.get(sensor,set()) for sensor,years in REQUIRED.items()))
 expected={f'{sensor}_{year}_{country}.csv' for sensor,years in REQUIRED.items() for year in years for country in names}
 archive_names={f'{sensor}_{year}_all_countries.zip' for sensor,years in REQUIRED.items() for year in years}
 return names,[r for r in rows if r['filename'] in expected],[r for r in rows if r['filename'] in archive_names]

def download(row):
 RAW.mkdir(parents=True,exist_ok=True)
 path=RAW/row['filename'];receipt=path.with_suffix('.receipt.json');url=BASE+row['filename']
 if path.exists() and receipt.exists() and path.stat().st_size==int(row['size']):
  d=json.loads(receipt.read_text(encoding='utf-8'))
  if sha(path)==d['sha256']:return d
 for attempt in range(4):
  try:
   partial=path.with_suffix('.part');h=hashlib.sha256()
   with requests.get(url,stream=True,timeout=(30,120)) as r:
    r.raise_for_status()
    with partial.open('wb') as f:
     for b in r.iter_content(4*1024*1024):f.write(b);h.update(b)
   if partial.stat().st_size!=int(row['size']):raise ValueError('Advertised archive size mismatch')
   with zipfile.ZipFile(partial) as z:
    if not z.namelist():raise ValueError('Empty archive')
   partial.replace(path)
   d=dict(row,url=url,sha256=h.hexdigest(),retrieved_utc=datetime.now(timezone.utc).isoformat())
   receipt.write_text(json.dumps(d,indent=2),encoding='utf-8')
   print('Downloaded',row['filename'],int(row['size']),flush=True);return d
  except Exception as e:
   if attempt==3:raise RuntimeError(f"{row['filename']}: {type(e).__name__}: {e}") from e
   time.sleep(2**attempt)

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--workers',type=int,default=4);args=parser.parse_args()
 names,files,archives=inventory();assert len(names)==185 and len(files)==5550 and len(archives)==30
 inventory_path=ROOT/'reports/global-source-inventory.json'
 inventory_path.write_text(json.dumps({'countries':names,'files':files,'archives':archives,'catalog_sha256':sha(ROOT/'reports/global-eligible-catalog.csv'),'created_utc':datetime.now(timezone.utc).isoformat()},indent=2),encoding='utf-8')
 results=[]
 with ThreadPoolExecutor(max_workers=args.workers) as pool:
  for future in as_completed([pool.submit(download,r) for r in archives]):
   results.append(future.result())
   (ROOT/'reports/global-archive-receipts.json').write_text(json.dumps(sorted(results,key=lambda r:r['filename']),indent=2),encoding='utf-8')
 print('Complete',len(results),'archives',flush=True)
if __name__=='__main__':main()
