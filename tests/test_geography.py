import importlib.util,json,gzip,hashlib
from pathlib import Path
import pandas as pd
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('geography',ROOT/'pipeline/21_geographic_workbench.py')
g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
WORLD=ROOT/'web/public/data/world'

def test_model_has_no_held_out_or_known_outage_leakage():
 rows=[[y,m,0,0,20,10,40,20] for y in range(2019,2026) for m in range(1,13)]
 expected=g.fit_model(rows)
 for r in rows:
  if r[0]>=2022 or (r[0]==2020 and r[1] in [8,9]):r[5]=999999;r[7]=1
 assert g.fit_model(rows)==expected
 assert all(x['factor']==.5 for x in expected)

def test_filter_preserves_source_identity_confidence_and_daily_dedup():
 d=pd.DataFrame([dict(latitude=1,longitude=100,acq_date='2023-01-01',acq_time=t,satellite=s,confidence=c,version='6.1') for t,s,c in [('0100','A',80),('0200','A',80),('0300','T',90),('0400','A',10)]])
 z=g.filtered(d,'aqua');a,raw,active=g.aggregate(z,'aqua')
 assert raw==2 and active==1
 assert set(z.satellite)=={'A'}
 assert a.raw.sum()==2 and a.active.sum()==1

def test_catalog_hashes_and_world_platform_counts():
 c=json.loads((WORLD/'catalog.json').read_text(encoding='utf-8'))
 assert sum(x['sources'] for x in c['countries'])==90
 for e in c['countries']:
  b=(WORLD/e['package']).read_bytes();assert hashlib.sha256(b).hexdigest()==e['sha256']
  p=json.loads(gzip.decompress(b));score,_=g.assess(p['rows'],p['factors']);assert score==p['validation']
 b=(WORLD/c['global_recent']['path']).read_bytes();assert hashlib.sha256(b).hexdigest()==c['global_recent']['sha256']
 a=np.array(json.loads(gzip.decompress(b)))
 assert int(a[:,5].sum())==c['global_recent']['totals']['aqua']
 assert int(a[:,7].sum())==c['global_recent']['totals']['noaa20']
 assert set(a[:,0])=={2026} and set(a[:,1])=={11} and a[:,2].max()==13

def test_original_observation_export_reconciles_to_primary_month():
 for country in ['india','australia','indonesia']:
  p=json.loads(gzip.decompress((WORLD/country/'package.json.gz').read_bytes()))
  for y,m in [(2019,9),(2023,11)]:
   d=pd.read_csv(WORLD/country/f'points-{y}-{m:02}.csv.gz')
   total=next(r for r in p['totals'] if r['year']==y and r['month']==m)
   assert len(d)==total['raw_aqua' if y<=2021 else 'raw_noaa20']
   assert set(d.satellite.astype(str).str.upper()).issubset({'A','AQUA'} if y<=2021 else {'N20','NOAA-20','JPSS-1'})
   assert {'acq_time','confidence','version','latitude','longitude'}.issubset(d.columns)
