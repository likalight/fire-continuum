"""Download advertised NASA FIRMS annual files; retain sizes, hashes and retrieval times."""
import csv,hashlib,io,json,time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timezone
from pathlib import Path
import requests
ROOT=Path(__file__).resolve().parents[1]
BASE='https://firms.modaps.eosdis.nasa.gov/data/country/'
def main():
 s=requests.Session();s.trust_env=False
 r=s.get(BASE+'yearly_summary_files.txt',timeout=45);r.raise_for_status()
 (ROOT/'reports/annual_catalog.csv').write_text(r.text)
 rows=[x for x in csv.DictReader(io.StringIO(r.text)) if x['filename'].endswith('_Indonesia.csv') and int(x['filename'].split('_')[1])>=2003]
 out=ROOT/'data/raw';out.mkdir(parents=True,exist_ok=True)
 def get(row):
  name=row['filename'];path=out/name;url=BASE+name
  for attempt in range(3):
   try:
    if not path.exists() or path.stat().st_size!=int(row['size']):
     session=requests.Session();session.trust_env=False
     with session.get(url,stream=True,timeout=(20,90)) as response:
      response.raise_for_status()
      with (out/(name+'.part')).open('wb') as f:
       for block in response.iter_content(1024*1024):f.write(block)
     partial=out/(name+'.part');assert partial.stat().st_size==int(row['size']), 'Advertised length differs'
     with partial.open() as f:assert {'latitude','longitude','acq_date','confidence','satellite'}<=set(next(csv.reader(f)))
     partial.replace(path)
    h=hashlib.sha256(path.read_bytes()).hexdigest()
    print('Verified',name,path.stat().st_size,flush=True)
    return dict(row,url=url,sha256=h,retrieved_utc=datetime.now(timezone.utc).isoformat())
   except Exception as e:
    if attempt==2:raise RuntimeError(f'{name}: {type(e).__name__}') from None
    time.sleep(2)
 with ThreadPoolExecutor(max_workers=6) as pool:result=list(pool.map(get,rows))
 (ROOT/'reports/source_manifest.json').write_text(json.dumps(result,indent=2))
 print('Complete:',len(result),'NASA annual files',flush=True)
if __name__=='__main__':main()
