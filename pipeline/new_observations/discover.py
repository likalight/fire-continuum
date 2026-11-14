from pathlib import Path
import requests,json,re,hashlib
from datetime import datetime,timezone
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urljoin
from common import OUT, ROOT, REPORTS, verify_input
urls={
 'country':'https://firms.modaps.eosdis.nasa.gov/data/country/',
 'aqua_daily':'https://nrt3.modaps.eosdis.nasa.gov/archive/FIRMS/modis-c6.1/Global/',
 'noaa20_daily':'https://nrt3.modaps.eosdis.nasa.gov/archive/FIRMS/noaa-20-viirs-c2/Global/',
}
def get_directory(item):
 key,url=item
 try:
  r=requests.get(url,timeout=60);r.raise_for_status()
  links=sorted(set(urljoin(url,x) for x in re.findall(r'href=[\"\']([^\"\']+)',r.text)))
  (OUT/f'{key}-directory.html').write_text(r.text,encoding='utf-8')
  relevant=[x for x in links if ('2026' in x and (key!='country' or any(c in x for c in ['Mexico','Australia','all_countries'])))]
  dates=sorted(set(re.findall(r'_2026(\d{3})\.txt',r.text)))
  return {'kind':key,'url':url,'http':r.status_code,'links':relevant,'first_doy':dates[0] if dates else None,'last_doy':dates[-1] if dates else None,'daily_count':len(dates)}
 except Exception as e:return {'kind':key,'url':url,'error':type(e).__name__}
def cmr(product):
 params={'short_name':product,'temporal':'2026-05-01T00:00:00Z,2026-05-01T23:59:59Z','bounding_box':'-105,20,-103,22','page_size':100}
 r=requests.get('https://cmr.earthdata.nasa.gov/search/granules.json',params=params,timeout=60);r.raise_for_status();data=r.json();(OUT/f'{product}-cmr.json').write_text(json.dumps(data,indent=2),encoding='utf-8')
 return {'kind':product,'query':params,'granules':[{'id':g.get('producer_granule_id'),'cmr_id':g['id'],'time':g['time_start'],'daynight':g.get('day_night_flag'),'links':[l['href'] for l in g.get('links',[]) if l.get('rel','').endswith('/data#')]} for g in data['feed']['entry']]}
if __name__=='__main__':
 with ThreadPoolExecutor(max_workers=5) as p:
  jobs=[p.submit(get_directory,x) for x in urls.items()]+[p.submit(cmr,x) for x in ['MYD14','VJ114IMG']]
  results=[]
  for j in jobs:
   try:results.append(j.result())
   except Exception as e:results.append({'error':type(e).__name__})
 (OUT/'discovery.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
 print(json.dumps(results,indent=2))
