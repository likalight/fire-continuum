"""Capture a dated, separate rolling FIRMS snapshot; never fill missing archive months."""
import io,json,hashlib
from pathlib import Path
from datetime import datetime,timezone
import requests,pandas as pd
from shapely.geometry import shape
from shapely.ops import unary_union
from shapely import contains_xy
ROOT=Path(__file__).resolve().parents[1]
def main():
 s=requests.Session();s.trust_env=False
 meta=json.loads((ROOT/'reports/boundary_metadata.json').read_text())
 r=s.get(meta['gjDownloadURL'],timeout=60);r.raise_for_status();boundary=r.json();(ROOT/'data/raw/boundary.geojson').write_text(r.text)
 polygon=unary_union([shape(f['geometry']) for f in boundary['features']]);sources=[];records=[]
 urls={'aqua':'https://firms.modaps.eosdis.nasa.gov/data/active_fire/modis-c6.1/csv/MODIS_C6_1_Global_7d.csv','noaa20':'https://firms.modaps.eosdis.nasa.gov/data/active_fire/noaa-20-viirs-c2/csv/J1_VIIRS_C2_Global_7d.csv'}
 for sensor,url in urls.items():
  r=s.get(url,timeout=60);r.raise_for_status();df=pd.read_csv(io.StringIO(r.text),dtype={'acq_time':str,'confidence':str});global_span=[str(df.acq_date.min()),str(df.acq_date.max())]
  keep=contains_xy(polygon,df.longitude.to_numpy(),df.latitude.to_numpy());df=df[keep].copy()
  if sensor=='aqua':df=df[df.satellite.isin(['Aqua','A'])&(pd.to_numeric(df.confidence)>=30)]
  else:df=df[df.confidence.str.lower().isin(['n','h','nominal','high'])]
  df=df.drop_duplicates(['latitude','longitude','acq_date','acq_time','satellite']);df['sensor']=sensor
  fields=['latitude','longitude','acq_date','acq_time','sensor','confidence','frp']
  records.extend(df[fields].to_dict('records'));sources.append({'sensor':sensor,'url':url,'sha256':hashlib.sha256(r.content).hexdigest(),'global_file_date_span':global_span,'indonesia_retained_detections':len(df),'versions':sorted(map(str,df.version.unique()))})
 result={'retrieved_utc':datetime.now(timezone.utc).isoformat(),'sources':sources,'records':records,'status':'Rolling NRT snapshot; not a complete 2026 month; unharmonized, not a live feed','boundary_source':meta['gjDownloadURL'],'boundary_attribution':'geoBoundaries / OpenStreetMap contributors, ODbL 1.0; country mask may differ from FIRMS archive assignment'}
 (ROOT/'web/public/data/recent.json').write_text(json.dumps(result,separators=(',',':'),allow_nan=False));print('Snapshot:',len(records),'retained detections',sources,flush=True)
if __name__=='__main__':main()
