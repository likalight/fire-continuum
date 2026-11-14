import importlib.util,json,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'pipeline'))
from global_model import evaluate
spec=importlib.util.spec_from_file_location('gp',ROOT/'pipeline/23_global_process.py');gp=importlib.util.module_from_spec(spec);spec.loader.exec_module(gp)
PROTOCOL=json.loads((ROOT/'reports/global-evaluation-protocol.json').read_text(encoding='utf-8'))

def fixture():
 rows=[]
 for year in range(2003,2026):
  for month in range(1,13):
   aqua=[80,90,100,110,130][(year-2003)%5] if year<=2017 else 100 if year<=2021 else [80,110,200][month%3]
   rows.append(dict(year=year,month=month,raw_aqua=aqua,aqua=aqua,raw_noaa20=aqua*5,noaa20=aqua*5))
 return rows

def test_perfect_supported_calibration_passes_with_rare_event_checks():
 factors,result=evaluate(fixture(),PROTOCOL)
 assert all(f['factor']==.2 for f in factors)
 assert result['status']=='agreement_checks_passed'
 assert result['wape']==0 and result['category_agreement']==1
 assert result['reference_extreme_months']==16
 assert result['primary_policy']=='aqua_then_adjusted_noaa20'

def test_failed_transfer_uses_aqua_history_and_preserves_bad_candidate():
 rows=fixture()
 for r in rows:
  if r['year']>=2022:r['noaa20']*=2
 factors,result=evaluate(rows,PROTOCOL)
 assert result['status']=='mixed_or_poor_agreement'
 assert result['primary_policy']=='aqua_only' and result['wape']==1
 assert all(f['factor']==.2 for f in factors)
 assert any(r['adjusted']!=r['aqua'] for r in result['rows'])

def test_sparse_quarter_withholds_factor_instead_of_using_zero():
 rows=fixture()
 for r in rows:
  if 2019<=r['year']<=2021 and r['month']<=3:r['aqua']=0
 factors,result=evaluate(rows,PROTOCOL)
 assert factors[0]['factor'] is None
 assert result['status']=='insufficient_support' and result['wape'] is None
 assert result['primary_policy']=='aqua_only'

def test_absence_of_rare_test_events_is_not_perfect_rare_event_validation():
 rows=fixture()
 for r in rows:
  if r['year']>=2022:r['aqua']=100;r['noaa20']=500
 _,result=evaluate(rows,PROTOCOL)
 assert result['status']=='limited_event_evidence'
 assert result['reference_extreme_months']==0 and result['category_recall'][2] is None

def test_test_years_and_known_outage_never_change_fit():
 rows=fixture();expected,_=evaluate(rows,PROTOCOL)
 for r in rows:
  if r['year']>=2022 or (r['year']==2020 and r['month'] in [8,9]):r['aqua']=99999;r['noaa20']=1
 factors,_=evaluate(rows,PROTOCOL);assert factors==expected

def test_stream_chunk_boundaries_do_not_change_duplicate_or_cell_day_results():
 rows=np.array([[20230101,100,100,1,200,2,1000,2000],[20230101,100,100,1,200,2,1000,2000],[20230101,200,100.001,1,200,2,1000,2000],[20230102,200,100.001,1,200,2,1000,2000]],float)
 full=gp.reduce_observations([rows]);chunked=gp.reduce_observations([rows[:1],rows[1:3],rows[3:]])
 assert full==chunked
 daily,retained,duplicates=full;assert retained==3 and duplicates==1
 assert sum(r[5] for r in daily)==3 and sum(r[6] for r in daily)==2

def test_all_185_boundaries_resolve_and_overseas_france_is_separate():
 from shapely.geometry import Point
 if (ROOT/'data/raw/world-map-units-natural-earth.geojson').exists():
  p=gp.boundaries()
 else:
  from shapely.geometry import shape
  coverage=json.loads((ROOT/'web/public/data/global/coverage.geojson').read_text(encoding='utf-8'))
  p={f['properties']['name'].replace(' ','_'):{'geometry':shape(f['geometry']),'record':json.loads((ROOT/'web/public/data/global'/f['properties']['id']/'manifest.json').read_text(encoding='utf-8'))['boundary']} for f in coverage['features']}
 assert len(p)==185
 assert not p['France']['geometry'].contains(Point(-53,4))
 assert p['French_Guiana']['geometry'].contains(Point(-53,4))
 assert p['Reunion']['geometry'].contains(Point(55.5,-21.1))
 assert all(x['geometry'].is_valid for x in p.values())
 assert p['Egypt']['record']['repair']=='shapely.make_valid'
